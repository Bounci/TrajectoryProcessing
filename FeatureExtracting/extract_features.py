# -*- coding: utf-8 -*-
# author: Bounci
# time: 2022/2/20
# description: 提取各轨迹点的基本特征，如速度、加速度、转向角度。
#              提取轨迹点间的特征：时间、距离等
#              提取90速度、最大加速度……
import math
import os
import pandas as pd
import FileOperation.traj_read_and_write as trw


def delta_time(t1, t2):
    """
    计算时间间隔（s）。

    :param t1: i-1点的时间戳
    :param t2: i点的时间戳（datetime）
    :return: delta_T 时间间隔（s）
    """
    return (t2 - t1).total_seconds()


def cal_distance(lat1, lon1, lat2, lon2):
    """
    半正矢公式计算两点间的距离（m）。

    :param lat1: 前一点的纬度
    :param lon1: 前一点的经度
    :param lat2: 后一点的纬度
    :param lon2: 后一点的经度
    :return: 两点间的距离。
    """
    R = 6378137.0  # 地球半径，单位：米
    dlat = math.radians(lat2 - lat1)  # 两点纬度之差
    dlon = math.radians(lon2 - lon1)  # 两点经度之差
    # 计算两点距离的公式
    s = 2 * math.asin(math.sqrt(math.pow(math.sin(dlat / 2), 2) +
                                math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
                                math.pow(math.sin(dlon / 2), 2)))
    s = s * R  # 弧长乘地球半径，半径为米

    return round(s, 4)


def get_velocity(distance, delta_T):
    """
    计算平均速度（m/s）。

    :return: 两点间平均速度
    """
    return round(distance / delta_T, 4)


def get_accelerate(v1, v2, delta_T):
    """
    计算加速度（m/s）。

    :param v1: 前一点的速度
    :param v2: 后一点的速度
    :param delta_T: 时间间隔 s
    :return:加速度 m/s
    """
    return round((v2 - v1) / delta_T, 4)


def get_azimuth(lat1, lon1, lat2, lon2):
    """
    计算航向（度）。
    极坐标法：可用于地球上任意两点间航向的求算，将地球放在一个球坐标系中并适当
    调整三个参数的起始点以减少后面的运算量，然后将各点由球坐标转化为直角坐标，
    然后依据平面法向量的定理求得二面夹角也就是航向，然后转化为符合航向定义的度数。

    :param lat1: 前一点的纬度
    :param lon1: 前一点的经度
    :param lat2: 后一点的纬度
    :param lon2: 后一点的经度
    :return:
    """
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    x = math.sin(lon2_rad - lon1_rad) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(
        lon2_rad - lon1_rad)
    bearing = math.atan2(x, y)  # 方向角，返回值单位为 弧度
    bearing = 180 * bearing / math.pi
    bearing = float((bearing + 360.0) % 360.0)
    return round(bearing, 3)


def get_steering_angle(azimuth1, azimuth2):
    """
    计算转向角（度），范围 0~180度。

    :param azimuth1: 前一段的方位角
    :param azimuth2: 后一段的方位角
    :return: 转向角
    """
    if azimuth2 <= 180 + azimuth1:
        steering_angle = abs(azimuth1 - azimuth2)
    else:
        steering_angle = abs(360 + azimuth1 - azimuth2) % 360
    return round(steering_angle, 3)


def cal_common_feature(trajDF):
    """
    计算包括①与前一点的距离 ②速度 ③加速度 ④航向角 ⑤转向角 在内的轨迹点特征。

    :param trajDF: 轨迹数据
    :return: 添加特征属性后的trajDF
    """
    distance = [0]  # 第1点的距离默认为0
    velocity = [0]  # 第1点的速度默认为0
    accelerate = [0]  # 第1点的加速度默认为0
    bearing = []  # 航向
    # 起点处的航向
    azimuth = get_azimuth(trajDF.iloc[0, 0], trajDF.iloc[0, 1], trajDF.iloc[1, 0], trajDF.iloc[1, 1])
    bearing.append(azimuth)
    steering_angle = [0]  # 转向角，第一点和最后一点默认为0
    for i in range(1, len(trajDF)):
        deltaT = delta_time(trajDF.iloc[i - 1, 3], trajDF.iloc[i, 3])  # 与前一点的时间差 s
        # 计算距离 m
        s = cal_distance(trajDF.iloc[i - 1, 0], trajDF.iloc[i - 1, 1], trajDF.iloc[i, 0], trajDF.iloc[i, 1])
        distance.append(s)  # 第i点与前一点的距离
        # 计算速度
        vi = get_velocity(s, deltaT)
        velocity.append(vi)
        # 计算加速度
        ai = get_accelerate(velocity[i], velocity[i - 1], deltaT)
        accelerate.append(ai)
        if i != len(trajDF) - 1:
            # 计算航向角
            azimuth = get_azimuth(trajDF.iloc[i, 0], trajDF.iloc[i, 1], trajDF.iloc[i + 1, 0], trajDF.iloc[i + 1, 1])
            bearing.append(azimuth)
            # 计算转向角
            steer = get_steering_angle(bearing[i - 1], bearing[i])
            steering_angle.append(steer)
        else:
            bearing.append(0)  # 最后一点的航向角默认为0
            steering_angle.append(0)  # 最后一点的转向角默认为0
    trajDF['distance'] = distance
    trajDF['velocity'] = velocity
    trajDF['accelerate'] = accelerate
    trajDF['bearing'] = bearing
    trajDF['steering_A'] = steering_angle
    return trajDF


def add_features_to_txt(path):
    """
    给轨迹文件中各轨迹点添加特征值。

    :param path: 轨迹文件存放路径
    :return:
    """
    traj_files = os.listdir(path)  # 轨迹文件列表
    # 依次处理每个轨迹文件
    for file in traj_files:
        traj_path = os.path.join(path, file)
        trajDF = trw.read_mode_traj(traj_path)  # 由于经过前期处理，每条轨迹点数不为0，故可不讨论为0的情况
        featureDF = cal_common_feature(trajDF)
        featureDF.to_csv(traj_path, sep=',', index=False, header=True)


def extract_distance_part(trajDF):
    """
    提取特征向量中的 距离部分。
    """
    distance = [trajDF['distance'].sum()]
    return distance


def extract_velocity_part(trajDF):
    """
    提取特征向量中的 速度部分。
    """
    velocity = []
    v_max = trajDF['velocity'].max()  # 最大值
    v_quantile = round(trajDF['velocity'].quantile([0.95, 0.75, 0.5, 0.25]), 4)  # 分位数
    v_mean = round(trajDF['velocity'].mean(), 4)  # 均值
    v_var = round(trajDF['velocity'].var(), 4)  # 方差
    v_r = v_max - trajDF['velocity'].min()  # 极差
    velocity.append(v_max)
    velocity.append(v_quantile.iloc[0])
    velocity.append(v_quantile.iloc[1])
    velocity.append(v_quantile.iloc[2])
    velocity.append(v_quantile.iloc[3])
    velocity.append(v_mean)
    velocity.append(v_var)
    velocity.append(v_r)
    return velocity


def extract_accelerate_part(trajDF):
    """
    提取特征向量中的 加速度部分。
    """
    accelerate = []
    a_max = trajDF['accelerate'].max()  # 最大值
    a_quantile = round(trajDF['accelerate'].quantile([0.95, 0.75, 0.5, 0.25]), 4)  # 分位数
    a_mean = round(trajDF['accelerate'].mean(), 4)  # 均值
    a_var = round(trajDF['accelerate'].var(), 4)  # 方差
    a_r = a_max - trajDF['accelerate'].min()  # 极差
    accelerate.append(a_max)
    accelerate.append(a_quantile.iloc[0])
    accelerate.append(a_quantile.iloc[1])
    accelerate.append(a_quantile.iloc[2])
    accelerate.append(a_quantile.iloc[3])
    accelerate.append(a_mean)
    accelerate.append(a_var)
    accelerate.append(a_r)
    return accelerate


def extract_bearing_part(trajDF):
    """
    提取特征向量中的 航向角部分。
    """
    bearing = []
    b_max = trajDF['bearing'].max()  # 最大值
    b_quantile = round(trajDF['bearing'].quantile([0.95, 0.75, 0.5, 0.25]), 4)  # 分位数
    b_mean = round(trajDF['bearing'].mean(), 4)  # 均值
    b_var = round(trajDF['bearing'].var(), 4)  # 方差
    b_r = b_max - trajDF['bearing'].min()  # 极差
    bearing.append(b_max)
    bearing.append(b_quantile.iloc[0])
    bearing.append(b_quantile.iloc[1])
    bearing.append(b_quantile.iloc[2])
    bearing.append(b_quantile.iloc[3])
    bearing.append(b_mean)
    bearing.append(b_var)
    bearing.append(b_r)
    return bearing


def extract_steering_part(trajDF):
    """
    提取特征向量中的 转向角部分。
    """
    steering = []
    s_max = trajDF['steering_A'].max()  # 最大值
    s_quantile = round(trajDF['steering_A'].quantile([0.95, 0.75, 0.5, 0.25]), 4)  # 分位数
    s_mean = round(trajDF['steering_A'].mean(), 4)  # 均值
    s_var = round(trajDF['steering_A'].var(), 4)  # 方差
    s_r = s_max - trajDF['steering_A'].min()  # 极差
    steering.append(s_max)
    steering.append(s_quantile.iloc[0])
    steering.append(s_quantile.iloc[1])
    steering.append(s_quantile.iloc[2])
    steering.append(s_quantile.iloc[3])
    steering.append(s_mean)
    steering.append(s_var)
    steering.append(s_r)
    return steering


def extract_features(path, target_path):
    """
    提取每条轨迹的特征。

    :param path: 带特征的轨迹文件存放路径
    :param target_path: 特征存放路径
    """
    traj_files = os.listdir(path)  # 轨迹文件列表
    # 依次处理每个轨迹文件
    for file in traj_files:
        feature_vector = []  # 由5部分组成：距离、速度、加速度、航向角、转向角
        traj_path = os.path.join(path, file)
        trajDF = trw.read_traj_with_feature(traj_path)
        feature_vector.extend(extract_distance_part(trajDF))
        feature_vector.extend(extract_velocity_part(trajDF))
        feature_vector.extend(extract_accelerate_part(trajDF))
        feature_vector.extend(extract_bearing_part(trajDF))
        feature_vector.extend(extract_steering_part(trajDF))
        # 将特征保存为文本
        pd.DataFrame([feature_vector]).to_csv(os.path.join(target_path, file), sep=',', index=False, header=False)


if __name__ == '__main__':
    # 计算轨迹点的特征
    file_path = r"E:\Users\Desktop\Traffic_Pattern_Mining\2_TrajectoryModeClassify\3_Data\Sub_traj_with_feature"
    # add_features_to_txt(file_path)

    # file_path = r"E:\Users\Desktop\Traffic_Pattern_Mining\2_TrajectoryModeClassify\3_Data\test"
    # 提取轨迹特征 33个
    save_path = r"E:\Users\Desktop\Traffic_Pattern_Mining\2_TrajectoryModeClassify\3_Data\Traj_extracted_features"
    extract_features(file_path, save_path)
    # a1 = get_azimuth(40.14023, 116.88945, 40.12394, 117.05897)
    # a2 = get_azimuth(40.12394, 117.05897, 41.345, 118.276)
    # print(get_steering_angle(a1, a2))
