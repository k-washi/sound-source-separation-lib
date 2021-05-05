import numpy as np

def beamformer(input_data, mask):
    return np.einsum("skt, mkt->mskt", mask, input_data)