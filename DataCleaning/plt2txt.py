# -*- coding: utf-8 -*-
# author: Bounci
# time: 2021/12/12
# description: 将plt文件转为txt文件，同时删除每个文件中的前6行无用数据

import os
import shutil   # 复制文件需要使用


def plt2txt_one_file(traj_file_path, store_path):
    """
    读取单一的plt文件，并转为txt文件。

    :param traj_file_path: plt轨迹文件的路径。
    :param store_path: 志愿者数据存放路径，至010级。
    :return: 同名txt文件
    """
    with open(traj_file_path, 'r') as fp1:
        # fp1.read()    # 读取整个文件
        lines = fp1.readlines()  # 按行读取
    # 数据为前六行为说明，无实际用途，不读取
    l_list = lines[6:]

    # 获取文件名（不含扩展名） os.path.split()将目录分为路径和文件名，再利用一个split函数将文件名和扩展名分开
    file_name = os.path.basename(traj_file_path).split('.')[0]
    # file_name = os.path.split(traj_file_path)[1].split('.')[0]

    # 判断某一志愿者轨迹数据文件夹是否存在，若不存在，则创建
    output_path = os.path.join(store_path, "Trajectory")
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    # 此处为txt文件存入位置，可以自动创建新的文本
    traj_path = os.path.join(output_path, "{}.txt".format(file_name))
    # 'w+'表示打开一个文件用于读写。如果该文件已存在则打开文件，并从开头开始编辑，即原有内容会被删除。如果该文件不存在，创建新文件。
    with open(traj_path, 'w+') as fp:
        for line in l_list:  # 循环读取行数据
            fp.write(line)


def plt2txt_one_folder(data_root_path, userdata_folder_path):
    """
    处理一个文件夹数据格式转换。

    :param data_root_path: 数据文件夹的路径。
    :param userdata_folder_path: 原始志愿者数据文件夹的路径。
    :return:
    """
    # 获取某一志愿者轨迹数据文件夹（指定文件夹）下所有文件名列表
    user_folder_files_list = os.listdir(userdata_folder_path)

    # 获取志愿者数据文件夹名 如：010
    folder_name = userdata_folder_path.split('\\')[-1]
    # 处理结果存储路径 eg. E:\Users\Desktop\Traffic_Pattern_Mining\2_TrajectoryModeClassify\3_Data\Process_01\010
    store_path = os.path.join(data_root_path, "Process_01/{}".format(folder_name))
    print(store_path)   # 输出目前处理至哪一userdata文件夹
    # 判断文件夹是否存在，若不在，则创建。
    if not os.path.exists(store_path):
        os.mkdir(store_path)

    # 对志愿者轨迹数据文件夹中的各个文件进行操作,eg.010……
    for file in user_folder_files_list:
        # 各个志愿者轨迹文件夹中文件的路径 eg.Trajectory、labels.txt
        raw_file_path = os.path.join(userdata_folder_path, file)

        # 判断该文件是否为文件夹：否，则其为labels.txt，复制至Process_01文件夹对应位置；
        #                     是，则证明其为 Trajectory文件夹，继续后续处理
        if not os.path.isdir(raw_file_path):
            output_path = os.path.join(store_path, "labels.txt")
            shutil.copyfile(raw_file_path, output_path)  # 复制labels.txt
            continue

        # 获取Trajectory文件夹中的轨迹文件名列表
        traj_files_list = os.listdir(raw_file_path)
        # 对单个plt文件进行操作
        for traj in traj_files_list:
            # 各个轨迹plt文件路径
            traj_file_path = os.path.join(raw_file_path, traj)
            plt2txt_one_file(traj_file_path, store_path)


def plt2txt_all_folders(data_root_path):
    """
    处理所有文件夹下的轨迹文件格式转换。

    :param data_root_path: 数据文件夹的路径。
    :return: 转换为txt格式的数据文件，存储于原始数据同级目录下，Process_01文件夹中。
    """

    # 带标签的原始数据路径 E:\Users\Desktop\Traffic_Pattern_Mining\2_TrajectoryModeClassify\3_Data\Labeled_Data
    labeled_data_folder_path = os.path.join(data_root_dir, "Labeled_Data")

    # 获取原始轨迹数据文件夹（指定文件夹）下所有文件名列表
    raw_traj_folder_list = os.listdir(labeled_data_folder_path)

    # 对原始数据中的各个文件进行操作
    for file in raw_traj_folder_list:
        # 各个志愿者轨迹文件路径 eg.010……
        file_path = os.path.join(labeled_data_folder_path, file)
        # 如 E:\Users\Desktop\Traffic_Pattern_Mining\2_TrajectoryModeClassify\3_Data\Labeled_Data\010

        # 判断该文件是否为文件夹：是，则进行单文件夹操作；否，不处理跳过。
        if not os.path.isdir(file_path):
            continue
        plt2txt_one_folder(data_root_path, file_path)


if __name__ == '__main__':
    # 获取数据路径
    data_root_dir = os.path.abspath(os.path.join(os.getcwd(), "../../3_Data"))
    # E:\Users\Desktop\Traffic_Pattern_Mining\2_TrajectoryModeClassify\3_Data
    # 轨迹文件格式批量转换
    plt2txt_all_folders(data_root_dir)
