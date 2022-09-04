import csv
import json
import logging
from enum import Enum
import sys
import numpy as np
# import PlacementManager
# import RFSMLogic
# import RFSMManager
from CommunicatorInterface import EntityTypeEnum


class EntityConfig:
    def __init__(self, entity_type: EntityTypeEnum):
        self.entity_type = entity_type
        self.entity_id = 0



class ConfigManager:
    entity_config_data = []
    placement_config_data = []
    areas_config_data = []

    min_entity_to_create_list = []
    max_entity_to_create_list = []

    config_data = None
    # entities per area
    min_number_of_entity = 4
    max_number_of_entity = 7


    min_number_of_civilians = 0
    max_number_of_civilians = 0

    min_number_of_civilians_area_of_interest = 0
    max_number_of_civilians_area_of_interest = 0
    min_number_of_anti_tank_area_of_interest = 0
    max_number_of_anti_tank_area_of_interest = 0

    radius_to_hit = 15
    my_rand = None

    compounds_dict = dict()

    @staticmethod
    def init() -> None:

        configfileName = "Resources/RFSMConfig.json"
        with open(configfileName, "r") as config_file:
            ConfigManager.config_data = json.load(config_file)


    @staticmethod
    def GetMode() -> str:
        return ConfigManager.config_data['Mode']

    @staticmethod
    def GetTimeOrTickMode() -> str:
        return ConfigManager.config_data['TickOrTimeMode']

    @staticmethod
    def GetTickTimeInSec() -> float:
        return ConfigManager.config_data['TickTimeInSec']

    @staticmethod
    def GetGodotIp() -> str:
        return str(ConfigManager.config_data['Godot_ip_local']).strip()

    @staticmethod
    def GetGodotIRemote() -> str:
        return str(ConfigManager.config_data['Godot_ip_remote']).strip()

    @staticmethod
    def GetGodotControlServerPort() -> int:
        return int(ConfigManager.config_data['Godot_control_server_port'])

    @staticmethod
    def GetGodotSaeServerPort() -> int:
        return int(ConfigManager.config_data['Godot_sae_server_port'])

    @staticmethod
    def GetGodotGTServerPort() -> int:
        return int(ConfigManager.config_data['Godot_gt_server_port'])

    @staticmethod
    def GetGodotScenarioControlClientPort() -> int:
        return int(ConfigManager.config_data['Godot_scenario_control_client_port'])

    @staticmethod
    def GetGodotTickCompletePort() -> int:
        return int(ConfigManager.config_data['Godot_tick_complete_port'])

    @staticmethod
    def GetLogLevel():
        log_level = ConfigManager.config_data['Logger_Level']
        return logging.getLevelName(log_level)

    @staticmethod
    def GetTeleportEntities() -> bool:
        if ConfigManager.config_data['TeleportEntities'] == "FALSE":
            return False
        else:
            return True

    @staticmethod
    # moving position speed in m/s
    def GetMovingPosSpeed() -> float:
        return ConfigManager.config_data['MovingPosSpeed']


    @staticmethod
    def getEntityConfig(entity_type: str) -> EntityConfig:
        try:
            if type(entity_type) != str:
                entity_type = str(entity_type.name).strip()
            elif ('EntityTypeEnum.' in entity_type):
                entity_type = entity_type[15:].strip()
            current_config_dict = {}
            entity_type = entity_type.strip().upper()
            for i in range(len(ConfigManager.entity_config_data)):
                current_entity_to_check = str.upper(ConfigManager.entity_config_data[i].get("type")).strip()
                if current_entity_to_check == entity_type:
                    current_config_dict = ConfigManager.entity_config_data[i]
                    break

            entity_config = EntityConfig(entity_type)
            entity_config.entity_id = current_config_dict.get("id")
            if ConfigManager.GetMode() == "VRF":
                entity_config.vrf_or_godot_id = current_config_dict.get("vrfid")

            elif ConfigManager.GetMode() == "GODOT":
                entity_config.vrf_or_godot_id = current_config_dict.get("godotid")
                pass

            entity_config.spawnmin = int(current_config_dict.get("spawnmin"))
            entity_config.spawnmax = int(current_config_dict.get("spawnmax"))
            entity_config.timeop = current_config_dict.get("timeop")
            entity_config.timecover = current_config_dict.get("timecover")
            entity_config.probability = float(current_config_dict.get("probabilty"))
            entity_config.relevant_weapon = current_config_dict.get("relevantweapon")
            entity_config.weapon_range = float(current_config_dict.get("weaponrange"))
            entity_config.underfire_range = float(current_config_dict.get("underfirerange"))
            entity_config.detection_range = float(current_config_dict.get("detectionrange"))
            entity_config.hearing_range = float(current_config_dict.get("hearingRange"))
            entity_config.Spawn_probability = current_config_dict.get("SpawnProbability")
            entity_config.enemy_detection_probability = float(current_config_dict.get("enemydetectionprobability"))
            entity_config.max_range_next_op = float(current_config_dict.get("maxrange"))
            entity_config.min_range_next_op = float(current_config_dict.get("minrange"))
            return entity_config
        except:
            logging.debug("error create entity configuration")

    @staticmethod
    def GetPlacementConfig() -> list:
        try:
            return ConfigManager.placement_config_data

        except:
            logging.error("error to return placement config data")
            sys.exit(1)

    @staticmethod
    def GetCompoundsDict() -> dict:
        try:
            return ConfigManager.compounds_dict

        except:
            logging.error("error to return compounds dictionary")
            sys.exit(1)

    @staticmethod
    def GetForceRemote() -> str:
        try:
            return str(ConfigManager.config_data['ReceivingForcesRemotely']).strip().upper()
        except:
            logging.error("error to return forces remote or local")
            sys.exit(1)

    @staticmethod
    def SetRandomSeed(seed: int):
        config_seed = int(ConfigManager.config_data['Random_Seed'])
        # case 1 getting seed number from godot
        if seed:
            np.random.seed(seed)
            logging.debug("random seed set with value: " + str(seed))
        # case 2 getting seed number from config file
        elif config_seed != -1:
            np.random.seed(config_seed)
            logging.debug("random seed set with value: " + str(config_seed))

        # case 3 stay with random seed number
