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
                    name!='AccuracyConfiguration':

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
    relevant = deepcopy(methods[task])
    methods_index_to_add=[]
    params_to_add=[]
    for i in range(len(relevant)):
        method=relevant[i]
        method_name=method.__name__
        params=mc.get_method_params(method_name)
        if params!= None:
            methods_index_to_add.append(i)
            params_to_add.append(params)
    for i in (methods_index_to_add):
        current_method=relevant[i]
        relevant.pop(i)
        for k in range(len(params_to_add[i])):
            relevant.append([current_method,(params_to_add[i][k])])
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
def shop_m(state, tasks):
    #print("starting to find a plan!") - log print
    result = seek_mcts_plan(state, tasks, [], 0)  # state, tasks, plan, depth
    return result

# The actual planner
#Non recursive function
def seek_mcts_plan(state, tasks, plan, depth):
    if tasks == []:
        #print("final step")
        ###print('depth {} returns plan {}'.format(depth, plan))
        return plan
    task1 = tasks[0] #current task goes to task1
    #case that current task is compound:
    print("_______________________")
    print("Planning step")
    print(str(task1[0]))
    if task1[0] in methods:
        ###print('depth {} method instance {}'.format(depth, task1))
        S_c = state #local copy of state
        relevant_methods = methods[task1[0]] # return relevant method list after grouding.
        if len(relevant_methods)==1:
            index=0
        else:
            index = MCTS_HTN(S_c, tasks,relevant_methods)
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
             solution = seek_mcts_plan(state, subtasks + tasks[1:], plan, depth + 1)
             if solution != False:
                 return solution
    #case that current task is primitive
    if task1[0] in operators:
            ###print('depth {} action {}'.format(depth, task1))
            operator = operators[task1[0]]
            newstate = operator(copy.deepcopy(state), *task1[1:])
            ###print('depth {} new state:'.format(depth))
            #print_state_simple(newstate)
            if newstate:
                solution = seek_mcts_plan(newstate, tasks[1:], plan + [task1], depth + 1)
                if solution != False:
                    return solution
    print('depth {} returns failure'.format(depth))
    return False

def MCTS_HTN(initial_state, tasks,relevant_methods):
    length2measure=len(relevant_methods)# returns real length of methods vector
    Q = [0] * length2measure
    N = [0] * length2measure
    NumSim = 400 #was 400
    ### initiation lines:
    root_nodes = []
    for task in tasks:
        task_name = task[0]
        if task_name in methods:
            root_nodes.append(TreeNode(task[0], 'task'))
        elif task_name in operators:
            root_nodes.append(TreeNode(task[0], 'operator'))
    for i in range(NumSim):
        S_c = initial_state
        for task_ind, task in enumerate(tasks):
            task_name=task[0]
            if task_name in methods:
                [S_c, index, Q_t] = MCTS_Task(S_c, task, root_nodes[task_ind], 1, True,i)
            elif task_name in operators:
                [S_c, Q_t] = MCTS_OperatorEvlt(S_c, task, root_nodes[task_ind], 1, "ROLLOUT")
            if task == tasks[0]:
                Q[index] += Q_t
                N[index] += 1
    # sort Q and N in descending order
    index = best_med(Q, N)
    print(Q)
    print(N)
    print(index)
    return index

def MCTS_Task(S_c, task, node, d, indicator,NumSim):
    relevant = methods[task[0]]
    if indicator==False:
        S_c.debug_task += 1
    # if all methods in relevant have been simulated
     #default value in order to not return null
    if node.fully_expanded: #means that all the children has been visited
        index = Selection_Med(node)             #good
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
    [S_c, Q_m] = MCTS_Method(S_c, task, med, newnode, d,NumSim) # Exactly according to the paper
    #newnode.Q+=Q_m #add
    node.children[index].Q += Q_m
    node.N += 1
    node.Q = avg_q(node)
    return S_c, index, node.Q

def MCTS_Method(S_c, task, med, node,d,NumSIm):
    S_c.debug_method+=1
    par=node.par #parameter of parent node
    d_max = 100  # maximum depth - arbitrary number
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
            [S_c, index, Q_o] = MCTS_Task(S_c, subtask, newnode, d + 1, False,NumSIm)  # inserted subtask instead of task
            node.children[-1].Q += Q_o
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
    if subtask[0]=='choose_position_op':
        ret_val=0
        val_squad_to_PolygonCenter=0
        val_squad_to_Position=0
        percent_exposure_polygon=0
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
        relation = ((state.distance_positions_from_BluePolygonCentroid[subtask[1]]) / max(state.distance_positions_from_BluePolygonCentroid))
        val_squad_to_PolygonCenter = 100*relation

        ret_val=state.weights['choose_position_op_dist_from_position']*val_squad_to_Position +\
                state.weights['choose_position_op_dist_from_polygon']*val_squad_to_PolygonCenter+\
                state.weights['choose_position_op_percent_exposure']*percent_exposure_polygon
        ret_val=state.weights['choose_position_op']*ret_val

        # print("choose_position_op")
        # try:
        #     # print("POSITION NUMBER IS: " + str(state.positions.index(state.loc)) + "ret value is: " + str(ret_val))
        # except:
            # print("POSITION NUMBER IS Unknown: " + "ret value is: " + str(ret_val))

    elif subtask[0]=='scan_for_enemy_op':
        #-value of unit of evaluation-#
        #-supports only in Eitan , Ohez, SUECIDE_DRONE and UNknown-#
        Eitan_number=0
        Ohez_number=0
        for enemy in state.assesedBlues:
            if enemy.classification == EntityTypeEnum.EITAN:
                Eitan_number+=1
            elif (enemy.classification == EntityTypeEnum.OHEZ) or \
                 (enemy.classification == EntityTypeEnum.SUICIDE_DRONE) or\
                 (enemy.classification==EntityTypeEnum.UNKNOWN):
                Ohez_number+=1
        sum=2*Ohez_number+7*Eitan_number
        x=100/sum #value for each evaluation unit
        #evaluation:
        ret_val=0
        for enemy in state.assesedBlues:
            if (enemy.observed == True) and (enemy.is_alive==True): #value only for alive observed entites of blue
                if enemy.classification==EntityTypeEnum.EITAN:
                    ret_val += x * 7
                elif (enemy.classification == EntityTypeEnum.OHEZ) or \
                     (enemy.classification == EntityTypeEnum.SUICIDE_DRONE) or \
                     (enemy.classification==EntityTypeEnum.UNKNOWN):
                    ret_val += x * 2
        ret_val=state.weights['scan_for_enemy_op']*ret_val

        # print("scan_for_enemy_op")
        # print("POSITION NUMBER IS: " + str(state.positions.index(state.loc)) + "ret value is: " + str(ret_val))

    elif subtask[0] == 'locate_at_position_op':
        totalAccuracy=0
        knownEnemies = 0
        for k, enemy in enumerate(state.assesedBlues):
            if enemy.is_alive==True:
                classification=enemy.classification.name
                maxRange=float(state.AccuracyConfiguration.at[str(classification), 'MAX_RANGE'])
                blueDistance=state.distance_from_assesedBlues[k]
                rangeString=None
                if blueDistance!= None:

                    if blueDistance<=50:
                        rangeString="TO_50"
                    elif blueDistance>50 and blueDistance<=100:
                        rangeString = "TO_100"
                    elif blueDistance > 100 and blueDistance <=500:
                        rangeString = "TO_500"
                    elif blueDistance > 500:
                        rangeString = "TO_MAX_RANGE"
                    if blueDistance > maxRange:
                        rangeString= "AFTER_MAX_RANGE"
                    blueAccuracy=float(state.AccuracyConfiguration.at[str(classification), str(rangeString)])
                    # print(str(rangeString))
                    # print(str(classification))
                    # print(blueAccuracy)
                    # print("POSITION NUMBER IS: " + str(state.positions.index(state.loc)))
                    # print("-----")
                    totalAccuracy+=blueAccuracy
                    knownEnemies += 1
        # print(totalAccuracy)
        # print(knownEnemies)
        ret_val=state.weights['locate_at_position_op']*(100/knownEnemies)*(knownEnemies-totalAccuracy)

        # print("locate_at_position_op")
        # print("POSITION NUMBER IS: " + str(state.positions.index(state.loc))+ "ret calue is: " + str(ret_val))


        # print(totalAccuracy)
        # print("SCORE IS:" + str(ret_val))
        # print("----------")
    else:
        ret_val=0.00001 #active operators return non zero value
    if ret_val==0:
        ret_val=0.00001
    return ret_val


def avg_q(node):
    # average Q of children
    Q_children = 0
    for child in node.children:
        Q_children += child.Q
    try:
        return Q_children/len(node.children)  # devision by 0
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
# input = node. output= index of children node of input node with maximum  Q_c (according to UCB1)
def Selection_Med(node):
    c = 2
    children = node.children
    Q_c = []
    for child in children:
        try:
            q = child.Q + c*math.sqrt(math.log(node.N) / child.N)
        except:  # case of division by 0
            q = 0
        Q_c.append(q)
    index = Q_c.index(max(Q_c))
    return index

def best_med(Q, N):
    c = 2
    Q_c = []
    for k in range(len(Q)):
        try:
            q = Q[k] + c*math.sqrt(math.log(sum(N)) / N[k])
        except:
            q = 0
        # q = child.Q/child.N + c*math.sqrt(math.log(node.N) / child.N)
        Q_c.append(q)
    index = Q_c.index(max(Q_c))
    return index