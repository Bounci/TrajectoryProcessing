# -*- coding: utf-8 -*-
# author: Bounci
# time: 2021/12/12
# description: 文件读取相关操作

import os


def plt2txt_test(data_root_path):
    """
    测试读取单一的plt文件，并转为txt文件。

    :param data_root_path: plt轨迹文件的路径。
    :return: 同名txt文件
    """
    # 该处为要打开的plt文件路径。注意：路径拼接时第二部分为相对路径，开头不能有”/“
    file_dir = os.path.abspath(os.path.join(data_root_path, "Labeled_Data/147/Trajectory/20110301213535.plt"))
    with open(file_dir, 'r') as fp1:
        # fp1.read()    # 读取整个文件
        lines = fp1.readlines()  # 按行读取
    # 数据为前六行为说明，无实际用途，不读取
    l_list = lines[6:]
    # 获取文件名（不含扩展名）。os.path.split()将目录分为路径和文件名，再利用一个split函数将文件名和扩展名分开
    file_name = os.path.split(file_dir)[1].split('.')[0]
    # 此处为txt文件存入位置，可以自动创建新的文本
    output_path = os.path.join(data_root_path, "Process_01/{}.txt".format(file_name))
    # 'w+'表示打开一个文件用于读写。如果该文件已存在则打开文件，并从开头开始编辑，即原有内容会被删除。如果该文件不存在，创建新文件。
    with open(output_path, 'w+') as fp:
        for line in l_list:  # 循环读取行数据
            fp.write(line)


if __name__ == '__main__':
    # 当前文件目录路径
    print(os.getcwd())
    # 获取当前文件上级目录
    print(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
    print(os.path.abspath(os.path.join(os.getcwd(), "..")))
    print(os.path.dirname(os.getcwd()))
    # 设置路径为当前文件夹上层目录的XX文件夹
    path = os.path.join(os.path.dirname(os.getcwd()), "XX")
    print(path)
    # 获取当前文件夹的上两级目录
    print(os.path.abspath(os.path.join(os.getcwd(), "../..")))
