import logging
import sys
import time
from os import path as os_path
import rticonnextdds_connector as rti
import threading
from CommunicatorInterface import *
from ConfigManager import ConfigManager
from singleton import Singleton

file_path = os_path.dirname(os_path.realpath(__file__))
sys.path.append(file_path)


class Communicator(CommunicatorInterface):
    GetAreasListRequest_DW = "GetAreasListRequest_DW"
    GetAreasListResponse_DR = "GetAreasListResponse_DR"
    LosQueryResponse_DR = "LosQueryResponse_DR"
    GeoQueryResponse_DR = "GeoQueryResponse_DR"
    NavigationPathPlanningResponse_DR = "NavigationPathPlanningResponse_DR"
    EntityReport_DR = "EntityReport_DR"
    TickCounterReport_DR = "TickCounterReport_DR"
    AttackReport_DR = "AttackReport_DR"
    ScenarioStatus_DR = "ScenarioStatus_DR"
    TaskStatus_DR = "TaskStatus_DR"
    LosToPolygonResponse_DR = "LosToPolygonResponse_DR"
    HeightAboveTerrainResponse_DR = "HeightAboveTerrainResponse_DR"
    LosQueryRequest_DW = "LosQueryRequest_DW"
    GeoQueryRequest_DW = "GeoQueryRequest_DW"
    InitialEntitySnapshot_DW = "InitialEntitySnapshot_DW"
    SetEntityLocation_DW = "SetEntityLocation_DW"
    SetEntityHeading_DW = "SetEntityHeading_DW"
    AttackEntityCommand_DW = "AttackEntityCommand_DW"
    CreateEntity_DW = "CreateEntity_DW"
    EntityMoveCommand_DW = "EntityMoveCommand_DW"
    SpawnSquadCommand_DW = "SpawnSquadCommand_DW"
    EntityPosture_DW = "EntityPosture_DW"
    AimWeaponCommand_DW = "AimWeaponCommand_DW"
    StopTasksCommand_DW = "StopTasksCommand_DW"
    LosToPolygonRequest_DW = "LosToPolygonRequest_DW"
    CreateTacticalGraphicCommand_DW = "CreateTacticalGraphicCommand_DW"
    NavigationPathPlanningRequest_DW = "NavigationPathPlanningRequest_DW"
    HeightAboveTerrainRequest_DW = "HeightAboveTerrainRequest_DW"
    EntityFollowPathCommand_DW = "EntityFollowPathCommand_DW"
    FusionReport_DR = "FusionReport_DR"
    SensorDesignationRequest_DW = "SensorDesignationRequest_DW"
    SensorOperationalModeCommand_DW = "SensorOperationalModeCommand_DW"

    def __init__(self):
        super().__init__()
        try:
            self.RFSM_connector = rti.Connector(config_name="RFSM_Participant_Library::RFSM_Participant",
                                                url=file_path + "/DDS_Resources/RFSM_DDS_Participant_Config.xml")
        except Exception as e:
            logging.error(e)
            logging.error(
                "connector fail !, url to file: " + file_path + "/DDS_Resources/RFSM_DDS_Participant_Config.xml")

        try:
            self.Geo_connector = rti.Connector(config_name="RFSM_Participant_Library::Geo_Participant",
                                               url=file_path + "/DDS_Resources/RFSM_DDS_Participant_Config.xml")
        except Exception as e:
            logging.error(e)
            logging.error(
                "connector fail !, url to file: " + file_path + "/DDS_Resources/RFSM_DDS_Participant_Config.xml")

        self.publisher = "Publisher::"
        self.subscriber = "Subscriber::"
        self.lock_read_write = threading.Lock()
        self.geo_lock_read_write = threading.Lock()
        self.entity_counter = 0
        logging.debug(self.__class__.__name__ + " is initialized")
        self.current_status = ScenarioStatusEnum.NA



    def SetSensorOperationalModeCommand(self, message: dict) -> None:
        with self.lock_read_write:
            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.SensorOperationalModeCommand_DW)
                current_DW.instance.set_dictionary(message)
                current_DW.write()
            except:
                logging.error("writer " + self.SensorOperationalModeCommand_DW + " dont exist")

    def SendSensorDesignationRequest(self, message: dict) -> None:
        with self.lock_read_write:
            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.SensorDesignationRequest_DW)
                current_DW.instance.set_dictionary(message)
                current_DW.write()
            except:
                logging.error("writer " + self.SensorDesignationRequest_DW + " dont exist")

    def GetFusionReport(self) -> list:
        with self.lock_read_write:
            try:
                current_DR = self.RFSM_connector.getInput(self.subscriber + self.FusionReport_DR)
                listOfMessage = []
                current_DR.read()
                for sample in current_DR.samples:
                    if sample.valid_data:
                        listOfMessage.append(sample.get_dictionary())
                return listOfMessage

            except:
                logging.error("reader " + self.FusionReport_DR + " dont exist")
                return listOfMessage

    def GetScenarioEntitiesInfo(self) -> list:
        """
        This function returns the latest update for all entities in the scenario
        :return: list of EntityInfo class object
        """
        with self.lock_read_write:
            try:
                current_DR = self.RFSM_connector.getInput(self.subscriber + self.EntityReport_DR)
                listOfMessage = []
                current_DR.read()
                for sample in current_DR.samples:
                    if sample.valid_data:
                        listOfMessage.append(sample.get_dictionary())
                return listOfMessage

            except:
                logging.error("reader " + self.EntityReport_DR + " dont exist")
                return listOfMessage

    def GetFireEvent(self) -> list:
        """
        This function is responsible to get all the fire events since that last time this function was called.
        :return: list of dict of "shooter_id" and "under_fire" true if the entity is under fire
        example
        under_fire =
        [
            {
            entity_id: "GIL"
            "location":
                {
                    "latitude": 0,
                    "longitude": 0,
                    "altitude": 0
                }
            },
            {
            entity_id: "ITAY"
            "location":
                {
                    "latitude": 1,
                    "longitude": 0,
                    "altitude": 0
                }
            }
        ]
        """
        with self.lock_read_write:
            try:
                current_DR = self.RFSM_connector.getInput(self.subscriber + self.AttackReport_DR)
                listOfMessage = []
                current_DR.take()
                for sample in current_DR.samples:
                    if sample.valid_data:
                        listOfMessage.append(sample.get_dictionary())

                return listOfMessage

            except:
                logging.error("reader " + self.AttackReport_DR + " dont exist")
                return listOfMessage

    def GetScenarioStatus(self) -> ScenarioStatusEnum:
        """
        This function is responsible for get the current scenario status
        :return: ScenarioStatus enum

        """

        with self.lock_read_write:
            try:
                current_DR = self.RFSM_connector.getInput(self.subscriber + self.ScenarioStatus_DR)
                current_DR.read()
                for sample in current_DR.samples:
                    if sample.valid_data:
                        status = int(sample.get_string("engine_status"))
                        if status == 0:
                            self.current_status = ScenarioStatusEnum.NA
                        elif status == 1:
                            self.current_status = ScenarioStatusEnum.RUNNING
                        elif status == 2:
                            self.current_status = ScenarioStatusEnum.PAUSE
                        elif status == 3:
                            self.current_status = ScenarioStatusEnum.RESTART

                return self.current_status

            except Exception as e:
                print(str(e))
                logging.error("reader " + self.ScenarioStatus_DR + " dont exist")
                return self.current_status

    def TickCounter(self) -> int:
        """
        This function is responsible for get the scenario current tick counter
        :return: return the current number of tick
        """
        current_tick = 0
        with self.lock_read_write:
            try:
                current_DR = self.RFSM_connector.getInput(self.subscriber + self.TickCounterReport_DR)
                current_DR.read()
                for sample in current_DR.samples:
                    if sample.valid_data:
                        current_tick = int(sample.get_number("tickCounter"))

                return current_tick

            except:
                logging.error("reader " + self.TickCounterReport_DR + " dont exist")
                return current_tick

    def CheckLos(self, src_location: dict, dest_location: dict) -> bool:
        """
        This function is responsible to check los between 2 locations
        :param src_location, contain dict of latitude, longitude and altitude
        :param dest_location, contain dict of latitude, longitude and altitude
        :return: return true if have los and false if not (or if timeout)
        example:
        src_location = {'latitude': 33.3722451, 'longitude': 35.4959193, 'altitude': 458.95838399999997}
        dest_location = {'latitude': 33.372253934425, 'longitude': 35.495998623516, 'altitude': 454.32898318388}

        """
        los = False
        # start_time = time.time_ns()
        with self.lock_read_write:
            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.LosQueryRequest_DW)
            except:
                logging.error("writer " + self.LosQueryRequest_DW + " dont exist")
                return los

            current_DW.instance.set_dictionary({
                "requestId": 1,
                "losVectorSrc": [src_location],
                "losVectorDest": [dest_location]
            })
            current_DW.write()

        with self.lock_read_write:
            try:
                current_DR = self.RFSM_connector.getInput(self.subscriber + self.LosQueryResponse_DR)
                # wait for messages for 1 sec
                try:
                    current_DR.wait(1000)
                except:
                    logging.debug("wait to los response timeout")
                    return los

                current_DR.read()
                for sample in current_DR.samples:
                    if sample.valid_data:
                        los = sample.get_dictionary("losVectorRes")
                        # logging.debug(str(time.time_ns() - start_time))
                return los[0]
            except:
                logging.error("reader " + self.LosQueryResponse_DR + " dont exist")
                return los

    def getAreasQuery(self) -> list:
        areaList = []
        with self.lock_read_write:
            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.GetAreasListRequest_DW)
            except:
                logging.error("writer " + self.LosQueryRequest_DW + " dont exist")
                return areaList

            current_DW.instance.set_dictionary({
                "requestId": 1,
            })
            current_DW.write()

        with self.lock_read_write:
            try:
                current_DR = self.RFSM_connector.getInput(self.subscriber + self.GetAreasListResponse_DR)
                # wait for messages for 2 sec
                try:
                    current_DR.wait(2000)
                except:
                    logging.debug("wait to arealist response timeout")
                    return areaList

                current_DR.read()
                for sample in current_DR.samples:
                    if sample.valid_data:
                        areaList = sample.get_dictionary("areasList")
                        # logging.debug(str(time.time_ns() - start_time))
                return areaList
            except:
                logging.error("reader " + self.GetAreasListResponse_DR + " dont exist")
                return areaList

    def GetGeoQuery(self, src_locations: dict, dest_locations: dict, calcLos: bool, calcDistance: bool) -> dict:
        """
        This function is responsible to check los and distance between 2 vectors of locations
        :param src_location, contain vector of dict of latitude, longitude and altitude
        :param dest_location, contain vector of dict of latitude, longitude and altitude
        :param calcLos and calcDistance booleans to get distances and los
        :return: return dictionary with booleans for returning los/distances and relevant vectors of booleans and distances

        """
        ans = {
            "los": [],
            "distance": []
        }
        # start_time = time.time_ns()
        with self.geo_lock_read_write:
            try:
                current_DW = self.Geo_connector.getOutput(self.publisher + self.GeoQueryRequest_DW)
            except:
                logging.error("writer " + self.GeoQueryRequest_DW + " don't exist")
                return ans

            current_DW.instance.set_dictionary({
                "requestId": 45,
                "vector1": src_locations,
                "vector2": dest_locations,
                "calcLos": calcLos,
                "calcDistance": calcDistance
            })
            current_DW.write()

        with self.geo_lock_read_write:
            try:
                current_DR = self.Geo_connector.getInput(self.subscriber + self.GeoQueryResponse_DR)
                # wait for messages for 2 sec
                try:
                    current_DR.wait(2000)
                except:
                    logging.debug("wait to GeoQuery response timeout")
                    return ans

                start_time = time.perf_counter()
                while True:
                    if (time.perf_counter() - start_time) > 5:
                        logging.debug("No Geoquery response for more then 5 sec")
                        break
                    current_DR.take()

                    # current_DR.read()
                    for sample in current_DR.samples:
                        if sample.valid_data:
                            id = int(sample.get_number("requestId"))
                            if id == 45:
                                los = sample.get_dictionary("los")
                                distance = sample.get_dictionary("distance")
                                # logging.debug(str(time.time_ns() - start_time))
                                ans["los"] = los
                                ans["distance"] = distance
                                return ans
                return ans
            except:
                logging.error("reader " + self.GeoQueryResponse_DR + " don't exist")
                return ans

    def SendInitialEntitySnapshot(self, compounds_dict: dict, compound: str, interest_compound: str,
                                  entities_list_for_initial_snapshot: list) -> None:
        """
        This function is responsible to send the initial entity snapshot
        :param compounds_dict, contain dict of latitude, longitude and altitude of the areas of the entities
        :return: N/A

            temp_dict: dict = {"areaID": "ab", "area": [
                {
                    "latitude": 0,
                    "longitude": 0,
                    "altitude": 0
                },
                {
                    "latitude": 0,
                    "longitude": 0,
                    "altitude": 0
                },
                {
                    "latitude": 0,
                    "longitude": 0,
                    "altitude": 0
                },
                {
                    "latitude": 0,
                    "longitude": 0,
                    "altitude": 0
                }]
                               }
            current_DW.instance.set_dictionary({
                "entitySnapshot": [temp_dict,temp_dict2,temp_dict3]
            })
        """

        AreaDict = {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5", "F": "6", "G": "7", "X": "8", "Y": "9"}

        with self.lock_read_write:
            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.InitialEntitySnapshot_DW)
            except:
                logging.error("writer " + self.InitialEntitySnapshot_DW + " don't exist")
                return

            current_DW.instance.set_dictionary({
                "entitiySnapshotID": "45",
                "reportingSysytemID": "40",
                "entitySnapshot": [{"areaID": AreaDict[compound[0]], "areaName": compound[0],
                                    "snapshotType": {"area": compounds_dict[compound[0]]}, "action": 1,
                                    "areaCategory": 1},
                                   {"areaID": AreaDict[compound[1]], "areaName": compound[1],
                                    "snapshotType": {"area": compounds_dict[compound[1]]}, "action": 1,
                                    "areaCategory": 1},
                                   {"areaID": AreaDict[interest_compound], "areaName": interest_compound,
                                    "snapshotType": {"area": compounds_dict[interest_compound]}, "action": 1,
                                    "areaCategory": 1}],
                "knownEntitiesInArea": entities_list_for_initial_snapshot})
            # "entitySnapshot": [{"areaID": compound[0], "area": compounds_dict[compound[0]]}
            #   , {"areaID": compound[1], "area": compounds_dict[compound[1]]}
            #   , {"areaID": interest_compound, "area": compounds_dict[interest_compound]}],
            # "knownEntitiesInArea": entities_list_for_initial_snapshot})
            current_DW.write()

    def GetTaskStatusEvent(self) -> list:
        """
        This function is responsible to get all the task progress status events since the last time this
        function was called.
        :return: list of dict of "entity_id" and "task_name" "task_status" true for task success

        """
        with self.lock_read_write:
            try:
                current_DR = self.RFSM_connector.getInput(self.subscriber + self.TaskStatus_DR)
                listOfMessage = []
                current_DR.take()
                for sample in current_DR.samples:
                    if sample.valid_data:
                        listOfMessage.append(sample.get_dictionary())

                return listOfMessage

            except:
                logging.error("reader " + self.TaskStatus_DR + " don't exist")
                return listOfMessage

    def MoveEntityToLocation(self, entity_id: str, location: dict, speed) -> None:
        """
        This function is responsible to move entity to location
        :param entity_id: id of the entity to move
        :param location: location of the entity to move
        :return: N/A
        """
        with self.lock_read_write:

            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.EntityMoveCommand_DW)
            except:
                logging.error("writer " + self.EntityMoveCommand_DW + " dont exist")
                return
            current_DW.instance.set_dictionary({
                "unit_name": entity_id,
                "ordered_speed": speed,  # ConfigManager.GetMovingPosSpeed(),
                "altitude_reference": 0,
                "location": location
            })
            current_DW.write()

    def FireCommand(self, attacking_entity_id: str, to_attack_id: str, ammoNumber: int, weapon_type: str = "") -> None:
        """
        This function is responsible for make fire event
        :param attacking_entity_id: id of the entity to perform the fire
        :param to_attack_id: id of the entity to attack
        :param weapon_type: type of the weapon to attack with
        :return: N/A
        """
        with self.lock_read_write:
            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.AttackEntityCommand_DW)
            except:
                logging.error("writer " + self.AttackEntityCommand_DW + " dont exist")
                return

            current_DW.instance.set_dictionary({
                "attacking_entity_name": attacking_entity_id,
                "entity_to_attack_id": to_attack_id,
                "weapon_name": "ak",
                "maxRoundsToFire": ammoNumber
            })
            current_DW.write()
            # looks for "ak" and if it not find its fire with default weapon

    def CreateEntity(self, entity_to_create_list: list):
        """
        This function is responsible for create entity
        :param entity_to_create_list: list of EntityInfo class
        :return: N/A
        """
        with self.lock_read_write:
            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.CreateEntity_DW)
            except:
                logging.error("writer " + self.CreateEntity_DW + " dont exist")
                return
            for i in range(len(entity_to_create_list)):
                entity_config = ConfigManager.getEntityConfig(entity_to_create_list[i].classification)
                if str(entity_to_create_list[i].hostility.name).strip() == "OPPOSING":
                    hostility = 2
                if str(entity_to_create_list[i].hostility.name).strip() == "NEUTRAL":
                    hostility = 3
                if str(entity_to_create_list[i].hostility.name).strip() == "FRIENDLY":
                    hostility = 1
                current_DW.instance.set_dictionary({
                    "unit_name": str(entity_to_create_list[i].unit_name),
                    "location": entity_to_create_list[i].worldLocation.get("location"),
                    "hostility": hostility,
                    "enumeration": entity_config.vrf_or_godot_id
                })
                current_DW.write()
                time.sleep(0.3)

    def CreateEntitySimple(self, name, location, hostility, code):
        with self.lock_read_write:
            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.CreateEntity_DW)
            except:
                logging.error("writer " + self.CreateEntity_DW + " dont exist")
                return
            current_DW.instance.set_dictionary({
                "unit_name": name,
                "location": location,
                "hostility": hostility,
                "enumeration": code
            })
            current_DW.write()
            time.sleep(0.3)

    def createSquad(self, squad_name, location):
        with self.lock_read_write:
            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.SpawnSquadCommand_DW)
            except:
                logging.error("writer " + self.SpawnSquadCommand_DW + " dont exist")
                return
            current_DW.instance.set_dictionary({
                "squad_name": squad_name,
                "location": location
            })
            current_DW.write()
            time.sleep(0.2)

    def setEntityPosture(self, entity_name, posture):
        with self.lock_read_write:
            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.EntityPosture_DW)
            except:
                logging.error("writer " + self.EntityPosture_DW + " dont exist")
                return
            current_DW.instance.set_dictionary({
                "entity_name": entity_name,
                "posture": posture
            })
            current_DW.write()
            time.sleep(0.2)

    def setEntityHeading(self, entity_name, azimuth):
        with self.lock_read_write:
            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.SetEntityHeading_DW)
            except:
                logging.error("writer " + self.SetEntityHeading_DW + " dont exist")
                return
            current_DW.instance.set_dictionary({
                "entity_name": entity_name,
                "azimuth": azimuth
            })
            current_DW.write()
            time.sleep(0.2)

    def aim_weapon_at_target(self, entity_name, aiming_point):
        with self.lock_read_write:
            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.AimWeaponCommand_DW)
            except:
                logging.error("writer " + self.AimWeaponCommand_DW + " dont exist")
                return
            aiming_point['altitude'] = str(float(aiming_point['altitude']) + 1.5)
            current_DW.instance.set_dictionary({
                "entity_name": entity_name,
                "aiming_point": aiming_point
            })
            current_DW.write()
            time.sleep(0.2)

    def stopCommand(self, entity_name):
        with self.lock_read_write:
            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.StopTasksCommand_DW)
            except:
                logging.error("writer " + self.StopTasksCommand_DW + " dont exist")
                return
            current_DW.instance.set_dictionary({
                "attacking_entity_name": entity_name
            })
            current_DW.write()

    def getLosToPolygonQuery(self, sorce, polygon) -> list:
        responseList = []
        with self.lock_read_write:
            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.LosToPolygonRequest_DW)
            except:
                logging.error("writer " + self.LosToPolygonRequest_DW + " dont exist")

            current_DW.instance.set_dictionary({
                "requestId": 1,
                "losSrc": sorce,
                "polygon": polygon
            }, )
            current_DW.write()
            print("Sent LosToPolygonRequest")

        print("Waiting for Los To Polygon response:")
        with self.lock_read_write:
            try:
                current_DR = self.RFSM_connector.getInput(self.subscriber + self.LosToPolygonResponse_DR)
                # wait for messages for 2 sec
                try:
                    current_DR.wait(20000)
                except:
                    logging.debug("wait to LosToPolygonResponse_DR timeout")
                    return responseList
                current_DR.take()
                for sample in current_DR.samples:
                    if sample.valid_data:
                        # first - print the sample.
                        print(current_DR.name)
                        print(sample.get_dictionary())
                        responseList.append(sample.get_dictionary())

                    else:
                        print("Received non-valid message (Dispose)")
                return responseList
            except:
                logging.error("reader " + self.GetAreasListResponse_DR + " dont exist")
                return responseList

    def CreateTacticalGraphicCommand(self, TacticalGraphicName: str, tacticalGraphicKind: int, path) -> None:

        with self.lock_read_write:
            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.CreateTacticalGraphicCommand_DW)
            except:
                logging.error("writer " + self.CreateTacticalGraphicCommand_DW + " dont exist")
                return

            current_DW.instance.set_dictionary({
                "TacticalGraphicName": TacticalGraphicName,
                "tacticalGraphicKind": tacticalGraphicKind,
                "path": path,
            })
            current_DW.write()
            # looks for "ak" and if it not find its fire with default weapon

    def navigationPathPlan(self, origin, destination, locationToAvoid, avoidanceRadius, name, maximumNumberOfRoutes):
        responseList = []
        with self.lock_read_write:
            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.NavigationPathPlanningRequest_DW)
            except:
                logging.error("writer " + self.NavigationPathPlanningRequest_DW + " dont exist")
            # print(origin)
            # print(destination)
            if locationToAvoid != None:
                current_DW.instance.set_dictionary(
                    {
                        "maximumNumberOfRoutes": maximumNumberOfRoutes,
                        "sourceID": "RFA",
                        "recipientID": "test",
                        "requestID": "1",
                        "avoidanceRadius": avoidanceRadius,
                        "vehicleID": name,
                        "locationToAvoid": {
                            "latitude": locationToAvoid['latitude'],
                            "longitude": locationToAvoid['longitude'],
                            "altitude": locationToAvoid['altitude'],
                        },
                        "origin3DPoint": {
                            "latitude": origin['latitude'],
                            "longitude": origin['longitude'],
                            "altitude": origin['altitude'],
                        },
                        "destination3DPoint": {
                            "latitude": destination['latitude'],
                            "longitude": destination['longitude'],
                            "altitude": destination['altitude'],
                        },
                    }
                )
            else:
                current_DW.instance.set_dictionary(
                    {
                        "sourceID": "RFA",
                        "recipientID": "test",
                        "requestID": "1",
                        "vehicleID": name,
                        "origin3DPoint": {
                            "latitude": origin['latitude'],
                            "longitude": origin['longitude'],
                            "altitude": origin['altitude'],
                        },
                        "destination3DPoint": {
                            "latitude": destination['latitude'],
                            "longitude": destination['longitude'],
                            "altitude": destination['altitude'],
                        },
                    }
                )
            current_DW.write()
            time.sleep(0.01)
            # print("Sent pathPlan request")

        # print("Waiting for path response:")
        with self.lock_read_write:
            try:
                current_DR = self.RFSM_connector.getInput(self.subscriber + self.NavigationPathPlanningResponse_DR)
                # wait for messages for 2 sec
                try:
                    current_DR.wait(30000)
                except:
                    logging.debug("wait to path plan response timeout")
                    return responseList
                current_DR.take()
                for sample in current_DR.samples:
                    if sample.valid_data:
                        # first - print the sample.
                        responseList.append(sample.get_dictionary())
                        # print(sample.get_dictionary())
                    else:
                        print("Received non-valid message (Dispose)")
                return responseList
            except:
                logging.error("reader " + self.NavigationPathPlanningResponse_DR + " dont exist")
                return responseList

    def getHeightAboveSeaLevel(self, lat, long) -> float:
        response = 0
        with self.lock_read_write:
            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.HeightAboveTerrainRequest_DW)
            except:
                logging.error("writer " + self.HeightAboveTerrainRequest_DW + " dont exist")

            current_DW.instance.set_dictionary({
                "HeightRequestedVector": [
                    {
                        "latitude": lat,
                        "longitude": long,
                        "altitude": 0,
                    }
                ],
            }, )
            current_DW.write()
        with self.lock_read_write:
            try:
                current_DR = self.RFSM_connector.getInput(self.subscriber + self.HeightAboveTerrainResponse_DR)
                # wait for messages for 2 sec
                try:
                    current_DR.wait(20000)
                except:
                    logging.debug("wait to HeightAboveTerrainResponse_DR timeout")
                    return response
                current_DR.take()
                for sample in current_DR.samples:
                    if sample.valid_data:
                        # first - print the sample.
                        request = sample.get_dictionary()
                        lat = -request['HeightRequestedVector'][0][0]
                        response = (lat)
                    else:
                        print("Received non-valid message (Dispose)")
                return response
            except:
                logging.error("reader " + self.GetAreasListResponse_DR + " dont exist")
                return response

    def followPathCommand(self, unit_name, path, ordered_speed):
        with self.lock_read_write:
            try:
                current_DW = self.RFSM_connector.getOutput(self.publisher + self.EntityFollowPathCommand_DW)
            except:
                logging.error("writer " + self.EntityFollowPathCommand_DW + " dont exist")
                return
            current_DW.instance.set_dictionary({
                "unit_name": unit_name,
                "path_id_or_full": {
                    "full_path": path
                },
                "ordered_speed": ordered_speed,
            })
            current_DW.write()


class CommunicatorSingleton(metaclass=Singleton):
    def __init__(self):
        self.obj = Communicator()
