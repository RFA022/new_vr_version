import logging
import sys

import ConfigManager
import EntityCurrentState
#import PlacementManager
from HTNLogic import *
from EntityNextStateAndAction import *
from SpawnManager_Nadav import *
import time
import copy
import htnModel
import pandas as pd
import pymap3d as pm
from ext_funs import *
import ext_funs
from Communicator import CommunicatorSingleton



class RFAScenarioManager:
    def __init__(self):

        #Running and Configs:
        if ConfigManager.GetMode() == "VRF":
            self.communicator = CommunicatorSingleton().obj
            logging.debug("Running in vrf mode")
        else:
            logging.error("None valid mode")
            raise Exception("None valid mode")

        self.spawnPos = self.get_positions_fromCSV('RedSpawnPos.csv')
        self.AttackPos = self.get_positions_fromCSV('RedAttackPos.csv')
        self.Polygons = self.communicator.getAreasQuery()
        self.start_scenario_time = 0
        self.first_enter = True


        #Entities Lists:
        self.entity_list = []
        self.blue_entity_list = []
        self.blue_entity_list_HTN=[]

        #General config data:
        self.configuration = pd.read_csv('Configuration.csv',
                                         header=[0],
                                         index_col=[0])
        self.squadPosture = {}
        self.squadPosture['standing_height']  = float(self.configuration.at['standing_height', 'value'])
        self.squadPosture['crouching_height'] = float(self.configuration.at['crouching_height', 'value'])

        self.enemyDimensions = {}
        self.enemyDimensions['eitan_cg_height']=float(self.configuration.at['eitan_cg_height', 'value'])

        self.basicRanges = {}
        self.basicRanges['squad_view_range'] = float(self.configuration.at['squad_view_range', 'value'])
        self.basicRanges['rpg_range'] = float(self.configuration.at['rpg_range', 'value'])
        self.basicRanges['javelin_range'] = float(self.configuration.at['javelin_range', 'value'])
        self.basicRanges['ak47_range'] = float(self.configuration.at['ak47_range', 'value'])



        logging.debug(self.__class__.__name__ + " Constructor executed successfully")

    def Run(self):

        while True:
            if self.communicator.GetScenarioStatus() == ScenarioStatusEnum.RUNNING:
                time.sleep(0.5) #sleep time between every iteration
                if self.start_scenario_time == 0:
                    self.start_scenario_time = time.time()

                #update Red list from simulator and from last iteration
                self.entity_list=self.CreateAndUpdateEntityList(self.entity_list)
                #update Blue list from simulator and from last iteration (info about last seen location)
                self.blue_entity_list = self.getBlueEntityList(self.blue_entity_list)
                self.blue_entity_list_HTN=ext_funs.getBluesDataFromVRFtoHTN(self.blue_entity_list)

                numberOfAliveBlues=getNumberofAliveEnemies(self.blue_entity_list)
                if numberOfAliveBlues == 0:
                    logging.debug("Red as won the game")
                    break

                #Debug
                # for blue in self.blue_entity_list:
                #     print('alive status for blue list entity '+ str(blue.unit_name + "is: "+ str(blue.is_alive)))
                # for blue in self.blue_entity_list_HTN:
                #     print('alive status for HTN blue list entity ' + str(blue.unit_name + "is: " + str(blue.is_alive)))

                fire_list = self.communicator.GetFireEvent()
                task_status_list = self.communicator.GetTaskStatusEvent()

                #Debug
                # print(task_status_list)
                # print(fire_list)
                # Run over all entity
                for i in range(len(self.entity_list)):
                    current_entity = self.entity_list[i]
                    "Zeroing preGameBool for all entites after 10 seconds of game"
                    #Debug
                    # print(time.time()-self.start_scenario_time)
                    if time.time()-self.start_scenario_time>1:
                        if current_entity.preGameBool==True:
                            current_entity.preGameBool=False
                    if current_entity.alive:
                        #check movement status if unit is moving
                        if current_entity.state == PositionType.MOVE_TO_OP:
                                # Check task status for movement tasks
                                for task in task_status_list:
                                    if current_entity.unit_name == task.get("markingText"):
                                        if task.get("taskName") == "vrf-move-to-location-task":
                                            current_entity.movement_task_completed = task.get("currentStatus")
                                            current_entity.movement_task_success = task.get("taskSuccess")

                       #check fire status if unit is shooting
                        if current_entity.fireState == isFire.yes:
                                # Check task status for movement tasks
                                for task in task_status_list:
                                    if current_entity.unit_name == task.get("markingText"):
                                        if task.get("taskName") == "fire-at-target":
                                            current_entity.fire_task_completed = task.get("currentStatus")
                                            current_entity.fire_task_success = task.get("taskSuccess")
                                # Updating  Tasktime for fire if unit is shooting
                                for fire_event in fire_list:
                                    if fire_event['attacking_entity_name']== current_entity.unit_name:
                                        current_entity.taskTime=time.time()
                        # Debug:
                        # print("---Debug Seasson---")#
                        # print(str(current_entity.unit_name))
                        # print(current_entity.fireState)
                        # print(current_entity.fire_task_completed)
                        # print(current_entity.fire_task_success)
                        # print('--------------------------------')
                        # next state and action- every iteration even tough COA is empty
                        entity_next_state_and_action = HTNLogic().Step(current_entity,
                                                                       self.start_scenario_time, self.AttackPos)
                    #---#---get the next state and action---#---#
                    if current_entity.unit_name=="at_1":
                        # Debug:
                        # print("---Debug Seasson---")#
                        # print(current_entity.fireState)
                        # print(current_entity.fire_task_completed)
                        # print(current_entity.fire_task_success)
                        # print('--------------------------------')
                        # print(current_entity.state)
                                # print(current_entity.movement_task_completed)
                        # print(current_entity.movement_task_success)
                        # print('--------------------------------')
                        "Replan"
                        if current_entity.COA==[]:
                            current_entity.planBool=1

                        "planning able to plan only if COA is empty"
                        if current_entity.planBool==1 and current_entity.COA==[]:
                            current_entity.planBool=0
                            self.entity_list[i].COA=htnModel.findplan(self.basicRanges,
                                                                      self.squadPosture,
                                                                      self.enemyDimensions,
                                                                      current_entity.current_location,
                                                                      self.blue_entity_list_HTN)

                        #implementation of next state and action.
                        #check if takeAction bool == 1:
                        if current_entity.alive and (entity_next_state_and_action.takeAction == 1 or current_entity.preGameBool==True):
                            if current_entity.preGameBool==True:
                                current_entity.preGameBool=False
                            current_entity.COA.pop(0)
                            #Change nextPos:
                            if entity_next_state_and_action.nextPos != None:
                                current_entity.face = entity_next_state_and_action.nextPos
                                logging.debug("Next destination has been changed to: " + str(current_entity.face))

                            #Move entity:
                            elif entity_next_state_and_action.move_pos:
                                self.communicator.MoveEntityToLocation(entity_next_state_and_action.entity_id,
                                                                           entity_next_state_and_action.position_location)
                                current_entity.state = entity_next_state_and_action.position
                                current_entity.target_location = entity_next_state_and_action.position_location
                                logging.debug("Squad started to move to Attack position: " + str(current_entity.face))
                            #Locate at position:
                            elif entity_next_state_and_action.nextPosture == 'get_in_position':
                                    for j in range(len(self.entity_list)):
                                        self.communicator.setEntityPosture(self.entity_list[j].unit_name,12)
                                        logging.debug("Squad member " +  str(self.entity_list[j].unit_name) +"is locating in Attack position:  " + str(current_entity.face))

                            #LOS:
                            elif entity_next_state_and_action.scan_for_enemy == 1:
                                #Basic functionality - next step is to use LOS between point and entity:
                                logging.debug("Squad is scanning for enemies from Attack position: " + str(current_entity.face))
                                detectionCount=0
                                for enemy in (self.blue_entity_list):
                                    losRespose=ext_funs.losOperator(self.squadPosture,self.enemyDimensions, enemy, current_entity.current_location)
                                    if losRespose['distance'][0][0] < self.basicRanges['squad_view_range']:
                                        if losRespose['los'][0][0]==True:
                                             enemy.observed=True
                                             enemy.last_seen_worldLocation=enemy.location
                                             logging.debug("Enemy: " + str(
                                                 enemy.unit_name)+ " has been detected")
                                             detectionCount+=1
                                #updating HTN list which is used when shooting:
                                self.blue_entity_list_HTN = ext_funs.getBluesDataFromVRFtoHTN(self.blue_entity_list)
                                if detectionCount == 0:
                                    logging.debug("No enemy has been detected")
                            #Aim
                            #Atribute distFromSquad is local atribute for blue enemy only for Aim operator
                            elif entity_next_state_and_action.aim == True:
                                aim_list=[]
                                for enemy in self.blue_entity_list:
                                    if enemy.observed == True and enemy.is_alive==True:
                                        #new atribute:
                                        enemy.distFromSquad=ext_funs.getMetriDistance(current_entity.current_location,enemy.location)
                                        aim_list.append(enemy)
                                    else:
                                        enemy.distFromSquad=None
                                # sort: observed list by classification when Eitan comes before Ohez
                                if aim_list!=[]:
                                    #sort by value - next sort by value and then by distance
                                    aim_list = sorted(aim_list, key=lambda x: (x.val,-x.distFromSquad), reverse=True)
                                    self.aim_list = aim_list
                                    aim_list_names=[]
                                    for entity in aim_list:
                                        name= entity.unit_name
                                        aim_list_names.append(name)
                                    logging.debug(("Target list is: " + str(aim_list_names)))
                                if aim_list==[]:
                                    logging.debug("No enemy has been inserted to the aim list - emptying COA - planBool = 1")
                                    current_entity.COA=[]
                                    current_entity.planBool=1
                            #Shoot at target
                            # Names are specific for anti_tank squad
                            elif entity_next_state_and_action.shoot==True:
                                #NO CHECK FOR LOS and RANGE for each shooting unit.
                                logging.debug(
                                    "Try Shooting at target " + str(self.aim_list[0].unit_name))
                                target=self.aim_list[0]
                                if target.classification==EntityTypeEnum.EITAN:
                                    lat_0=current_entity.current_location['latitude'];lon_0=current_entity.current_location['longitude'];alt_0=current_entity.current_location['altitude']
                                    lat_1=target.location['latitude'];lon_1=target.location['longitude']; alt_1=target.location['altitude']
                                    azi, elev, geo_range = pm.geodetic2aer(lat_1,lon_1,alt_1,lat_0,lon_0,alt_0)
                                    self.communicator.setEntityHeading(current_entity.unit_name,azi)
                                    current_entity.taskTime = time.time()
                                    current_entity.fireState = isFire.yes
                                    amoNumber = 1
                                    self.communicator.setEntityPosture(current_entity.unit_name, 13)
                                    self.communicator.FireCommand(str('at_1'),str(target.unit_name),amoNumber,"dif")
                                elif target.classification==EntityTypeEnum.OHEZ:
                                    so_1 = (next(x for x in self.entity_list if x.unit_name == 'so_1'))
                                    so_2 = (next(x for x in self.entity_list if x.unit_name == 'so_2'))
                                    so_1.taskTime = time.time()
                                    so_2.taskTime = time.time()
                                    so_1.fireState = isFire.yes
                                    so_2.fireState = isFire.yes
                                    amoNumber=10
                                    self.communicator.setEntityPosture(so_1.unit_name, 13)
                                    self.communicator.setEntityPosture(so_2.unit_name, 13)
                                    self.communicator.FireCommand(str(so_1.unit_name),str(target.unit_name),amoNumber,"dif")
                                    self.communicator.FireCommand(str(so_2.unit_name), str(target.unit_name), amoNumber,"dif")


                    # check if entity arrived to location:
                    if current_entity.state == PositionType.MOVE_TO_OP:
                        if entity_next_state_and_action.position == PositionType.AT_OP:
                            #Change entity state to arrive at location:
                            current_entity.state = entity_next_state_and_action.position
                            current_entity.movement_task_completed = 0
                            current_entity.movement_task_success = False
                            logging.debug("entity: " + str(current_entity.unit_name) + " changed state to " + str(
                                current_entity.state.name) + " arrived to location ")
                    # check if firing ends:
                    if current_entity.fireState == isFire.yes:
                        if entity_next_state_and_action.timeOutAbortCurrentTask==True:
                            self.communicator.stopCommand(current_entity.unit_name)
                            logging.debug("entity: " + str(current_entity.unit_name) + " has aborted firing task")
                        if entity_next_state_and_action.shoot == False:
                            #Change entity state to arrive at location:
                            current_entity.fireState = isFire.no
                            current_entity.fire_task_completed=0
                            current_entity.fire_task_success= False
                            logging.debug("entity: " + str(current_entity.unit_name) + " finished fire task")

                    ##############

                    # update the entity parameters that changed during this iteration
                    self.entity_list[i] = current_entity


            elif self.communicator.GetScenarioStatus() == ScenarioStatusEnum.RESTART:
                self.first_enter = True
                while self.communicator.GetScenarioStatus() is ScenarioStatusEnum.RESTART or self.first_enter is True:
                    if self.first_enter:
                        self.first_enter = False
                        if ConfigManager.GetForceRemote() == "FALSE":
                            spawnManager = SpawnManager_Nadav(self.communicator,self.spawnPos,self.AttackPos)
                            spawnManager.Run()
                            self.entity_list = spawnManager.spawn_entity_list
                            self.blue_entity_list = self.getBlueEntityList()
                            self.blue_entity_list_HTN = ext_funs.getBluesDataFromVRFtoHTN(self.blue_entity_list)
                            # Squad commander COA push scanning operation before the game starts
                            for i in range(len(self.entity_list)):
                                current_entity = self.entity_list[i]
                                if current_entity.unit_name == "at_1":
                                    self.entity_list[i].COA.append(['scan_for_enemy_op','me'])
                                    logging.debug("scan_for_enemy_op has been added to Squad Commander")
                            logging.debug("Get Forces local ")
                        else:
                            logging.debug("Get Forces remotely ")

                self.start_scenario_time = time.time() #efshar limjok

    def get_positions_fromCSV(self,filename):
        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            header = next(csv_reader)
            locations = []
            for row in csv_reader:
                loaction = {
                    "latitude": row[6],
                    "longitude": row[7],
                    "altitude": row[8],
                }

                locations.append(loaction)
            return locations

    def getBlueEntityList(self,entity_previous_list=[]):
        entity_info_list = self.communicator.GetScenarioEntitiesInfo()
        return_list=[]
        if ConfigManager.GetMode() == "VRF":
            entity_info_list = self.CreateEntityInfoFromVrf(entity_info_list)
        for i in range(len(entity_info_list)):
            if entity_info_list[i].hostility == Hostility.FRIENDLY:
                return_list.append(entity_info_list[i])
        #dealing with the previous list:
        if entity_previous_list!=[]:
            for k in range(len(return_list)):
                current_entity=return_list[k]
                for i in range(len(entity_previous_list)):
                    if return_list[k].unit_name==entity_previous_list[i].unit_name:
                        live_unit=entity_previous_list[i]
                        break
                current_entity.last_seen_worldLocation=live_unit.last_seen_worldLocation
                current_entity.observed=live_unit.observed
                if current_entity.classification == EntityTypeEnum.EITAN:
                    current_entity.val = 1
                else:
                    current_entity.val = 0



        return return_list

    def CreateAndUpdateEntityList(self,entity_previous_list):
        entity_list=[] # creating new entity list from scratch
        entity_info_list = self.communicator.GetScenarioEntitiesInfo()
        entity_info_list = self.CreateEntityInfoFromVrf(entity_info_list)
        for k in range(len(entity_previous_list)): #only red
            for i in range(len(entity_info_list)): # blue and red
                if entity_previous_list[k].unit_name==entity_info_list[i].unit_name:
                    live_unit=entity_info_list[i]
            #data generated from simulator:
            current_entity = EntityCurrentState(entity_previous_list[k].unit_name)
            current_entity.power = live_unit.power
            current_entity.health = live_unit.health
            alive_status = live_unit.is_alive
            current_entity.alive = alive_status
            current_entity.current_location = {
                "latitude": live_unit.location.get("latitude"),
                "longitude":live_unit.location.get("longitude"),
                "altitude": live_unit.location.get("altitude")
            }
            current_entity.entity_damage_state = live_unit.entity_damage_state

            #data updated from last iteration:
            current_entity.classification = live_unit.classification
            current_entity.COA = entity_previous_list[k].COA
            current_entity.face = entity_previous_list[k].face
            current_entity.planBool = entity_previous_list[k].planBool
            current_entity.state = entity_previous_list[k].state
            current_entity.fireState = entity_previous_list[k].fireState
            current_entity.aim_list = entity_previous_list[k].aim_list
            current_entity.preGameBool=entity_previous_list[k].preGameBool

            #task statuses:
            current_entity.movement_task_completed = entity_previous_list[k].movement_task_completed
            current_entity.movement_task_success   = entity_previous_list[k].movement_task_success
            current_entity.fire_task_completed     = entity_previous_list[k].fire_task_completed
            current_entity.fire_task_success       = entity_previous_list[k].fire_task_success
            current_entity.taskTime = entity_previous_list[k].taskTime

            entity_list.append(current_entity)
        return entity_list

    def CreateEntityInfoFromVrf(self, entity_info_list: list) -> list:
        list_to_return = []
        for i in range(len(entity_info_list)):
            #create template from communicator interface:
            current_entity = EntityInfo(entity_info_list[i].get("unit_name"))

            hostility = entity_info_list[i].get("hostility")
            if hostility == 1:
                current_entity.hostility = Hostility.FRIENDLY
            elif hostility == 2:
                current_entity.hostility = Hostility.OPPOSING
            elif hostility == 3:
                current_entity.hostility = Hostility.NEUTRAL
            else:
                current_entity.hostility = Hostility.UNKNOWN

            current_entity.location = entity_info_list[i].get("worldLocation")['location']

            curr_type = entity_info_list[i].get("classification")
            if curr_type == 1:
                current_entity.classification = EntityTypeEnum.SOLDIER
            elif curr_type == 2:
                current_entity.classification = EntityTypeEnum.SHORT_RANGE_ANTI_TANK
            elif curr_type == 3:
                current_entity.classification = EntityTypeEnum.OBSERVER
            elif curr_type == 4:
                current_entity.classification = EntityTypeEnum.LONG_RANGE_ANTI_TANK
            elif curr_type == 5:
                current_entity.classification = EntityTypeEnum.SNIPER
            elif curr_type == 6:
                current_entity.classification = EntityTypeEnum.DRONE
            elif curr_type == 7:
                current_entity.classification = EntityTypeEnum.DRONE_OPERATOR
            elif curr_type == 8:
                current_entity.classification = EntityTypeEnum.HIGH_TRAJECTORY_WEAPON
            elif curr_type == 9:
                current_entity.classification = EntityTypeEnum.HQ
            elif curr_type == 10:
                current_entity.classification = EntityTypeEnum.EITAN
            elif curr_type == 11:
                current_entity.classification = EntityTypeEnum.HALUTZ_DRONE
            elif curr_type == 12:
                current_entity.classification = EntityTypeEnum.OHEZ
            elif curr_type == 13:
                current_entity.classification = EntityTypeEnum.HALUTZ
            elif curr_type == 14:
                current_entity.classification = EntityTypeEnum.SUICIDE_DRONE
            elif curr_type == 15:
                current_entity.classification = EntityTypeEnum.NLOS
            elif entity_info_list[i]["hostility"] == 3:
                current_entity.classification = EntityTypeEnum.CIVILIAN
            else:
                current_entity.entity_type = EntityTypeEnum.UNKNOWN.name

            current_entity.is_alive = True
            if entity_info_list[i].get("health") == 0:
                current_entity.is_alive = False

            current_entity.health=entity_info_list[i].get("health")
            current_entity.power = entity_info_list[i].get("power")
            current_entity.entity_damage_state = entity_info_list[i].get("entity_damage_state")
            current_entity.global_id = entity_info_list[i].get("global_id")

            list_to_return.append(current_entity)

        return list_to_return

    def GetTimeDiff(self, tick_counter: int, curr_tick: float) -> float:
        current = time.time()
        if ConfigManager.GetTimeOrTickMode() == "TIME":
            # delta time from start of the running
            return current - self.start_scenario_time
        else:
            logging.error("not valid time or tick mode")
            sys.exit(1)

    # def DetectedEnemy(self, current_entity: EntityCurrentState) -> dict:
    #
    #     entity_config = ConfigManager.getEntityConfig(str(current_entity.entity_type).strip())
    #     if entity_config.weapon_range is None:
    #         entity_config = ConfigManager.getEntityConfig(str(current_entity.entity_type.name).strip())
    #
    #     detected_range = 0
    #     if entity_config.detection_range is not None:
    #         detected_range = float(entity_config.detection_range)
    #     lat1 = current_entity.current_location.get("latitude")
    #     lon1 = current_entity.current_location.get("longitude")
    #     if lat1 is None or lon1 is None:
    #         lat1 = current_entity.current_location["location"].get("latitude")
    #         lon1 = current_entity.current_location["location"].get("longitude")
    #
    #     detected_entity = {
    #         "enemy_is_detected": False,
    #         "detected_entity_id": "",
    #         "general_classification": 0
    #     }
    #
    #     for i in range(len(self.blue_entity_list)):
    #         if self.blue_entity_list[i].alive:
    #             new_red_location = {}
    #             red_location = {}
    #             blue_location = {}
    #
    #             if ConfigManager.GetMode() == "GODOT" or ConfigManager.GetMode() == "VRF":
    #                 if self.blue_entity_list[i].current_location.get("latitude") is None or self.blue_entity_list[
    #                     i].current_location.get("longitude") == None:
    #                     logging.warning("Error in location of blue entity " + str(self.blue_entity_list[i].unit_name))
    #                     continue
    #                 lat2 = float(self.blue_entity_list[i].current_location.get("latitude"))
    #                 lon2 = float(self.blue_entity_list[i].current_location.get("longitude"))
    #                 blue_range = abs(PlacementManager.Range(lat1, lon1, lat2, lon2))
    #                 if detected_range < blue_range:
    #                     continue
    #                 blue_location = self.blue_entity_list[i].current_location
    #                 # [:15] to get only the number location without the prefix name
    #                 blue_location["latitude"] = float(str(blue_location.get("latitude"))[:15])
    #                 blue_location["longitude"] = float(str(blue_location.get("longitude"))[:15])
    #                 blue_location["altitude"] = float(
    #                     str(blue_location.get("altitude"))[:15]) + RFSMManager.los_blue_alt
    #                 red_location = copy.deepcopy(current_entity.current_location)
    #                 try:
    #                     # dont get "location" prefix
    #                     new_red_location["latitude"] = float(str(red_location.get("latitude"))[:15])
    #                     new_red_location["longitude"] = float(str(red_location.get("longitude"))[:15])
    #                     new_red_location["altitude"] = float(str(red_location.get("altitude"))[:15])
    #                     new_red_location["altitude"] = red_location["altitude"] + RFSMManager.los_red_alt
    #                 except:
    #                     # get "location" prefix
    #                     new_red_location["latitude"] = float(str(red_location["location"].get("latitude"))[:15])
    #                     new_red_location["longitude"] = float(str(red_location["location"].get("longitude"))[:15])
    #                     new_red_location["altitude"] = float(str(red_location["location"].get("altitude"))[:15])
    #                     new_red_location["altitude"] = new_red_location["altitude"] + RFSMManager.los_red_alt
    #
    #             if self.communicator.CheckLos(new_red_location, blue_location):
    #                 detected_entity["enemy_is_detected"] = True
    #                 detected_entity["detected_entity_id"] = self.blue_entity_list[i].entity_id
    #                 detected_entity["general_classification"] = self.blue_entity_list[i].general_classification
    #                 # logging.debug("LOS return TRUE entity1 = " + str(current_entity.entity_id) + " entity2 = " + str(
    #                 #     self.blue_entity_list[i].entity_id))
    #                 break
    #             # else:
    #             #     logging.debug("LOS return False entity1 = " + str(current_entity.entity_id) + " entity2 = " + str(
    #             #         self.blue_entity_list[i].entity_id))
    #
    #     return detected_entity

    # def GetBluesRelativeInformation(self, current_entity: EntityCurrentState) -> dict:
    #
    #     blues_relative_information_dict = {}
    #
    #     entity_config = ConfigManager.getEntityConfig(str(current_entity.entity_type).strip())
    #     if entity_config.weapon_range is None:
    #         entity_config = ConfigManager.getEntityConfig(str(current_entity.entity_type.name).strip())
    #
    #     detected_range = 0
    #     if entity_config.detection_range is not None:
    #         detected_range = float(entity_config.detection_range)
    #     lat1 = current_entity.current_location.get("latitude")
    #     lon1 = current_entity.current_location.get("longitude")
    #     if lat1 is None or lon1 is None:
    #         lat1 = current_entity.current_location["location"].get("latitude")
    #         lon1 = current_entity.current_location["location"].get("longitude")
    #
    #     my_los_location = copy.deepcopy(current_entity.current_location)
    #     try:
    #         # dont get "location" prefix
    #         my_los_location["latitude"] = float(str(my_los_location.get("latitude"))[:15])
    #         my_los_location["longitude"] = float(str(my_los_location.get("longitude"))[:15])
    #         my_los_location["altitude"] = float(str(my_los_location.get("altitude"))[:15]) + RFSMManager.los_red_alt
    #     except:
    #         # get "location" prefix
    #         my_los_location["latitude"] = float(str(my_los_location["location"].get("latitude"))[:15])
    #         my_los_location["longitude"] = float(str(my_los_location["location"].get("longitude"))[:15])
    #         my_los_location["altitude"] = float(str(my_los_location["location"].get("altitude"))[:15]) + RFSMManager.los_red_alt
    #
    #     for i in range(len(self.blue_entity_list)):
    #         if self.blue_entity_list[i].alive:
    #             blue_entity_information = {
    #                 "enemy_is_detected": False,
    #                 "detected_entity_general_classification": 0,
    #                 "latitude": 0,
    #                 "longitude": 0,
    #                 "altitude": 0,
    #                 "relative_distance": 0,
    #                 "blue_los_location": "",
    #                 "my_los_location": my_los_location
    #             }
    #             blue_entity_id = self.blue_entity_list[i].entity_id
    #             if self.blue_entity_list[i].current_location.get("latitude") is None or self.blue_entity_list[i].current_location.get("longitude") == None:
    #                 logging.warning("Error in location of blue entity " + str(self.blue_entity_list[i].unit_name))
    #                 continue
    #
    #             blue_entity_information["latitude"] = float(self.blue_entity_list[i].current_location.get("latitude"))
    #             blue_entity_information["longitude"] = float(self.blue_entity_list[i].current_location.get("longitude"))
    #             blue_entity_information["altitude"] = float(self.blue_entity_list[i].current_location.get("altitude"))
    #             blue_entity_information["relative_distance"] = abs(PlacementManager.Range(lat1, lon1, blue_entity_information.get("latitude"), blue_entity_information.get("longitude")))
    #
    #             blue_entity_information["blue_los_location"] = copy.deepcopy(self.blue_entity_list[i].current_location)
    #             blue_entity_information["blue_los_location"]["latitude"] = float(str(blue_entity_information["blue_los_location"].get("latitude"))[:15])
    #             blue_entity_information["blue_los_location"]["longitude"] = float(str( blue_entity_information["blue_los_location"].get("longitude"))[:15])
    #             blue_entity_information["blue_los_location"]["altitude"] = float(str( blue_entity_information["blue_los_location"].get("altitude"))[:15]) + RFSMManager.los_blue_alt
    #
    #
    #             blue_entity_information["detected_entity_general_classification"] = self.blue_entity_list[i].general_classification
    #
    #             blues_relative_information_dict[blue_entity_id] = blue_entity_information
    #
    #     src_los_vector = [my_los_location]
    #     dest_los_vector = []
    #     for blue_id in blues_relative_information_dict:
    #         if detected_range >= blues_relative_information_dict[blue_id].get("relative_distance"):
    #             dest_los_vector.append(blues_relative_information_dict[blue_id].get("blue_los_location"))
    #
    #     if len(dest_los_vector) > 0:
    #         ans = self.communicator.GetGeoQuery(src_los_vector, dest_los_vector, True, False)
    #         los_index = 0
    #         for blue_id in blues_relative_information_dict:
    #             if detected_range >= blues_relative_information_dict[blue_id].get("relative_distance"):
    #                 if ans["los"][0][los_index]:
    #                     blues_relative_information_dict[blue_id]["enemy_is_detected"] = True
    #                 los_index += 1
    #
    #     return blues_relative_information_dict
