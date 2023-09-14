from CommunicatorInterface import *
import random
from EntityCurrentState import *

class SpawnManager_Nadav:
    def __init__(self, communicator,spawnPos,AttackPos,squadsData,intervisibility_polygoins):
        self.communicator = communicator
        self.spawn_entity_list = []
        self.green_spawn_entity_list = []
        self.spawnPos = spawnPos
        self.AttackPos = AttackPos
        self.squadsData=squadsData
        self.intervisibility_polygoins=intervisibility_polygoins
        logging.debug(self.__class__.__name__ + " is initialized")


    def Run(self):
        "spawn squads"
        # agent creation:
        LOC_index =random.randrange(len(self.spawnPos))
        LOC=self.spawnPos[LOC_index]
        self.createRedSquad(LOC,'anti_tank_1')

        "Spawn green entities"

        for i in range(4):
            LOC_index = random.randrange(len(self.spawnPos))
            LOC = self.spawnPos[LOC_index]
            name=str("civil_")+(str(i))
            choices=["3:1:225:3:0:1:0","3:1:225:3:1:1:0"] #civil male, civil female,
            code=random.choice(choices)
            self.createGreenEntity(LOC,name,code)


        "Spawn and attack points"
        ##_______________code that creates positions as way points___________________###
        # ---# create positions #---##
        for i in range(len(self.AttackPos)):
            pos = [self.AttackPos[i]['latitude'], self.AttackPos[i]['longitude'], self.AttackPos[i]['altitude']]
            self.communicator.CreateEntitySimple('attack point' + str(i), pos, 3, '16:0:0:1:0:0:0')

        # for i in range(len(self.spawnPos)):
        #     pos=[self.spawnPos[i]['latitude'],self.spawnPos[i]['longitude'],self.spawnPos[i]['altitude']]
        #     self.communicator.CreateEntitySimple('spawn point' + str(i),pos,2,'16:0:0:1:0:0:0')

        # "Spawn intervisibility polygons"
        # for i in range(len(self.intervisibility_polygoins)):
        #         area=self.intervisibility_polygoins[i]['polygon']
        #         self.communicator.CreateTacticalGraphicCommand('cover_' + str(i),2,area)


    def createRedSquad(self,LOC,squadName):
        LOC = {
            "latitude":  LOC['latitude'],
            "longitude": LOC['longitude'],
            "altitude": LOC['altitude']
        }
        squadSize=len(self.squadsData.at[str(squadName),'unit_name'])
        for k in range(squadSize):
            current_entity = EntityCurrentState("")
            current_entity.current_location = {
                "latitude": LOC['latitude'],
                "longitude": LOC['longitude'],
                "altitude": LOC['altitude']
            }
            current_entity.hostility = Hostility.OPPOSING
            current_entity.unit_name = self.squadsData.at[str(squadName),'unit_name'][k]
            current_entity.role = self.squadsData.at[str(squadName), 'unit_type'][k]
            current_entity.squad = squadName
            self.spawn_entity_list.append(current_entity)
        self.communicator.createSquad(str(squadName), LOC)

    def createGreenEntity(self,LOC,name,code):
        LOC = {
            "latitude":  LOC['latitude'],
            "longitude": LOC['longitude'],
            "altitude": LOC['altitude']
        }

        current_entity = EntityCurrentState("")
        current_entity.worldLocation = {"location": {
                "latitude": LOC['latitude'],
                "longitude": LOC['longitude'],
                "altitude": LOC['altitude']}}
        current_entity.hostility = Hostility.NEUTRAL
        current_entity.unit_name = name
        current_entity.role = "ci"
        current_entity.squad = "CivilSquad"
        self.green_spawn_entity_list.append(current_entity)
        self.communicator.CreateEntitySimple(name, LOC, 3, code)