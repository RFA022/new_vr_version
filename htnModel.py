import random
import sys
import pyhop_mcts_game as pyhop
import numpy as np
import matplotlib.pyplot as plt
import ext_funs
from ext_funs import *
import scipy.stats
import pandas as pd
from Communicator import CommunicatorSingleton


def locate_at_position_op(state,a):
    state.squad_state = 'at_position'
    return state

def choose_position_op(state,nextPosition):
    state.nextPositionIndex=nextPosition
    return state

def move_to_position_op(state,a):
    state.squad_state = 'move'
    state.loc = ext_funs.getLocation(state, state.nextPositionIndex)
    state.nextPositionIndex = []
    state.distance_from_positions = ext_funs.update_distance_from_positions(state)
    return state

def scan_for_enemy_op(state,a):
    for enemy in state.assesedBlues:
        #if location is not known:
        if  (enemy['location']['latitude'] ==  None and
            enemy['location']['longitude'] ==  None and
            enemy['location']['altitude']  ==  None):
            #simple example: detected or not detected 50% ro be detected:
            num=1000
            r_n = scipy.stats.randint.rvs(0, num)
            if r_n>num*state.weights['basic_detection_probability']:
                enemy['observed']=True
        else:

            communicator = CommunicatorSingleton().obj
            enemy['observed'] = True
            num=random.randint(1,100)
            losRespose = communicator.GetGeoQuery([state.positions[0]], [enemy['location']], True, True)
            print(losRespose)
            # losRespose = ext_funs.losOperator(communicator,squadPosture,enemyDimensions, enemy, state.loc)
            # if losRespose['distance'][0][0] < self.basicRanges['squad_view_range']:
            #     if losRespose['los'][0][0] == True:
            #         enemy.last_seen_worldLocation = enemy.location
            #         logging.debug("Enemy: " + str(
            #             enemy.unit_name) + " has been detected")
            #         detectionCount += 1
    return state

def null_op(state,a):
    return state

def shoot_op(state,a):
    state.shoot=1
    return state

def aim_op(state,a):
    aim_list=[]
    for enemy in state.assesedBlues:
        if enemy['observed']==True:
            aim_list.append(enemy)
    #sort: observed list by classification when Eitan comes before Ohez
    aim_list=sorted(aim_list,key=lambda x:x['val'], reverse=True)
    state.aim_list=aim_list
    return state
pyhop.declare_operators(choose_position_op,move_to_position_op,locate_at_position_op,scan_for_enemy_op,null_op,aim_op,shoot_op)


def end_mission_m(state,a):
    # agent reach goal
    if (state.enemy_number == 0):
        #print("Mission accomplished")
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
    return [('scan_for_enemy_op', a),('continue_task',a)]

pyhop.declare_methods('scan_for_enemy', scan_for_enemy_m)
pyhop.declare_original_methods('scan_for_enemy', scan_for_enemy_m)

def attack_from_another_position_m(state,a):
    #agent still did not reach the target
    observed_count=0
    for enemy in state.assesedBlues:
        if enemy['observed']==True:
            observed_count+=1
    if (state.enemy_number == 0):
            return False
    if (observed_count!=0):
            return False
    return [('null_op',a)]

def aim_and_shoot_m(state,a):
    observed_count = 0
    for enemy in state.assesedBlues:
        if enemy['observed'] == True:
            observed_count += 1
    if (observed_count==0):
            return False
    return [('aim_op', a),('shoot',a)]

pyhop.declare_methods('continue_task',aim_and_shoot_m, attack_from_another_position_m)
pyhop.declare_original_methods('continue_task',aim_and_shoot_m, attack_from_another_position_m)

def shoot_m(state,a):
    return [('shoot_op',str(state.aim_list[0]['name']))]

pyhop.declare_methods('shoot',shoot_m)
pyhop.declare_original_methods('shoot',shoot_m)

#After defining all tasks - updating method list#
#####----------------------------------------#####
pyhop.update_method_list()
#####----------------------------------------#####


def findplan(communicator,squadPosture,enemyDimensions,loc,blueList):
    init_state = pyhop.State('init_state')
    #VRF configs:
    #init_state.communicator=communicator
    init_state.squadPosture=squadPosture
    init_state.enemyDimensions=enemyDimensions

    #HTN
    init_state.nextPositionIndex = []
    init_state.blues = []
    init_state.assesedBlues = []
    init_state.enemy_number = None
    init_state.positions = []
    init_state.squad_state = 'stand'
    init_state.distance_from_positions = []
    init_state.debug_task = 0
    init_state.debug_method = 0
    init_state.debug_ope = 0
    init_state.aim_list = 0

    # Update distances from positions
    init_state.positions = ext_funs.get_positions_fromCSV('RedAttackPos.csv')
    init_state.loc = loc
    init_state.distance_from_positions = ext_funs.update_distance_from_positions(init_state)
    init_state.assesedBlues = blueList
    init_state.enemy_number = len(init_state.assesedBlues)
    print('initial state is:')

    init_state.htnConfig = pd.read_csv('htnConfig.csv',
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
    init_state.weights['basic_detection_probability'] = float(
        init_state.htnConfig.at['basic_detection_probability', 'value'])

    pyhop.print_state_simple(init_state)

    plan = pyhop.shop_m(init_state, [('attack', 'me')])
    print(plan)
    return plan

