from os import sep
import sys
import pathlib
import argparse
import numpy as np
from matplotlib.pyplot import plot

module_path = pathlib.Path(__file__).parent.parent.parent.resolve()
if module_path not in sys.path:
    sys.path.append(str(module_path))

from src.audio.processing import WaveProcessing

from utils import get_logger, wave_path_check, Config
logger = get_logger()

parser = argparse.ArgumentParser(description='Audio record')

# args
parser.add_argument('-f', '--file_path', default='./data/test.wav', help='audio file path.')
parser.add_argument('-o', '--output_dir', default='./data', help='audio output dir.')
parser.add_argument('-m', '--mode', default=0, type=int, help='sound source sep mode')
parser.add_argument('-d', '--dirs', nargs="*", type=int, help="sound source directions (azimuth)")
parser.add_argument('--plot', action='store_true', help="plot")

def main():
    args = parser.parse_args()
    conf = Config.get_cnf()

    audio_conf = conf.audio
    
    
    file_path = args.file_path
    sss_mode = args.mode
    output_dir = args.output_dir
    ss_azimuth = args.dirs
    do_plot = args.plot

    if do_plot:
        logger.info("Plot mode...!")

    ok = wave_path_check(file_path)
    if not ok:
        logger.error(f"fail record... by args setting.")
        sys.exit(-1)

    if len(ss_azimuth) == 0:
        logger.error(f"Should set sound source azimuths by -d.")
        sys.exit(-1)
        
    wave_proc = WaveProcessing()
    

    # 音情報の読み込み
    data, wave_info = wave_proc.read_wav(file_path)
    if data is None:
        sys.exit(-1)
    logger.info("Success read wave data...!")

    # 周波数情報に変換
    stft_conf = audio_conf.stft
    freqs, stft_times, stft_data = WaveProcessing.stft(data, wave_info.sample_rate, stft_conf.window, stft_conf.nperseg, stft_conf.noverlap)
    
    # 音源分離
    if sss_mode == 0:
        # ビームフォーマ
        from src.sss.beamformer import SparseBeamforming
        ss_method = SparseBeamforming(conf, wave_info=wave_info)
    else:
        logger.error('Not define mode of sound source separation method.')
    
    sep_sound = ss_method(stft_data, ss_azimuth)
    
    # 時間領域情報に戻す
    for s in range(len(ss_azimuth)):
        _, wave_data = WaveProcessing.istft(sep_sound[0, s, ...], wave_info.sample_rate, stft_conf.window, stft_conf.nperseg, stft_conf.noverlap)
        print(wave_data.max(), wave_data.min())
        wave_proc.list_to_wave(f"{output_dir}/sep_{s}.wav", wave_data.astype(np.int16).tolist(), 1, wave_info.sample_rate, wave_info.sample_width)

    if do_plot:
        from src.display.plot import plot_mic_locations, plot_ss_locations, plot_spectrogram
        if sss_mode == 0:
            plot_mic_locations(ss_method.mic_locations[:2])
            plot_ss_locations(ss_method.vss_locations[:2])
            plot_spectrogram(ss_method.spectrogram, ss_method.vss_dirs[:, 1], stft_times)

    


if __name__ == "__main__":
    main()

    