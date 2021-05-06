import sys
import pathlib
import numpy as np


module_path = pathlib.Path(__file__).parent.parent.parent.resolve()
if module_path not in sys.path:
    sys.path.append(str(module_path))

from src.audio.processing import WaveProcessing
from src.sss.microphone_array import MicrophoneArray
from src.sss.localization import assign_locations
from src.format.output import AudioOutputStruct
from utils import get_logger, calc_circumference_locations
logger = get_logger()

class SparseBeamforming():
    """
    音声のスパース性 + ビームフォーマ
    マイクロホンアレイが2次元平面のある円周上に等間隔で並んでいるものとする。
    """
    def __init__(self, conf, wave_info:AudioOutputStruct) -> None:
        audio_conf = conf.audio
        self._assign_dir = audio_conf.assign_dir # +-角度の範囲を同一の音源とみなす
        self.mic_dirs, self.mic_locations = MicrophoneArray.get_locations(audio_conf.mic.distance, audio_conf.mic.num)

        ## 仮想音源の設定
        freqs = WaveProcessing.stft_freqs(wave_info.sample_rate, nperseg=audio_conf.stft.nperseg)
        self.vss_dirs, self.vss_locations = calc_circumference_locations(audio_conf.ss.distance, audio_conf.ss.interval_dir)
        self.steering_vectors = MicrophoneArray.calc_virtual_steering_vectors(self.mic_locations, self.vss_locations, freqs)
        self.spectrogram = None
        
    def __call__(self, stft_data, ss_azimuth):
        """
        ビームフォーマによる音源分離
        stft_data: freqs x vss x tims　# 収録音
        ss_azimuth: [s1_azimuth, s2_azimuth, ...]　分離する音源の方向

        @return:
            output: mic_num x sound source x freqs x times
            spectrograms freqs x vss xtimes
        """
        
        # 音源方向の推定
        localization_ss_dirs, self.spectrogram = self.beamforming(stft_data, self.steering_vectors)
        
        ## 各周波数ごとに最大方向を割り当て
        sound_source_mask = assign_locations(localization_ss_dirs, ss_azimuth, self.vss_dirs, self._assign_dir)
        # 音源分離
        output = np.einsum("skt, mkt->mskt", sound_source_mask, stft_data)
        return output

    def beamforming(self, stft_data, steering_vectors):
        """
        音源方向推定
        stft_data: mics x freqs x times
        steerin_vectors: freqs, virtual_ss, mics
        """


        inner_prod = np.einsum("kim,mkt->kit",
            np.conjugate(steering_vectors), stft_data
        ) # freqs x vss x times
        max_dirs = np.argmax(np.abs(inner_prod), axis=1)
        return max_dirs, np.abs(inner_prod)
        