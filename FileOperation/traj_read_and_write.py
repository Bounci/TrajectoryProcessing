# -*- coding: utf-8 -*-
# author: Bounci
# time: 2022/2/16
# description: 轨迹文件读写操作
import os
import pandas as pd


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


def read_raw_traj_txt(traj_txt_path):
    """
    读取原始轨迹数据文件。

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
    # 删除日期和时间两列数据
    trajDF.drop(['date', 'time'], axis=1, inplace=True)

    print(trajDF.shape)  # 输出数据表大小
    # print(type(trajDF['lat'][0]))
    # print(type(trajDF['timestamp'][0]))
    # print(trajDF.head())
    return trajDF


def read_traj_txt(traj_txt_path):
    """
    读取过滤后的轨迹数据文件。

    :param traj_txt_path: 轨迹数据文件路径
    :return: trajDF轨迹数据表
    """
    column_name = ['lat', 'lon', 'alt', 'timestamp']
    # 读取轨迹数据文件
    trajDF = pd.read_csv(traj_txt_path, sep=',', header=None, names=column_name)
    trajDF['timestamp'] = pd.to_datetime(trajDF['timestamp'], format='%Y/%m/%d %H:%M:%S')
    print(trajDF.shape)  # 输出数据表大小
    return trajDF


def read_mode_traj(traj_txt_path):
    """
    读取过滤后的轨迹数据文件。

    :param traj_txt_path: 轨迹数据文件路径
    :return: trajDF轨迹数据表
    """
    column_name = ['lat', 'lon', 'alt', 'timestamp', 'mode']
    # 读取轨迹数据文件
    trajDF = pd.read_csv(traj_txt_path, sep=',', header=None, names=column_name)
    trajDF['timestamp'] = pd.to_datetime(trajDF['timestamp'], format='%Y/%m/%d %H:%M:%S')
    print(trajDF.shape)  # 输出数据表大小
    return trajDF


def read_traj_with_feature(traj_txt_path):
    # 含轨迹点特征的数据 有表头，读取数据时需要跳过
    # 读取轨迹数据文件
    trajDF = pd.read_csv(traj_txt_path, sep=',', header=0)
    print(trajDF.shape)  # 输出数据表大小
    return trajDF


if __name__ == '__main__':
    pass
