
import numpy as np
def calc_circumference_locations(r, interval_dir):
    """
    円周上の配置を計算
    r: 中心からの距離[m]
    interval_dir: 角度間隔　(度), ex: 30度
    """
    dirs = np.array(
        [[np.pi / 2., theta/180 * np.pi] for theta in np.arange(0, 360, interval_dir)]
    ) # elevation, azimuth

    alignments = np.zeros((3, dirs.shape[0]), dtype=dirs.dtype) # x, y, z
    alignments[0, :] = np.cos(dirs[:, 1]) * np.sin(dirs[:, 0])
    alignments[1, :] = np.sin(dirs[:, 1]) * np.sin(dirs[:, 0])
    alignments[2, :] = np.sin(dirs[:, 0])
    alignments *= r
    return dirs, alignments