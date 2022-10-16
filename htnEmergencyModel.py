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
    return state

def e_move_to_closest_cover_op(state,a):
    state.entity_state = 'move'
    state.estimated_mission_time += state.estimated_time_to_cover
    return state
pyhop.declare_operators(e_continue_as_usual_op,e_move_to_closest_cover_op)

def e_wait_in_cover_op(state,estimated_time_to_cover):
    state.loc = state.closest_cover_point
    state.estimated_mission_time+=estimated_time_to_cover
    state.estimated_distance_to_cover=0
    state.estimated_time_to_cover=0
    state.in_cover =ext_funs.is_inside_polygon(state.loc,state.cover_polygon)
    #update static position variables:
    state.distance_from_positions = ext_funs.update_distance_from_positions(state.loc, state.positions)



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
    state.closest_cover_point=ext_funs.generate_interior_polygon_point(state.closest_cover_point,minimum_polygon_centroid,minimum_polygon)
    state.estimated_distance_to_cover=ext_funs.getMetriDistance(state.loc,state.closest_cover_point)
    state.estimated_time_to_cover = ext_funs.first_order_time_estimator(state.estimated_distance_to_cover,float(state.config['squad_speed']))
    state.estimated_cover_waiting_time=ext_funs.asses_waiting_time_in_waiting_location(state.config,state.loc,state.closest_cover_point,state.assesedBlues,state.enemies_relative_direction)

    return [('e_move_to_closest_cover_op', a),('e_be_in_cover')]

def e_continue_as_usual_m(state,a):
    if (0):
        return False
    return [('e_continue_as_usual_op',a)]

def e_shoot_from_position_m(state,a):
    return(0)

pyhop.declare_methods('high_exposure_protocol', e_continue_as_usual_m,e_go_to_cover_m,e_shoot_from_position_m)
pyhop.declare_original_methods('high_exposure_protocol', e_continue_as_usual_m,e_go_to_cover_m,e_shoot_from_position_m)

def e_wait_in_cover_m(state,a):
    if (0):
        return False
    else:
        return [('e_wait_in_cover_op',state,state.estimated_time_to_cover)]


pyhop.declare_methods('e_be_in_cover', e_wait_in_cover_m)
pyhop.declare_original_methods('e_be_in_cover', e_wait_in_cover_m)

def findplan(config,basicRanges,squadPosture,enemyDimensions,AccuracyConfiguration,loc,enemies_relative_direction,blueList,intervisibility_polygoins):
    init_state = pyhop.State('init_state')

    #VRF configs:
    init_state.config=config
    init_state.squadPosture=squadPosture
    init_state.enemyDimensions=enemyDimensions
    init_state.basicRanges=basicRanges
    init_state.intervisibility_polygoins=intervisibility_polygoins
    init_state.AccuracyConfiguration=AccuracyConfiguration

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

    e_go_to_cover_m(init_state,'me')
