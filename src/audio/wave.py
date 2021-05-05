import sys
import pathlib
import pyaudio
import struct
import wave
# パスを通す
module_path = pathlib.Path(__file__).parent.parent.parent.resolve()
if module_path not in sys.path:
    sys.path.append(str(module_path))

from utils import get_logger
logger = get_logger()


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
        