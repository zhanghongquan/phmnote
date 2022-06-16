import numpy as np
from scipy import signal
from .bearingdata import FaultFrequency

class FaultAlarm:
    '''
    故障预警利用轴承过往的数据，训练出一个AR模型， 然后使用这个模型进行一个预测。
    然后使用实际测量值和预测值做一个比较，如果趋势发生较大变化，就认为是出现了问题
    '''
    def __init__(self):
        pass

    def add_model_data(self):
        pass


def calc_fft(data, sample_rate):
    # 去除直流分量， 减少近0频率能量对数据的影响
    data = data- np.mean(data)
    amplitude = np.fft.fft(data)
    n = len(amplitude)
    data_upper_bound = (n-1)//2+1
    # a = np.abs(a) * 2 / n
    # 取abs，去除复数部分, 只取正频率的数据
    amplitude = np.abs(amplitude)[:data_upper_bound]
    frequency = np.fft.fftfreq(n, 1.0/sample_rate)[:data_upper_bound]
    return frequency, amplitude

def data_filter(data, band, order, method, sample_rate):
    sos = signal.butter(order, band, method, fs=sample_rate, output="sos")
    return signal.sosfilt(sos, data)

def demodulate(data, sample_rate):
    data = data - np.mean(data)
    analytical_data = signal.hilbert(data)
    envelope = np.abs(analytical_data)
    return calc_fft(envelope, sample_rate)


class DiagnosisResult:
    def __init__(self, **kwargs):
        self.frequency = kwargs.get("")


class FaultDiagnosis:
    def __init__(self, fault_frequency, **kwargs):
        self.fault_frequency = fault_frequency
        self.filter_order = kwargs.get("filter_order", 8)
        self.filter_band = kwargs.get("filter_band", 800)
        self.filter_method = kwargs.get("filter_method", "hp")
        self.power_ratio = kwargs.get("diagnose_ratio", 10.0)
        self.search_bandwidth = kwargs.get("search_bandwidth", 10)
    
    def get_argument(self, **kwargs):
        order = kwargs.get("filter_order", self.filter_order)
        band = kwargs.get("filter_band",self.filter_band)
        method = kwargs.get("filter_method", self.filter_method)
        return order, band, method
    
    def find_side_band(self, envelope_fft, ):
        pass

    def find_faulty_frequency(self, envelope_fft, round_per_second):
        '''
        '''
        fault_frequency = self.fault_frequency.clone().set_rps(round_per_second)
        bpfi = fault_frequency.bpfi
        bpfo = fault_frequency.bpfo
        bsf = fault_frequency.bsf
        ftf = fault_frequency.ftf


        
    def process(self, data, sample_rate, round_per_second, **kwargs):
        '''
        采用调制解调的方法，通过包络算法找到故障频率，如果故障频率的能量远远大于周边的频率能量，
        那么认为出现故障频率，当前轴承已经有故障
        '''
        order, band, method = self.get_argument(**kwargs)
        filtered_data = data_filter(data, band, order, method, sample_rate)
        envelope_fft = demodulate(filtered_data, sample_rate)
        return self.find_faulty_frequency(envelope_fft, round_per_second)