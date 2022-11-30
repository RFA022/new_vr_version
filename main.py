from RFAScenarioManager import *
import logging


if __name__ == '__main__':
    ConfigManager.init()

    logging.basicConfig(level=ConfigManager.GetLogLevel(),
                        format="%(asctime)s [%(levelname)s] %(message)s",
                        handlers=[logging.FileHandler("LOG/RFA_Log_" + str(time.time()) + ".log"), logging.StreamHandler()])
    logging.info("Initializing RFA")
    rfsm = RFAScenarioManager()
    rfsm.Run()
