import numpy as np
from scipy import signal, integrate


def acceleration2velocity(data, sample_rate, hp_frequency = 1, use_detrend=True):
    '''
    data collected by vibration sensors contain noise.
    data shift happens when we integrate acceleration to velocity,
    use high pass filter to filter out DC part in data, and then use 
    cumulative trapezoid to integrate data
    '''
    assert sample_rate > 0
    assert data is not None
    sos = signal.butter(6, hp_frequency, "hp", fs=sample_rate, output="sos")
    if use_detrend:
        data = signal.detrend(data)
    data = signal.sosfilt(sos, data)
    return integrate.cumulative_trapezoid(data, 1.0/sample_rate)


def poorman_integrate(data, sample_rate):
    pass

def poorman_differentiate(data, sample_rate):
    pass
