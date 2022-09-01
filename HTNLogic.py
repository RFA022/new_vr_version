import logging
import time

from EntityNextStateAndAction import *
from EntityCurrentState import *
#from PlacementManager import *
from ConfigManager import *
import copy

class HTNLogic:

    @staticmethod
    def Step(entity_current_state: EntityCurrentState,
             start_scenario_time: float,AttackPos) -> EntityNextStateAndAction:

        entity_next_state_and_action = EntityNextStateAndAction(entity_current_state.unit_name)
        entity_next_state_and_action.position_location = copy.deepcopy(entity_current_state.current_location)

        # case 1 alive check
        if entity_current_state.alive is False:
            logging.debug("Alive check Fail for " + entity_current_state.unit_name.strip())
            return entity_next_state_and_action

        #case 3:
        if entity_current_state.COA != []:
            if entity_current_state.state is PositionType.AT_OP:
                if entity_current_state.COA[0][0]=='choose_position_op':
                    entity_next_state_and_action.nextPos=entity_current_state.COA[0][1]
                    logging.debug(
                        "Next Primitive Action: Change next destination to Attack Position: "+ str(entity_current_state.COA[0][1]))
                if entity_current_state.COA[0][0]=='move_to_position_op':
                    entity_next_state_and_action.move_pos = True
                    new_position_location = {
                        "location_id": -1,
                        "latitude": AttackPos[entity_current_state.face]['latitude'],
                        "longitude": AttackPos[entity_current_state.face]['longitude'],
                        "altitude": AttackPos[entity_current_state.face]['altitude'],
                    }
                    entity_next_state_and_action.SetPosition(PositionType.MOVE_TO_OP, new_position_location)
                    logging.debug(
                        "Next Primitive Task: move to Attack position number:  " + str(entity_current_state.face))
                if entity_current_state.COA[0][0] == 'locate_at_position_op':
                    entity_next_state_and_action.nextPosture='get_in_position'
                    logging.debug(
                        "Next Primitive Task: locate in position")
                if entity_current_state.COA[0][0] == 'scan_for_enemy_and_assess_exposure_op':
                    entity_next_state_and_action.scan_for_enemy = 1
                    logging.debug(
                        "Next Primitive Task: scan for enemy ")
                if entity_current_state.COA[0][0] == 'aim_op':
                    entity_next_state_and_action.aim = True
                    logging.debug(
                        "Next Primitive Task: aim at most valuable enemy")
                if entity_current_state.COA[0][0] == 'shoot_op':
                    entity_next_state_and_action.HTN_target=entity_current_state.COA[0][1]
                    entity_next_state_and_action.shoot = True
                    logging.debug(
                        "Next Primitive Task: Fire the first enemy in the target list. According to HTN: " + str(entity_next_state_and_action.HTN_target))
                if entity_current_state.COA[0][0] == 'null_op':
                    entity_next_state_and_action.null = True
                    logging.debug(
                        "Next Primitive Task: null")
                entity_next_state_and_action.takeAction=1

        return entity_next_state_and_action

        ''''
        # case 3 check if entity is under fire
        if entity_current_state.under_fire['underFire']:
            # checking if shooter detected
            if entity_current_state.under_fire["los"]:
                entity_current_state.detected_entity_platform = RFSMLogic.GetGeneralClassification(entity_current_state.detected_entity_classification)
                if RFSMLogic().FireEvent(entity_config, entity_next_state_and_action, entity_current_state):
                    #logging.debug("case 3 check if entity is under fire " + entity_current_state.entity_id.strip())
                    entity_current_state.under_fire['underFire'] = False
                    entity_current_state.under_fire['los'] = False
                    logging.debug(
                        "case 3 " + entity_current_state.entity_id.strip() + " entity under fire " + entity_current_state.detected_entity_id.strip() + " firing back!")

                    return entity_next_state_and_action
                else:
                    logging.debug("case 3 " + entity_current_state.entity_id.strip() + " entity under fire " + entity_current_state.detected_entity_id.strip() + " entity chose not to fire back, going to cover")
            else:
                logging.debug("case 3 " + entity_current_state.entity_id.strip() + " entity under fire " + entity_current_state.detected_entity_id.strip() +" there is no los, go to cover!")
            new_position_location = PlacementManager.FindNextPosition(entity_current_state,
                                                                      StateType.Cover,
                                                                      entity_config.max_range_next_op,
                                                                      entity_config.min_range_next_op)
            if ConfigManager.GetTeleportEntities():
                entity_next_state_and_action.SetPosition(PositionType.AT_COVER, new_position_location)
            else:
                entity_next_state_and_action.SetPosition(PositionType.MOVE_TO_COVER, new_position_location)
            entity_next_state_and_action.move_pos = True
            entity_current_state.under_fire['underFire'] = False
            entity_current_state.under_fire['los'] = False
            return entity_next_state_and_action

        # case 4 check if entity detected enemy
        if entity_current_state.enemy_detected is True:
            entity_current_state.detected_entity_platform = RFSMLogic.GetGeneralClassification(entity_current_state.detected_entity_classification)
            if RFSMLogic().FireEvent(entity_config, entity_next_state_and_action, entity_current_state):
                logging.debug(
                    "case 4 " + entity_current_state.entity_id.strip() + " entity detected enemy " + entity_current_state.detected_entity_id.strip() + " fire event!")
                entity_current_state.enemy_detected = False
                return entity_next_state_and_action

            new_position_location = PlacementManager.FindNextPosition(entity_current_state,
                                                                      StateType.Cover,
                                                                      entity_config.max_range_next_op,
                                                                      entity_config.min_range_next_op)
            if ConfigManager.GetTeleportEntities():
                entity_next_state_and_action.SetPosition(PositionType.AT_COVER, new_position_location)
            else:
                entity_next_state_and_action.SetPosition(PositionType.MOVE_TO_COVER, new_position_location)
            entity_next_state_and_action.move_pos = True
            logging.debug(
                "case 4 " + entity_current_state.entity_id.strip() + " entity detected enemy " + entity_current_state.detected_entity_id.strip() + " run to cover event!")
            entity_current_state.enemy_detected = False
            return entity_next_state_and_action

        # case 5 check if time is pass and need to move position (from op to op position)
        time_difference = abs(current_time - entity_current_state.update_time)
        if entity_current_state.state is PositionType.AT_OP:
            timeop = str(entity_config.timeop).split(sep=",")
            timeop_min = float(timeop[0])
            timeop_max = None
            if len(timeop) > 1:
                timeop_max = float(timeop[1])
            rand_time = timeop_min
            if timeop_max is not None:
                rand_time = np.random.uniform(timeop_min, timeop_max)
            if float(time_difference) > rand_time:
                logging.debug("change op location -> time_difference = " + str(time_difference) + " rand_time = " + str(
                    rand_time) + " timeop_min = " + str(timeop_min) + " timeop_max = " + str(timeop_max))
                entity_next_state_and_action.move_pos = True
                new_position_location = PlacementManager().FindNextPosition(entity_current_state,
                                                                            StateType.Op,
                                                                            float(entity_config.max_range_next_op),
                                                                            float(entity_config.min_range_next_op))
                if ConfigManager.GetTeleportEntities():
                    entity_next_state_and_action.SetPosition(PositionType.AT_OP, new_position_location)
                else:
                    entity_next_state_and_action.SetPosition(PositionType.MOVE_TO_OP, new_position_location)
                logging.debug(
                    "case 5 time passed and need to move position (from op to op position) " + entity_current_state.entity_id.strip())
                return entity_next_state_and_action

        # case 6 check if time is pass and need to move position (from cover to op position)
        elif entity_current_state.state is PositionType.AT_COVER:
            timecover = str(entity_config.timecover).split(sep=",")
            timecover_min = float(timecover[0])
            timecover_max = None
            if len(timecover) > 1:
                timecover_max = float(timecover[1])

            rand_time = timecover_min
            if timecover_max is not None:
                rand_time = np.random.uniform(timecover_min, timecover_max)
            if time_difference > rand_time:
                logging.debug(
                    "change cover location -> time_difference = " + str(time_difference) + " rand_time = " + str(
                        rand_time) + " timecover_min = " + str(timecover_min) + " timecover_max = " + str(
                        timecover_max))

                entity_next_state_and_action.move_pos = True
                new_position_location = PlacementManager().FindNextPosition(entity_current_state,
                                                                            StateType.Op,
                                                                            float(entity_config.max_range_next_op),
                                                                            float(entity_config.min_range_next_op))

                if ConfigManager.GetTeleportEntities():
                    entity_next_state_and_action.SetPosition(PositionType.AT_OP, new_position_location)
                else:
                    entity_next_state_and_action.SetPosition(PositionType.MOVE_TO_OP, new_position_location)
                return entity_next_state_and_action

        return entity_next_state_and_action
    
    @staticmethod
    def FireEvent(entity_config: EntityConfig, entity_next_state: EntityNextStateAndAction,
                  entity_current_state: EntityCurrentState) -> bool:
        # check if enemy is in fire range
        if entity_current_state.detected_entity_range <= float(entity_config.weapon_range):
            # check if entity have relevant weapon
            if str.upper(entity_current_state.detected_entity_platform).strip() == str.upper(entity_config.relevant_weapon).strip():
                randNum = np.random.uniform(0.0, 100.0)
                if randNum < 100 - float(entity_config.probability):
                    entity_next_state.SetFireEvent(entity_current_state.detected_entity_id)
                    return True
            else:
                logging.debug("current weopon " + str.upper(
                    entity_config.relevant_weapon).strip() + " doesn't match platform " + str.upper(
                    entity_current_state.detected_entity_platform).strip())
        else:
            logging.debug("current weapon range is too small")
        return False

    @staticmethod
    def GetGeneralClassification(entity_type: EntityTypeEnum) -> str:
        classification = int(entity_type.value[0])

        if classification == 1 or classification == 2 or classification == 3 or classification == 4 or \
                classification == 5 or classification == 7 or classification == 16 or classification == 8 or \
                classification == 9 or classification == 10 or classification == 13 or classification == 15:
            # GROUNDPLATFORM
            return "GROUNDPLATFORM"

        elif classification == 6 or classification == 11 or classification == 12 or classification == 14:
            # AIRPLATFORMS
            return "AIRPLATFORMS"
        return "UNKNOWN"
    '''
