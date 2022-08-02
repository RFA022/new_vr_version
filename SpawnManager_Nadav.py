#from PlacementManager import *
from Communicator import *
from ConfigManager import *
import random
from EntityCurrentState import *
import numpy as np
class SpawnManager_Nadav:
    def __init__(self, communicator,spawnPos,AttackPos,BluePolygon):
        self.communicator = communicator
        self.spawn_entity_list = []
        self.spawnPos=spawnPos
        self.AttackPos = AttackPos
        self.BluePolygon=BluePolygon
        logging.debug(self.__class__.__name__ + " is initialized")

        ###_____not in use____###:
        #self.entity_to_create_list = []

    def Run(self):
        #agent creation:
        LOC_index =random.randrange(len(self.spawnPos))
        #print(LOC_index)
        LOC=self.spawnPos[LOC_index]
        self.createATSquad(LOC,'anti_tank',[EntityTypeEnum.SHORT_RANGE_ANTI_TANK,EntityTypeEnum.OBSERVER,EntityTypeEnum.SOLDIER,EntityTypeEnum.SOLDIER],['at_1','ob_1','so_1','so_2'])
        ###_______________old code that creates old single entity___________________###
        #self.createEntity(EntityTypeEnum.SOLDIER,LOC,Hostility.OPPOSING,'Agent')
        #self.communicator.CreateEntity(self.entity_to_create_list) #important line that creates for real the enteties

        ###_______________code that creates positions as way points___________________###
        ##---# create positions #---##
        for i in range(len(self.AttackPos)):
            pos = [self.AttackPos[i]['latitude'], self.AttackPos[i]['longitude'], self.AttackPos[i]['altitude']]
            self.communicator.CreateEntitySimple('attack point' + str(i), pos, 3, '16:0:0:1:0:0:0')
        #
        # for i in range(len(self.spawnPos)):
        #     pos=[self.spawnPos[i]['latitude'],self.spawnPos[i]['longitude'],self.spawnPos[i]['altitude']]
        #     self.communicator.CreateEntitySimple('spawn point' + str(i),pos,2,'16:0:0:1:0:0:0')
        # for i in range(len(self.BluePolygon)):
        #     pos=[self.BluePolygon[i]['latitude'],self.BluePolygon[i]['longitude'],self.BluePolygon[i]['altitude']]
        #     self.communicator.CreateEntitySimple('Poly' + str(i),pos,1,'17:1:0:0:5:1:0')
        #---# create positions #---##

    def createATSquad(self,LOC,squadName,classification_vec,names_vec):
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
            current_entity.classification = classification_vec[k]
            current_entity.unit_name = names_vec[k]
            self.spawn_entity_list.append(current_entity)
        self.communicator.createSquad('anti_tank', LOC)

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


