import numpy as np
from numpy.fft import fft, ifft


def frenquecy_synchronous_average(data_array):
    '''
    average data in frequency space
    '''
    assert isinstance(data_array, list) and len(data_array) > 0
    length = len(data_array[0])
    assert length > 0
    ffts = []
    for data in data_array:
        if len(data) != length:
            raise RuntimeError("inconsistent data length")
        ffts.append(fft(data))
    avg_fft = np.sum(ffts, axis=0) / len(data_array)
    data = ifft(avg_fft)
    return data
