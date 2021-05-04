import logging

loggers = {}

def get_logger(name=None):
    global loggers
    if name is None:
        name = "sound-source-sep"

    if loggers.get(name):
        return loggers.get(name)

    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(levelname)-8s: %(asctime)s | %(filename)-12s - %(funcName)-12s : %(lineno)-4s -- %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    loggers[name] = logger

    return logger

if __name__ == "__main__":
    logger = get_logger()
    logger.info("test")