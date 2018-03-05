'''
使用logging模块记录日志
日志等级为5个: logging.DEBUG|INFO|WARNING|ERROR|CRITICAL  (实质为数字常量10 20,...)
对应5个记录日志的方法

而创建日志分为两种方式：1.使用模块提供方法直接调用  2.创建Logger对象通过它进行调用
后者可以同时对控制台与文件输出日志内容。
'''
import logging

# 1.使用模块提供方法,配置日志后调用,只能在Console与文件间择一输出
logging.basicConfig(level=logging.INFO,  # 日志等级,只有大于等于该等级的日志才会被输出

                    filename='./log.txt',   # 文件输出路径
                    filemode='a',           # 文件写入格式,如果不写这两行就是向Console输出

                    # 输出格式,有许多功能,主要记住%(asctime)s 当前时间 %(message)s 日志信息, 其余详情请查表。
                    format='%(asctime)s--%(filename)s[line:%(lineno)d]--%(levelname)s--%(message)s'
                    )

logging.debug('This is a debug message.')   # 无法输出,因为级别小于设置的日志等级
logging.info('This is a info message.')
print(logging.DEBUG)

# 2.使用Logger对象同时对控制台与文件输出,其中可以通过处理器对不同输出做不同设置
lg = logging.getLogger()    # 获取Logger对象
lg.setLevel(logging.INFO)   # 设置基础信息等级,与处理器等级有冲突时按照等级更高者设定

# 创建由Logger对象管理的文件处理器,用于处理日志如何写入文件
fh = logging.FileHandler('./log.txt','a')
fh.setLevel(logging.WARNING)

# 同上,创建一个流处理器,处理日志输出至控制台
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)

# 定义输出日志的格式
formatter = logging.Formatter('%(asctime)s--%(levelname)s--%(message)s')
sh.setFormatter(formatter)
fh.setFormatter(formatter)

# 将各处理器交由Logger对象管理
lg.addHandler(sh)
lg.addHandler(fh)

# 使用
lg.info('Logger() info message')
lg.critical('Logger() critical message')