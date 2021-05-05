import sys
import os
import pathlib
import pyaudio
import struct
import wave
from omegaconf import OmegaConf
import numpy as np
import scipy.signal as sp

# パスを通す
module_path = pathlib.Path(__file__).parent.parent.parent.resolve()
if module_path not in sys.path:
    sys.path.append(str(module_path))

from utils import get_logger
logger = get_logger()

from src.format.output import AudioOutputStruct

class WaveProcessing():
    def __init__(self) -> None:
        self._pAudio = pyaudio.PyAudio()

    
    def list_to_wave(self, save_file, list_data, ch_num, sample_rate, sample_width=2):
        """
        save_file:
        list_data [ch num * sec ***]
        ch_num
        sample_rate
        width=2 # 基本的に2, ハイレゾ対応をするなら4
        """
        logger.info(f"Start wav save to {save_file}, {len(list_data)/sample_rate/ch_num}")

        data = struct.pack('h' * len(list_data), *list_data)
        with wave.open(save_file, 'wb') as w:
            w.setnchannels(ch_num)
            w.setsampwidth(sample_width)
            w.setframerate(sample_rate)
            w.writeframes(data)
            logger.info(f"End wave save as {save_file}")

        return True
    
    def read_wav(self, wave_file):
        """
        音ファイルを読み込む
        wave_file: ファイルパス

        @return:
            wave_list: List
            wave_info: 
        """
        
        if not os.path.isfile(wave_file):
            logger.error(f"{wave_file} is not exist.")
            return None, None
        
        with wave.open(wave_file, 'r') as r:
            ch_num = r.getnchannels()
            sample_width = r.getsampwidth()
            sample_rate = r.getframerate()
            frame_num = r.getnframes()

            logger.info(f'Name {wave_file} | ChannelNum {ch_num} | Width {sample_width} | SamplingRate {sample_rate} | FrameNum {frame_num} | TotalTime {frame_num / sample_rate}')
        
            output = OmegaConf.structured(AudioOutputStruct(
                sample_rate=sample_rate,
                sample_width=sample_width,
                ch_num=ch_num,
                sample_num=frame_num
            ))

            data = r.readframes(frame_num)
            r.close()
            if sample_width == 2:
                data = np.frombuffer(data, dtype=np.int16)
            elif sample_width == 4:
                data = np.frombuffer(data, dtype=np.int32)
            else:
                logger.error("ハイレゾ音源などの対応していないデータです。")
                return None, None

            data = self.conv_wave2np(data, ch_num) # mix_id x framesに変換

            logger.info(f"Convert numpy ver wave data: ch x frames {data.shape}")
        
        return data, output
            


    @staticmethod
    def conv_wave2np(data, ch_num):
        """
        [0, 1, 2, 3, 4, 5] 
        =>.reshape([2,3]) 
        [[0,1,2],[3,4,5]]
        =>.reshape([フレーム数, チャンネル数]).T （転置 または、order オプションを使用する）
        """
        return data.reshape([-1, ch_num]).T

    @staticmethod
    def stft(data, sample_rate, window="hann", nperseg=512, noverlap=256):
        """
        data: channel x frames
        sample_rate: サンプリング周波数
        window: stft windon
        nperseg: fftのサンプル幅
        noverlap: 各サンプルのオーバラップ度合い

        @return:
        f, t, stft_data: 周波数, 時間, ch x freq x time
        """
        f, t, stft_data = sp.stft(data, sample_rate, window=window, nperseg=nperseg, noverlap=noverlap)
        return f, t, stft_data
    
    @staticmethod
    def istft(data, sample_rate, window="hann", nperseg=512, noverlap=256):
        t, wave_data = sp.istft(data, sample_rate, window=window, nperseg=nperseg, noverlap=noverlap)
        return t, wave_data
    
    @staticmethod
    def stft_freqs(sample_rate, nperseg=512):
        Nk = int(nperseg/2 + 1)
        freqs = np.arange(0, Nk, 1) * sample_rate / nperseg
        return freqs

if __name__ == "__main__":
    file_name = "./data/test.wav"
    wave_proc = WaveProcessing()
    data, wave_info = wave_proc.read_wav(file_name)
    print(wave_info) # {'sample_rate': 16000, 'sample_width': 2, 'ch_num': 8, 'sample_num': 80384}
    f, t, stft_data = WaveProcessing.stft(data, wave_info.sample_rate)
    print(f.shape, t.shape, stft_data.shape) # (257,) (315,) (8, 257, 315)

    t, wave_data = WaveProcessing.istft(stft_data, wave_info.sample_rate)
    print(t.shape, wave_data.shape) # (8,) (8, 80384)

    freqs = WaveProcessing.stft_freqs(wave_info.sample_rate)
    print(freqs.shape)

