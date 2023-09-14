from RFAScenarioManager import *
import logging


if __name__ == '__main__':
    # 1.0 init configManager
    ConfigManager.init()

    # 2.0 init Logger
    logging.basicConfig(level=ConfigManager.GetLogLevel(),
                        format="%(asctime)s [%(levelname)s] %(message)s",
                        handlers=[logging.FileHandler("LOG/RFA_Log_" + str(time.time()) + ".log"), logging.StreamHandler()])
    # 2.1 ingone matplotlib debug notes
    mpl_logger = logging.getLogger('matplotlib')
    mpl_logger.setLevel(logging.ERROR)

    # 2.2 ignore PIl logger
    pil_logger = logging.getLogger('PIL')
    pil_logger.setLevel(logging.ERROR)

    # 2.3 ignore tkinter logger
    tkinter_logger = logging.getLogger('tkinter')
    tkinter_logger.setLevel(logging.ERROR)

    # 3.0 init RFA
    logging.info("main.py - Initializing RFA")
    rfa = RFAScenarioManager()

    # 4.0 running RFA
    logging.info("main.py  - Running RFA")
    rfa.Run()
