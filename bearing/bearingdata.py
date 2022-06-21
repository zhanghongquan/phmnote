from abc import abstractmethod
import os
from re import sub
import scipy.io as spio
import pandas as pd
import numpy as np
from scipy import stats
from .features import BearingDataFeature

class InvalidParamaterException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

INNER_FAULT = 1
OUTER_FAULT = 2
BALL_FAULT = 4
CAGE_FAULT = 8


class FaultFrequency:
    def __init__(self, bpfi, bpfo, bsf, ftf):
        self.bpfi_rate = bpfi
        self.bpfo_rate = bpfo
        self.bsf_rate = bsf
        self.tft_rate = ftf
        self.rps = 0.0
    
    def clone(self):
        return FaultFrequency(self.bpfi, self.bpfo, self.bsf, self.ftf)
    
    def set_rps(self, rps):
        self.rps = rps
        return self
    
    @property
    def bpfi(self):
        return self.bpfi_rate * self.rps
    
    @property
    def bpfo(self):
        return self.bpfo_rate * self.rps
    
    @property
    def tft(self):
        return self.ftf_rate * self.rps
    
    @property
    def bsf(self):
        return self.bsf_rate * self.rps
    
    def __repr__(self) -> str:
        return f"bpfi:{self.bpfi} bpfo:{self.bpfo} tft:{self.ftf} bsf:{self.bsf} rps:{self.rps}"
 

class BearingData:
    def __init__(self, root, file_path):
        self.root = root
        self.file_path = file_path
        self.rps = 0.0
        self.sample_rate = 0.0
        self.bpfo_rate = 0.0
        self.bpfi_rate = 0.0
        self.ftf_rate = 0.0
        self.bsf_rate = 0.0
        self.faulty_part = 0
        self.feature_data = None
        self._loaded = False
    
    def __repr__(self):
        fault = []
        if self.inner_fault:
            fault.append("inner")
        if self.outer_fault:
            fault.append("outer")
        if self.ball_fault:
            fault.append("ball")
        if self.cage_fault:
            fault.append("cage")
        return f"{self.file_name} rps:{self.rps} sample_rate:{self.sample_rate} bpfi:{self.bpfi} bpfo:{self.bpfo} tft:{self.ftf} bsf:{self.bsf} fault:{'|'.join(fault)}" 
    
    @property
    def data_file_path(self):
        return os.path.join(self.root, self.file_path)
    
    @property
    def file_name(self):
        return self.file_path
    
    @property
    def bpfi(self):
        return self.bpfi_rate * self.rps
    
    @property
    def bpfo(self):
        return self.bpfo_rate * self.rps
    
    @property
    def ftf(self):
        return self.ftf_rate * self.rps
    
    @property
    def bsf(self):
        return self.bsf_rate * self.rps

    def set_rps(self, rps):
        self.rps = rps
        return self
    
    def set_fault_part(self, fault):
        self.faulty_part = fault
        return self
    
    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        return self
    
    def set_bpfi_rate(self, bpfi):
        self.bpfi_rate = bpfi
        return self
    
    def set_bpfo_rate(self, bpfo):
        self.bpfo_rate = bpfo
        return self
    
    def set_bsf_rate(self, bsf):
        self.bsf_rate = bsf
        return self
    
    def set_ftf_rate(self, ftf):
        self.ftf_rate = ftf
        return self
    
    @property
    def outer_fault(self):
        return (self.faulty_part & OUTER_FAULT) != 0

    @property
    def inner_fault(self):
        return (self.faulty_part & INNER_FAULT) != 0
    
    @property
    def ball_fault(self):
        return (self.faulty_part & BALL_FAULT) != 0

    @property
    def cage_fault(self):
        return (self.faulty_part & CAGE_FAULT) != 0
    
    def to_fault_frequency(self):
        result = FaultFrequency(self.bpfi_rate, self.bpfo_rate, self.bsf_rate, self.ftf_rate)
        result.set_rps(self.rps)
        return result
    
    def calculate_features(self, data):
        '''
        计算单通道数据特征
        '''
        f = BearingDataFeature()
        abs_data = np.abs(data)
        f.mean = np.mean(abs_data)
        f.peak = np.max(abs_data)
        f.peakpeak = np.max(data) - np.min(data)
        f.rms = np.sqrt(np.dot(data, data) / len(data))
        f.root_square = (np.sum(np.sqrt(abs_data)) / len(abs_data)) ** 2
        if f.rms > 0.000001:
            f.peak_factor = f.peakpeak / f.rms
        else:
            f.peak_factor = 0.0
        f.kurtosis_factor = stats.kurtosis(data)
        f.skewness_factor = stats.skew(data)
        f.pulse_factror = f.peak / f.mean
        f.allowance_factor = f.peak / f.root_square
        f.variance = np.var(data)
        f.std_var = np.sqrt(f.variance)
        return f

    
    @abstractmethod
    def load_data(self):
        pass


class XJTUBearingData(BearingData):
    """
    西交大的数据请访问
    V和H两个pandas的数据
    """
    def __init__(self, root, file_path, bearing_name):
        super().__init__(root, file_path)
        self.data_H = None
        self.data_V = None
        self.bearing_name = bearing_name
    
    @property
    def H(self):
        return self.data_H
    
    @property
    def V(self):
        return self.data_V

    def load_data(self):
        if self._loaded:
            return self
        df = pd.read_csv(self.data_file_path)
        df = df.rename(columns={"Horizontal_vibration_signals":"H", "Vertical_vibration_signals":"V"})
        self.data_H = df.H
        self.data_V = df.V
        self._loaded = True
        return self
    
    def calculate_features(self):
        for d in ["H", "V"]:
            data = getattr(self, d)
            f = super(XJTUBearingData, self).calculate_features(data)
            f.filename = self.file_name
            f.channel = d
            f.bearing_name = self.bearing_name
            f.file_idx = int(os.path.splitext(os.path.basename(self.file_name))[0])
            yield f


class CWRUBearingData(BearingData):
    """
    西储大学的数据请访问
    fe, be, ba
    数据可能为空
    """
    def __init__(self, root, file_path):
        super().__init__(root, file_path)
        self.fault_part_size = 0.0
        self.data_de = None # driver end 
        self.data_fe = None # fan end
        self.data_ba = None # base
        self.diretion_data = 0

    @property
    def de(self):
        return self.data_de
    
    @property
    def fe(self):
        return self.data_fe
    
    @property
    def ba(self):
        return self.data_ba
    
    @property
    def fault_size(self):
        return self.fault_part_size
    
    @property
    def direction(self):
        return self.direction_data
    
    def load_data(self):
        if self._loaded:
            return self
        data = spio.loadmat(self.data_file_path)
        for (key, value) in data.items():
            if key.endswith("BA_time"):
                self.data_ba = value
            elif key.endswith("FE_time"):
                self.data_fe = value
            elif key.endswith("DE_time"):
                self.data_de = value
            elif key.endswith("RPM"):
                self.set_rps(int(value)/60.0)
        name = os.path.basename(self.file_name)
        prefix = None
        if name.startswith("IR"):
            self.set_fault_part(INNER_FAULT | self.faulty_part)
            prefix = "IR"
        elif name.startswith("B"):
            self.set_fault_part(BALL_FAULT | self.faulty_part)
            prefix = "B"
        elif name.startswith("OR"):
            self.set_fault_part(OUTER_FAULT | self.faulty_part)
            prefix = "OR"
        name = name[len(prefix):]
        name = name.split("_")[0]
        sects = name.split("@")
        if len(sects) == 2:
            self.direction = int(sects[1])
        name = sects[0]
        name = name.strip("0")
        self.fault_part_size = int(name)
        self._loaded = True
        return self


class XJTUData:
    '''
    西交数据集， 含有完整生命周期数据的数据集，含有不同的rps和不同的故障类型
    '''
    def __init__(self, root_path="./data/xjtu_data"):
        """
        西交大的数据， 一共有15个轴承数据， 
        每一个轴承的数据量各不相同, 少的100多个，多个上千个文件。 
        每个文件都是采样频率25.6K, 一共采样1.28S的数据
        """
        self.data = []
        self.folder2params = {
            "35Hz12kN/Bearing1_1": [35, OUTER_FAULT],
            "35Hz12kN/Bearing1_2": [35, OUTER_FAULT],
            "35Hz12kN/Bearing1_3": [35, OUTER_FAULT],
            "35Hz12kN/Bearing1_4": [35, CAGE_FAULT],
            "35Hz12kN/Bearing1_5": [35, OUTER_FAULT | INNER_FAULT],
            "37.5Hz11Kn/Bearing2_1": [37.5, INNER_FAULT],
            "37.5Hz11Kn/Bearing2_2": [37.5, OUTER_FAULT],
            "37.5Hz11Kn/Bearing2_3": [37.5, CAGE_FAULT],
            "37.5Hz11Kn/Bearing2_4": [37.5, OUTER_FAULT],
            "37.5Hz11Kn/Bearing2_5": [37.5, OUTER_FAULT],
            "40Hz10Kn/Bearing3_1": [40, OUTER_FAULT],
            "40Hz10Kn/Bearing3_2": [40, OUTER_FAULT | INNER_FAULT| BALL_FAULT | CAGE_FAULT],
            "40Hz10Kn/Bearing3_3": [40, INNER_FAULT],
            "40Hz10Kn/Bearing3_4": [40, INNER_FAULT],
            "40Hz10Kn/Bearing3_5": [40, OUTER_FAULT],
        }
        self.sample_rate = 25600
        self.bpfo_rate = 8 / 2.0 * (1 - 7.92 / 34.55)
        self.bpfi_rate = 8 / 2.0 * (1 + 7.92 / 34.55)
        self.ftf_rate = 1.0 / 2.0 * (1 - 7.92 /34.55)
        self.bsf_rate = 34.55 / 7.92 * (1 - (7.92/ 34.55)**2)
        self.list_files(root_path)

    def list_files(self, root_path):
        for folder_name, v in self.folder2params.items():
            index = 1
            files = []
            while True:
                filename = os.path.join(root_path, folder_name, f"{index}.csv")
                if not os.path.exists(filename):
                    break
                data = XJTUBearingData(root_path, os.path.join(folder_name, f"{index}.csv"), folder_name.split("/")[1])
                data.set_sample_rate(self.sample_rate)
                data.set_rps(v)
                data.set_bpfi_rate(self.bpfi_rate)
                data.set_bpfo_rate(self.bpfo_rate)
                data.set_ftf_rate(self.ftf_rate)
                data.set_bsf_rate(self.bsf_rate)
                files.append(data)
                index += 1
            self.data.append(files)
    
    def refresh_features(self, db):
        features = []
        for bearing in self.data:
            for bearing_file in bearing:
                bearing_file.load_data()
                for feature in bearing_file.calculate_features():
                   features.append(feature)
                   if len(features) >= 50:
                       db.add_features(features)
                       features = []
        if len(features) > 0:
            db.add_features(features)


class CWRUData:
    '''
    西储大学数据集， 含有正常数据和异常数据，异常数据中含有不同类型的故障
    '''
    def __init__(self, root_path="./data/cwru_data"):
        self.normal_data = []
        self.f12kde_data = []
        self.f48kde_data = []
        self.fe_data = []
        self.folder2samplerate =  {
                        "12KDriveEnd": [12 * 1000, (5.4152, 3.5848, 0.39828, 4.7135) , lambda x: self.f12kde_data.append(x)],
                        "48KDriveEnd": [48 * 1000, (5.4152, 3.5848, 0.39828, 4.713), lambda x: self.f48kde_data.append(x)],
                        "FanEnd":  [12 * 1000, (4.9469, 3.0530, 0.3817, 3.9874), lambda x: self.fe_data.append(x)],
                        "normal": [12 * 1000, (1, 1, 1, 1), lambda x: self.normal_data.append(x)] #normal data do not need fault frequency
                    }
        self.list_files(root_path)

    @property
    def fe(self):
        return self.fe_data
    
    @property
    def de12k(self):
        return self.f12kde_data
    
    @property
    def de48k(self):
        return self.f48kde_data
    
    @property
    def normal(self):
        return self.normal_data

    def list_files(self, root_path):
        for folder_name, v in self.folder2samplerate.items():
            file_names = os.listdir(os.path.join(root_path,folder_name))
            for file_name in file_names:
                data = CWRUBearingData(root_path, os.path.join(folder_name, file_name))
                data.set_sample_rate(v[0])
                fault_freq_rate = v[1]
                data.set_bpfi_rate(fault_freq_rate[0])
                data.set_bpfo_rate(fault_freq_rate[1])
                data.set_ftf_rate(fault_freq_rate[2])
                data.set_bsf_rate(fault_freq_rate[3])
                v[2](data)


def test():
    bearing = CWRUData()


if __name__ == "__main__":
    test()
