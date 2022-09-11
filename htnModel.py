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


def locate_at_position_op(state,a):
    state.squad_state = 'at_position'
    state.loc = ext_funs.getLocation(state, state.nextPositionIndex)
    # Index exchange:
    state.currentPositionIndex = state.nextPositionIndex
    state.nextPositionIndex = []
    # Updateting dynamic distances list:
    state.distance_from_positions = ext_funs.update_distance_from_positions(state.loc, state.positions)
    state.distance_from_assesedBlues = ext_funs.update_distance_from_blues(state.loc, state.assesedBlues)
    return state

def choose_position_op(state,nextPosition):
    state.nextPositionIndex=nextPosition
    return state

def move_to_position_op(state,a):
    state.squad_state = 'move'
    return state

def scan_for_enemy_and_assess_exposure_op(state,a):
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
            if losRespose['distance'][0][0] < state.basicRanges['squad_view_range']:
                 if losRespose['los'][0][0] == True:
                    enemy.observed = True

    # Exposure Assesment part:
    state_copy = deepcopy(state)
    knownEnemies, totalAccuracy, accuracyVec = ext_funs.getAccumulatedHitProbability(state_copy)
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
        enemy.observed = False # parameter is down
    #sort: observed list by classification when Eitan comes before Ohez needed to add distance classification.
    if aim_list != []:
        # sort by value - next sort by value and then by distance
        aim_list = sorted(aim_list, key=lambda x: (x.val, -x.distFromSquad), reverse=True)
        state.aim_list = aim_list
        for entity in aim_list:
            name = entity.unit_name
            state.aim_list_names.append(name)
    return state

def null_op(state,a):
    return state

def shoot_op(state,a):
    state.shoot=1
    return state

pyhop.declare_operators(choose_position_op,move_to_position_op,locate_at_position_op,scan_for_enemy_and_assess_exposure_op,null_op,aim_op,shoot_op)




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


def choose_position_m(state,param,a):
    nextPosition=param
    return [('choose_position_op',nextPosition),('move_to_position',a)]

pyhop.declare_methods('choose_position', choose_position_m)
pyhop.declare_original_methods('choose_position', choose_position_m)

def move_to_position_m(state,a):
    return [('move_to_position_op',a),('locate_at_position_op',a),('scan_for_enemy',a)]

pyhop.declare_methods('move_to_position', move_to_position_m)
pyhop.declare_original_methods('move_to_position', move_to_position_m)

def scan_for_enemy_m(state,a):
    return [('scan_for_enemy_and_assess_exposure_op', a),('continue_task',a)]

pyhop.declare_methods('scan_for_enemy', scan_for_enemy_m)
pyhop.declare_original_methods('scan_for_enemy', scan_for_enemy_m)

def attack_from_another_position_m(state,a):
    #agent still did not reach the target
    observedAndalive_count=0
    for enemy in state.assesedBlues:
        if (enemy.observed == True) and (enemy.is_alive == True):
            observedAndalive_count+=1
    if (state.enemy_number == 0):
            return False
    if (observedAndalive_count!=0):
            return False
    return [('null_op',a)]

def aim_and_shoot_m(state,a):
    observedAndalive_count = 0
    for enemy in state.assesedBlues:
        if (enemy.observed == True) and (enemy.is_alive == True):
            observedAndalive_count += 1
    if (observedAndalive_count==0):
            return False
    return [('aim_op', a),('shoot',a)]

pyhop.declare_methods('continue_task',aim_and_shoot_m, attack_from_another_position_m)
pyhop.declare_original_methods('continue_task',aim_and_shoot_m, attack_from_another_position_m)

def shoot_m(state,a):
    return [('shoot_op',str(state.aim_list[0].unit_name))]

pyhop.declare_methods('shoot',shoot_m)
pyhop.declare_original_methods('shoot',shoot_m)

#After defining all tasks - updating method list#
#####----------------------------------------#####
pyhop.update_method_list()
#####----------------------------------------#####

def findplan(basicRanges,squadPosture,enemyDimensions,loc,blueList,BluePolygonCentroid,AccuracyConfiguration,bluePolygon):
    init_state = pyhop.State('init_state')
    #VRF configs:
    init_state.squadPosture=squadPosture
    init_state.enemyDimensions=enemyDimensions
    init_state.basicRanges=basicRanges
    #HTN
    init_state.nextPositionIndex = []
    init_state.currentPositionIndex=[]
    init_state.assesedBlues = []
    init_state.enemy_number = None
    init_state.positions = []
    init_state.squad_state = 'stand'
    init_state.distance_from_positions = []
    init_state.debug_task = 0
    init_state.debug_method = 0
    init_state.debug_ope = 0
    init_state.aim_list = []
    init_state.aim_list_names=[]
    init_state.positiveHits=[]
    init_state.negativeHitsProbability=[]
    # Scenario Data:
    init_state.BluePolygonCentroid = BluePolygonCentroid
    init_state.bluePolygon=bluePolygon

    # Update distances from positions
    init_state.positions = ext_funs.get_positions_fromCSV('Resources\RedAttackPos.csv')
    init_state.loc = loc
    init_state.distance_from_positions = ext_funs.update_distance_from_positions(init_state.loc,init_state.positions)
    "edit blueList - append fake location to unknown blues"
    for blue in blueList:
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
    init_state.weights['locate_at_position_op'] = float(init_state.htnConfig.at['locate_at_position_op', 'value'])
    init_state.weights['scan_for_enemy_op'] = float(init_state.htnConfig.at['scan_for_enemy_op', 'value'])
    init_state.weights['bda_op'] = float(init_state.htnConfig.at['bda_op', 'value'])
    init_state.weights['shoot_enemy_op'] = float(init_state.htnConfig.at['shoot_enemy_op', 'value'])
    init_state.weights['basic_detection_probability'] = float(init_state.htnConfig.at['basic_detection_probability', 'value'])
    init_state.weights['choose_position_op_dist_from_position'] = float(init_state.htnConfig.at['choose_position_op_dist_from_position', 'value'])
    init_state.weights['choose_position_op_dist_from_polygon'] = float(init_state.htnConfig.at['choose_position_op_dist_from_polygon', 'value'])
    init_state.weights['choose_position_op_percent_exposure'] = float(init_state.htnConfig.at['choose_position_op_percent_exposure', 'value'])
    init_state.weights['eitan_val'] = float(init_state.htnConfig.at['eitan_val', 'value'])
    init_state.weights['ohez_val'] = float(init_state.htnConfig.at['ohez_val', 'value'])

    # Weapons Accuracy Data:
    init_state.AccuracyConfiguration=AccuracyConfiguration

    #pyhop.print_state_simple(init_state)
    debug_level = 0
    if debug_level >= 2:
        print("init state is:")
        pyhop.print_state(init_state)
    print("Begin Planning Red:")
    plan = pyhop.shop_m(init_state, [('attack', 'me')],debug_level) #third parameter is debug mode
    print(plan)
    return plan

