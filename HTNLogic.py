from EntityNextStateAndAction import *
from EntityCurrentState import *
import logging
import copy

class HTNLogic:

    @staticmethod
    def Step(entity_current_state: EntityCurrentState,
             start_scenario_time: float,AttackPos,SpawnPos) -> EntityNextStateAndAction:

        entity_next_state_and_action = EntityNextStateAndAction(entity_current_state.unit_name)
        entity_next_state_and_action.position_location = copy.deepcopy(entity_current_state.current_location)

        # case 1 alive check
        if entity_current_state.alive is False:
            logging.debug("Alive check Fail for " + entity_current_state.unit_name.strip())
            return entity_next_state_and_action

        #case 3:
        if entity_current_state.COA != []:
            if entity_current_state.state  is PositionType.AT_OP and \
            entity_current_state.fireState is isFire.no and \
            entity_current_state.waitState is isWait.no and \
            entity_current_state.scanState is isScan.no:
                "---------Red HTN---------"
                if entity_current_state.COA[0][0]=='choose_position_op':
                    entity_next_state_and_action.nextPos=entity_current_state.COA[0][1]
                    entity_next_state_and_action.nextLocation=entity_current_state.COA[0][2]
                    logging.debug(str(entity_current_state.squad) +
                        ": Next Primitive Action - Change next destination to Attack Position "+ str(entity_current_state.COA[0][1]))
                if entity_current_state.COA[0][0]=='move_to_position_op':
                    if entity_current_state.face!="current_position":
                        entity_next_state_and_action.move_pos = True
                    new_position_location = {
                        "location_id": -1,
                        "latitude": entity_current_state.nextLocation['latitude'],
                        "longitude": entity_current_state.nextLocation['longitude'],
                        "altitude": entity_current_state.nextLocation['altitude'],
                    }
                    entity_next_state_and_action.SetPosition(PositionType.MOVE_TO_OP, new_position_location)
                    entity_next_state_and_action.positionType="Attack"
                    logging.debug(str(entity_current_state.squad) +
                        ": Next Primitive Task: move to Attack position number " + str(entity_current_state.face))
                if entity_current_state.COA[0][0] == 'locate_at_position_op':
                    entity_next_state_and_action.nextPosture='get_in_position'
                    logging.debug(str(entity_current_state.squad) +
                        ": Next Primitive Task- locate in position")
                if entity_current_state.COA[0][0] == 'scan_for_enemy_op':
                    entity_next_state_and_action.scan_for_enemy = 1
                    logging.debug(str(entity_current_state.squad) +
                        ": Next Primitive Task- scan for enemy ")
                if entity_current_state.COA[0][0] == 'aim_op':
                    entity_next_state_and_action.aim = True
                    logging.debug(str(entity_current_state.squad) +
                        ": Next Primitive Task - aim at most valuable enemy")
                if entity_current_state.COA[0][0] == 'shoot_op':
                    entity_next_state_and_action.HTN_target=entity_current_state.COA[0][1]
                    entity_next_state_and_action.shoot = True
                    logging.debug(str(entity_current_state.squad) +
                        ": Next Primitive Task - Fire the first enemy in the target list. According to HTN: " + str(entity_next_state_and_action.HTN_target))
                if entity_current_state.COA[0][0] == 'abort_op':
                    entity_next_state_and_action.null = True
                    logging.debug(str(entity_current_state.squad) +
                        ": Next Primitive Task: abort plan")

                "---------Green HTN---------:"
                if entity_current_state.COA[0][0]=='green_choose_random_position_op':
                    entity_next_state_and_action.nextPos=entity_current_state.COA[0][1]
                    # logging.debug(str(entity_current_state.unit_name) +
                    #     ": Next Primitive Action: Change next destination to Spawn Position - "+ str(entity_current_state.COA[0][1]))
                if entity_current_state.COA[0][0]=='green_move_to_position_op':
                    entity_next_state_and_action.move_pos = True
                    new_position_location = {
                        "location_id": -1,
                        "latitude": SpawnPos[entity_current_state.face]['latitude'],
                        "longitude": SpawnPos[entity_current_state.face]['longitude'],
                        "altitude": SpawnPos[entity_current_state.face]['altitude'],
                    }
                    entity_next_state_and_action.SetPosition(PositionType.MOVE_TO_OP, new_position_location)
                    entity_next_state_and_action.positionType = "Spawn"
                    # logging.debug(str(entity_current_state.unit_name) +
                    #     ": Next Primitive Action-move to Spawn position number " + str(entity_current_state.face))
                if entity_current_state.COA[0][0] == 'green_locate_and_wait_at_position_op':
                    entity_next_state_and_action.wait_at_position = True
                    entity_next_state_and_action.waitTime = entity_current_state.COA[0][2]
                    # logging.debug(str(entity_current_state.unit_name) +
                    #               ": Next Primitive Action: wait at position for " + str( entity_current_state.COA[0][2]) +" seconds")
                entity_next_state_and_action.takeAction=1

        return entity_next_state_and_action