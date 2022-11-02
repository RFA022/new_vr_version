import random
import sys
import pyhop_mcts_game as pyhop
import numpy as np
import matplotlib.pyplot as plt
import ext_funs
from ext_funs import *
import scipy.stats

import pandas as pd
import logging
from copy import deepcopy

def evaluate_HTN_subPlan_survivability_op(state,a):
    return state

def depart_position_op(state,a):
    if state.deployment_style=='full_anti_tank':
        if state.squad_state=='attack_position':
            state.missionTime  += float(state.config['attack_position_departure_mean_time'])
            state.positionTime += float(state.config['attack_position_departure_mean_time'])
        elif state.squad_state=='nearest_cover_position' or  state.squad_state=='current_position':
            state.missionTime  += float(state.config['open_position_departure_mean_time'])
            state.positionTime += float(state.config['open_position_departure_mean_time'])
        state.squad_state = 'depart_from_position'
    elif state.deployment_style=='rapid': #not adding any excesive time for rapid deployment
        pass
    return state

def locate_at_position_op(state,deployment_style):
    state.loc = ext_funs.getLocation(state, state.nextPositionIndex)
    state.squad_state = ext_funs.getSquadState(state,state.nextPositionIndex)
    state.deployment_style=deployment_style
    # Index exchange:
    state.currentPositionIndex = state.nextPositionIndex
    state.nextPositionIndex = []
    # Updateting dynamic distances list:
    state.distance_from_positions = ext_funs.update_distance_from_positions(state.loc, state.positions)
    state.distance_from_assesedBlues = ext_funs.update_distance_from_blues(state.loc, state.assesedBlues)

    #state location
    state.estimated_distance_to_position = 0
    state.estimated_time_to_position = 0

    #Add time to mission time
    if state.deployment_style=='full_anti_tank':
        if state.squad_state=='attack_position':
            state.missionTime  += float(state.config['attack_position_deployment_mean_time'])
            state.positionTime += float(state.config['attack_position_deployment_mean_time'])

        elif state.squad_state=='nearest_cover_position' or  state.squad_state=='current_position':
            state.missionTime  += float(state.config['open_position_deployment_mean_time'])
            state.positionTime += float(state.config['open_position_deployment_mean_time'])
    elif state.deployment_style=='rapid':
        #means no time is added to mission time or position time
        pass
    return state

def choose_position_op(state,nextPosition,nextLoc):
    state.nextPositionIndex=nextPosition
    "reset observation of enemies - before beggining of moving to another positions"
    for enemy in state.assesedBlues:
        enemy.observed=False
    return state

def move_to_position_op(state,a):
    state.squad_state = a
    state.missionTime+= float(state.estimated_time_to_position) #added only for mission time and not to position time
    return state

def scan_for_enemy_and_assess_exposure_op(state,a):
    state.missionTime  += state.config['scan_time']
    state.positionTime += state.config['scan_time']
    if state.deployment_style=='full_anti_tank':
        scan_range=state.basicRanges['squad_view_range']
    elif state.deployment_style=='rapid':
        scan_range=state.basicRanges['squad_eyes_range']
    #Scan part:
    for enemy in state.assesedBlues:
        #if location is not known:
        if(enemy.location['latitude'] ==  None and
            enemy.location['longitude'] ==  None and
            enemy.location['altitude']  ==  None):
            #simple example: detected or not detected 50% ro be detected:
            num=1000
            r_n = scipy.stats.randint.rvs(0, num)
            if state.weights['basic_detection_probability']>r_n/num:
                enemy.observed = True
        else:
            losRespose = ext_funs.losOperator(state.squadPosture,state.enemyDimensions,enemy,state.loc)
            #print(losRespose)
            if losRespose['distance'][0][0] < scan_range:
                 if losRespose['los'][0][0] == True:
                    enemy.observed = True
    # Exposure Assesment part:
    state_copy = deepcopy(state)
    knownEnemies, totalAccuracy, accuracyVec = ext_funs.getAccumulatedHitProbability(state_copy,state_copy.AccuracyConfiguration,'observation')
    if knownEnemies > 0:
        totalprobability = 1
        for accuracy in accuracyVec:
            totalprobability = totalprobability * (1 - accuracy)
        probabilityToGetHit = (1 - totalprobability)
        state.negativeHitsProbability.append(probabilityToGetHit)
    return state


def aim_op(state,a):
    aim_list=[]
    for k, enemy in enumerate(state.assesedBlues):
        if enemy.observed==True and enemy.is_alive==True:
            #Atribute distFromSquad is local atribute for blue enemy only for Aim operator
            if (enemy.location['latitude'] == None and
                    enemy.location['longitude'] == None and
                    enemy.location['altitude'] == None):
                #if enemy has been observed statistically we assume its in the middle of the polygon
                enemy.distFromSquad=ext_funs.getMetriDistance(state.loc, state.BluePolygonCentroid)
            else:
                enemy.distFromSquad = state.distance_from_assesedBlues[k]
            aim_list.append(enemy)
        else:
            enemy.distFromSquad = None
    #sort: observed list by classification when Eitan comes before Ohez needed to add distance classification.
    if aim_list != []:
        # sort by value - next sort by value and then by distance
        if state.deployment_style == 'full_anti_tank':
            pass
        elif state.deployment_style == 'rapid': #remove all EITANs from the list
            index_remove_list=[]
            for k , entity in enumerate(aim_list):
                if entity.classification==EntityTypeEnum.EITAN:
                    index_remove_list.append(k)
            for index in sorted(index_remove_list, reverse=True):
                del aim_list[index]
        aim_list = sorted(aim_list, key=lambda x: (x.val, -x.distFromSquad), reverse=True)
        state.aim_list = aim_list
        for entity in aim_list:
            name = entity.unit_name
            state.aim_list_names.append(name)
    return state

def abort_op(state,a):
    return state

def shoot_op(state,a):
    state.shoot=1
    state.missionTime  += float(state.config['shooting_time'])
    state.positionTime += float(state.config['shooting_time'])
    return state

pyhop.declare_operators(choose_position_op,move_to_position_op,locate_at_position_op,scan_for_enemy_and_assess_exposure_op,abort_op,aim_op,shoot_op,depart_position_op,evaluate_HTN_subPlan_survivability_op)


def end_mission_m(state,a):
    # agent reach goal
    if (state.enemy_number == 0):
        print("Mission accomplished - no need to plan")
        return []
    return False

def attack_from_position_m(state,a):
    #agent still did not reach the target
    if (state.enemy_number == 0):
            return False
    return [('choose_position',a)]

pyhop.declare_methods('attack', attack_from_position_m,end_mission_m)
pyhop.declare_original_methods('attack', attack_from_position_m,end_mission_m)


def choose_attack_position_m(state,param,a):
    nextPosition=param
    nextLoc=ext_funs.getLocation(state,nextPosition)
    state.estimated_distance_to_position = state.distance_from_positions[nextPosition]
    state.estimated_time_to_position = ext_funs.first_order_time_estimator(state.estimated_distance_to_position,
                                                                           float(state.config['squad_speed']))
    return [('choose_position_op',nextPosition,nextLoc),('move_to_position',a)]

def choose_cover_position_m(state,a):
    nextPosition="nearest_cover_position"
    #find clocest cover point
    min_distance_to_cover = float('inf')
    minimum_polygon = None
    for polygon in state.intervisibility_polygoins:
        for vertex in polygon:
            distance_to_cover = ext_funs.getMetriDistance(vertex, state.loc)
            if distance_to_cover < min_distance_to_cover:
                min_distance_to_cover = distance_to_cover
                state.estimated_distance_to_position = min_distance_to_cover
                state.closest_cover_point = vertex
                minimum_polygon = polygon
    minimum_polygon_centroid = ext_funs.getPolygonCentroid(minimum_polygon)
    state.cover_polygon = minimum_polygon
    state.closest_cover_point = ext_funs.generate_interior_polygon_point(state.closest_cover_point,
                                                                         minimum_polygon_centroid, minimum_polygon)
    state.estimated_time_to_position = ext_funs.first_order_time_estimator(state.estimated_distance_to_position,
                                                                      float(state.config['squad_speed']))
    nextLoc = ext_funs.getLocation(state, nextPosition)
    return [('choose_position_op',nextPosition,nextLoc), ('move_to_position', a)]

def choose_current_position_m(state,a):
    nextPosition='current_position'
    nextLoc=ext_funs.getLocation(state,nextPosition)
    state.estimated_distance_to_position = 0
    state.estimated_time_to_position = 0
    return [('choose_position_op',nextPosition,nextLoc),('move_to_position',a)]


pyhop.declare_methods('choose_position', choose_attack_position_m,choose_current_position_m,choose_cover_position_m)
pyhop.declare_original_methods('choose_position', choose_attack_position_m,choose_current_position_m,choose_cover_position_m)

def move_to_position_by_foot_m(state,a):
    return [('move_to_position_op','move_by_foot'),('deploy_at_position',a)]

pyhop.declare_methods('move_to_position', move_to_position_by_foot_m)
pyhop.declare_original_methods('move_to_position', move_to_position_by_foot_m)

def full_anti_tank_deployment_m(state,a):
    deployment_style='full_anti_tank'
    return([('locate_at_position_op',deployment_style),('scan_for_enemy',a)])

def rapid_deployment_m(state,a):
    deployment_style='rapid'
    return([('locate_at_position_op',deployment_style),('scan_for_enemy',a)])

pyhop.declare_methods('deploy_at_position', full_anti_tank_deployment_m,rapid_deployment_m)
pyhop.declare_original_methods('deploy_at_position', full_anti_tank_deployment_m,rapid_deployment_m)

def scan_for_enemy_m(state,a):
    return [('scan_for_enemy_and_assess_exposure_op', a),('aim_and_shoot',a)]

pyhop.declare_methods('scan_for_enemy', scan_for_enemy_m)
pyhop.declare_original_methods('scan_for_enemy', scan_for_enemy_m)

def abort_m(state,a):
    #agent still did not reach the target
    observedAndalive_count=0
    for enemy in state.assesedBlues:
        if (enemy.observed == True) and (enemy.is_alive == True):
            observedAndalive_count+=1
    if (state.enemy_number == 0):
            return False
    if (observedAndalive_count!=0):
            return False
    return [('abort_op',a,),('depart',a)]

def aim_and_shoot_m(state,a):
    observedAndalive_count = 0
    for enemy in state.assesedBlues:
        if (enemy.observed == True) and (enemy.is_alive == True):
            observedAndalive_count += 1
    if (observedAndalive_count==0):
            return False
    return [('aim_op', state.deployment_style),('shoot',state.deployment_style),('depart',a)]

pyhop.declare_methods('aim_and_shoot',aim_and_shoot_m, abort_m)
pyhop.declare_original_methods('aim_and_shoot',aim_and_shoot_m, abort_m)

def shoot_m(state,a):
    if len(state.aim_list)>0:
        return [('shoot_op',str(state.aim_list[0].unit_name))]
    else:
        return [('shoot_op', "none")]

pyhop.declare_methods('shoot',shoot_m)
pyhop.declare_original_methods('shoot',shoot_m)

def depart_m(state,a):
    return [('depart_position_op',a),('evaluate_HTN_subPlan_survivability_op',a)]

pyhop.declare_methods('depart',depart_m)
pyhop.declare_original_methods('depart',depart_m)


#After defining all tasks - updating method list#
#####----------------------------------------#####
pyhop.update_method_list()
#####----------------------------------------#####

def findplan(config,intervisibility_polygoins,basicRanges,squadPosture,enemyDimensions,loc,blueList,BluePolygonCentroid,AccuracyConfiguration,bluePolygon):
    init_state = pyhop.State('init_state')
    #VRF configs:
    init_state.intervisibility_polygoins=intervisibility_polygoins
    init_state.squadPosture=squadPosture
    init_state.enemyDimensions=enemyDimensions
    init_state.basicRanges=basicRanges
    init_state.config=config
    #HTN
    init_state.nextPositionIndex = [] #both can be index or string-> 'cover', 'current_position'
    init_state.currentPositionIndex = []
    init_state.loc=None
    init_state.assesedBlues = []
    init_state.enemy_number = None
    init_state.positions = []
    init_state.squad_state = 'starting_position' # attack_position,current_position,nearest_cover_position
    init_state.distance_from_positions = []
    init_state.aim_list = []
    init_state.aim_list_names=[]
    init_state.deployment_style=None #full_anti_tank, rapid
    #Cover point related state attributes
    init_state.cover_polygon=None
    init_state.closest_cover_point=None
    #next position
    init_state.estimated_distance_to_position=None
    init_state.estimated_time_to_position=None
    #intersection time with targert
    init_state.estimated_intersection_time=None

    #Scoring and Times
    init_state.missionTime=0  #Time counting for the complete mission
    init_state.positionTime=0 #Time counting for position related tasks
    init_state.positiveHits=[]
    init_state.negativeHitsProbability=[]

    #Debug Data:
    init_state.debug_task = 0
    init_state.debug_method = 0
    init_state.debug_ope = 0

    # Scenario Data:
    init_state.BluePolygonCentroid = BluePolygonCentroid
    init_state.bluePolygon=bluePolygon

    # Update distances from positions
    init_state.positions = ext_funs.get_positions_fromCSV('Resources\RedAttackPos.csv')
    init_state.loc = loc
    init_state.distance_from_positions = ext_funs.update_distance_from_positions(init_state.loc,init_state.positions)
    init_state.approximated_max_mission_time=\
    max(init_state.distance_from_positions)/float(init_state.config['squad_speed']) +\
    +float(init_state.config['attack_position_deployment_mean_time']) +\
    +float(init_state.config['scan_time']) +\
    +float(init_state.config['shooting_time'])+\
    +float(init_state.config['attack_position_departure_mean_time'])
    init_state.approximated_max_position_time= \
        +float(init_state.config['open_position_deployment_mean_time']) + \
        +float(init_state.config['scan_time']) + \
        +float(init_state.config['shooting_time']) + \
        +float(init_state.config['open_position_departure_mean_time'])

    "edit blueList - append fake location to unknown blues"
    for blue in blueList:
        blue.observed=False
        if blue.locationType==HTNbluLocationType.fake:
            blue.location=ext_funs.generatePointInPolygon(bluePolygon)
    init_state.assesedBlues = blueList
    init_state.distance_from_assesedBlues=ext_funs.update_distance_from_blues(init_state.loc,init_state.assesedBlues)
    init_state.enemy_number = ext_funs.getNumberofAliveEnemies(init_state.assesedBlues)

    "edit exposure list"
    exposure_list=[]
    for position in init_state.positions:
        exposure_list.append(float(position['exposure']))
    init_state.position_exposure_level=exposure_list

    #stays constant throught the whole scenario:
    init_state.distance_positions_from_BluePolygonCentroid=ext_funs.update_distance_from_positions(init_state.BluePolygonCentroid,init_state.positions)
    init_state.htnConfig = pd.read_csv('Resources\htnConfig.csv',
                                       header=[0],
                                       index_col=[0])
    # updateSpecificConfigs
    init_state.weights = {}
    init_state.weights['choose_position_op'] = float(init_state.htnConfig.at['choose_position_op', 'value'])
    init_state.weights['move_to_position_op'] = float(init_state.htnConfig.at['move_to_position_op', 'value'])
    init_state.weights['evaluate_HTN_subPlan_survivability_op'] = float(init_state.htnConfig.at['evaluate_HTN_subPlan_survivability_op', 'value'])
    init_state.weights['scan_for_enemy_op'] = float(init_state.htnConfig.at['scan_for_enemy_op', 'value'])
    init_state.weights['bda_op'] = float(init_state.htnConfig.at['bda_op', 'value'])
    init_state.weights['shoot_enemy_op'] = float(init_state.htnConfig.at['shoot_enemy_op', 'value'])
    init_state.weights['basic_detection_probability'] = float(init_state.htnConfig.at['basic_detection_probability', 'value'])
    init_state.weights['choose_position_op_dist_from_position'] = float(init_state.htnConfig.at['choose_position_op_dist_from_position', 'value'])
    init_state.weights['choose_position_op_dist_from_polygon'] = float(init_state.htnConfig.at['choose_position_op_dist_from_polygon', 'value'])
    init_state.weights['choose_position_op_percent_exposure'] = float(init_state.htnConfig.at['choose_position_op_percent_exposure', 'value'])
    init_state.weights['eitan_val'] = float(init_state.htnConfig.at['eitan_val', 'value'])
    init_state.weights['ohez_val'] = float(init_state.htnConfig.at['ohez_val', 'value'])


    #add more things to basic config
    init_state.config['exploration_value_rollout'] = float(init_state.htnConfig.at['exploration_value_rollout', 'value'])
    init_state.config['exploration_value_nextmove'] = float(init_state.htnConfig.at['exploration_value_nextmove', 'value'])
    init_state.config['choose_position_op_cover_exposure_factor'] = float(init_state.htnConfig.at['choose_position_op_cover_exposure_factor', 'value'])
    init_state.config['choose_position_op_position_bound'] = float(init_state.htnConfig.at['choose_position_op_position_bound', 'value'])
    init_state.config['attack_position_survivability_factor'] = float(init_state.htnConfig.at['attack_position_survivability_factor', 'value'])
    init_state.config['open_position_survivability_factor'] = float(init_state.htnConfig.at['open_position_survivability_factor', 'value'])
    init_state.config['cover_position_survivability_factor'] = float(init_state.htnConfig.at['cover_position_survivability_factor', 'value'])
    init_state.config['evaluate_HTN_subPlan_survivability_op_time_importance'] = float(init_state.htnConfig.at['evaluate_HTN_subPlan_survivability_op_time_importance', 'value'])


    # Weapons Accuracy Data:
    init_state.AccuracyConfiguration=AccuracyConfiguration

    #pyhop.print_state_simple(init_state)
    debug_level = 1
    if debug_level >= 2:
        print("init state is:")
        pyhop.print_state_simple(init_state)
    print("Begin Planning Red:")

    plan = pyhop.shop_m(init_state, [('attack', 'me')],debug_level) #third parameter is debug mode
    print(plan)
    return plan

"""""""""
"Debug section with the ability to plot the location of the first enemy"
pos = [init_state.assesedBlues[0].location['latitude'], init_state.assesedBlues[0].location['longitude'],
       init_state.assesedBlues[0].location['altitude']]
communicator = CommunicatorSingleton().obj
communicator.CreateEntitySimple('enemy' + str(random.randint(0, 10000000000)), pos, 2, '16:0:0:1:0:0:0')
"""""""""""