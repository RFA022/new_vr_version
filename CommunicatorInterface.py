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

