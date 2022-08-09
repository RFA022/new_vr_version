from enum import Enum
import CommunicatorInterface as CI

class PositionType(Enum):
    AT_OP = 0,
    MOVE_TO_OP = 1

class isFire(Enum):
    yes = 1,
    no = 0

class EntityCurrentState: #red entities

    def __init__(self, entity_id: str):
        self.unit_name = entity_id
        self.classification = CI.EntityTypeEnum.UNKNOWN
        self.global_id = None
        self.hostility = CI.Hostility.UNKNOWN
        self.worldLocation = {
            "latitude": 0,
            "longitude": 0,
            "altitude": 0
        }
        self.is_alive = True
        self.power = None
        self.health = None
        self.entity_damage_state = None


        self.movement_task_completed = 0
        self.movement_task_success = False

        self.fire_task_completed = 0
        self.fire_task_success = False

        self.target_location = {
            "latitude": 0,
            "longitude": 0,
            "altitude": 0
        }
        self.COA=[]
        self.face=None
        self.planBool=1
        self.state = PositionType.AT_OP
        self.fireState = isFire.no
        self.aim_list=[]
        self.taskTime=None
        self.preGameBool=True # boolean that active for first 10 seconds of the game. able to activate operations before first HTN search

class HTNentity:
    def __init__(self, entity_id: str):
        self.unit_name=entity_id
        self.classification = CI.EntityTypeEnum.UNKNOWN
        self.location = {
            "latitude": None,
            "longitude": None,
            "altitude": None
        }
        self.observed=False
        self.is_alive = None
        self.val=None
