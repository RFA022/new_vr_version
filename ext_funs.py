import copy

import numpy as np
import csv
import math
from CommunicatorInterface import EntityTypeEnum
from Communicator import *
from EntityCurrentState import  *
import utm

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

def update_distance_from_positions(loc,list):
    '''
    function that returns list of distances from one location to multiple locations
    '''
    list_of_distances=[]
    for i in range(len(list)):
        dist=getMetriDistance(loc,list[i])
        list_of_distances.append(dist)
    return list_of_distances

def update_distance_from_blues(loc,enemies):
    '''
        function that returns list of distances from one location to multiple blues locations
    '''
    list_of_distances=[]
    for enemy in enemies:
        if (enemy.location['latitude'] == None and
                enemy.location['longitude'] == None and
                enemy.location['altitude'] == None):
            dist=None
        else:
            dist=getMetriDistance(loc,enemy.location)
        list_of_distances.append(dist)
    return list_of_distances

#helper functions
def simple_getLocation(state,index):
    return [state.positions[index][0],state.positions[index][1]]

def getLocation(state,index):
    #float casting of location because altitude somehow automated casted to be str
    loc={'latitude':(state.positions[index]['latitude']),
         'longitude':(state.positions[index]['longitude']),
         'altitude':(state.positions[index]['altitude'])}
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

#creates HTN entity list using HTNentity class
def getBluesDataFromVRFtoHTN(blueList):
    entities=[]
    for entity in blueList:
        val=0
        if entity.classification==EntityTypeEnum.EITAN:
            val=1
        Newentity=HTNentity(entity.unit_name)
        Newentity.classification=entity.classification
        Newentity.location=entity.last_seen_worldLocation
        Newentity.is_alive = entity.is_alive
        Newentity.val=val
        entities.append(Newentity)
    return entities

#los Operator for 1 entity and 1 location to be used from HTN and ScenarioManager as well
def losOperator(squadPosture,enemyDimensions,enemy,source_location):
    communicator = CommunicatorSingleton().obj
    source=copy.deepcopy(source_location)
    source['altitude'] = str(float(source['altitude']) +float(squadPosture['standing_height']))
    target = enemy.location
    if enemy.classification == EntityTypeEnum.EITAN:
        target['altitude'] += enemyDimensions['eitan_cg_height']
    losRespose = (communicator.GetGeoQuery([source], [target], True, True))
    return losRespose

def getNumberofAliveEnemies(blues):
    aliveBluesNumber=0
    for blue in blues:
        if blue.is_alive==True:
            aliveBluesNumber+=1
    return aliveBluesNumber

def getPolygonCentroid(polygon) -> float:
        list=[]
        for vertex in  polygon:
            list.append (utm.from_latlon(vertex['latitude'],vertex['longitude']))
        Cx=0
        Cy=0
        A=0
        alt=0
        list.append(list[0])
        for k in reversed(range(len(list)-1)):
            Cx+= (list[k][0]+list[k+1][0])*(list[k][0]*list[k+1][1] - list[k+1][0]*list[k][1])
            Cy+= (list[k][1]+list[k+1][1])*(list[k][0]*list[k+1][1] - list[k+1][0]*list[k][1])
            A+=  (list[k][0]*list[k+1][1] -list[k+1][0]*list[k][1])

        for vertex in polygon:
            alt+=vertex['altitude']/len(polygon)
        A=A/2
        Cx=Cx/(6*A)
        Cy=Cy/(6*A)
        centroidLatLong=utm.to_latlon(Cx, Cy, list[0][2],str(list[0][3]))

        centroid={
           'latitude': centroidLatLong[0],
            'longitude': centroidLatLong[1],
            'altitude':alt
        }
        return centroid