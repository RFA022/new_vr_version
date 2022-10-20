"""
Pyhop, version 1.2.2 -- a simple SHOP-like planner written in Python.
Author: Dana S. Nau, 2013.05.31

Copyright 2013 Dana S. Nau - http://www.cs.umd.edu/~nau

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Pyhop should work correctly in both Python 2.7 and Python 3.2.
For examples of how to use it, see the example files that come with Pyhop.

Pyhop provides the following classes and functions:

- foo = State('foo') tells Pyhop to create an empty state object named 'foo'.
  To put variables and values into it, you should do assignments such as
  foo.var1 = val1

- bar = Goal('bar') tells Pyhop to create an empty goal object named 'bar'.
  To put variables and values into it, you should do assignments such as
  bar.var1 = val1

- print_state(foo) will print the variables and values in the state foo.

- print_goal(foo) will print the variables and values in the goal foo.

- declare_operators(o1, o2, ..., ok) tells Pyhop that o1, o2, ..., ok
  are all of the planning operators; this supersedes any previous call
  to declare_operators.

- print_operators() will print out the list of available operators.

- declare_methods('foo', m1, m2, ..., mk) tells Pyhop that m1, m2, ..., mk
  are all of the methods for tasks having 'foo' as their taskname; this
  supersedes any previous call to declare_methods('foo', ...).

- print_methods() will print out a list of all declared methods.

- pyhop(state1,tasklist) tells Pyhop to find a plan for accomplishing tasklist
  (a list of tasks), starting from an initial state state1, using whatever
  methods and operators you declared previously.

- In the above call to pyhop, you can add an optional 3rd argument called
  'verbose' that tells pyhop how much debugging printout it should provide:
- if verbose = 0 (the default), pyhop returns the solution but prints nothing;
- if verbose = 1, it prints the initial parameters and the answer;
- if verbose = 2, it also prints a message on each recursive call;
- if verbose = 3, it also prints info about what it's computing.
"""

# Pyhop's planning algorithm is very similar to the one in SHOP and JSHOP
# (see http://www.cs.umd.edu/projects/shop). Like SHOP and JSHOP, Pyhop uses
# HTN methods to decompose tasks into smaller and smaller subtasks, until it
# finds tasks that correspond directly to actions. But Pyhop differs from
# SHOP and JSHOP in several ways that should make it easier to use Pyhop
# as part of other programs:
#
# (1) In Pyhop, one writes methods and operators as ordinary Python functions
#     (rather than using a special-purpose language, as in SHOP and JSHOP).
#
# (2) Instead of representing states as collections of logical assertions,
#     Pyhop uses state-variable representation: a state is a Python object
#     that contains variable bindings. For example, to define a state in
#     which box b is located in room r1, you might write something like this:
#     s = State()
#     s.loc['b'] = 'r1'
#
# (3) You also can define goals as Python objects. For example, to specify
#     that a goal of having box b in room r2, you might write this:
#     g = Goal()
#     g.loc['b'] = 'r2'
#     Like most HTN planners, Pyhop will ignore g unless you explicitly
#     tell it what to do with g. You can do that by referring to g in
#     your methods and operators, and passing g to them as an argument.
#     In the same fashion, you could tell Pyhop to achieve any one of
#     several different goals, or to achieve them in some desired sequence.
#
# (4) Unlike SHOP and JSHOP, Pyhop doesn't include a Horn-clause inference
#     engine for evaluating preconditions of operators and methods. So far,
#     I've seen no need for it; I've found it easier to write precondition
#     evaluations directly in Python. But I could consider adding such a
#     feature if someone convinces me that it's really necessary.
#
# Accompanying this file are several files that give examples of how to use
# Pyhop. To run them, launch python and type "import blocks_world_examples"
# or "import simple_travel_example".


from __future__ import print_function
import copy, sys, pprint
from copy import deepcopy
import random
import math
import numpy as np
import methods_config as mc
from CommunicatorInterface import EntityTypeEnum
import ext_funs
############################################################
# States and goals

class State():
    """A state is just a collection of variable bindings."""

    def __init__(self, name):
        self.__name__ = name


class Goal():
    """A goal is just a collection of variable bindings."""

    def __init__(self, name):
        self.__name__ = name


### print_state and print_goal are identical except for the name

def print_state(state, indent=4):
    """Print each variable in state, indented by indent spaces."""
    if state != False:
        for (name, val) in vars(state).items():
            if name != '__name__':
                for x in range(indent): sys.stdout.write(' ')
                sys.stdout.write(state.__name__ + '.' + name)
                print(' =', val)
    else:
        print('False')

def print_state_simple(state, indent=4):
    """Print each variable in state, indented by indent spaces."""
    # green htn :
    #htnConfig
    #config
    if state != False:
        for (name, val) in vars(state).items():
            if name != '__name__' and \
                    name!= 'htnConfig' and \
                    name!='weights' and\
                    name!='squadPosture' and\
                    name!='enemyDimensions' and\
                    name!='basicRanges' and\
                    name!='positions' and\
                    name!='distance_from_positions' and \
                    name !='BluePolygonCentroid' and \
                    name !='distance_positions_from_BluePolygonCentroid' and \
                    name != 'htnConfig' and \
                    name != 'config' and \
                    name !='AccuracyConfiguration' and\
                    name != 'bluePolygon':

                for x in range(indent): sys.stdout.write(' ')
                sys.stdout.write(state.__name__ + '.' + name)
                print(' =', val)
                if name== 'assesedBlues':
                    for blue in val:
                        attrs = vars(blue)
                        print(', '.join("     %s: %s" % item for item in attrs.items()))

    else:
        print('False')

def print_goal(goal, indent=4):
    """Print each variable in goal, indented by indent spaces."""
    if goal != False:
        for (name, val) in vars(goal).items():
            if name != '__name__':
                for x in range(indent): sys.stdout.write(' ')
                sys.stdout.write(goal.__name__ + '.' + name)
                print(' =', val)
    else:
        print('False')


############################################################
# Helper functions that may be useful in domain models

def forall(seq, cond):
    """True if cond(x) holds for all x in seq, otherwise False."""
    for x in seq:
        if not cond(x): return False
    return True


def find_if(cond, seq):
    """
    Return the first x in seq such that cond(x) holds, if there is one.
    Otherwise return None.
    """
    for x in seq:
        if cond(x): return x
    return None


############################################################
# Commands to tell Pyhop what the operators and methods are

operators = {}
methods = {}
original_methods={}

def declare_operators(*op_list):
    """
    Call this after defining the operators, to tell Pyhop what they are.
    op_list must be a list of functions, not strings.
    """
    operators.update({op.__name__: op for op in op_list})
    return operators


def declare_methods(task_name, *method_list):
    """
    Call this once for each task, to tell Pyhop what the methods are.
    task_name must be a string.
    method_list must be a list of functions, not strings.
    """
    methods.update({task_name: list(method_list)})
    return methods[task_name]

def declare_original_methods(task_name, *method_list):
    """
    Call this once for each task, to tell Pyhop what the methods are.
    task_name must be a string.
    method_list must be a list of functions, not strings.
    """
    original_methods.update({task_name: list(method_list)})
    return original_methods[task_name]

############################################################
# Commands to find out what the operators and methods are

def print_operators(olist=operators):
    """Print out the names of the operators"""
    print('OPERATORS:', ', '.join(olist))


def print_methods(mlist=methods):
    """Print out a table of what the methods are for each task"""
    print('{:<14}{}'.format('TASK:', 'METHODS:'))
    for task in mlist:
        print('{:<14}'.format(task) + ', '.join([f.__name__ for f in mlist[task]]))

######################### Custom helper functions ################################
def update_method_list():
    for key in methods:
        methods[key]=get_relevant_methods(key)
    #print('Methods list has been updated')

def get_relevant_methods(task):
    relevant = deepcopy(original_methods[task])
    methods_index_to_add=[]
    params_to_add=[]
    for i in range(len(relevant)):
        method=relevant[i]
        method_name=method.__name__
        params=mc.get_method_params(method_name)
        if params!= None:
            methods_index_to_add.append(i)
            params_to_add.append(params)
        else:
            params_to_add.append("NONE")
    for i in (methods_index_to_add):
        current_method=relevant[i]
        for k in range(len(params_to_add[i])):
            relevant.append([current_method,(params_to_add[i][k])])
    for k in (methods_index_to_add):
        reduce_couter=0
        for i, index in enumerate(methods_index_to_add):
            if methods_index_to_add[k]> methods_index_to_add[i]:
                reduce_couter+=1
        relevant.pop(k-reduce_couter)
    return relevant

######################### MCTS HTN PAPER ################################
class TreeNode():
    def __init__(self, name, tp, parent=None,par=None):
        self.type = tp
        self.name = name
        self.parent = parent
        self.N = 0
        self.Q = 0
        self.children = []
        self.fully_expanded = False
        self.par = par

#mcts planner
def shop_m(state, tasks,debug_level):
    #print("starting to find a plan!") - log print
    result = seek_mcts_plan(state, tasks, [], 0,debug_level)  # state, tasks, plan, depth,debug_level
    return result

# The actual planner
#Non recursive function
def seek_mcts_plan(state, tasks, plan, depth,debug_level):
    if tasks == []:
        #print("final step")
        ###print('depth {} returns plan {}'.format(depth, plan))
        return plan
    task1 = tasks[0] #current task goes to task1
    #case that current task is compound:
    if debug_level>=1:
        print("_______________________")
        print("HTN - Planning step")
        print(str(task1[0]))
    if task1[0] in methods:
        ###print('depth {} method instance {}'.format(depth, task1))
        S_c = state #local copy of state
        relevant_methods = methods[task1[0]] # return relevant method list after grouding.
        if len(relevant_methods)==1:
            index=0
        else:
            index = MCTS_HTN(S_c, tasks,relevant_methods,debug_level)
        # 2 cases- 1 case is that the next method is grounded. 2 case is that the next method is lifted.
        if len(original_methods[task1[0]])==len(relevant_methods): #grounded method case
            method = methods[task1[0]][index]
            subtasks = method(state, *task1[1:])
        elif len(original_methods[task1[0]])!=len(relevant_methods): #lifted method case
            method = relevant_methods[index] #method=[lifted method, parameter]
            par = method[1]
            subtasks = method[0](S_c,par, *task1[1:])
        ###print('depth {} new tasks: {}'.format(depth, subtasks))
        if subtasks != False:
             solution = seek_mcts_plan(state, subtasks + tasks[1:], plan, depth + 1,debug_level)
             if solution != False:
                 return solution
    #case that current task is primitive
    if task1[0] in operators:
            ###print('depth {} action {}'.format(depth, task1))
            operator = operators[task1[0]]
            newstate = operator(copy.deepcopy(state), *task1[1:])
            ###print('depth {} new state:'.format(depth))
            if debug_level>=2:
                print_state_simple(newstate)
            if newstate:
                solution = seek_mcts_plan(newstate, tasks[1:], plan + [task1], depth + 1,debug_level)
                if solution != False:
                    return solution
    print('depth {} returns failure'.format(depth))
    return False

def MCTS_HTN(initial_state, tasks,relevant_methods,debug_level):
    length2measure=len(relevant_methods)# returns real length of methods vector
    Q = [0] * length2measure
    N = [0] * length2measure
    NumSim = 40 #was 400
    ucb1_exploration_value=initial_state.config['exploration_value']
    ### initiation lines:
    print("________________________choose method index________________________")
    root_nodes = []
    for task in tasks:
        task_name = task[0]
        if task_name in methods:
            root_nodes.append(TreeNode(task[0], 'task'))
        elif task_name in operators:
            root_nodes.append(TreeNode(task[0], 'operator'))
    for i in range(NumSim):
        #print("_______new roll out_______")
        S_c = copy.deepcopy(initial_state)
        for task_ind, task in enumerate(tasks):
            task_name=task[0]
            if task_name in methods:
                [S_c, index, Q_t] = MCTS_Task(S_c, task, root_nodes[task_ind], 1, True,i,ucb1_exploration_value)
            elif task_name in operators:
                [S_c, Q_t] = MCTS_OperatorEvlt(S_c, task, root_nodes[task_ind], 1, "ROLLOUT")
            if task == tasks[0]:
                Q[index] += ( Q_t -Q[index])
                N[index] += 1
    # sort Q and N in descending order
    index = best_med(Q, N,ucb1_exploration_value)
    #DEBUG printing
    if debug_level>=1:
        print('Q - vector for methods is: ' + str(Q))
        print('N - vector for methods is: ' + str(N))
        print('Q over N - vector for methods is: ' + str(get_mean_score(Q,N)))
        print('UCB1 - vector for methods is: ' + str(get_ucb1_vector(Q,N,ucb1_exploration_value)))
        print('UCB1 exploration calue is: ' + str(ucb1_exploration_value))
        print('chosen index is: ' +str(index))
    return index

def get_mean_score(Q,N):
    mean_score_vec=[0]*len(Q)
    for k in range ( len(Q)):
        mean_score_vec[k]=Q[k]/N[k]
    return mean_score_vec

def get_UCB1(Q,N):

    return

def MCTS_Task(S_c, task, node, d, indicator,NumSim,ucb1_exploration_value):
    relevant = methods[task[0]]
    if indicator==False:
        S_c.debug_task += 1
    # if all methods in relevant have been simulated
     #default value in order to not return null
    if node.fully_expanded: #means that all the children has been visited
        index = Selection_Med(node,ucb1_exploration_value)#good
        med = relevant[index]
        newnode = node.children[index]          #good
    else:
        #choose the next method that has not been simulated:
        case=None
        for ind, method in enumerate(relevant):
            if callable(relevant[ind])==False:
                par=relevant[ind][1]
                case='lifted'
                method_name=method[0].__name__
            else:
                par=node.par #task par should be None
                case='grounded'
                method_name=method.__name__
            if is_child_simulated(node, method_name,par) == False:
                med = method
                index = ind
                break
        newnode = TreeNode(method_name, 'method', node,par)
        node.children.append(newnode)
        if len(node.children) == len(relevant):
            node.fully_expanded = True
    [S_c, Q_m] = MCTS_Method(S_c, task, med, newnode, d,NumSim,ucb1_exploration_value) # Exactly according to the paper
    #newnode.Q+=Q_m #add
    #node.children[index].Q += Q_m - reduced line
    node.N += 1
    node.Q = avg_q(node)
    return S_c, index, node.children[index].Q

def MCTS_Method(S_c, task, med, node,d,NumSIm,ucb1_exploration_value):
    S_c.debug_method+=1
    par=node.par #parameter of parent node
    d_max = 30  # maximum depth - arbitrary number
    if d > (d_max):
        return S_c, node.Q   # 0 = arbitrary return
    try:
        subtasks = med(S_c, *task[1:])
    except:
        subtasks = med[0](S_c,par, *task[1:])
    if not subtasks:
        if subtasks == []: #final state in target
            node.Q = 10
        else:
            node.Q = 0
        node.N += 1
        return S_c, node.Q
    for subtask in subtasks:
        if subtask[0] in methods:
            # if subtask has been simulated then:
            if is_child_simulated(node, subtask[0],par=None):
                node_ind = next_child(node, subtask[0],par=None)
                newnode = node.children[node_ind-1] #value fixed to be node_ind-1
            else:
                newnode = TreeNode(subtask[0], 'task', node)  # first arg subtask? # task to subtask
                node.children.append(newnode)
            [S_c, index, Q_o] = MCTS_Task(S_c, subtask, newnode, d + 1, False,NumSIm,ucb1_exploration_value)  # inserted subtask instead of task
            #node.children[-1].Q += Q_o ###reduced line
        elif subtask[0] in operators:
            # if subtask has been simulated then:
            if is_child_simulated(node, subtask[0],par=None):
                node_ind = next_child(node, subtask[0],par=None)
                newnode = node.children[node_ind-1]
            else:
                newnode = TreeNode(subtask[0], 'operator', node)  # first arg subtask? # task to subtask
                node.children.append(newnode)
            [S_c, Q_t] = MCTS_OperatorEvlt(S_c, subtask, newnode, d + 1, 'method')  # inserted subtask instead of task
            node.children[-1].Q += Q_t # last child recive Q
    node.N += 1
    node.Q = avg_q(node)

    return S_c, node.Q

def MCTS_OperatorEvlt(S_c, subtask, node, d, sender):
    if sender=="ROLLOUT":
        S_c.debug_ope+=1
    operator = operators[subtask[0]]
    S_c = operator(copy.deepcopy(S_c), *subtask[1:])
    Q_o = calValue(S_c,subtask)
    return S_c, Q_o

def calValue(state,subtask):
    ret_val = 0
    if subtask[0]=='choose_position_op':

        "value relative to distance to position"
        if state.distance_from_positions[subtask[1]] == min(state.distance_from_positions): #suppose catch when both zero or equal
            relation=1
        else:
             if min(state.distance_from_positions)<0.001:
                 minDistanceFromPositions = 0.001
             else:
                 minDistanceFromPositions = min(state.distance_from_positions)
             relation=((state.distance_from_positions[subtask[1]])/minDistanceFromPositions)

        val_squad_to_Position= 100/relation

        "value relative to distance to BluePolygon center"
        if state.weights['choose_position_op_dist_from_polygon']>=0:
            relation = ((state.distance_positions_from_BluePolygonCentroid[subtask[1]]) / max(state.distance_positions_from_BluePolygonCentroid))
            val_squad_to_PolygonCenter = 100*relation
        elif state.weights['choose_position_op_dist_from_polygon']<0:
            relation = ((state.distance_positions_from_BluePolygonCentroid[subtask[1]]) / min(state.distance_positions_from_BluePolygonCentroid))
            val_squad_to_PolygonCenter=100/relation

        "value relative to distance to BluePolygon center"
        relation = ((state.position_exposure_level[subtask[1]]) / max(state.position_exposure_level))
        val_percent_exposure_polygon = 100 * relation

        ret_val=state.weights['choose_position_op_dist_from_position']*val_squad_to_Position +\
                abs(state.weights['choose_position_op_dist_from_polygon'])*val_squad_to_PolygonCenter+\
                state.weights['choose_position_op_percent_exposure']*val_percent_exposure_polygon
        ret_val=state.weights['choose_position_op']*ret_val

        # print('position is: ' +str(subtask[1]) + ', operator name is:' + str(
        #     subtask[0]) + ", retval is: " + str(ret_val))

    elif subtask[0]=='scan_for_enemy_and_assess_exposure_op':
        "Value relative to scanning"
        "value of unit of evaluation"
        "supports only in Eitan , Ohez, SUECIDE_DRONE and UNknown"
        Eitan_number=0
        Ohez_number=0
        for enemy in state.assesedBlues:
            if enemy.classification == EntityTypeEnum.EITAN:
                Eitan_number+=1
            elif (enemy.classification == EntityTypeEnum.OHEZ) or \
                 (enemy.classification == EntityTypeEnum.SUICIDE_DRONE) or\
                 (enemy.classification==EntityTypeEnum.UNKNOWN):
                Ohez_number+=1
        sum=(state.weights['ohez_val'])*Ohez_number+(state.weights['eitan_val'])*Eitan_number
        x=100/sum #value for each evaluation unit

        #evaluation:
        ret_val_scan=0
        for enemy in state.assesedBlues:
            if (enemy.observed == True) and (enemy.is_alive==True): #value only for alive observed entites of blue
                if enemy.classification==EntityTypeEnum.EITAN:
                    ret_val_scan += x * (state.weights['eitan_val'])
                elif (enemy.classification == EntityTypeEnum.OHEZ) or \
                     (enemy.classification == EntityTypeEnum.SUICIDE_DRONE) or \
                     (enemy.classification==EntityTypeEnum.UNKNOWN):
                    ret_val_scan += x * (state.weights['ohez_val'])
        ret_val_scan=state.weights['scan_for_enemy_op']*ret_val_scan
        # print('position is: ' + str(state.currentPositionIndex) + ', operator name is: scan'  + ", retval is: " + str(ret_val_scan))
        "Value relative to Exposure"
        state_copy=deepcopy(state)
        knownEnemies, totalAccuracy, accuracyVec = ext_funs.getAccumulatedHitProbability(state_copy,state_copy.AccuracyConfiguration)
        if knownEnemies > 0:
            totalprobability = 1
            for accuracy in accuracyVec:
                totalprobability = totalprobability * (1 - accuracy)
            probabilityToGetHit = (1 - totalprobability)
            ret_val_exposure=state.weights['locate_at_position_op']*100*(1-probabilityToGetHit)
            #OLD-ret_val=state.weights['locate_at_position_op']*(100/knownEnemies)*(knownEnemies-totalAccuracy)

            "If we dont know any of the enemies location we return exposure scan 100"
        elif knownEnemies==0:
            ret_val_exposure = state.weights['locate_at_position_op']*100 #means that Agent dont know about any enemies
        # print('position is: ' + str(state.currentPositionIndex) + ', operator name is: exposure' + ", retval is: " + str(
        #     ret_val_exposure))
        ret_val=ret_val_scan+ret_val_exposure
        # print('position is: ' + str(state.currentPositionIndex) + ', operator name is:' + str(
        #     subtask[0]) + ", retval is: " + str(ret_val))
    elif subtask[0] == 'shoot_op':
        flag=0
        enemy=state.aim_list[0]
        blueDistance=ext_funs.calculate_blue_distance(state.loc,enemy)
        if blueDistance == None:
             blueDistance = ext_funs.getMetriDistance(state.loc, state.BluePolygonCentroid)
             flag=1
        if enemy.classification==EntityTypeEnum.EITAN:
             shooterClassification="LONG_RANGE_ANTI_TANK"
             ratio=1
        elif (enemy.classification == EntityTypeEnum.OHEZ) or \
             (enemy.classification == EntityTypeEnum.SUICIDE_DRONE) or \
             (enemy.classification == EntityTypeEnum.UNKNOWN):
             shooterClassification = "SOLDIER"
             ratio=(state.weights['ohez_val'])/(state.weights['ohez_val']+state.weights['eitan_val'])
        maxRange = float(state.AccuracyConfiguration.at[str(shooterClassification), 'MAX_RANGE'])
        accuracy = ext_funs.getAccuracy(state.AccuracyConfiguration, blueDistance, maxRange, shooterClassification)
        ret_val = state.weights['shoot_enemy_op']*100*accuracy*ratio
        if flag ==1:
             ret_val=0.00001
        # print("position is: " + str(state.currentPositionIndex) + " " + "operator is " + str(
        #     subtask[0]) + " " + "blueDistance is: " + str(blueDistance) + "score is: " + str(ret_val), " accuracy is: "+ str(accuracy), " maxRange is: "+ str(maxRange))
        # print('position is: ' + str(state.currentPositionIndex) + ', operator name is:' + str(
        #     subtask[0]) + ", retval is: " + str(ret_val))
    elif subtask[0]=='e_continue_as_usual_op':
        ret_val=70
    elif subtask[0]=='e_move_to_closest_cover_op':
        ret_val=np.random.normal(35,1)
    elif subtask[0] == 'e_wait_in_cover_op':
        ret_val=np.random.normal(40,1)
    elif subtask[0] == 'e_shoot_op':
        ret_val=np.random.normal(5,10)
    elif subtask[0] == 'e_wait_in_position_op':
        ret_val=100
    if ret_val==0:
        ret_val=0.00001
    if ret_val>100:
        ret_val=100
    return ret_val

def avg_q(node):
    # average Q of children
    Q_children = 0
    number_of_different_futures=0
    for child in node.children:
        Q_children += child.Q
        if child.type=='method':
            number_of_different_futures+=1
    if number_of_different_futures==0:
        number_of_different_futures=1
    try:
        return Q_children#/len(node.children)  # devision by 0
    except: #not in use
        return 0

def is_child_simulated(node, child_name,par):
    is_simulated = False
    for child in node.children:
        if child.name == child_name and child.par==par:
            is_simulated = True
            return is_simulated
    return is_simulated


def next_child(node, child_name,par):
    for ind, child in enumerate(node.children):
        if child.name == child_name and child.par == par:
            return_value = ind + 1
            if return_value> len(node.children):
                return_value=-1 # Error value - not in use
            return return_value
    return False


# selection_med function:
# input = node. output= index of children node of input node with maximum  Q_c (according to UCB1) - edited
def Selection_Med(node,ucb1_exploration_value):
    c = ucb1_exploration_value # exploration value
    children = node.children
    Q_c = []
    for child in children:
        try:
            q = child.Q/child.N + c*math.sqrt(math.log(node.N) / child.N)
        except:  # case of division by 0
            q = 0
        Q_c.append(q)
    index = Q_c.index(max(Q_c))
    return index

def best_med(Q, N,ucb1_exploration_value):
    c = ucb1_exploration_value # exploration value
    Q_c = []
    for k in range(len(Q)):
        try:
            q = Q[k]/N[k] + c*math.sqrt(math.log(sum(N)) / N[k])
        except:
            q = 0
        # q = child.Q/child.N + c*math.sqrt(math.log(node.N) / child.N)
        Q_c.append(q)
    index = Q_c.index(max(Q_c))
    return index

def get_ucb1_vector(Q, N,ucb1_exploration_value):
    c = ucb1_exploration_value  # exploration value
    Q_c = []
    for k in range(len(Q)):
        try:
            q = Q[k] / N[k] + c * math.sqrt(math.log(sum(N)) / N[k])
        except:
            q = 0
        # q = child.Q/child.N + c*math.sqrt(math.log(node.N) / child.N)
        Q_c.append(q)
    return Q_c