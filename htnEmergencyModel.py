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
pyhop.declare_operators(e_continue_as_usual_op)


def e_continue_as_usual_m(state,a):
    if (0):
        return False
    return [('e_continue_as_usual_op',a)]

# pyhop.declare_methods('energency', e_continue_as_usual_m,e_go_to_cover_m,e_shoot_from_position_m)
# pyhop.declare_original_methods('energency', e_continue_as_usual_m,e_go_to_cover_m,e_shoot_from_position_m)

def findplan(basicRanges,squadPosture,enemyDimensions,loc,blueList,AccuracyConfiguration,intervisibility_polygoins):
    init_state = pyhop.State('init_state')
    #VRF configs:
    init_state.squadPosture=squadPosture
    init_state.enemyDimensions=enemyDimensions
    init_state.basicRanges=basicRanges
    init_state.intervisibility_polygoins=intervisibility_polygoins
    #HTN
    init_state.loc = loc
    init_state.positions = ext_funs.get_positions_fromCSV('Resources\RedAttackPos.csv')
    init_state.distance_from_positions = []
    init_state.distance_from_positions = ext_funs.update_distance_from_positions(init_state.loc, init_state.positions)

    init_state.assesedBlues = blueList
    init_state.distance_from_assesedBlues = ext_funs.update_distance_from_blues(init_state.loc, init_state.assesedBlues)
    init_state.enemy_number = ext_funs.getNumberofAliveEnemies(init_state.assesedBlues)


    init_state.in_cover = False
    for polygon in init_state.intervisibility_polygoins:
        answer= ext_funs.is_inside_polygon(init_state.loc,polygon)
        if answer==True:
            init_state.in_cover = True
            break
    init_state.debug_task = 0
    init_state.debug_method = 0
    init_state.debug_ope = 0
    # Weapons Accuracy Data:
    init_state.AccuracyConfiguration=AccuracyConfiguration