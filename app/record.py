import sys
import pathlib
import argparse

module_path = pathlib.Path(__file__).parent.parent.parent.resolve()
if module_path not in sys.path:
    sys.path.append(str(module_path))

from src.audio.processing import WaveProcessing
from src.microphone.device import AudioDevice

from utils import get_logger, wave_path_check
logger = get_logger()

parser = argparse.ArgumentParser(description='Audio record')

# args
parser.add_argument('-f', '--file_path', default='./data/test.wav', help='record file path.')
parser.add_argument('-mid', '--mic_id', default=0, type=int, help='microphone device id')
parser.add_argument('-t', '--record_time', default=2, type=float, help='record time')
parser.add_argument('-i', '--mic_info', action='store_true', help='display mic device info.')

def main():
    args = parser.parse_args()
    mic_info_display = args.mic_info

    device = AudioDevice()
    if mic_info_display:
        device.get_audio_devices_info()
        sys.exit(0)
    
    file_path = args.file_path
    mic_id = args.mic_id
    record_time = args.record_time

    ok = wave_path_check(file_path)
    if not ok:
        logger.error(f"fail record... by args setting.")
        sys.exit(-1)
    
    wave_proc = WaveProcessing()

    record_data, record_info = device.record(mic_id, record_time, sample_width=2)
    if record_data is None:
        logger.error(f"fail record...")
        sys.exit(-1)
    wave_proc.list_to_wave(file_path, record_data, record_info.ch_num, record_info.sample_rate, record_info.sample_width)
    logger.info("Success reocrd!")

if __name__ == "__main__":
    main()

