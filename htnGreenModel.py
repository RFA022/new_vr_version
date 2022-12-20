import random
import pyhop_mcts_game as pyhop
import ext_funs
from ext_funs import *
import pandas as pd

def green_choose_random_position_op(state,nextPositionIndex):
    state.nextPositionIndex=nextPositionIndex
    return state

def green_move_to_position_op(state,nextPositionIndex):
    state.entity_state = 'move'
    return state

def green_locate_and_wait_at_position_op(state,nextPositionIndex,waiting_time):
    state.entity_state = 'at_position'
    state.loc = ext_funs.getLocation(state, state.nextPositionIndex)
    # Index exchange:
    state.currentPositionIndex = nextPositionIndex
    state.waiting_time=waiting_time
    state.nextPositionIndex = []
    return state

pyhop.declare_operators(green_choose_random_position_op,green_move_to_position_op,green_locate_and_wait_at_position_op)

def green_end_mission_m(state,a):
    # agent reach goal
    if (0):
        print("Mission accomplished - no need to plan")
        return []
    return False

def green_go_and_wait_at_position_m(state,a):
    #agent still did not reach the target
    if (0):
        return False
    positionIndexVec = []
    for i in range(len(state.positions)):
        positionIndexVec.append(i)
    nextPositionIndex = random.choice(positionIndexVec)
    return [('green_choose_position',nextPositionIndex)]

pyhop.declare_methods('green_be', green_go_and_wait_at_position_m,green_end_mission_m)
pyhop.declare_original_methods('green_be', green_go_and_wait_at_position_m,green_end_mission_m)

def green_choose_random_position_m(state,a):
    #agent still did not reach the target
    if (0):
        return False
    return [('green_choose_random_position_op',a),('green_locate_and_wait_at_position',a)]

pyhop.declare_methods('green_choose_position', green_choose_random_position_m)
pyhop.declare_original_methods('green_choose_position', green_choose_random_position_m)

def green_locate_and_wait_at_position_m(state,a):
    #agent still did not reach the target
    if (0):
        return False

    waiting_time=np.random.normal(state.config['waiting_time_mean'],state.config['waiting_time_std'])
    while waiting_time<0:
        waiting_time = np.random.normal(state.config['waiting_time_mean'], state.config['waiting_time_std'])
    waiting_time=round(waiting_time)
    return [('green_move_to_position_op',state.nextPositionIndex),('green_locate_and_wait_at_position_op',state.nextPositionIndex,waiting_time)]

pyhop.declare_methods('green_locate_and_wait_at_position', green_locate_and_wait_at_position_m)
pyhop.declare_original_methods('green_locate_and_wait_at_position', green_locate_and_wait_at_position_m)

#After defining all tasks - updating method list#
#####----------------------------------------#####
pyhop.update_method_list()
#####----------------------------------------#####


def findplan(loc):
    init_state = pyhop.State('init_state')
    # HTN
    init_state.loc=loc
    init_state.nextPositionIndex = []
    init_state.currentPositionIndex = []
    init_state.positions = []
    init_state.entity_state = 'at_position'
    init_state.waiting_time=[]
    # Update distances from positions
    init_state.positions = ext_funs.get_positions_fromCSV('Resources\RedSpawnPos.csv')
    htnConfig = pd.read_csv('Resources\greenHtnConfig.csv',
                                       header=[0],
                                       index_col=[0])
    # updateSpecificConfigs
    init_state.config = {}
    init_state.config['waiting_time_mean'] = float(htnConfig.at['waiting_time_mean', 'value'])
    init_state.config['waiting_time_std']  = float(htnConfig.at['waiting_time_std', 'value'])
    init_state.config['exploration_value_rollout'] = float(htnConfig.at['exploration_value', 'value'])
    init_state.config['exploration_value_nextmove'] = float(htnConfig.at['exploration_value', 'value'])

    init_state.debug_task = 0
    init_state.debug_method = 0
    init_state.debug_ope = 0

    debug_level = 0
    if debug_level >= 2:
        print("init state is:")
        pyhop.print_state(init_state)
    #print("Begin Planning Green:")
    plan = pyhop.shop_m(init_state, [('green_be', 'me')],debug_level) #third parameter is debug mode
    #print(plan)
    return(plan)


# init_state = pyhop.State('init_state')
# # HTN
# init_state.loc=[]
# init_state.nextPositionIndex = []
# init_state.currentPositionIndex = []
# init_state.positions = []
# init_state.entity_state = 'at_position'
# init_state.waiting_time=[]
# # Update distances from positions
# init_state.positions = ext_funs.get_positions_fromCSV('Resources\RedSpawnPos.csv')
# htnConfig = pd.read_csv('Resources\greenHtnConfig.csv',
#                                    header=[0],
#                                    index_col=[0])
# # updateSpecificConfigs
# init_state.config = {}
# init_state.config['waiting_time_mean'] = float(htnConfig.at['waiting_time_mean', 'value'])
# init_state.config['waiting_time_std'] = float(htnConfig.at['waiting_time_std', 'value'])
#
#
# init_state.debug_task = 0
# init_state.debug_method = 0
# init_state.debug_ope = 0
# debug_level=0
# if debug_level>=2:
#     print("init state is:")
#     pyhop.print_state(init_state)
# plan = pyhop.shop_m(init_state, [('green_be', 'me')],debug_level)
# print(plan)