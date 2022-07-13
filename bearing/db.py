'''
计算轴承数据的特征并存储到数据库，后续可以直接使用
当前只计算西交大的轴承数据的特征
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


# 轴承数据
DATA_TYPE = 0

#齿轮数据
DATA_TYPE = 1


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


class BearingInfo:
    id = 0

    name = ""

    bpfi = 0.0

    bpfo = 0.0

    bsf = 0.0

    ftf =0.0

class Gear(Base):
    __tablename__ = "gear_info"

    id = Column(Integer, primary_key=True)

    deviceinfo_Id = Column(Integer, ForeignKey("deviceinfo.id"))


class GearInfo:

    id = 0

    name = ""

 
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
    
