import sys
BOUND=1000
import pyhop_mcts_game as pyhop
import numpy as np
import matplotlib.pyplot as plt
import ext_funs
import scipy.stats

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
            r_n = scipy.stats.randint.rvs(0, 1000)
            if r_n>500:
                enemy['observed']=True
        else:
            pass

    return state


pyhop.declare_operators(choose_position_op,move_to_position_op,locate_at_position_op,scan_for_enemy_op)


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
    return [('choose_position',a),('move_to_position',a),('locate_at_position_op',a),('scan_for_enemy',a)]

pyhop.declare_methods('attack', attack_from_position_m,end_mission_m)
pyhop.declare_original_methods('attack', attack_from_position_m,end_mission_m)


def choose_position_m(state,param,a):
    nextPosition=param
    return [('choose_position_op',nextPosition)]

pyhop.declare_methods('choose_position', choose_position_m)
pyhop.declare_original_methods('choose_position', choose_position_m)

def move_to_position_m(state,a):
    return [('move_to_position_op',a)]

pyhop.declare_methods('move_to_position', move_to_position_m)
pyhop.declare_original_methods('move_to_position', move_to_position_m)

def scan_for_enemy_m(state,a):
    return [('scan_for_enemy_op', a)]

pyhop.declare_methods('scan_for_enemy', scan_for_enemy_m)
pyhop.declare_original_methods('scan_for_enemy', scan_for_enemy_m,)


#After defining all tasks - updating method list#
#####----------------------------------------#####
pyhop.update_method_list()
#####----------------------------------------#####



def plot_map(state):
    blue_polygon=state.blue_polygon
    blue_polygon.append(state.blue_polygon[0])
    x_pol, y_pol = zip(*state.blue_polygon)  # create lists of x and y values
    x_pos=[]
    y_pos=[]
    col_pos=[]
    for i in range(len(state.positions)):
        x_pos.append(state.positions[i][0])
        y_pos.append(state.positions[i][1])
        col_pos.append(state.positions[i][2]/10)
    plt.figure()
    plt.plot(x_pol, y_pol)
    for i in range(len(state.positions)):
        plt.scatter(x_pos[i],y_pos[i],c=[col_pos[i],0,0])
    plt.show()




def findplan(loc):
    init_state = pyhop.State('init_state')
    init_state.nextPositionIndex=[]
    init_state.assesedBlues=[]
    init_state.enemy_number=None
    init_state.squad_state='stand'
    init_state.positions=[]
    init_state.distance_from_positions=[]
    init_state.debug_task=0
    init_state.debug_method=0
    init_state.debug_ope=0
    #Update distances from positions
    init_state.positions=ext_funs.get_positions_fromCSV('RedAttackPos.csv')
    init_state.loc = loc
    init_state.distance_from_positions=ext_funs.update_distance_from_positions(init_state)
    init_state.assesedBlues = ext_funs.getBluesDataFromCSV('BluesConfig.csv')
    init_state.enemy_number = len(init_state.assesedBlues)
    print('initial state:')
    pyhop.print_state(init_state)
    plan = pyhop.shop_m(init_state, [('attack','me')])
    print("Plan is:", plan)
    return (plan)
