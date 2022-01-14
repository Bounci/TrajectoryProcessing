# -*- coding: utf-8 -*-
# author: Bounci
# time: 2021/12/12
# description: 学习pandas的一些使用操作

import pandas as pd

if __name__ == '__main__':
    # pd.to_datetime(arg, errors='raise', dayfirst=False, yearfirst=False,
    #                utc=None, box=True, format=None, exact=True, unit=None,
    #                infer_datetime_format=False, origin='unix', cache=False)  # 转为datetime数据类型
    # 应用：要转换Series类似日期的对象或类似列表的对象, 例如字符串, 纪元或混合
    # 返回：DatetimeIndex，datetime64系列，标量时间戳，本身

    # 实例4.2：实现精确精度的唯一方法是使用固定宽度类型（例如int64）
    # pd.to_datetime([39298.1462037037, 1490195805.433502912], unit='s')  # 对于float arg，可能会发生精确舍入
    # DatetimeIndex(['2017-03-22 15:16:45.433000088', '2017-03-22 15:16:45.433502913'], dtype='datetime64[ns]', freq=None)

    # 实例5.1：使用origin参数-替代起点1970-1-1
    # print(pd.to_datetime([1, 2, 3], unit='D', origin=pd.Timestamp('1960-1-1'))) # 使用1899-12-30作为开始日期
    # DatetimeIndex(['1960-01-02', '1960-01-03', '1960-01-04'], dtype='datetime64[ns]', freq=None)

    # 第一个参数为要转换的数据，unit是指第一个数据的单位，origin为时间转换参考起点。
    # print(pd.to_datetime([39298.1462037037], unit='D', origin=pd.Timestamp('1899-12-30')))  # 使用1899-12-30作为开始日期
    datetime1 = pd.to_datetime([39298.1462037037], unit='D', origin=pd.Timestamp('1899-12-30'))[0]
    print(datetime1)
    # DatetimeIndex(['2007-08-04 03:30:31.999999488'], dtype='datetime64[ns]', freq=None)
