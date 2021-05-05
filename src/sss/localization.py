import sys
import pathlib
import numpy as np


module_path = pathlib.Path(__file__).parent.parent.parent.resolve()
if module_path not in sys.path:
    sys.path.append(str(module_path))

from utils import get_logger
logger = get_logger()

class Localization():
    """
    マイクロホンアレイが2次元平面のある円周上に等間隔で並んでいるものとする。
    """
    def __init__(self) -> None:
        pass

    
    def beamforming(self, stft_data, steering_vectors):
        """
        stft_data: mics x freqs x times
        steerin_vectors: freqs, virtual_ss, mics
        """


        inner_prod = np.einsum("kim,mkt->kit",
            np.conjugate(steering_vectors), stft_data
        ) # freqs x vss x times
        max_dirs = np.argmax(np.abs(inner_prod), axis=1)
        return max_dirs, np.abs(inner_prod)
    
    def assign_locations(self, max_dirs, ss_azimuth, virtual_dirs, assign_dir):
        """
        各周波数でmax_dirsをssに割り当てる # azimuth方向のみで考える
        max_dirs: freqs x times # 各周波数ごとの最大方向
        ss_azimuth: ss_num x [eve, azi]: 分離方向:あらかじめ指定
        virtual_dirs: vss_num x [eve, azi]
        assigen_dir: この範囲内だと割り当てる [deg]
        """
        ss_num = len(ss_azimuth)
        ss_azimuth = [s / 180. * np.pi for s in ss_azimuth]

        def modify_angle_diff(diff):
            # np.pi 以上のものを削除するようにする
            diff = np.where(diff < -np.pi, diff + np.pi*2, diff)
            diff = np.where(diff > np.pi, diff - np.pi * 2, diff)
            return diff
        
        omega = np.array([
            np.abs(modify_angle_diff(
                virtual_dirs[:, 1] - ss_azimuth[s]
            )) < assign_dir/180 * np.pi for s in range(ss_num)
        ]) # ss_num x vss_dirss 割り当てる角度範囲指定

        n_omega = omega.shape[1]
        estimate_doa_mask = np.identity(n_omega)[max_dirs] # freq x time x dir
        output_mask = np.einsum("kti,si->skt", estimate_doa_mask, omega)
        
        return output_mask





        




