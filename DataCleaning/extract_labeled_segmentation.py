# -*- coding: utf-8 -*-
# author: Bounci
# time: 2022/1/11
# description: 按标签文件提取有出行方式的轨迹片段，并剔除北京市范围外的轨迹
#              处理时默认轨迹数据文件按时间顺序排列

import os
import pandas as pd
import numpy as np


def read_label_txt(folder_path):
    """
    读取出行方式标签文件。

    :param folder_path: 标签文件所在文件夹路径
    :return: labelDF标签文件数据表
    """
    # 出行方式标签文件所在路径
    txt_path = os.path.join(folder_path, "labels.txt")
    column_name = ['start_time', 'end_time', 'mode']
    # 读取标签文件,names指定列名，skiprows指定跳过第1行数据，
    labelDF = pd.read_csv(txt_path, sep='\t', header=None, names=column_name, skiprows=1)
    # 原始读取数据类型均为str，需要将时间转换为datetime类型，便于后续据时间分段轨迹
    labelDF['start_time'] = pd.to_datetime(labelDF['start_time'], format='%Y/%m/%d %H:%M:%S')
    labelDF['end_time'] = pd.to_datetime(labelDF['end_time'], format='%Y/%m/%d %H:%M:%S')

    # print(labelDF.shape)  # 输出数据表大小
    # print(type(labelDF['start_time'][0]))
    # print(type(labelDF['end_time'][0]))
    # print(type(labelDF['mode'][0]))
    # print(labelDF.head())
    return labelDF


def read_traj_txt(traj_txt_path):
    """
    读取轨迹数据文件。

    :param traj_txt_path: 轨迹数据文件路径
    :return: trajDF轨迹数据表
    """
    column_name = ['lat', 'lon', '0', 'alt', 'datetime', 'date', 'time']
    # 读取轨迹数据文件
    trajDF = pd.read_csv(traj_txt_path, sep=',', header=None, names=column_name)
    # 删除0和datetime列的数据（无意义/不使用）
    trajDF.drop(['0', 'datetime'], axis=1, inplace=True)
    # 将日期和时间列合并，并转为datetime类型数据
    trajDF['timestamp'] = trajDF['date'] + ' ' + trajDF['time']
    trajDF['timestamp'] = pd.to_datetime(trajDF['timestamp'], format='%Y/%m/%d %H:%M:%S')
    trajDF.drop(['date', 'time'], axis=1, inplace=True)

    print(trajDF.shape)  # 输出数据表大小
    # print(type(trajDF['lat'][0]))
    # print(type(trajDF['timestamp'][0]))
    # print(trajDF.head())
    return trajDF


def traj_segmentation_one_folder(folder_path, output_path):
    """
    根据交通方式标签文件分割轨迹片段（实验标准数据准备阶段）。

    :param folder_path: 欲处理的轨迹文件所属志愿者编号文件夹路径。
    :param output_path: 子轨迹输出文件夹路径。
    :return:
    """
    # 读取交通方式标签数据
    labelsDF = read_label_txt(folder_path)
    label_num = labelsDF.shape[0]  # 交通方式标签数据行数
    traj_folder_path = os.path.join(folder_path, "Trajectory")  # 轨迹文件所在文件夹路径
    traj_file_list = os.listdir(traj_folder_path)  # 获取所有轨迹文件名
    traj_file_num = len(traj_file_list)  # 轨迹文件数量
    traj_file_index = 0  # 初始轨迹文件索引为0
    sub_traj_id = 1  # 子轨迹id

    traj_file_name = traj_file_list[traj_file_index]  # 获取轨迹文件名，后续输出轨迹片段也要使用
    traj_path = os.path.join(traj_folder_path, traj_file_name)  # 轨迹文件所在路径
    # 读取轨迹数据
    trajectoryDF = read_traj_txt(traj_path)
    is_traj_left = True  # 判断当前轨迹数据是否还有数据未遍历，初始情况下无需读取轨迹数据文件，为Ture

    # 根据交通方式标签数据，依次划分轨迹片段，并另存为轨迹片段文件
    for ilabel in range(0, label_num):
        seg_start_time = labelsDF.iloc[ilabel, 0]  # 轨迹段开始时间
        seg_end_time = labelsDF.iloc[ilabel, 1]  # 轨迹段结束时间
        seg_mode = labelsDF.iloc[ilabel, 2]  # 轨迹段交通模式

        # 轨迹文件已经处理完，标签数据还有剩余的情况
        if traj_file_index >= traj_file_num:
            return

        # 依次读取每个轨迹文件夹中的轨迹数据
        while traj_file_index < traj_file_num:
            # 判断当前轨迹数据表中是否还有数据未遍历，初始情况下
            if not is_traj_left:
                sub_traj_id = 1  # 子轨迹id，以轨迹文件为单次递增空间，输出子轨迹时使用
                traj_file_name = traj_file_list[traj_file_index]  # 获取轨迹文件名，后续输出轨迹片段也要使用
                traj_path = os.path.join(traj_folder_path, traj_file_name)  # 轨迹文件所在路径
                trajectoryDF = read_traj_txt(traj_path)  # 读取轨迹数据

                print(traj_path)  # 输出当前处理轨迹数据路径

            traj_start_time = trajectoryDF.iloc[0, 3]  # 轨迹文件起始时间
            traj_end_time = trajectoryDF.iloc[-1, 3]  # 轨迹文件结束时间
            sub_traj_output_start = 0  # 子轨迹起始索引
            sub_traj_output_end = 0  # 子轨迹终止索引

            # 标记开始时间晚于轨迹文件结束时间，说明该轨迹文件无对应交通方式标签
            # 读取并处理下一轨迹数据文件
            if seg_start_time >= traj_end_time:
                traj_file_index = traj_file_index + 1  # 获取下一个文件名索引
                is_traj_left = False  # 需要读取新的轨迹文件
                continue

            # 标记轨迹段结束时间早于轨迹文件起始时间，说明该标签①无对应轨迹；②标记时间范围轨迹分割已结束
            # 进行下一个标签段的处理
            if seg_end_time < traj_start_time:
                is_traj_left = True  # 不读取新的轨迹文件
                break

            # 标签结束时间在轨迹文件起始时间之后，说明可能有对应轨迹数据
            if seg_end_time >= traj_start_time:
                # 情景一：轨迹数据起始时间早于等于标签起始时间，遍历定位轨迹数据在标签范围内的起始索引
                if seg_start_time >= traj_start_time:
                    # 按行遍历轨迹数据，定位标签范围内的子轨迹起始索引、终止索引
                    for index, row in trajectoryDF.iterrows():
                        # 遍历定位晚于标签起始时间的轨迹数据索引
                        if row['timestamp'] < seg_start_time:
                            sub_traj_output_start = index + 1
                        # 遍历定位标签范围内的子轨迹结束索引
                        if row['timestamp'] <= seg_end_time:
                            sub_traj_output_end = index
                        # 若某处轨迹数据时间晚于标签结束时间，此时轨迹数据还未遍历结束，跳出遍历
                        if row['timestamp'] > seg_end_time:
                            is_traj_left = True  # 提前结束，还有轨迹数据未遍历，不读取新的轨迹文件
                            break
                        is_traj_left = False  # 需要读取新的轨迹文件

                # 情景二：轨迹数据起始时间晚于标签起始时间，要输出的轨迹数据起始索引为0
                if seg_start_time < traj_start_time:
                    # 按行遍历轨迹数据，定位标签范围内的子轨迹起始索引、终止索引
                    for index, row in trajectoryDF.iterrows():
                        # 遍历定位标签范围内的子轨迹结束索引
                        if row['timestamp'] <= seg_end_time:
                            sub_traj_output_end = index
                        # 若某处轨迹数据时间晚于标签结束时间，此时轨迹数据还未遍历结束，跳出遍历
                        if row['timestamp'] > seg_end_time:
                            is_traj_left = True  # 提前结束，还有轨迹数据未遍历，不读取新的轨迹文件
                            break
                        is_traj_left = False  # 需要读取新的轨迹文件

                # 标签时间区间内，无对应轨迹；进行下一个标签段的处理
                if sub_traj_output_start > sub_traj_output_end:
                    # 删除已经输出的子轨迹，或只有一个点的轨迹片段
                    trajectoryDF.drop(np.arange(0, sub_traj_output_end + 1, 1, int), axis=0, inplace=True)
                    trajectoryDF = trajectoryDF.reset_index(drop=True)  # 重置索引
                    break

                if sub_traj_output_start <= sub_traj_output_end:
                    sub_traj = trajectoryDF[sub_traj_output_start:sub_traj_output_end + 1]
                    # 删除已经输出的子轨迹，或只有一个点的轨迹片段
                    trajectoryDF.drop(np.arange(0, sub_traj_output_end + 1, 1, int), axis=0, inplace=True)
                    trajectoryDF = trajectoryDF.reset_index(drop=True)  # 重置索引
                    # 子轨迹起始和结束索引不一致时，才保存子轨迹文件
                    if sub_traj_output_start < sub_traj_output_end:
                        # 子轨迹输出路径
                        sub_traj_path = os.path.join(output_path,
                                                     "{0}_{1}_{2}_{3}.txt".format(folder_path.split('\\')[-1],
                                                                                  traj_file_name.split('.')[0],
                                                                                  sub_traj_id,
                                                                                  seg_mode))
                        sub_traj.to_csv(sub_traj_path, sep=',', index=False, header=True)
                        sub_traj_id += 1  # 增加子轨迹id
                # 轨迹数据表无数据剩余
                if trajectoryDF.shape[0] <= 1:
                    is_traj_left = False
                if not is_traj_left:
                    traj_file_index = traj_file_index + 1  # 获取下一个文件名索引


def training_traj_segmentation(data_path, output_path):
    """
    批量处理：根据交通方式标签文件分割轨迹片段（实验标准数据准备阶段）。

    :param data_path: 要处理的轨迹数据文件夹路径。
    :param output_path: 分段轨迹文件存储路径。
    """
    # 获取轨迹文件夹列表
    traj_folder_list = os.listdir(data_path)
    # 对数据文件夹中的各个文件进行操作
    for folder_name in traj_folder_list:
        # 各个志愿者轨迹文件路径 eg.010……
        traj_folder_path = os.path.join(data_path, folder_name)
        # 如 E:\Users\Desktop\Traffic_Pattern_Mining\2_TrajectoryModeClassify\3_Data\Process_01\010
        # 判断该文件是否为文件夹：是，则进行单文件夹轨迹片段分割；否，不处理跳过。
        if not os.path.isdir(traj_folder_path):
            continue
        traj_segmentation_one_folder(traj_folder_path, output_path)


if __name__ == '__main__':
    path = "E:/Users/Desktop/Traffic_Pattern_Mining/2_TrajectoryModeClassify/3_Data/Process_01"
    output = "E:/Users/Desktop/Traffic_Pattern_Mining/2_TrajectoryModeClassify/3_Data/Training_traj_segments_02"
    # read_label_txt(path)
    # traj_path = "E:/Users/Desktop/Traffic_Pattern_Mining/2_TrajectoryModeClassify/3_Data/Process_01/010/Trajectory/20080328144824.txt"
    # read_traj_txt(traj_path)
    # traj_segmentation_one_folder(path, output)
    # 按照标签文件批量分割轨迹片段
    training_traj_segmentation(path, output)

    # DataFrame测试
    # df = pd.DataFrame(np.arange(12).reshape((3, 4)), columns=list('abcd'))
    # print(df)
    # df.drop(np.arange(0, 1, 1, int), axis=0, inplace=True)
    # df = df.reset_index(drop=True)
    # print(df)
    # print(df[0:2])
