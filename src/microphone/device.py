import sys
import pathlib
import pyaudio
import numpy as np
import time
from omegaconf import OmegaConf
from dataclasses import dataclass

# パスを通す
module_path = pathlib.Path(__file__).parent.parent.parent.resolve()
if module_path not in sys.path:
    sys.path.append(str(module_path))

from utils import get_logger
logger = get_logger()

@dataclass
class RecordOutputStruct():
    sample_rate: int
    sample_width: int
    ch_num: int

class AudioDevice():
    """
    音響デバイスに関して
    """
    def __init__(self) -> None:
        self._pAudio = pyaudio.PyAudio()
        self._mic_id = 0 # default

        self._audio_dtype = np.int16
    
    def get_audio_devices_info(self):
        """
        情報の取得
        """
        device_dict = {}
        for i in range(self._pAudio.get_device_count()):
            dev = self._pAudio.get_device_info_by_index(i)
            text = f"Index: {dev['index']} | Name: {dev['name']} | ChannelNum: in {dev['maxInputChannels']} out {dev['maxOutputChannels']} | SampleRate: {dev['defaultSampleRate']}"
            print(text)
            
            device_dict[int(dev['index'])] = dev
        return device_dict
    
    def get_audio_divice_info(self, mic_id):
        """
        情報の格納
        """
        devices_info = self.get_audio_devices_info()

        dev = devices_info.get(mic_id, None)
        if dev is None:
            logger.error(f"Can not set mic info: {mic_id}, mic id list: {devices_info.keys()}")
            return None

        return dev
    
    def __record_callback(self, in_data, frame_count, time_info, status):
        in_data = np.frombuffer(in_data, self._audio_dtype)
        self._record_list.extend(in_data.tolist())
        return (in_data, pyaudio.paContinue)
    def record(self, mic_id, record_time= 5, sample_width=2, stream_chunk=512):
        """
        mic_id: マイクのID
        record_time: 録音する秒数(sec)
        """

        # デバイス情報を取得・セット
        device_info = self.get_audio_divice_info(mic_id)
        if device_info is None:
            sys.exit(-1)
        
        mic_name = device_info['name']
        input_channel_num = int(device_info['maxInputChannels'])
        sample_rate = int(device_info['defaultSampleRate'])

        record_output = OmegaConf.structured(RecordOutputStruct(
            sample_rate=sample_rate,
            sample_width=sample_width,
            ch_num=input_channel_num
        ))

        logger.info(f"Record Device: {mic_name}, CH num: {input_channel_num}, Sample rate: {sample_rate}")
        
        if sample_width == 2:
            audio_format = pyaudio.paInt16
            self._audio_dtype = np.int16
        else:
            logger.error("ハイレゾ: SampleWidth:2以外は、まだ、対応していないです。")
            return None

        # 収録
        self._record_list = []
        
        stream = self._pAudio.open(
            format=audio_format,
            rate=sample_rate,
            channels=input_channel_num,
            input=True,
            output=False,
            input_device_index=mic_id,
            output_device_index=None,
            stream_callback=self.__record_callback,
            frames_per_buffer=stream_chunk
        )
        stream.start_stream()
        logger.info("Recording start...")
        start_time = time.time()

        while stream.is_active():
            if len(self._record_list) / sample_rate / input_channel_num > record_time:
                break
            """
            if time.time() - start_time > record_time:
                break
            """

        stream.close()
        self._pAudio.terminate()
        logger.info(f"Recording stop! tims is {len(self._record_list)/sample_rate/input_channel_num}")

        return self._record_list, record_output
        

        


    
    
if __name__ == "__main__":
    from utils import Config
    from src.audio.wave import WaveProcessing
    conf = Config.get_cnf()
    logger.info(conf)

    device_id = 1
    record_time = 2
    save_file = "./data/test.wav"

    device = AudioDevice()
    wave_proc = WaveProcessing()

    record_data, record_info = device.record(device_id, record_time, sample_width=2)
    if record_data is None:
        print("error")
    wave_proc.list_to_wave(save_file, record_data, record_info.ch_num, record_info.sample_rate, record_info.sample_width)