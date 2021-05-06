import sys
import pathlib
import numpy as np


module_path = pathlib.Path(__file__).parent.parent.parent.resolve()
if module_path not in sys.path:
    sys.path.append(str(module_path))

from utils import get_logger, calc_circumference_locations
logger = get_logger()

from src.audio.processing import WaveProcessing



class MicrophoneArray():
    """
    マイクロホンアレイが2次元平面のある円周上に等間隔で並んでいるものとする。
    """
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def get_locations(r, mic_num):
        """
        マイクを配置
        r: 中心からの距離[m]
        mic_num: マイク数
        """

        #　マイクアレイ中心からみた方向を計算
        dir_interval = 360 // mic_num
        mic_dirs, mic_alignments = calc_circumference_locations(r, dir_interval)

        return mic_dirs, mic_alignments
    
    @staticmethod
    def calc_virtual_steering_vectors(mic_locations, ss_locations, freqs, sound_speed=340, is_use_far=False):
        """
        mic_locations: 3 x M
        ss_locations: 3 x Ns
        freqs: Nk
        sound_speed: 音速 [m/s]
        is_use_far: Farを使うかどうか
        """
        n_channels = mic_locations.shape[0]

        if is_use_far:
            # 音源位置を正規化
            norm_source_locations = ss_locations / np.linalg.norm(ss_locations, 2, axis=0, keepdims=True) # 3x72 / 1x72

            # 位相を求める
            steering_phase = np.einsum(
                'k,ism,ism->ksm',
                2.j * np.pi/sound_speed*freqs, # k
                norm_source_locations[..., None], #3x72x1
                mic_locations[:, None, :] # 3x1x8
            ) # k x 72 x 8

            steering_vector = 1. / np.sqrt(n_channels) * np.exp(steering_phase)

            
        else:
            # 音源とマイクの距離を求める
            # distance Ns x Nm
            distance = np.sqrt(np.sum(np.square(
                ss_locations[..., None] - mic_locations[:, None, :]
            ), axis=0))

            # 遅延時間 [sec]
            delay = distance / sound_speed

            # 位相の計算
            #ステアリングベクトルの位相を求める
            steering_phase=np.einsum('k,sm->ksm',-2.j*np.pi*freqs, delay)
        
            #音量の減衰
            steering_decay_ratio=1./distance

            #ステアリングベクトルを求める
            steering_vector=steering_decay_ratio[None,...]*np.exp(steering_phase)

            #大きさを1で正規化する
            steering_vector=steering_vector/np.linalg.norm(steering_vector, 2, axis=2, keepdims=True)

        return steering_vector



if __name__ == "__main__":
    mic = MicrophoneArray()
    sample_rate = 16000

    freqs = WaveProcessing.stft_freqs(sample_rate)
    print(freqs.shape) #(257,)
    _, mic_locs = mic.get_locations(0.1, 8)
    print(mic_locs.shape, mic_locs[..., None].shape, mic_locs[:, None, :].shape)
    _, ss_locs = calc_circumference_locations(1, 5)
    print(ss_locs.shape, np.linalg.norm(ss_locs, 2, axis=0, keepdims=True).shape)
    st_vector = mic.calc_virtual_steering_vectors(mic_locs, ss_locs, freqs)
    print(st_vector.shape) #(257, 72, 8)


