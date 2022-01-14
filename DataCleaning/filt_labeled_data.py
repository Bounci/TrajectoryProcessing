# -*- coding: utf-8 -*-
# author: Bounci
# time: 2021/12/13
# description: 从Geolife数据集中选出带标签文件的数据

import os
import shutil


def labeled_data_filter():
    # 原始geolife数据集存放路径，至 ./Data一级
    raw_geolife_path = "E:/Users/Desktop/Traffic_Pattern_Mining/2_TrajectoryModeClassify/1 Data_Graduate Design Experiment/Geolife Trajectories 1.3/Data"

    # 筛选出的数据存放路径
    store_dir = "E:/Users/Desktop/Traffic_Pattern_Mining/2_TrajectoryModeClassify/3_Data/Labeled_Data"

    # 获取geolife数据集文件夹下所有文件名列表
    user_folder_list = os.listdir(raw_geolife_path)
    for folder in user_folder_list:
        # 路径至 ./000 一级
        user_folder_path = os.path.join(raw_geolife_path, folder)
        print(user_folder_path)
        # 获取user文件夹下所有文件名列表
        user_file_list = os.listdir(user_folder_path)
        # 若user文件夹中包含两个文件，则包含有标签文件，将该user文件拷贝至指定路径
        if len(user_file_list) != 2:
            continue
        # 复制user文件夹至路径：
        target_store_path = os.path.join(store_dir, folder)
        # 复制文件夹
        shutil.copytree(user_folder_path, target_store_path)


if __name__ == '__main__':
    # 筛选有标签文件数据
    labeled_data_filter()
