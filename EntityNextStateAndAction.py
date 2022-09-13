from EntityCurrentState import *


class EntityNextStateAndAction:
    def __init__(self, entity_id: str):
        "Red"
        self.entity_id = entity_id
        self.position: PositionType = None
        self.positionType = None
        self.position_location = {"latitude": -1, "longitude": -1, "altitude": -1}
        self.entity_to_fire = ""
        self.move_pos = False
        self.takeAction = 0
        self.nextPos = None
        self.nextPosture = None
        self.scan_for_enemy=None
        self.aim=False
        self.shoot=None #none is not shoot and not stop shoot. True is to shoot. False is to stop shooting
        self.null=None
        self.HTN_target=[]
        self.timeOutAbortCurrentTask=False
        "Green"
        self.wait_at_position=False
        self.waitTime=None
        self.nextRoute=None
    def SetPosition(self, new_position: PositionType, location: dict):
        self.position = new_position
        self.position_location["latitude"] = location["latitude"]
        self.position_location["longitude"] = location["longitude"]
        self.position_location["altitude"] = location["altitude"]
        self.position_location_id = location["location_id"]


    def SetFireEvent(self, entity_to_fire: str):
        self.to_fire = True
        self.entity_to_fire = entity_to_fire

