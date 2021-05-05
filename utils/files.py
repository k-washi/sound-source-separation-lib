import sys
import os
import pathlib

# utilsのパスを通す
module_path = pathlib.Path(__file__).parent.parent.resolve()
if module_path not in sys.path:
    sys.path.append(str(module_path))

from utils import get_logger
logger = get_logger()

AUDIO_EXT = ["wav", "mp3"]

def wave_path_check(file_path):
    # ディレクトリのチェック
    dir_name = os.path.dirname(file_path)
    if not os.path.isdir(dir_name):
        logger.error(f'Dir: {dir_name} is not exist.')
        return False

    # extのチェック
    _, ext = os.path.splitext(file_path)
    ext = ext.replace(".", "")
    if ext not in AUDIO_EXT:
        logger.error(f'ext: {ext} is not audio extension.')
        return False
    return True