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

def green_choose_random_position_op(state,a):
    positionIndexVec=[]
    for i in range(len(state.nextPositionIndex)):
        positionIndexVec.append(i)
    state.nextPositionIndex=random.choice(positionIndexVec)
    return state

def green_move_to_position_op(state,a):
    state.entity_state = 'move'
    return state

def green_locate_and_wait_at_position_op(state,a):
    state.entity_state = 'at_position'
    state.loc = ext_funs.getLocation(state, state.nextPositionIndex)
    # Index exchange:
    state.currentPositionIndex = state.nextPositionIndex
    state.nextPositionIndex = []
    # Updateting dynamic distances list:
    state.distance_from_positions = ext_funs.update_distance_from_positions(state.loc, state.positions)
    state.distance_from_assesedBlues = ext_funs.update_distance_from_blues(state.loc, state.assesedBlues)
    return state

pyhop.declare_operators(green_choose_random_position_op,green_move_to_position_op,green_locate_and_wait_at_position_op)


def findPlan(loc):
    init_state = pyhop.State('init_state')

    # HTN
    init_state.nextPositionIndex = []
    init_state.currentPositionIndex = []
    init_state.positions = []
    init_state.entity_state = 'stand'

    # Update distances from positions
    init_state.positions = ext_funs.get_positions_fromCSV('Resources\RedSpawnPos.csv')