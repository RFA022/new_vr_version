import random
import sys
import pyhop_mcts_game as pyhop
import numpy as np
import matplotlib.pyplot as plt
import ext_funs
from ext_funs import *
import pandas as pd
import logging
from copy import deepcopy



def e_continue_as_usual_op(state,a):
    #print("e_continue_as_usual_op")
    return state

def e_move_to_closest_cover_op(state,a):
    #print("e_move_to_closest_cover_op")
    state.entity_state = 'move'
    state.estimated_mission_time += state.estimated_time_to_cover
    return state

def e_wait_in_cover_op(state,estimated_cover_waiting_time):
    #print("e_wait_in_cover_op")
    #not taking in account the movement of enemies
    #update squad state:
    state.entity_state="wait_in_cover"
    state.loc = state.closest_cover_point
    state.in_cover = ext_funs.is_inside_polygon(state.loc, state.cover_polygon)
    state.distance_from_positions = ext_funs.update_distance_from_positions(state.loc, state.positions)
    state.estimated_mission_time += estimated_cover_waiting_time
    state.estimated_distance_to_cover = 0
    state.estimated_time_to_cover = 0
    #update enemies state:
    state.assesedBlues=ext_funs.estimate_enemies_location_in_t_seconds_from_now(state.assesedBlues,estimated_cover_waiting_time)
    state.enemies_relative_direction=ext_funs.update_enemies_relative_direction(state.loc,state.assesedBlues,copy.deepcopy(state.enemies_relative_direction))
    state.vulnerability = ext_funs.assess_vulnerability(state.loc, state.enemies_relative_direction,state.assesedBlues, state.AccuracyConfiguration)
    state.distance_from_assesedBlues = ext_funs.update_distance_from_blues(state.loc, state.assesedBlues)
    return state

def e_wait_in_position_op(state,estimated_time_to_wait):
    #print("e_wait_in_position_op")
    #not taking in account the movement of enemies
    #update squad state:
    state.entity_state="wait_in_position"
    state.estimated_mission_time+=estimated_time_to_wait

    #update enemies state:
    state.assesedBlues = ext_funs.estimate_enemies_location_in_t_seconds_from_now(state.assesedBlues,estimated_time_to_wait)
    state.enemies_relative_direction = ext_funs.update_enemies_relative_direction(state.loc, state.assesedBlues,copy.deepcopy(state.enemies_relative_direction))
    state.vulnerability = ext_funs.assess_vulnerability(state.loc, state.enemies_relative_direction, state.assesedBlues,state.AccuracyConfiguration)
    state.distance_from_assesedBlues = ext_funs.update_distance_from_blues(state.loc, state.assesedBlues)
    return state

def e_shoot_op(state,a):
    #print("e_shoot_op")
    state.entity_state='shoot'
    return state

pyhop.declare_operators(e_continue_as_usual_op,e_move_to_closest_cover_op, e_wait_in_cover_op,e_wait_in_position_op,e_shoot_op)

def e_continue_as_usual_m(state,a):
    return [('e_continue_as_usual_op',a)]

def e_go_to_cover_m(state,a):
    "find closest_cover_point:"
    min_distance_to_cover= float('inf')
    minimum_polygon=None
    for polygon in state.intervisibility_polygoins:
        for vertex in polygon:
            distance_to_cover=ext_funs.getMetriDistance(vertex,state.loc)
            if distance_to_cover<min_distance_to_cover:
                min_distance_to_cover=distance_to_cover
                state.estimated_distance_to_cover=min_distance_to_cover
                state.closest_cover_point=vertex
                minimum_polygon=polygon
    minimum_polygon_centroid=ext_funs.getPolygonCentroid(minimum_polygon)
    state.cover_polygon=minimum_polygon
    state.closest_cover_point=ext_funs.generate_interior_polygon_point(state.closest_cover_point,minimum_polygon_centroid,minimum_polygon)
    state.estimated_distance_to_cover=ext_funs.getMetriDistance(state.loc,state.closest_cover_point)
    state.estimated_time_to_cover = ext_funs.first_order_time_estimator(state.estimated_distance_to_cover,float(state.config['squad_speed']))
    state.estimated_cover_waiting_time=ext_funs.asses_waiting_time_in_waiting_location(state.config,state.closest_cover_point,state.assesedBlues,state.enemies_relative_direction)
    return [('e_be_in_cover',a)]

def e_shoot_from_position_m(state,a):
    state.estimated_intersection_time=asses_intersection_time_with_fastest_target(state.basicRanges,state.config,state.loc,state.assesedBlues,state.enemies_relative_direction)
    return [('e_shoot_thread_from_current_position',a)]

pyhop.declare_methods('high_exposure_protocol', e_continue_as_usual_m,e_go_to_cover_m,e_shoot_from_position_m)
pyhop.declare_original_methods('high_exposure_protocol', e_continue_as_usual_m,e_go_to_cover_m,e_shoot_from_position_m)

def e_wait_in_cover_m(state,a):
        return [('e_move_to_closest_cover_op', a), ('e_wait_in_cover_op', state.estimated_cover_waiting_time)]

pyhop.declare_methods('e_be_in_cover', e_wait_in_cover_m)
pyhop.declare_original_methods('e_be_in_cover', e_wait_in_cover_m)

def e_shoot_immediately_m(state,a):
        return [('e_shoot_op',a)]

def e_wait_and_then_shoot_m(state,a):
        return [('e_wait_in_position_op',state.estimated_intersection_time),('e_shoot_op',a)]

pyhop.declare_methods('e_shoot_thread_from_current_position', e_shoot_immediately_m,e_wait_and_then_shoot_m)
pyhop.declare_original_methods('e_shoot_thread_from_current_position', e_shoot_immediately_m,e_wait_and_then_shoot_m)

# #After defining all tasks - updating method list#
# #####----------------------------------------#####
# pyhop.update_method_list()
# #####----------------------------------------#####

def findplan(config,basicRanges,squadPosture,enemyDimensions,AccuracyConfiguration,loc,enemies_relative_direction,blueList,intervisibility_polygoins):
    init_state = pyhop.State('init_state')

    #VRF configs:
    init_state.config=config
    init_state.squadPosture=squadPosture
    init_state.enemyDimensions=enemyDimensions
    init_state.basicRanges=basicRanges
    init_state.intervisibility_polygoins=intervisibility_polygoins
    init_state.AccuracyConfiguration=AccuracyConfiguration

    htnConfig = pd.read_csv('Resources\HighExplorationHtnConfig.csv',
                                       header=[0],
                                       index_col=[0])

    # updateSpecificConfigs
    init_state.config['exploration_value'] = float(htnConfig.at['exploration_value', 'value'])
    init_state.config['treshold_time'] = float(htnConfig.at['treshold_time', 'value'])

    init_state.weights = {}
    init_state.weights['e_move_to_closest_cover_op'] = float(htnConfig.at['e_move_to_closest_cover_op', 'value'])
    init_state.weights['eitan_val'] = float(htnConfig.at['eitan_val', 'value'])
    init_state.weights['ohez_val'] = float(htnConfig.at['ohez_val', 'value'])

    #HTN
    init_state.loc = loc
    init_state.enemies_relative_direction=enemies_relative_direction
    init_state.entity_state = 'entry'
    init_state.estimated_mission_time=0
    init_state.positions = ext_funs.get_positions_fromCSV('Resources\RedAttackPos.csv')
    init_state.distance_from_positions = []
    init_state.distance_from_positions = ext_funs.update_distance_from_positions(init_state.loc, init_state.positions)

    init_state.cover_polygon=None
    init_state.closest_cover_point=None
    init_state.estimated_distance_to_cover=None
    init_state.estimated_cover_waiting_time=None
    init_state.estimated_time_to_cover=None
    init_state.estimated_intersection_time=None

    init_state.assesedBlues = blueList
    init_state.distance_from_assesedBlues = ext_funs.update_distance_from_blues(init_state.loc, init_state.assesedBlues)
    init_state.enemy_number = ext_funs.getNumberofAliveEnemies(init_state.assesedBlues)

    init_state.vulnerability = ext_funs.assess_vulnerability(init_state.loc, init_state.enemies_relative_direction,
                                                             init_state.assesedBlues, init_state.AccuracyConfiguration)

    init_state.in_cover = False
    for polygon in init_state.intervisibility_polygoins:
        answer= ext_funs.is_inside_polygon(init_state.loc,polygon)
        if answer==True:
            init_state.in_cover = True
            init_state.cover_polygon=polygon
            break
    init_state.debug_task = 0
    init_state.debug_method = 0
    init_state.debug_ope = 0
    # Weapons Accuracy Data:
    init_state.AccuracyConfiguration=AccuracyConfiguration

    #pyhop.print_state_simple(init_state)
    debug_level = 1
    if debug_level >= 2:
        print("init state is:")
        pyhop.print_state_simple(init_state)
    print("Begin Planning Red:")
    plan = pyhop.shop_m(init_state, [('high_exposure_protocol', 'me')],debug_level) #third parameter is debug mode
    print(plan)
    return plan

