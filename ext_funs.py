import numpy as np
import csv
import math
from CommunicatorInterface import EntityTypeEnum
from Communicator import *
from EntityCurrentState import  *


def comm():
    if 'communicator' not in globals():
        communicator=Communicator()
        return communicator

def simple_update_distance_from_positions(state):
    '''
    function that update Aget distance from each operational position
    '''
    list_of_distances=[]
    for i in range(len(state.positions)):
        dist_x_sq = (abs(state.loc[0]-state.positions[i][0]))**2
        dist_y_sq = (abs(state.loc[1]-state.positions[i][1]))**2
        dist = np.sqrt(dist_x_sq+dist_y_sq)
        list_of_distances.append(dist)
    return list_of_distances

def update_distance_from_positions(state):
    '''
    function that update Aget distance from each operational position
    '''
    list_of_distances=[]
    for i in range(len(state.positions)):
        dist=getMetriDistance(state.loc,state.positions[i])
        list_of_distances.append(dist)
    return list_of_distances

#helper functions
def simple_getLocation(state,index):
    return [state.positions[index][0],state.positions[index][1]]

def getLocation(state,index):
    #float casting of location because altitude somehow automated casted to be str
    loc={'latitude':float(state.positions[index]['latitude']),'longitude':float(state.positions[index]['longitude']),'altitude':float(state.positions[index]['altitude'])}
    return loc

def getMetriDistance(loc1,loc2):
    R = 6371000 # Eart Radius - m
    dLat = (math.radians(float(loc1['latitude'])) - math.radians(float(loc2['latitude'])))
    dLon = (math.radians(float(loc1['longitude'])) - math.radians(float(loc2['longitude'])))

    a = math.sin(dLat / 2) * math.sin(dLat / 2)+ \
        math.cos(math.radians(float(loc1['latitude'])))*math.cos(math.radians(float(loc2['latitude'])))* \
        math.sin(dLon / 2) * math.sin(dLon / 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    return d

def get_positions_fromCSV(filename):
     with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        header = next(csv_reader)
        locations= []
        for row in csv_reader:
            loaction = {
                "latitude": row[6],
                "longitude": row[7],
                "altitude": row[8]
            }

            locations.append(loaction)
        return locations

def getBluesDataFromCSV(filename):
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        header = next(csv_reader)
        entities = []
        for row in csv_reader:
            entity={'name':row[1],
                    'classification':row[0],
                    'location': {"latitude": None,"longitude":None,"altitude": None},
                    'observed':False
                    }
            entities.append(entity)
        return entities

def getBluesDataFromVRFtoHTN(blueList):
    entities=[]
    for entity in blueList:
        val=0
        if entity.classification==EntityTypeEnum.EITAN:
            val=1
        entit=HTNentity(entity.unit_name)

        HTNentitya = {'name': entity.unit_name,
                  'classification': entity.classification,
                  'location': entity.last_seen_worldLocation,
                  'observed': False,
                  'is_alive': entity.is_alive,
                  'val': val
                  }
        entities.append(HTNentitya)
    return entities

#los Operator for 1 entity and 1 location to be used from HTN and ScenarioManager as well
def losOperator(squadPosture,enemyDimensions,enemy,source_location):
    communicator = CommunicatorSingleton().obj
    source_location['altitude'] += squadPosture['crouching_height']
    target = enemy.location
    if enemy.classification == EntityTypeEnum.EITAN:
        target['altitude'] += enemyDimensions['eitan_cg_height']
    losRespose = (communicator.GetGeoQuery([source_location], [target], True, True))
    return losRespose
