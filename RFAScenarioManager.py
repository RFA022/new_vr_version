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
import htnGreenModel
import pandas as pd
import pymap3d as pm
from ext_funs import *
import ext_funs
from Communicator import CommunicatorSingleton
import utm
import geopandas
import threading

#MADGIMON
class RFAScenarioManager:
    def __init__(self):

        #Running and Configs:
        if ConfigManager.GetMode() == "VRF":
            self.communicator = CommunicatorSingleton().obj
            logging.debug("Running in vrf mode")
        else:
            logging.error("None valid mode")
            raise Exception("None valid mode")

        self.spawnPos =  ext_funs.get_positions_fromCSV('Resources\RedSpawnPos.csv')
        self.AttackPos = ext_funs.get_positions_fromCSV('Resources\RedAttackPos.csv')
        self.Polygons = self.communicator.getAreasQuery()

        BluePolygon=next(x for x in self.Polygons if x['areaName'] == 'BluePolygon')

        self.BluePolygonCentroid=ext_funs.getPolygonCentroid(BluePolygon['polygon'])

        self.start_scenario_time = 0
        self.first_enter = True


        #Entities Lists:
        self.entity_list = []
        self.green_entity_list= []
        self.blue_entity_list = []
        self.blue_entity_list_HTN=[]

        #General config data:
        self.configuration = pd.read_csv('Resources\Configuration.csv',
                                         header=[0],
                                         index_col=[0])
        self.squadPosture = {}
        self.squadPosture['standing_height']  = float(self.configuration.at['standing_height', 'value'])
        self.squadPosture['crouching_height'] = float(self.configuration.at['crouching_height', 'value'])

        self.enemyDimensions = {}
        self.enemyDimensions['eitan_cg_height']=float(self.configuration.at['eitan_cg_height', 'value'])

        self.basicRanges = {}
        self.basicRanges['squad_view_range'] = float(self.configuration.at['squad_view_range', 'value'])
        self.basicRanges['squad_eyes_range'] = float(self.configuration.at['squad_eyes_range', 'value'])

        self.basicRanges['rpg_range'] = float(self.configuration.at['rpg_range', 'value'])
        self.basicRanges['javelin_range'] = float(self.configuration.at['javelin_range', 'value'])
        self.basicRanges['ak47_range'] = float(self.configuration.at['ak47_range', 'value'])

        self.config = {}
        self.config['rePlan_range'] = float(self.configuration.at['rePlan_range', 'value'])
        self.config['scan_time'] = float(self.configuration.at['scan_time', 'value'])
        self.config['shoot_timeout_time'] = float(self.configuration.at['shoot_timeout_time', 'value'])
        self.config['move_type'] = str(self.configuration.at['move_type', 'value'])

        self.squadsDatalocation=str(self.configuration.at['squadsDataLocation', 'value'])
        self.squadsData = pd.read_csv(self.squadsDatalocation,
                            header=[0],
                            index_col=[6]) #Squad name column
        self.AccuracyConfiguration = pd.read_csv('Resources/AccuracyConfiguration.csv',
                                                 header=[0],
                                                 index_col=[0])  # WeaponName column
        logging.debug(self.__class__.__name__ + " Constructor executed successfully")
        # simulatedLocation={
        #     'latitude':33.3710914531,
        #     'longitude':35.4963506969,
        #     'altitude':443.4963506969
        # }
        # re = self.communicator.navigationPathPlan(self.AttackPos[3], self.spawnPos[8], self.AttackPos[7], 150, "at_1_1",2)
        # print(re)
        # for k in range(len(re[0]['pathPlanningResponseVector'][0]['path'])):
        #     self.communicator.CreateEntitySimple('path_point_0_' + str(k),
        #                                          re[0]['pathPlanningResponseVector'][0]['path'][k], 2, '16:0:0:1:0:0:0')
        # for k in range(len(re[0]['pathPlanningResponseVector'][1]['path'])):
        #     self.communicator.CreateEntitySimple('path_point_1_' + str(k),
        #                                          re[0]['pathPlanningResponseVector'][1]['path'][k], 3, '16:0:0:1:0:0:0')
    def Run(self):
        while True:
            if self.communicator.GetScenarioStatus() == ScenarioStatusEnum.RUNNING:
                time.sleep(0.5) #sleep time between every iteration - CPU time
                if self.start_scenario_time == 0:
                    self.start_scenario_time = time.time()
                "Entites list update"
                #update Red list from simulator and from last iteration
                self.entity_list=self.CreateAndUpdateEntityList(self.entity_list)
                #update Green list from simulator and from last iteration - same format as blues
                self.green_entity_list=self.CreateAndUpdateEntityList(self.green_entity_list)
                #update Blue list from simulator and from last iteration (info about last seen location)
                self.blue_entity_list = self.getBlueEntityList(self.blue_entity_list)
                self.blue_entity_list_HTN=ext_funs.getBluesDataFromVRFtoHTN(self.blue_entity_list)

                "Check if Red won"
                numberOfAliveBlues=getNumberofAliveEnemies(self.blue_entity_list)
                if numberOfAliveBlues == 0:
                    logging.debug("Red as won the game")
                    break
                #Debug
                # for blue in self.blue_entity_list:
                #     print('alive status for blue list entity '+ str(blue.unit_name + "is: "+ str(blue.is_alive)))
                # for blue in self.blue_entity_list_HTN:
                #     print('alive status for HTN blue list entity ' + str(blue.unit_name + "is: " + str(blue.is_alive)))

                "Update fire and task lists from simulator"
                fire_list = self.communicator.GetFireEvent()
                task_status_list = self.communicator.GetTaskStatusEvent()
                #Debug
                # print(task_status_list)
                # print(fire_list)
                # Run over all entity
                # print("---Debug Seasson---")  #
                # print(fire_list)
                # print(task_status_list)
                "Green Entities Control"
                for i in range(len(self.green_entity_list)):
                    current_entity = self.green_entity_list[i]
                    if current_entity.alive:
                        "external function that handles all functionalities that relates to move and  fire"
                        self.handle_move_fire_scan_wait(current_entity,task_status_list,fire_list)
                        if current_entity.state == PositionType.MOVE_TO_OP:
                            pass
                        if current_entity.COA == []:
                            current_entity.planBool = 1
                        if current_entity.planBool == 1 and current_entity.COA == []:
                            current_entity.planBool = 0
                            current_entity.COA = htnGreenModel.findplan(current_entity.current_location)
                            logging.debug("New Plan has been given to " + str(current_entity.unit_name))
                        entity_next_state_and_action = HTNLogic().Step(current_entity,
                                                                       self.start_scenario_time, self.AttackPos, self.spawnPos)
                        "next task implementation"
                        if entity_next_state_and_action.takeAction == 1 :
                            current_entity.COA.pop(0)
                            self.entity_next_state_and_action_impleneter(entity_next_state_and_action, current_entity)
                    # update the entity parameters that changed during this iteration
                    self.green_entity_list[i] = current_entity
                "Red Entities Control"
                for i in range(len(self.entity_list)):
                    current_entity = self.entity_list[i]
                    #Debug
                    # print(time.time()-self.start_scenario_time)
                    "Zeroing preGameBool for all entites after 5 seconds of game"
                    if time.time()-self.start_scenario_time>0.5:
                        if current_entity.preGameBool==True:
                            current_entity.preGameBool=False
                    if current_entity.alive:
                        "external function that handles all functionalities that relates to move and  fire"
                        self.handle_move_fire_scan_wait(current_entity,task_status_list,fire_list)
                        #print("current entity:" + str(current_entity.unit_name) + "status: " + str(current_entity.movement_task_completed) + "success" + str(current_entity.movement_task_success) )
                        # # Debug:
                        # print("---Debug Seasson---")#
                        # print(str(current_entity.unit_name))
                        # print(current_entity.fireState)
                        # print(current_entity.fire_task_completed)
                        # print(current_entity.fire_task_success)
                        # print('--------------------------------')

                        # #Debug:
                        # if self.entity_list[1].fireState== isFire.yes and self.entity_list[2].fireState== isFire.no:
                        #     print('ss')
                        # next state and action - every iteration even tough COA is empty
                        # Executing next task in COA:
                    #---#---get the next state and action---#---#
                    if current_entity.role=="co": #commander roll type
                        print("______________________")
                        print(current_entity.state)
                        print(current_entity.movement_task_success)
                        print(current_entity.movement_task_completed)
                        print("______________________")
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
                        "scan for enemies if squad is on the move"
                        if current_entity.state==PositionType.MOVE_TO_OP:
                            for enemy in (self.blue_entity_list):
                                losRespose = ext_funs.losOperator(self.squadPosture, self.enemyDimensions, enemy,
                                                                  current_entity.current_location)
                                if losRespose['distance'][0][0] < self.basicRanges['squad_eyes_range']:
                                    if losRespose['los'][0][0] == True:
                                        enemy.last_seen_worldLocation = enemy.location
                                        if enemy.is_alive==True:
                                            pass
                                            logging.debug("Alive enemy: " + str(
                                                enemy.unit_name) + " has been detected during motion")
                                        elif enemy.is_alive==False:
                                            pass
                                            logging.debug("Destroyed enemy: " + str(
                                                enemy.unit_name) + " has been detected during motion")
                                        if (ext_funs.checkIfWorldViewChangedEnough(enemy,current_entity,self.basicRanges,self.config)):
                                            "REPLAN according to certain characteristics"
                                            "-----------------DRONE CASE----------------"
                                            if (enemy.classification == EntityTypeEnum.OHEZ) or \
                                                    (enemy.classification == EntityTypeEnum.SUICIDE_DRONE) or \
                                                    (enemy.classification == EntityTypeEnum.UNKNOWN):
                                                        self.communicator.stopCommand(current_entity.unit_name)
                                                        current_entity.state = PositionType.AT_OP
                                                        current_entity.movement_task_completed = 0
                                                        current_entity.movement_task_success = False
                                                        current_entity.aim_list = []
                                                        current_entity.aim_list.append(enemy)
                                                        current_entity.COA=[]
                                                        current_entity.COA.append((['shoot_op',str(enemy.unit_name)]))
                                            "-----------------LAV CASE----------------"
                                            if enemy.classification == EntityTypeEnum.EITAN:
                                                        self.communicator.stopCommand(current_entity.unit_name)
                                                        current_entity.state = PositionType.AT_OP
                                                        current_entity.movement_task_completed = 0
                                                        current_entity.movement_task_success = False
                                                        current_entity.COA = []
                            # updating HTN list which is used when shooting:
                            self.blue_entity_list_HTN = ext_funs.getBluesDataFromVRFtoHTN(self.blue_entity_list)
                        if current_entity.COA==[]:
                            fire_bool=0
                            for testEntity in self.entity_list:
                                if testEntity.fireState == isFire.yes:
                                    fire_bool = 1
                            # print("fire bool is" + str(fire_bool))
                            if fire_bool==0:
                                current_entity.planBool=1
                        "Plan new plan if COA is empty and planbool =1"
                        if current_entity.planBool==1 and current_entity.COA==[]:
                            current_entity.planBool=0
                            current_entity.COA=htnModel.findplan(self.basicRanges,
                                                                      self.squadPosture,
                                                                      self.enemyDimensions,
                                                                      current_entity.current_location,
                                                                      self.blue_entity_list_HTN,
                                                                      self.BluePolygonCentroid,
                                                                      self.AccuracyConfiguration,
                                                                      next(x for x in self.Polygons if x['areaName'] == 'BluePolygon')['polygon'])
                            logging.debug("New Plan has been given to Squad")
                            # print('s')
                            # r=self.communicator.navigationPathPlan(self.spawnPos[16], self.spawnPos[17], 100, self.spawnPos[16])
                            # if r!= []:
                            #     print(r)
                            "Update HTN target"
                            current_entity.HTNtarget=[]
                            for primitive_task in self.entity_list[i].COA:
                                if primitive_task[0]=='shoot_op':
                                    target= next(x for x in self.blue_entity_list_HTN if x.unit_name == (primitive_task[1]))
                                    if calculate_blue_distance(current_entity.current_location,target)==None:
                                        current_entity.HTNtarget.append([target.unit_name,"assesed"])
                                    else:
                                        current_entity.HTNtarget.append([target.unit_name,"real"])
                            # print(str(current_entity.HTNtarget))
                            "Update HTN frozen world view"
                            current_entity.HTNbluesFrozen=self.blue_entity_list_HTN
                            # for entity in current_entity.HTNbluesFrozen:
                            #     print("entity name: " + str(entity.unit_name))
                            #     print("entity location: " + str(entity.location))
                        "Generates next state and action for Squad commander"
                        entity_next_state_and_action = HTNLogic().Step(current_entity,
                                                                       self.start_scenario_time, self.AttackPos,self.spawnPos)

                        "next task implementation"
                        if current_entity.alive and (((entity_next_state_and_action.takeAction == 1) and (current_entity.preGameBool==False)) or \
                                                     ((current_entity.preGameBool==True) and (entity_next_state_and_action.takeAction == 0))):
                            if current_entity.preGameBool==True:
                                current_entity.preGameBool=False
                            current_entity.COA.pop(0)
                            self.entity_next_state_and_action_impleneter(entity_next_state_and_action, current_entity)
                    # update the entity parameters that changed during this iteration
                    self.entity_list[i] = current_entity
            elif self.communicator.GetScenarioStatus() == ScenarioStatusEnum.RESTART:
                self.first_enter = True
                while self.communicator.GetScenarioStatus() is ScenarioStatusEnum.RESTART or self.first_enter is True:
                    if self.first_enter:
                        self.first_enter = False
                        if ConfigManager.GetForceRemote() == "FALSE":
                            spawnManager = SpawnManager_Nadav(self.communicator,self.spawnPos,self.AttackPos,self.squadsData)
                            spawnManager.Run()
                            self.entity_list = spawnManager.spawn_entity_list
                            self.green_entity_list=spawnManager.green_spawn_entity_list
                            self.blue_entity_list = self.getBlueEntityList()
                            self.blue_entity_list_HTN = ext_funs.getBluesDataFromVRFtoHTN(self.blue_entity_list)
                            # Squad commander COA push scanning operation before the game starts
                            for i in range(len(self.entity_list)):
                                current_entity = self.entity_list[i]
                                if current_entity.role == "co":
                                    self.entity_list[i].COA.append(['scan_for_enemy_and_assess_exposure_op','me'])
                                    logging.debug("scan_for_enemy_op has been added to Squad Commander")
                            logging.debug("Get Forces local ")
                        else:
                            logging.debug("Get Forces remotely ")
                self.start_scenario_time = time.time()


    #Funtion that implements according to next state and action object
    def entity_next_state_and_action_impleneter(self,entity_next_state_and_action,current_entity):
        # Change nextPos:
        if entity_next_state_and_action.nextPos != None:
            current_entity.face = entity_next_state_and_action.nextPos
            logging.debug("Next destination has been changed to: " + str(current_entity.face))

        # Move entity:
        elif entity_next_state_and_action.move_pos:
            # print("current location is: " + str(current_entity.current_location))
            # print("current destination is: "+ str(entity_next_state_and_action.position_location) )
            if current_entity.role=='co':
                logging.debug(
                    "Squad started to move to " + str(entity_next_state_and_action.positionType) + " position: " + str(
                        current_entity.face))

                if self.config['move_type']=="destination":
                    self.communicator.MoveEntityToLocation(entity_next_state_and_action.entity_id,
                                                           entity_next_state_and_action.position_location,
                                                           4.5)
                elif self.config['move_type']=="path":
                    paths=self.communicator.navigationPathPlan(current_entity.current_location
                                                         ,entity_next_state_and_action.position_location,
                                                         None,100,current_entity.unit_name,2)
                    if paths[0]['pathPlanningResponseVector']==[]:
                        logging.debug("mobility agent didnt work")
                        self.communicator.MoveEntityToLocation(entity_next_state_and_action.entity_id,
                                                               entity_next_state_and_action.position_location,
                                                               4.5)
                    else:
                        if len(paths[0]['pathPlanningResponseVector'])==2:
                            path=paths[0]['pathPlanningResponseVector'][1]['path']
                            self.communicator.followPathCommand(current_entity.unit_name
                                                                , path
                                                                , 4.5)
                        elif len(paths[0]['pathPlanningResponseVector'])==1:
                            path=paths[0]['pathPlanningResponseVector'][0]['path']
                            self.communicator.followPathCommand(current_entity.unit_name
                                                                , path
                                                                , 4.5)
                        path=paths[0]['pathPlanningResponseVector'][0]['path']
                        self.communicator.followPathCommand(current_entity.unit_name
                                                                , path
                                                                , 4.5)
            elif current_entity.role=='ci':
                logging.debug("Civil started to move to " + str(entity_next_state_and_action.positionType) + " position: " + str(current_entity.face))
                self.communicator.MoveEntityToLocation(entity_next_state_and_action.entity_id,
                                                       entity_next_state_and_action.position_location,
                                                       3)
            current_entity.state = entity_next_state_and_action.position
            current_entity.target_location = entity_next_state_and_action.position_location
        # Locate at position:
        elif entity_next_state_and_action.nextPosture == 'get_in_position':
            for j in range(len(self.entity_list)):
                self.communicator.setEntityPosture(self.entity_list[j].unit_name, 12)
                logging.debug(
                    "Squad member " + str(self.entity_list[j].unit_name) + "is locating in Attack position:  " + str(
                        current_entity.face))

        # LOS:
        elif entity_next_state_and_action.scan_for_enemy == 1:
            # Basic functionality - next step is to use LOS between point and entity:
            logging.debug("Squad is scanning for enemies from Attack position: " + str(current_entity.face))
            current_entity.scanState=isScan.yes
            current_entity.scanDetectionList=[]
            current_entity.taskTime=time.time()
        # Aim
        # Atribute distFromSquad is local atribute for blue enemy only for Aim operator
        elif entity_next_state_and_action.aim == True:
            aim_list = []
            for enemy in self.blue_entity_list:
                if enemy.observed == True and enemy.is_alive == True:
                    # new atribute:
                    enemy.distFromSquad = ext_funs.getMetriDistance(current_entity.current_location, enemy.location)
                    aim_list.append(enemy)
                else:
                    enemy.distFromSquad = None
                enemy.observed=False # parameter is down after we used it
            # sort: observed list by classification when Eitan comes before Ohez
            if aim_list != []:
                # sort by value - next sort by value and then by distance
                aim_list = sorted(aim_list, key=lambda x: (x.val, -x.distFromSquad), reverse=True)
                "Put emergency drones with short distance first:"
                for enemy in aim_list:
                    if (enemy.classification == EntityTypeEnum.OHEZ) or \
                     (enemy.classification == EntityTypeEnum.SUICIDE_DRONE) or \
                     (enemy.classification==EntityTypeEnum.UNKNOWN):
                        if enemy.distFromSquad<self.basicRanges['ak47_range']:
                            aim_list.remove(enemy)
                            aim_list.insert(0,enemy)
                            logging.debug("Drone type enemy has been pushed to the top of the aim list due to an emergency situation")

                current_entity.aim_list = aim_list
                aim_list_names = []
                for entity in aim_list:
                    name = entity.unit_name
                    aim_list_names.append(name)
                logging.debug(("Target list is: " + str(aim_list_names)))
            if aim_list == []:
                logging.debug("No enemy has been inserted to the aim list - emptying COA - planBool = 1")
                current_entity.COA = []
                current_entity.planBool = 1
        # Shoot at target
        # Names are specific for anti_tank squad
        elif entity_next_state_and_action.shoot == True:
            # NO CHECK FOR LOS and RANGE for each shooting unit.
            logging.debug(
                "Starting shooting procedure at target " + str(current_entity.aim_list[0].unit_name))
            target = current_entity.aim_list[0]
            squad_name=current_entity.squad
            if target.classification == EntityTypeEnum.EITAN:
                shooting_entity=next(x for x in self.entity_list if x.squad == squad_name and x.role == "co") #based on uniqeness of at unit in a squad
                lat_0 = shooting_entity.current_location['latitude'];
                lon_0 = shooting_entity.current_location['longitude'];
                alt_0 = shooting_entity.current_location['altitude']
                lat_1 = target.location['latitude'];
                lon_1 = target.location['longitude'];
                alt_1 = target.location['altitude']
                azi, elev, geo_range = pm.geodetic2aer(lat_1, lon_1, alt_1, lat_0, lon_0, alt_0)
                self.communicator.setEntityHeading(shooting_entity.unit_name, azi)
                shooting_entity.taskTime = time.time()
                shooting_entity.fireState = isFire.yes
                amoNumber = 1
                self.communicator.setEntityPosture(shooting_entity.unit_name, 13)
                self.communicator.FireCommand(shooting_entity.unit_name, str(target.unit_name), amoNumber, "dif")
                logging.debug("1 Shell fire command has been sent to entity to fire at target")
            elif    (target.classification == EntityTypeEnum.OHEZ) or \
                    (target.classification == EntityTypeEnum.SUICIDE_DRONE) or \
                    (target.classification == EntityTypeEnum.UNKNOWN):
                shooting_entities=[x for x in self.entity_list if x.squad == squad_name and x.classification == EntityTypeEnum.SOLDIER]  # based on uniqeness of at unit in a squad
                if ext_funs.getMetriDistance(current_entity.current_location,target.location)<=self.basicRanges['ak47_range']:
                    shootCounter=0
                    amoNumber = 5
                    for entity in shooting_entities:
                        losResponse = ext_funs.losOperator(self.squadPosture, self.enemyDimensions, target, entity.current_location)
                        if losResponse['los'][0][0] == True:
                            shootCounter+=1
                            entity.taskTime = time.time()
                            entity.fireState=isFire.yes
                            self.communicator.setEntityPosture(entity.unit_name, 13)
                            self.communicator.FireCommand(str(entity.unit_name), str(target.unit_name), amoNumber, "dif")
                        else:
                            logging.debug("entity: " + str(entity.unit_name) + " did not have line of sight to target. Therefore did not shoot" )
                    logging.debug(str(int(amoNumber)*int(shootCounter) )+ " bullets has been fired at target from "+ str(len(shooting_entities)) + " shooting entities")
                else:
                    logging.debug("Target is too far: Task didn't started")
                    #Debug
                    # print(str(ext_funs.getMetriDistance(current_entity.current_location,target.location)))
                    # print(str(current_entity.current_location))
                    # print(str(target.location))
            current_entity.aim_list=[]
        elif entity_next_state_and_action.null == True:
            for enemy in self.blue_entity_list:
                if enemy.observed==True:
                    current_entity.COA.append(['aim_op','me'])
                    current_entity.COA.append(['shoot_op', str(enemy.unit_name)])
                    break
            "Green unique operations"
        elif entity_next_state_and_action.wait_at_position==True:
            logging.debug(str(current_entity.unit_name) + ": is waiting at Spwan position: " + str(current_entity.face))
            current_entity.waitState=isWait.yes
            current_entity.waitTime=entity_next_state_and_action.waitTime
            current_entity.taskTime = time.time()
    #Function that handle termination of firing and moving tasks
    def handle_move_fire_scan_wait(self,current_entity,task_status_list,fire_list):
        # check movement status if unit is moving
        if current_entity.state == PositionType.MOVE_TO_OP:
            # Check task status for movement tasks
            for task in task_status_list:
                if current_entity.unit_name == task.get("markingText"):
                    if task.get("taskName") == "vrf-move-to-location-task":
                        current_entity.movement_task_completed = task.get("currentStatus")
                        current_entity.movement_task_success = task.get("taskSuccess")
            # check task status
            if current_entity.movement_task_completed == 1:
                if current_entity.movement_task_success:
                    # At this case we arrived to location
                    if current_entity.state == PositionType.MOVE_TO_OP:
                        current_entity.state = PositionType.AT_OP
                    current_entity.movement_task_completed = 0
                    current_entity.movement_task_success = False
                    logging.debug(
                        "entity: " + str(
                            current_entity.unit_name) + " changed state to " + str(
                            current_entity.state.name) + " arrived to location ")
                    logging.debug(
                        "case 1 " + current_entity.unit_name.strip() + " Entity arrived to location " + str(
                            current_entity.face) + " movement task completed")
                else:
                    logging.debug(
                        "case 2 - Task completed, didn't arrive to location, unwanted situation")

        # check fire status if unit is shooting
        if current_entity.fireState == isFire.yes:
            # Check task status for fire tasks
            for task in task_status_list:
                if current_entity.unit_name == task.get("markingText"):
                    if task.get("taskName") == "fire-at-target":
                        current_entity.fire_task_completed = task.get("currentStatus")
                        current_entity.fire_task_success = task.get("taskSuccess")
            # Updating  Tasktime for fire if unit is shooting
            for fire_event in fire_list:
                if fire_event['attacking_entity_name'] == current_entity.unit_name:
                    current_entity.taskTime = time.time()
            # check task status
            if current_entity.fire_task_completed == 1:
                if current_entity.fire_task_success:
                    # check if firing ends:
                    current_entity.fireState = isFire.no
                    current_entity.fire_task_completed = 0
                    current_entity.fire_task_success = False
                    logging.debug(
                        "entity: " + str(current_entity.unit_name) + " finished fire task successfully")
                else:
                    logging.debug("Task completed, fire failed, unwanted situation")
            # check if not able to initiate fire task:
            if current_entity.fire_task_success == True:
                if current_entity.fire_task_completed == 0:
                    curr_time = time.time()
                    # Debug
                    # print(curr_time-entity_current_state.taskTime)
                    waitingTime = self.config['shoot_timeout_time']
                    if curr_time - current_entity.taskTime > waitingTime:
                        logging.debug("case 1.1 - can't start firing after " + str(
                            waitingTime) + " seconds of trying. aborting task")
                        current_entity.fireState = isFire.no
                        current_entity.fire_task_completed = 0
                        current_entity.fire_task_success = False
                        #abort task: needed to be checked
                        #self.communicator.stopCommand(current_entity.unit_name)
            if current_entity.fire_task_success == False:
                curr_time = time.time()
                waitingTime = self.config['shoot_timeout_time']
                if curr_time - current_entity.taskTime > waitingTime:
                    logging.debug(
                        "case 1.2 - firing command has not been sent to " + str(
                            waitingTime) + "aborting task")
                    current_entity.fireState = isFire.no
                    current_entity.fire_task_completed = 0
                    current_entity.fire_task_success = False
                    # abort task: needed to be checked
                    #self.communicator.stopCommand(current_entity.unit_name)
        if current_entity.scanState==isScan.yes:
            breakBool=0
            for enemy in (self.blue_entity_list):
                losRespose = ext_funs.losOperator(self.squadPosture, self.enemyDimensions, enemy,
                                                  current_entity.current_location)
                scan_range=self.basicRanges['squad_view_range']
                if losRespose['distance'][0][0] < scan_range:
                    if losRespose['los'][0][0] == True:
                        enemy.observed = True
                        enemy.last_seen_worldLocation = enemy.location
                        current_entity.scanDetectionList.append(enemy)
                        "case of emergency drone detection:"
                        if enemy.is_alive==True:
                            if (enemy.classification == EntityTypeEnum.OHEZ) or \
                                    (enemy.classification == EntityTypeEnum.SUICIDE_DRONE) or \
                                    (enemy.classification == EntityTypeEnum.UNKNOWN):
                                if losRespose['distance'][0][0] < self.basicRanges['ak47_range']:
                                    logging.debug( "Drone type enemy has been detected in emergency situation")
                                    breakBool=1
                            "case of fire opportunity lav detection:"
                            if enemy.classification == EntityTypeEnum.EITAN:
                                if losRespose['distance'][0][0] < self.basicRanges['javelin_range']:
                                    logging.debug( "Good shooting Opporunity at Armored vehicle")
                                    breakBool = 1
            # updating HTN list which is used when shooting:
            self.blue_entity_list_HTN = ext_funs.getBluesDataFromVRFtoHTN(self.blue_entity_list)
            currTime = time.time()
            if currTime - current_entity.taskTime > self.config['scan_time'] or breakBool==1:
                #logging.debug(str(current_entity.squad) +": Scan Timeout")
                if len(current_entity.scanDetectionList) == 0:
                    logging.debug("No enemy has been detected within " + str(self.config['scan_time']) + " seconds of scanning")
                else:
                    reduced_scanned_names_list=[]
                    [reduced_scanned_names_list.append([enemy.unit_name, enemy.is_alive]) for enemy in current_entity.scanDetectionList if [enemy.unit_name, enemy.is_alive] not in reduced_scanned_names_list]
                    print_list=[]
                    for object in reduced_scanned_names_list:
                        if object[1] == True:
                            print_list.append(str(object[0]) + str("-Alive entity" ))
                        else:
                            print_list.append(str(object[0]) + str("-Destroyed entity"))
                    #logging.debug("Entities: " + str(print_list) +" has been discovered during scanning proccess with range of " + str(scan_range))
                current_entity.scanState=isScan.no
        if current_entity.waitState == isWait.yes:
            currTime = time.time()
            if currTime - current_entity.taskTime > current_entity.waitTime:
                logging.debug(str(current_entity.unit_name) + ": Wait time out")
                current_entity.waitState=isWait.no
                current_entity.waitTime=None

    #Creates Blue list
    # Uses EntityInfo class to describe an entity
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

    #Creates Red list
    # Creates Blue list
    # Creates general list from VRF format to known format - uses EntityInfo class to describe an entity
    # then, translates to format of EntityCurrentState class to describe an entity
    def CreateAndUpdateEntityList(self,entity_previous_list):
        entity_list=[] # creating new entity list from scratch
        entity_info_list = self.communicator.GetScenarioEntitiesInfo()
        entity_info_list = self.CreateEntityInfoFromVrf(entity_info_list)
        for k in range(len(entity_previous_list)): #only red
            for i in range(len(entity_info_list)): # blue and red
                if entity_previous_list[k].unit_name == entity_info_list[i].unit_name:
                    live_unit=entity_info_list[i]
            #data generated from simulator:
            current_entity                      = EntityCurrentState(entity_previous_list[k].unit_name)
            current_entity.power                = live_unit.power
            current_entity.health               = live_unit.health
            alive_status                        = live_unit.is_alive
            current_entity.alive                = alive_status
            current_entity.entity_damage_state  = live_unit.entity_damage_state

            current_entity.current_location = {
                "latitude": live_unit.location.get("latitude"),
                "longitude":live_unit.location.get("longitude"),
                "altitude": live_unit.location.get("altitude")
            }

            #data updated from last iteration:
            current_entity.classification   = live_unit.classification
            current_entity.COA              = entity_previous_list[k].COA
            current_entity.face             = entity_previous_list[k].face
            current_entity.planBool         = entity_previous_list[k].planBool
            current_entity.state            = entity_previous_list[k].state
            current_entity.fireState        = entity_previous_list[k].fireState
            current_entity.scanState        = entity_previous_list[k].scanState
            current_entity.scanDetectionList        = entity_previous_list[k].scanDetectionList
            current_entity.waitState        = entity_previous_list[k].waitState
            current_entity.waitTime        = entity_previous_list[k].waitTime

            current_entity.aim_list         = entity_previous_list[k].aim_list
            current_entity.preGameBool      = entity_previous_list[k].preGameBool
            current_entity.squad            = entity_previous_list[k].squad
            current_entity.role             = entity_previous_list[k].role
            current_entity.HTNtarget        = entity_previous_list[k].HTNtarget
            current_entity.HTNbluesFrozen   = entity_previous_list[k].HTNbluesFrozen

            #task statuses:
            current_entity.movement_task_completed = entity_previous_list[k].movement_task_completed
            current_entity.movement_task_success   = entity_previous_list[k].movement_task_success
            current_entity.fire_task_completed     = entity_previous_list[k].fire_task_completed
            current_entity.fire_task_success       = entity_previous_list[k].fire_task_success
            current_entity.taskTime = entity_previous_list[k].taskTime


            entity_list.append(current_entity)
        return entity_list

    # Creates general list from VRF format to known format - uses EntityInfo class to describe an entity
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
