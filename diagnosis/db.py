'''
计算轴承数据的特征并存储到数据库，后续可以直接使用
当前只计算西交大的轴承数据的特征
'''

import os
from sqlalchemy import Column, create_engine, String, Float, Integer, LargeBinary
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

# 西交大全生命周期数据
DATASOURCE_XJTU = 0
# 西储大学数据
DATASOURCE_CWRU = 1


# 轴承数据
DATA_TYPE = 0

#齿轮数据
DATA_TYPE = 1


class DataSource(Base):
    '''
    data source is used to tell you which group does a dataset belongs to
    '''
    __tablename__ = "datasource"

    id = Column(Integer, primary_key=True, autoincrement=False)

    name = Column(String(64),unique=True)

    description = Column(String(256))


    def __repr__(self) -> str:
        return f"{self.name}:{self.id}"

class DataType(Base):
    __tablename__ = "datatype"

    id = Column(Integer, primary_key=True, autoincrement=False)

    name = Column(String(64), unique=True)

    description = Column(String(256))

    def __repr__(self) -> str:
        return f"{self.name}:{self.id}"


class DataMeta(Base):
    __tablename__ = "datameta"

    id = Column(Integer, primary_key=True)

    # data type such as bearing or gear data
    data_type = Column(Integer)

    # data name such as bearing_0
    name = Column(String(128))


class BearingAttribute(Base):
    '''
    轴承固有属性，主要用于定位内圈，外圈等故障频率系数
    '''
    __tablename__ = "bearing_attribute"

    id = Column(Integer, primary_key=True)

    name = Column(String(128), unique=True)

    bpfo = Column(Float)

    bpfi = Column(Float)

    bsf = Column(Float)

    ftf = Column(Float)


class BearingParameter(Base):
    __tablename__ = "bearing_parameter"

    id = Column(Integer, primary_key=True)

    name = Column(String(128), unique=True)

    rps = Column(Float)

    load = Column(Float)

    # 使用时钟方向0~11来指定负载方向
    direction = Column(Integer)


class VibrationDataSet(Base):
    __tablename__ = "vibration_data_set"

    id = Column(Integer, primary_key=True)

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



class BearingDataFeature(Base):
    __tablename__ = "bearing_features"

    id = Column(Integer, primary_key=True)

    source = Column(Integer) #数据来源 0 --> xjtu, 1 --> cwru

    filename = Column(String(128), index=True) #文件名

    channel = Column(String(12), index=True) # 例如横轴数据， 驱动端数据

    file_idx = Column(Integer, index=True)

    bearing_name = Column(String, index=True)

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
