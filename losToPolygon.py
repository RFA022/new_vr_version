from Communicator import CommunicatorSingleton
communicator = CommunicatorSingleton().obj
import ext_funs


AttackPos = ext_funs.get_positions_fromCSV('Resources/RedAttackPos.csv')
Polygons = []
while not Polygons:
    Polygons = communicator.getAreasQuery()
BluePolygon = next(x for x in Polygons if x['areaName'] == 'BluePolygon')['polygon']
responsevec=[]

# AttackPos=[
# {
#                     "latitude": 33.371803,
#                     "longitude":35.497934,
#                     "altitude":457
#                 }
# ]
for k in range (len(AttackPos)):
    inloc={
                    "latitude": AttackPos[k]['latitude'],
                    "longitude": AttackPos[k]['longitude'],
                    "altitude": str(float(AttackPos[k]['altitude'])+ 1.5)
                }
    print("position: " + str(k) + "height is: " + inloc["altitude"])
    response=communicator.getLosToPolygonQuery(inloc,BluePolygon)
    print(response)
    try:
        responsevec.append(response[0]['exposedPolygon'])
        communicator.CreateTacticalGraphicCommand("po"+str(k), 2, response[0]['exposedAreasInThePolygon'][0])
    except:
        print('ss')
        responsevec.append(0)

max_visibility = max(responsevec)
for k,item in enumerate(responsevec):
    responsevec[k]= 100*(item/max_visibility)
print('ss')

with open('./Resources/polygonresponse.txt', 'w') as f:
    for k in range(len(AttackPos)):
            f.write("position number is: "+ str(k))
            f.write('\n')
            f.write(str(responsevec[k]))
            f.write('\n')
