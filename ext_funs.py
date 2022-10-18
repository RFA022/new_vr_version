import copy
import random

import numpy as np
import csv
import math
from CommunicatorInterface import EntityTypeEnum
from Communicator import *
from EntityCurrentState import  *
import utm
import shapely
from shapely.geometry import Point
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
        dist=calculate_blue_distance(loc,enemy)
        list_of_distances.append(dist)
    return list_of_distances

def calculate_blue_distance(loc,enemy):
    if (enemy.location['latitude'] == None and
            enemy.location['longitude'] == None and
            enemy.location['altitude'] == None):
        dist = None
    else:
        dist = getMetriDistance(loc, enemy.location)
    return dist
#helper functions
def simple_getLocation(state,index):
    return [state.positions[index][0],state.positions[index][1]]

#HTN function only
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
    d_flat = R * c
    d_alt=abs(float(loc2['altitude'])-float(loc1['altitude']))
    d=math.sqrt(d_flat**2+ d_alt**2)
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
                "altitude": row[8],
                "id":row[5],
                "exposure":row[9]
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
        Newentity.velocity = entity.last_seen_velocity
        Newentity.is_alive = entity.is_alive
        Newentity.val=val
        Newentity.observed=entity.observed
        entities.append(Newentity)
        if Newentity.location['latitude'] == None and \
           Newentity.location['longitude'] == None and \
           Newentity.location['altitude'] == None:
                Newentity.locationType=HTNbluLocationType.fake
        else:
                Newentity.locationType = HTNbluLocationType.real
    return entities

#los Operator for 1 entity and 1 location to be used from HTN and ScenarioManager as well
def losOperator(squadPosture,enemyDimensions,enemy,source_location):
    communicator = CommunicatorSingleton().obj
    source=copy.deepcopy(source_location)
    source['altitude'] = str(float(source['altitude']) +float(squadPosture['standing_height']))
    target = copy.deepcopy(enemy.location)
    if enemy.classification == EntityTypeEnum.EITAN:
        target['altitude'] += enemyDimensions['eitan_cg_height']
    losRespose = (communicator.GetGeoQuery([source], [target], True, True))
    return losRespose

#los Operator for 1 source location to vector of destinations
def losOperatorlist (squadPosture,enemyDimensions,enemy_vector,source_location):
    communicator = CommunicatorSingleton().obj
    source=copy.deepcopy(source_location)
    source['altitude'] = str(float(source['altitude']) +float(squadPosture['standing_height']))
    enemies_location_list=[]
    for enemy in (enemy_vector):
        destination=copy.deepcopy(enemy.location)
        if enemy.classification == EntityTypeEnum.EITAN:
            destination['altitude'] += enemyDimensions['eitan_cg_height']
        enemies_location_list.append(destination)
    losRespose = (communicator.GetGeoQuery([source], enemies_location_list, True, True))
    return losRespose


def getNumberofAliveEnemies(blues):
    aliveBluesNumber=0
    for blue in blues:
        if blue.is_alive==True:
            aliveBluesNumber+=1
    return aliveBluesNumber
def generatePointInPolygon(polygon):
    communicator = CommunicatorSingleton().obj
    polygonUTM = []
    polygonUTM_neto = []
    for vertex in polygon:
        polygonUTM.append(utm.from_latlon(vertex['latitude'], vertex['longitude']))
    for i,vertex in enumerate(polygonUTM):
        polygonUTM_neto.append([vertex[0],vertex[1]])
    shapelyPolygonUTM=shapely.geometry.Polygon(polygonUTM_neto)
    minx, miny, maxx, maxy = shapelyPolygonUTM.bounds
    successBool=0
    while successBool==0:
        pnt = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
        if shapelyPolygonUTM.contains(pnt):
            successBool=1
            pnt=utm.to_latlon(pnt.x, pnt.y, polygonUTM[0][2],str(polygonUTM[0][3]))
            pnt = {
                'latitude': pnt[0],
                'longitude': pnt[1],
                'altitude': communicator.getHeightAboveSeaLevel(pnt[0],pnt[1])
            }
    return pnt
def is_inside_polygon(pnt,polygon):
    pntUTM =utm.from_latlon(pnt['latitude'], pnt['longitude'])
    pntUTM_neto=Point([pntUTM[0],pntUTM[1]])
    polygonUTM = []
    polygonUTM_neto = []
    for vertex in polygon:
        polygonUTM.append(utm.from_latlon(vertex['latitude'], vertex['longitude']))
    for i,vertex in enumerate(polygonUTM):
        polygonUTM_neto.append([vertex[0],vertex[1]])
    shapelyPolygonUTM=shapely.geometry.Polygon(polygonUTM_neto)
    if shapelyPolygonUTM.contains(pntUTM_neto):
        return True
    return False
def getPolygonCentroid(polygon) -> float:
        communicator = CommunicatorSingleton().obj
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
        A=A/2
        Cx=Cx/(6*A)
        Cy=Cy/(6*A)
        centroidLatLong=utm.to_latlon(Cx, Cy, list[0][2],str(list[0][3]))
        alt= communicator.getHeightAboveSeaLevel(centroidLatLong[0],centroidLatLong[1])
        centroid={
           'latitude': centroidLatLong[0],
            'longitude': centroidLatLong[1],
            'altitude':alt
        }
        return centroid

"HTN FUNCTION ONLY"
def getAccumulatedHitProbability(state,AccuracyConfiguration):
    totalAccuracy = 0
    knownEnemies = 0
    accuracyVec=[]
    for k, enemy in enumerate(state.assesedBlues):
        if enemy.is_alive == True and enemy.observed == True:
            classification = enemy.classification.name
            maxRange = float(state.AccuracyConfiguration.at[str(classification), 'MAX_RANGE'])
            blueDistance = state.distance_from_assesedBlues[k]
            if blueDistance==None: #Ignore None Distance
                #if enemy has been observed statistically we assume its in the middle of the polygon
                blueDistance=getMetriDistance(state.loc, state.BluePolygonCentroid)
            else:
                blueAccuracy = getAccuracy(AccuracyConfiguration,blueDistance,maxRange,classification)
                totalAccuracy += blueAccuracy
                knownEnemies += 1
                accuracyVec.append(blueAccuracy)
    return (knownEnemies,totalAccuracy,accuracyVec)

"HTN FUNCTION ONLY"
def getAccuracy(AccuracyConfiguration,distance,maxRange,classification):
    rangeString = None
    if distance <= 15:
        rangeString = "TO_15"
    elif distance>15 and distance <= 50:
        rangeString = "TO_50"
    elif distance > 50 and distance <= 100:
        rangeString = "TO_100"
    elif distance > 100 and distance <= 300:
        rangeString = "TO_300"
    elif distance > 300 and distance <= 500:
        rangeString = "TO_500"
    elif distance > 500 and distance <= 550:
        rangeString = "TO_550"
    elif distance > 550:
        rangeString = "TO_MAX_RANGE"
    if distance > maxRange:
        rangeString = "AFTER_MAX_RANGE"
    #Debug
    #print("classification is: " + str(classification) + ". disntace is: " + str(distance)+ ". str is: " + str(rangeString) +". accuracy is:" + str(float(state.AccuracyConfiguration.at[str(classification), str(rangeString)])))
    return float(AccuracyConfiguration.at[str(classification), str(rangeString)])

def checkIfWorldViewChangedEnough(enemy,current_entity,basicRanges,config):
    if ((enemy.classification == EntityTypeEnum.OHEZ) or \
            (enemy.classification == EntityTypeEnum.SUICIDE_DRONE) or \
            (enemy.classification == EntityTypeEnum.UNKNOWN)) and enemy.is_alive==True:
        enemyDistance = calculate_blue_distance(current_entity.current_location, enemy)
        #print(enemyDistance)
        "case drone is too close:"
        if enemyDistance!=None and enemyDistance<basicRanges['ak47_range']:
            logging.debug("Drone type enemy has been Detected in an emergency situation:" + str(enemy.unit_name) + " " + str(enemy.is_alive))
            return True
        "case: changed direction:"
        frozen_enemy = next(x for x in current_entity.HTNbluesFrozen if x.unit_name == enemy.unit_name)
        #print("velocity is" + str(frozen_enemy.velocity))
        frozen_enemy_velocity_norm=0
        enemy_velocity_norm=0
        if (frozen_enemy.velocity['east']!=None) and \
           (frozen_enemy.velocity['north'] != None) and \
           (frozen_enemy.velocity['up'] != None):
                frozen_enemy_velocity_norm = math.sqrt(
                    frozen_enemy.velocity['east'] ** 2 + frozen_enemy.velocity['north'] ** 2)
        if enemy.velocity['east'] != None and \
           enemy.velocity['north'] != None and \
           enemy.velocity['up'] != None:
                enemy_velocity_norm = math.sqrt(
                    enemy.velocity['east'] ** 2 + enemy.velocity['north'] ** 2)

        if frozen_enemy_velocity_norm!=0 and enemy_velocity_norm!=0:
            frozen_enemy_unit_vector_velocity = {
                "east": frozen_enemy.velocity["east"] / frozen_enemy_velocity_norm,
                "north": frozen_enemy.velocity["north"] / frozen_enemy_velocity_norm
            }
            enemy_unit_vector_velocity={
                "east": enemy.velocity["east"]/enemy_velocity_norm,
                "north":enemy.velocity["north"]/enemy_velocity_norm
            }
            scalar_multiplication = enemy_unit_vector_velocity['east'] * frozen_enemy_unit_vector_velocity[
                'east'] + \
                                    enemy_unit_vector_velocity['north'] * frozen_enemy_unit_vector_velocity[
                                        'north']
            #print("scalar multi= " +str(scalar_multiplication))
        # diff_angle=math.acos(scalar_multiplication)
        # print(diff_angle)
    if (enemy.classification == EntityTypeEnum.EITAN) and enemy.is_alive==True:
        frozen_enemy = next(x for x in current_entity.HTNbluesFrozen if x.unit_name == enemy.unit_name)
        if calculate_blue_distance(current_entity.current_location, frozen_enemy) == None:
            if calculate_blue_distance(current_entity.current_location, enemy) != None:
                logging.debug("New Armored vehicle type enemy has been detected: " + str(enemy.unit_name))
                return True
        else:
            distanceDifference = getMetriDistance(enemy.location, frozen_enemy.location)
            if distanceDifference > config['rePlan_range']:
                logging.debug(
                    "Significant change in world view has been observed by the squad: " + str(enemy.unit_name))
                return True
    return False

def readIntervisibilityCSV():
    intervisibility=open('Resources/PolygonsIntervisebility.csv')
    intervisibility_config=csv.reader(intervisibility)
    intervisibility_polygoins=[]
    header = next(intervisibility_config)

    for k,row in enumerate(intervisibility_config):
        print(k)
        i=0
        instance={"name":[], "polygon":[]}
        instance['name'] = str("cover")+ str("_")+str(k)
        while 1:
            if i>0:
                seperate_string=str(row[i]).split(",")
                point={
                "latitude":seperate_string[0],
                "longitude":seperate_string[1],
                "altitude":seperate_string[2]
                }
                instance['polygon'].append(point)
            i = i + 1
            try:
                if not row[i]:
                    break
            except:
                break
        intervisibility_polygoins.append(instance)
    return intervisibility_polygoins

def evaluate_relative_direction(source,destination,destination_velocity):
    source_utm=(utm.from_latlon(source['latitude'],source['longitude']))
    destination_utm=(utm.from_latlon(destination['latitude'],destination['longitude']))
    utm_vector_destination_to_source= {
                            "east":source_utm[0]-destination_utm[0],
                            "north": source_utm[1]-destination_utm[1],
                                       }
    destination_velocity_norm=math.sqrt(destination_velocity['east']**2+destination_velocity['north']**2)
    utm_destination_to_source_norm=math.sqrt(utm_vector_destination_to_source['east']**2+utm_vector_destination_to_source['north']**2)

    if destination_velocity_norm!=0 and utm_destination_to_source_norm!=0:
        destination_unit_vector_velocity={
            "east": destination_velocity["east"]/destination_velocity_norm,
            "north":destination_velocity["north"]/destination_velocity_norm
        }

        utm_unit_vector_destination_to_source={
            "east": utm_vector_destination_to_source["east"]/utm_destination_to_source_norm,
            "north":utm_vector_destination_to_source["north"]/utm_destination_to_source_norm
        }
        scalar_multiplication=destination_unit_vector_velocity['east']*utm_unit_vector_destination_to_source['east']+ \
                              destination_unit_vector_velocity['north'] * utm_unit_vector_destination_to_source['north']
        return scalar_multiplication
    else:
        return None

def assess_vulnerability(loc,enemies_relative_direction,blueList,AccuracyConfiguration):
    vulnerability=0
    vulnerability_vec=[]
    # print("relative direction: " + str(enemies_relative_direction))
    for k, enemy in enumerate(blueList):
        if enemy.is_alive == True:
            classification = enemy.classification.name
            maxRange = float(AccuracyConfiguration.at[str(classification), 'MAX_RANGE'])
            blueDistance = calculate_blue_distance(loc,enemy)
            if blueDistance==None: #Ignore None Distance
                pass
            else:
                # print(enemy.unit_name)
                blueAccuracy = getAccuracy(AccuracyConfiguration,blueDistance,maxRange,classification)
                # print("distance is: " + str(blueDistance))
                # print("accuracy is: " + str(blueAccuracy))
                if not any(item['unit_name'] == enemy.unit_name for item in
                           enemies_relative_direction):
                    scalar_multiplication_value = 0 #case squad cant see enemy right now - we assume not a dangerous situation
                else:
                    scalar_multiplication_entity = next(x for x in enemies_relative_direction if
                                                        x['unit_name'] == enemy.unit_name)
                    if enemy.classification!=EntityTypeEnum.EITAN: #Drone case
                        if scalar_multiplication_entity['value']!= None:
                            scalar_multiplication_value = scalar_multiplication_entity['value']
                            if scalar_multiplication_entity['value']>0.95 and blueAccuracy>0.00: #drone is defenetly heading towards me
                                blueAccuracy=1.0
                        elif ((enemy.velocity['east'])**2 + enemy.velocity['north']**2) <0.05: # case that enemy is at halt - we assume not very dengerous situation
                            scalar_multiplication_value=0
                        else:
                            scalar_multiplication_value=1.0 #case squad is at halt
                    else:
                        scalar_multiplication_value=1.0
                if scalar_multiplication_value<0:
                    scalar_multiplication_value=0 #deadzone
                # print("scalar_multiplication_value:" + str(scalar_multiplication_value))
                vulnerability += blueAccuracy*scalar_multiplication_value
                vulnerability_vec.append(blueAccuracy*scalar_multiplication_value)
    miss_probability = 1
    for probability in vulnerability_vec:
        miss_probability=miss_probability*(1-probability)
    self_hit_probability=1-miss_probability
    return self_hit_probability

"Emerrgency HTN"
def update_enemies_relative_direction(loc,bluelist,enemies_relative_direction):
    enemies_relative_direction_copy=copy.deepcopy(enemies_relative_direction)
    for item in enemies_relative_direction_copy:
        enemy = next(x for x in bluelist if x.unit_name==item['unit_name'])
        item['value']=evaluate_relative_direction(loc, enemy.location, enemy.velocity)
    return enemies_relative_direction_copy

def generate_interior_polygon_point(vertex,centroid,polygon):
    communicator = CommunicatorSingleton().obj
    vertex_utm=utm.from_latlon(vertex['latitude'],vertex['longitude'])
    centroid_utm=utm.from_latlon(centroid['latitude'],centroid['longitude'])

    finish_bool=0
    counter=0
    while finish_bool==0:
            centroid_utm_copy = copy.deepcopy(centroid_utm)
            random_centroid_movement_x_meter = np.random.normal(0,15)
            random_centroid_movement_y_meter = np.random.normal(0,15)
            centroid_utm_copy=list(centroid_utm_copy)
            centroid_utm_copy[0] += random_centroid_movement_x_meter
            centroid_utm_copy[1] += random_centroid_movement_y_meter
            centroid_utm_copy=tuple(centroid_utm_copy)
            utm_vector_vertex_to_centroid = {
                "east": centroid_utm_copy[0] - vertex_utm[0],
                "north": centroid_utm_copy[1] - vertex_utm[1],
            }
            utm_vector_vertex_to_centroid_norm=math.sqrt(utm_vector_vertex_to_centroid['east']**2+utm_vector_vertex_to_centroid['north']**2)
            utm_unit_vector_vertex_to_centroid_norm = {
                "east": utm_vector_vertex_to_centroid["east"] / utm_vector_vertex_to_centroid_norm,
                "north": utm_vector_vertex_to_centroid["north"] / utm_vector_vertex_to_centroid_norm
            }
            interior_point_utm= {"east":None,"north":None,}
            random_push_into_polygon_meter=np.random.normal(40,15)
            interior_point_utm['east']=vertex_utm[0] + random_push_into_polygon_meter * utm_unit_vector_vertex_to_centroid_norm['east']
            interior_point_utm['north'] = vertex_utm[1] + random_push_into_polygon_meter  * utm_unit_vector_vertex_to_centroid_norm['north']

            #Transormations:"
            interior_point_LatLong = utm.to_latlon(interior_point_utm['east'], interior_point_utm['north'], vertex_utm[2], vertex_utm[3])
            alt = communicator.getHeightAboveSeaLevel(interior_point_LatLong[0], interior_point_LatLong[1])
            interior_point = {
                'latitude': interior_point_LatLong[0],
                'longitude': interior_point_LatLong[1],
                'altitude': alt
            }
            if (is_interior_point_valid_related_to_its_vertex(vertex,interior_point) and is_inside_polygon(interior_point,polygon)) or counter>30:
                finish_bool=1
                if counter>10: #could not find good cover point
                    interior_point=vertex
            counter+=1

            # centroid_copy_swiched_LatLong=utm.to_latlon(centroid_utm_copy[0], centroid_utm_copy[1], centroid_utm_copy[2], centroid_utm_copy[3])
            # cent_alt = communicator.getHeightAboveSeaLevel(centroid_copy_swiched_LatLong[0], centroid_copy_swiched_LatLong[1])
            # centroid_swiched= {
            #     'latitude': centroid_copy_swiched_LatLong[0],
            #     'longitude': centroid_copy_swiched_LatLong[1],
            #     'altitude': cent_alt
            # }

    # communicator.CreateEntitySimple('vertex', vertex, 2, '16:0:0:1:0:0:0')
    # communicator.CreateEntitySimple('centroid_swiched', centroid_swiched, 2, '16:0:0:1:0:0:0')
    # communicator.CreateEntitySimple('interior pt', interior_point, 2, '16:0:0:1:0:0:0')
    return interior_point

def is_interior_point_valid_related_to_its_vertex(vertex,point): #Assume flat surface
    communicator = CommunicatorSingleton().obj
    vertex_height = communicator.getHeightAboveSeaLevel(vertex['latitude'], vertex['longitude'])
    point_height = communicator.getHeightAboveSeaLevel(point['latitude'], point['longitude'])
    if abs(vertex_height-point_height)> 1.5: #resonable tree height in meter - not configured
        return False
    else:
        return True

def asses_waiting_time_in_waiting_location(config,waiting_location,bluelist,enemies_relative_direction):
    # waiting_point - is the desired waiting point
    # enemies_relative_direction - relative direction from enemies to current location.
    waiting_times=[]
    waiting_time=0
    if enemies_relative_direction!= []: # Squad can see one of the enemies right now
        for item in enemies_relative_direction:
            if item['value']!= None:
                if item['value']>0:
                    enemy = next(x for x in bluelist if x.unit_name == item['unit_name'])
                    enemy_velocity_norm=np.linalg.norm([enemy.velocity['east'],enemy.velocity['north'],enemy.velocity['up']])
                    enemy_distance=getMetriDistance(enemy.location,waiting_location)
                    waiting_times.append(first_order_time_estimator(enemy_distance,enemy_velocity_norm))
        waiting_time=sum(waiting_times)/len(waiting_times) #average waiting time * safety factor - not configured
    else:
        waiting_time=config.basic_cover_waiting_time
    return waiting_time

def asses_intersection_time_with_fastest_target(config,waiting_location,bluelist,enemies_relative_direction):
    # waiting_point - is the desired waiting point
    # enemies_relative_direction - relative direction from enemies to current location.
    waiting_times=[]
    waiting_time=0
    if enemies_relative_direction!= []: # Squad can see one of the enemies right now
        for item in enemies_relative_direction:
            if item['value']!= None:
                if item['value']>0:
                    enemy = next(x for x in bluelist if x.unit_name == item['unit_name'])
                    enemy_velocity_norm=np.linalg.norm([enemy.velocity['east'],enemy.velocity['north'],enemy.velocity['up']])
                    enemy_distance=getMetriDistance(enemy.location,waiting_location)
                    waiting_times.append(first_order_time_estimator(enemy_distance,enemy_velocity_norm))
        waiting_time=min(waiting_times)
    else:
        waiting_time=config['squad_eyes_range']/config['default_enemy_speed'] #case we cant see enemy
    return waiting_time

def first_order_time_estimator(distance,velocity):
    time=distance/velocity
    return time

