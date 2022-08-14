#from PlacementManager import *
#from Communicator import *
from CommunicatorInterface import *
from ConfigManager import *
import random
from EntityCurrentState import *
import numpy as np
import pandas as pd

class SpawnManager_Nadav:
    def __init__(self, communicator,spawnPos,AttackPos,squadsData):
        self.communicator = communicator
        self.spawn_entity_list = []
        self.spawnPos = spawnPos
        self.AttackPos = AttackPos
        self.squadsData=squadsData
        logging.debug(self.__class__.__name__ + " is initialized")


    def Run(self):
        #agent creation:
        LOC_index =random.randrange(len(self.spawnPos))
        LOC=self.spawnPos[LOC_index]
        self.createRedSquad(LOC,'anti_tank')
        ###_______________old code that creates old single entity___________________###
        #self.createEntity(EntityTypeEnum.SOLDIER,LOC,Hostility.OPPOSING,'Agent')
        #self.communicator.CreateEntity(self.entity_to_create_list) #important line that creates for real the enteties
        "Spawn and attack points"
        # ##_______________code that creates positions as way points___________________###
        #---# create positions #---##
        # for i in range(len(self.AttackPos)):
        #     pos = [self.AttackPos[i]['latitude'], self.AttackPos[i]['longitude'], self.AttackPos[i]['altitude']]
        #     self.communicator.CreateEntitySimple('attack point' + str(i), pos, 3, '16:0:0:1:0:0:0')
        #
        # for i in range(len(self.spawnPos)):
        #     pos=[self.spawnPos[i]['latitude'],self.spawnPos[i]['longitude'],self.spawnPos[i]['altitude']]
        #     self.communicator.CreateEntitySimple('spawn point' + str(i),pos,2,'16:0:0:1:0:0:0')


    def createRedSquad(self,LOC,squadName):
        LOC = {
            "latitude":  LOC['latitude'],
            "longitude": LOC['longitude'],
            "altitude": LOC['altitude']
        }
        for k in range(4):
            current_entity = EntityCurrentState("")
            current_entity.worldLocation = {"location": {
                "latitude": LOC['latitude'],
                "longitude": LOC['longitude'],
                "altitude": LOC['altitude']
            }
            }
            current_entity.hostility = Hostility.OPPOSING
            current_entity.unit_name = self.squadsData.at[str(squadName),'unit_name'][k]
            self.spawn_entity_list.append(current_entity)
        self.communicator.createSquad(str(squadName), LOC)

    ###_______________single entity creation- not in use___________________###
    #not supported function
    # def createEntity(self, entity_to_create: EntityTypeEnum,LOC,hostility,NAME):
    #     current_entity = EntityInfo("")
    #     current_entity.worldLocation = {"location": {
    #         "latitude":  LOC['latitude'],
    #         "longitude": LOC['longitude'],
    #         "altitude": LOC['altitude']
    #     }
    #     }
    #     current_entity.hostility = hostility
    #     current_entity.classification = entity_to_create
    #     current_entity.unit_name = NAME
    #     self.entity_to_create_list.append(current_entity)
    #
    #     entityData = EntityCurrentState(current_entity.unit_name)
    #
    #     entityData.current_location = {
    #         "latitude":  LOC['latitude'],
    #         "longitude": LOC['longitude'],
    #         "altitude": LOC['altitude']
    #     }
    #     entityData.entity_type = str.upper(entity_to_create.name).strip()
    #     entityData.general_classification = entity_to_create
    #     entityData.alive = True
    # self.spawn_entity_list.append(entityData)


