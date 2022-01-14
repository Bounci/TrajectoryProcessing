# -*- coding: utf-8 -*-
# author: Bounci
# time: 2021/12/11
# description: 轨迹点类：用于存储各个轨迹点的属性信息

class TrajPoint(object):

    def __init__(self, lon, lat, date, altitude):
        """
        初始化类实例（从原始数据集中添加）。

        :param lon: 经度
        :param lat: 纬度
        :param date: 时间戳
        :param altitude: 高程
        """
        self.lon = lon  # 经度
        self.lat = lat  # 纬度
        self.date = date  # 时间戳
        self.altitude = altitude  # 高程


if __name__ == '__main__':
    # 测试添加属性
    trace_p1 = TrajPoint(139, 39, 39298.1462037037, 13)
    trace_p1.velocity = 2     # 额外添加速度特征属性
    print(trace_p1.date, trace_p1.velocity)
