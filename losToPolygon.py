from Communicator import CommunicatorSingleton
communicator = CommunicatorSingleton().obj
import ext_funs

AttackPos = ext_funs.get_positions_fromCSV('RedAttackPos.csv')
Polygons = communicator.getAreasQuery()
BluePolygon = next(x for x in Polygons if x['areaName'] == 'BluePolygon')['polygon']
r=communicator.getLosToPolygonQuery()
communicator.CreateTacticalGraphicCommand("A", 2, r[0]['exposedAreasInThePolygon'][0])