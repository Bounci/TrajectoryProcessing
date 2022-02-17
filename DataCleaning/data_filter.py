# -*- coding: utf-8 -*-
# author: Bounci
# time: 2022/2/16
# description: ①处理时间戳重复的轨迹点
#              处理策略：取相同时间戳点的均值替代所有同时刻点。
#              ②剔除给定范围经纬度范围外的数据
#              处理策略：遇到范围外的点即切断，存为单独的子轨迹文件，删除范围外的点；剔除少于3个点的轨迹段。

import os
import pandas as pd
import shutil  # 复制文件需要使用
from shapely.geometry import Polygon, Point
import FileOperation.traj_read_and_write as trw


def repetition_filter(trajectory):
    """
    过滤时间戳重复的轨迹点。

    :param trajectory: 轨迹数据
    :return: 时间戳去重后的轨迹数据
    """
    # 获取各个时间戳第一条数据
    traj = trajectory.drop_duplicates(subset='timestamp', keep="first", inplace=False).copy()
    # 按时间戳分组，计算各组数据lat、lon的均值
    location_mean = pd.DataFrame(trajectory.groupby('timestamp', as_index=False)[['lat', 'lon']].mean())
    # 将位置坐标均值赋予相应时间戳轨迹点
    traj.loc[:, 'lat'] = location_mean['lat'].values  # 若不加.values则会报错
    traj.loc[:, 'lon'] = location_mean['lon'].values
    return traj


def scope_filter(trajectory, output_path):
    """
    筛选北京范围内的轨迹数据，并存储。

    :param trajectory: 待筛选范围轨迹数据
    :param output_path: 轨迹输出路径
    """
    # sub_traj_index 初始轨迹文件索引为0
    sub_traj_index = 0
    # 构造范围矩形
    polygon = Polygon([(39.3, 115.3), (39.3, 117.6), (41.1, 117.6), (41.1, 39.3)])
    # 输出轨迹点起始索引
    sub_traj_start = 0
    # 轨迹是否被切断的标记
    traj_is_cut = False
    num = 0  # 记录删除了多少个点
    org_traj_num = len(trajectory)  # 原始轨迹点数
    # 逐点判断轨迹点是否在范围内
    for point_num in range(0, org_traj_num):
        traj_point = Point(trajectory.iloc[point_num, 0], trajectory.iloc[point_num, 1])
        # 若点在范围外,则删除，并切断轨迹
        if not polygon.contains(traj_point):
            num += 1
            # 获取子轨迹片段
            sub_traj = trajectory[sub_traj_start: point_num]
            trajectory.drop(axis=0, index=point_num, inplace=True)  # 删除范围外的点
            traj_is_cut = True
            sub_traj_start = point_num + 1  # 更新输出轨迹起始索引
            sub_traj2txt(sub_traj, output_path, sub_traj_index)
            sub_traj_index += 1
        # 轨迹经过裁剪且最后一个点在范围内
        if traj_is_cut & point_num == org_traj_num:
            sub_traj = trajectory[sub_traj_start: point_num]
            sub_traj2txt(sub_traj, output_path, sub_traj_index)
    # 轨迹未被裁剪，则直接存储整条轨迹
    if not traj_is_cut:
        # 轨迹输出路径+具体文件名
        sub_traj_path = "{}.txt".format(output_path)
        trajectory.to_csv(sub_traj_path, sep=',', index=False, header=True)
    print("范围外：", num)


def sub_traj2txt(sub_traj, output_path, sub_traj_index):
    """
    将裁剪出的子轨迹保存为txt文档。

    :param sub_traj: 子轨迹dataframe
    :param output_path: 输出路径
    :param sub_traj_index: 子轨迹编号
    """
    # 判断子轨迹点数量是否小于3，对于少于3个轨迹点的轨迹不另存为txt
    if len(sub_traj) < 3:
        return
    sub_traj_path = "{0}_{1}.txt".format(output_path, sub_traj_index)
    sub_traj.to_csv(sub_traj_path, sep=',', index=False, header=True)


def traj_filter_one_folder(folder_path, output_path):
    """
    过滤时间戳重复的轨迹点及北京范围外的轨迹点。(单个文件夹)

    :param folder_path: 欲处理的轨迹文件所属志愿者编号文件夹路径。
    :param output_path: 轨迹输出文件夹路径。
    :return: traj处理后的轨迹
    """
    # 轨迹文件所在文件夹路径
    traj_folder_path = os.path.join(folder_path, "Trajectory")
    traj_file_list = os.listdir(traj_folder_path)  # 获取所有轨迹文件名
    traj_file_num = len(traj_file_list)  # 轨迹文件数量

    for traj_file_index in range(0, traj_file_num):

        traj_file_name = traj_file_list[traj_file_index]  # 获取轨迹文件名，后续输出轨迹片段也要使用
        traj_path = os.path.join(traj_folder_path, traj_file_name)  # 轨迹文件所在路径
        # 读取轨迹数据
        trajectoryDF = trw.read_traj_txt(traj_path)

        # 轨迹输出路径
        sub_traj_path = os.path.join(output_path, traj_file_name.split('.')[0])

        # 判断轨迹是否存在时间戳[timestamp]重复的问题；若不存在，则进行范围筛选处理
        if not trajectoryDF.timestamp.duplicated().any():
            # 筛选北京范围内的数据
            scope_filter(trajectoryDF, sub_traj_path)
            continue
        # 存在重复
        traj = repetition_filter(trajectoryDF)
        # 筛选北京范围内的数据
        scope_filter(traj, sub_traj_path)


def traj_filter(data_path, output_path):
    """
    批量处理：过滤时间戳重复及北京范围外的轨迹点。

    :param data_path: 要处理的轨迹数据文件夹路径。
    :param output_path: 轨迹文件存储路径。
    """
    # 获取轨迹文件夹列表
    traj_folder_list = os.listdir(data_path)
    # 对数据文件夹中的各个文件进行操作
    for folder_name in traj_folder_list:
        # 各个志愿者轨迹文件路径 eg.010……
        traj_folder_path = os.path.join(data_path, folder_name)
        # 如 E:\Users\Desktop\Traffic_Pattern_Mining\2_TrajectoryModeClassify\3_Data\Process_01\010
        # 判断该文件是否为文件夹：是，则进行同时间戳点去重；否，不处理跳过。
        if not os.path.isdir(traj_folder_path):
            continue

        # 处理后的轨迹数据输出路径
        output_path = os.path.join(output_path, folder_name)
        out_traj_path = os.path.join(output_path, "Trajectory")
        # 判断输出文件夹是否存在，若不在，则创建。
        if not os.path.exists(output_path):
            os.mkdir(output_path)
            os.mkdir(out_traj_path)
            # 原始labels文件路径
            raw_file_path = os.path.join(traj_folder_path, "labels.txt")
            # 复制至
            txt_path = os.path.join(output_path, "labels.txt")
            shutil.copyfile(raw_file_path, txt_path)  # 复制labels.txt
        # 去重选范围
        traj_filter_one_folder(traj_folder_path, out_traj_path)


if __name__ == '__main__':
    path = "E:/Users/Desktop/Traffic_Pattern_Mining/2_TrajectoryModeClassify/3_Data/Process_01"
    output = "E:/Users/Desktop/Traffic_Pattern_Mining/2_TrajectoryModeClassify/3_Data/Training_traj_segments_02"
    traj_filter(path, output)

    # df = {'id': [1, 2, 3, 4, 1, 1, 2, 4], 'score': [2, 2, 4, 5, 6, 2, 4, 3], 'dis': [3, 4, 4, 3, 3, 6, 6, 8]}
    # df = pd.DataFrame(df)
    # print(df)
    # df2 = df.drop_duplicates(subset='id', keep="first", inplace=False).copy()
    # print(df2)
    # score_sum = pd.DataFrame(df.groupby('id', as_index=False)[['score', 'dis']].sum())
    # # score_sum.rename(columns={'score': '总分'}, inplace=True)
    # print(score_sum)
    # df2.loc[:, 'score'] = score_sum['score']
    # print(df2)
