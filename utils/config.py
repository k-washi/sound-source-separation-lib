import sys
import os
import pathlib
from hydra.experimental import compose, initialize_config_dir

# utilsのパスを通す
module_path = pathlib.Path(__file__).parent.parent.resolve()
if module_path not in sys.path:
    sys.path.append(str(module_path))

from utils.logger import get_logger
logger = get_logger()

class Config():
    """
    hydraによる設定値の取得 (conf)
    """
    @staticmethod
    def get_cnf():
        """
        設定値の辞書を取得
        @param
            conf_path: str
        @return
            cnf: OmegaDict
        """
        conf_dir = os.path.join(os.getcwd(), "conf")
        if not os.path.isdir(conf_dir):
            logger.error(f"Can not find file: {conf_dir}.")
            sys.exit(-1)

        with initialize_config_dir(config_dir=conf_dir):
            cnf = compose(config_name="default.yaml")
            return cnf

if __name__ == "__main__":
    conf = Config.get_cnf()
    print(conf)