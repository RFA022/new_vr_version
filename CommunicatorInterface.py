from enum import Enum


class EntityTypeEnum(Enum):
    UNKNOWN = 0,
    SOLDIER = 1,
    SHORT_RANGE_ANTI_TANK = 2,
    OBSERVER = 3,
    LONG_RANGE_ANTI_TANK = 4,
    SNIPER = 5,
    DRONE = 6,
    DRONE_OPERATOR = 7,
    HIGH_TRAJECTORY_WEAPON = 8,
    HQ = 9,
    EITAN = 10,
    HALUTZ_DRONE = 11,
    OHEZ = 12,
    HALUTZ = 13,
    SUICIDE_DRONE = 14,
    NLOS = 15,
    CIVILIAN = 16


class Hostility(Enum):
    UNKNOWN = 0,
    FRIENDLY = 1,
    OPPOSING = 2,
    NEUTRAL = 3


class EntityInfo: #Blue entites data structure
    def __init__(self, entity_id: str):
        self.unit_name = entity_id
        # EntityTypeEnum
        self.classification = EntityTypeEnum.UNKNOWN
        self.global_id = None
        self.hostility = Hostility.UNKNOWN
        self.location = {
                    "latitude": None,
                    "longitude": None,
                    "altitude": None
                }
        self.last_seen_worldLocation = {
                    "latitude": None,
                    "longitude": None,
                    "altitude": None
                }
        self.interception_time=None
        # false not alive and true alive
        self.is_alive = True
        self.power = None
        self.health = None
        self.entity_damage_state = None
        self.observed=False
        self.val=None
        self.velocity={
                    "east": None,
                    "north": None,
                    "up": None
                }
        self.last_seen_velocity={
                    "east": None,
                    "north": None,
                    "up": None
                }


class ScenarioStatusEnum(Enum):
    NA = 0,
    RUNNING = 1,
    PAUSE = 2,
    RESTART = 3


class CommunicatorInterface:
    def __init__(self):
        pass

    def GetScenarioEntitiesInfo(self) -> list:
        """
        This function returns the latest update for all entities in the scenario
        :return: list of EntityInfo class object
        """
        pass

    def GetFireEvent(self) -> list:
        """
        This function is responsible to get all the fire events since that last time this function was called.
        :return: list of dict of "attacking_entity_name" and "attack_location" , if no attack event occurred,
        aan empty list will return example
        under_fire = [ {
        attacking_entity_name: "GIL" "attack_location": {"latitude": 0, "longitude": 0, "altitude": 0 } },
         { attacking_entity_name: "ITAY" "attack_location": {"latitude": 1, "longitude": 0, "altitude": 0 }
         }]
        """
        pass

    def GetScenarioStatus(self) -> ScenarioStatusEnum:
        """
        This function is responsible for get the current scenario status
        :return: ScenarioStatus enum
        """
        pass

    def TickCounter(self) -> int:
        """
        This function is responsible for get the scenario current tick counter
        :return: return the current number of tick
        """
        pass

    def CheckLos(self, src_location: dict, dest_location: dict) -> bool:
        """
        This function is responsible to check los between 2 locations
        :param src_location, contain dict of latitude, longitude and altitude
        :param dest_location, contain dict of latitude, longitude and altitude
        :return: return true if have los and false if not (or if timeout)
        example:
        src_location = {'latitude': 33.3722451, 'longitude': 35.4959193, 'altitude': 458.95838399999997}
        dest_location = {'latitude': 33.372253934425, 'longitude': 35.495998623516, 'altitude': 454.32898318388}

        """
        pass

    def GetTaskStatusEvent(self) -> list:
        """
        This function is responsible to get all the task progress status events since the last time this
        function was called.
        :return: list of dict of "entity_id" and "task_name" "task_status" true for task success
        """

        pass

    def MoveEntityToLocation(self, entity_id: str, location: dict) -> None:
        """
        This function is responsible to move entity to location
        :param entity_id: id of the entity to move
        :param location: location of the entity to move
        :return: N/A
        """
        pass

    def FireCommand(self, attacking_entity_id: str, to_attack_id: str, weapon_type: str = "") -> None:
        """
        This function is responsible for make fire event
        :param attacking_entity_id: id of the entity to perform the fire
        :param to_attack_id: id of the entity to attack
        :param weapon_type: type of the weapon to attack with
        :return: N/A
        """
        pass

    def CreateEntity(self, entity_to_create_list: list) -> None:
        """
        This function is responsible for create entity
        :param entity_to_create_list: list of EntityInfo class
        :return: N/A
        """
        pass

    def GetRandomSeed(self) -> int:
        """
        This function is responsible for return the random seed number
        :return: random seed number
        """
        pass

    def createSquad(self, squad_name: str,location: dict) -> None:
        """
        This function is responsible for create squad
        :param squad name: string from excel; location as a dict.
        :return: N/A
        """
        pass

    def setEntityPosture(self, entity_name: str,posture: int) ->None:
        """
        function that changes entity posture
        """
        pass