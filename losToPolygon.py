from Communicator import CommunicatorSingleton
communicator = CommunicatorSingleton().obj
import ext_funs

AttackPos = ext_funs.get_positions_fromCSV('RedAttackPos.csv')
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
                    "altitude": str(float(AttackPos[k]['altitude']))
                }
    print("position: " + str(k) + "height is: " + inloc["altitude"])
    response=communicator.getLosToPolygonQuery(inloc,BluePolygon)
    responsevec.append(response)

with open('polygonresponse.txt', 'w') as f:
    for k in range(len(AttackPos)):
            f.write("position number is: "+ str(k))
            f.write('\n')
            f.write(str(responsevec[k]))
            f.write('\n')
communicator.CreateTacticalGraphicCommand("po", 2, responsevec[3][0]['exposedAreasInThePolygon'][0])