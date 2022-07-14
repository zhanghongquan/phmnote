'''
计算轴承数据的特征并存储到数据库，后续可以直接使用

故障数据的元数据有如下几个
1. 数据类型，例如是轴承数据、齿轮数据
2. 数据产生放(租户)
3. 数据集合
4. 逻辑部件名称
5.      部件属性
6.          测点
7.              数据
8.              参数
'''

from ast import For
from enum import unique
import os
from unicodedata import category
from sqlalchemy import Column, ForeignKey, create_engine, String, Float, Integer, LargeBinary, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base, relationship


Base = declarative_base()

# 西交大全生命周期数据
DATASOURCE_XJTU = 0
# 西储大学数据
DATASOURCE_CWRU = 1


# 目录数据

DATA_CATEGORY_FOLDER = 0
# 轴承数据

DATA_CATEGORY_BEARING = 1

#齿轮数据
DATA_CATEGORY_GEAR = 2


class TreeNode(Base):
    __tablename__ = "tree_node"

    id = Column(Integer, primary_key=True)

    name = Column(String(64))

    description = Column(String(256))

    category = Column(Integer) # 轴承数据/齿轮数据/目录

    parent_id = Column(Integer) # 0 means current node is root node


class DataCollection(Base):
    '''
    '''
    __tablename__ = "data_collection"

    id = Column(Integer, primary_key=True, autoincrement=False)

    name = Column(String(64),unique=True)

    description = Column(String(256))

    def __repr__(self) -> str:
        return f"{self.name}:{self.id}"


class DeviceInfo(Base):
    __tablename__ = "device_info"

    id = Column(Integer, primary_key=True)

    name = Column(String(128))

    category = Column(Integer)


class Bearing(Base):
    __tabelname__ = "bearing_info"

    id = Column(Integer, primary_key=True)

    deviceinfo_Id = Column(Integer, ForeignKey("deviceinfo.id"))

    bpfi = Column(Float)

    bpfo = Column(Float)

    bsf = Column(Float)

    ftf = Column(Float)


class Gear(Base):
    __tablename__ = "gear_info"

    id = Column(Integer, primary_key=True)

    deviceinfo_Id = Column(Integer, ForeignKey("deviceinfo.id"))


class BearingParameter(Base):
    __tablename__ = "bearing_parameter"

    id = Column(Integer, primary_key=True)

    name = Column(String(128), unique=True)

    rps = Column(Float)

    load = Column(Float)

    # 使用时钟方向0~11来指定负载方向
    direction = Column(Integer)

    def __repr__(self) -> str:
        return f"{self.name}/rps:{self.rps}/dir:{self.direction}"


class GearParameter(Base):
    __tablename__ = "gear_parameter"

    id = Column(Integer, primary_key=True)

    name = Column(String(128))


class DataChannel(Base):
    __tablename__ = "data_channel"

    id = Column(Integer, primary_key=True)

    device_id = Column(Integer, ForeignKey("device_info.id"))

    name = Column(String(128), unique=True)


class VibrationData(Base):
    '''
    vibration data, esspecial the acceleration data.
    '''
    __tablename__ = "vibration_data"

    id = Column(Integer, primary_key=True)

    channel_id = Column(Integer, ForeignKey("data_channel.id"))

    timestamp = Column(DateTime)

    mean = Column(Float) #均值

    peak = Column(Float) #单峰值

    peakpeak = Column(Float) #峰峰值
    
    rms = Column(Float) #均方根

    root_square = Column(Float) #方根幅值

    root = Column(Float) #方根幅值

    peak_factor = Column(Float) #峰值因子， peak/rms

    kurtosis_factor = Column(Float) # 峭度

    skewness_factor = Column(Float) # 偏度

    allowance_factor = Column(Float) #裕度因子

    pulse_factror = Column(Float) #脉冲因为

    std_var = Column(Float) # 标准差

    variance = Column(Float) # 方差

    wave = Column(LargeBinary) #原始波形



class Database:
    def __init__(self, db_url = None):
        if db_url is None:
            db_file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../bearing_features.db"))
            db_url = f"sqlite:///{db_file_path}"
        self.engine = create_engine(db_url)
        self.session_base = sessionmaker(bind= self.engine)
        Base.metadata.create_all(self.engine)
    
    def load_base_tree(self):
        nodes = None
        with self.session_base() as sess:
            nodes = sess.query(TreeNode).all()
        if nodes is None:
            return None
        
    
    def list_features(self, bearing_name, channel, *features):
        result = []
        for feature in features:
            result.append([])
        filtered = []
        for feature in features:
            filtered.append(Column(feature))
        with self.session_base() as sess:
            for x in sess.query(BearingDataFeature).filter_by(bearing_name=bearing_name, channel=channel).values(*filtered):
                for i in range(0, len(features)):
                    result[i].append(x[i])
        return result

    def delete_all_features(self):
        with self.session_base() as sess:
            sess.query(BearingDataFeature).delete()
            sess.commit()
    
    def add_features(self, feature):
        with self.session_base() as sess:
            if isinstance(feature, list):
                for f in feature:
                    sess.add(f)
            else:
                sess.add(f)
            sess.commit()
    
