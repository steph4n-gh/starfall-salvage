#pragma bank 255
#include <gbdk/platform.h>
#include <string.h>
#include "actor.h"
#include "bankdata.h"
#include "camera.h"
#include "fade_manager.h"
#include "vm.h"
#include "vm_exceptions.h"
#include "starfall_rooms.h"
#include "data/scene_mission_01_room_00.h"
#include "data/scene_mission_01_room_01.h"
#include "data/scene_mission_01_room_02.h"
#include "data/scene_mission_01_room_03.h"
#include "data/scene_mission_02_room_00.h"
#include "data/scene_mission_02_room_01.h"
#include "data/scene_mission_02_room_02.h"
#include "data/scene_mission_02_room_03.h"
#include "data/scene_mission_03_room_00.h"
#include "data/scene_mission_03_room_01.h"
#include "data/scene_mission_03_room_02.h"
#include "data/scene_mission_03_room_03.h"
#include "data/scene_mission_04_room_00.h"
#include "data/scene_mission_04_room_01.h"
#include "data/scene_mission_04_room_02.h"
#include "data/scene_mission_04_room_03.h"
#include "data/scene_mission_05_room_00.h"
#include "data/scene_mission_05_room_01.h"
#include "data/scene_mission_05_room_02.h"
#include "data/scene_mission_05_room_03.h"
#include "data/scene_mission_06_room_00.h"
#include "data/scene_mission_06_room_01.h"
#include "data/scene_mission_06_room_02.h"
#include "data/scene_mission_06_room_03.h"
#include "data/scene_mission_07_room_00.h"
#include "data/scene_mission_07_room_01.h"
#include "data/scene_mission_07_room_02.h"
#include "data/scene_mission_07_room_03.h"
#include "data/scene_mission_08_room_00.h"
#include "data/scene_mission_08_room_01.h"
#include "data/scene_mission_08_room_02.h"
#include "data/scene_mission_08_room_03.h"
#include "data/scene_mission_09_room_00.h"
#include "data/scene_mission_09_room_01.h"
#include "data/scene_mission_09_room_02.h"
#include "data/scene_mission_09_room_03.h"
#include "data/scene_mission_10_room_00.h"
#include "data/scene_mission_10_room_01.h"
#include "data/scene_mission_10_room_02.h"
#include "data/scene_mission_10_room_03.h"
#include "data/scene_mission_11_room_00.h"
#include "data/scene_mission_11_room_01.h"
#include "data/scene_mission_11_room_02.h"
#include "data/scene_mission_11_room_03.h"
#include "data/scene_mission_12_room_00.h"
#include "data/scene_mission_12_room_01.h"
#include "data/scene_mission_12_room_02.h"
#include "data/scene_mission_12_room_03.h"
#include "data/scene_mission_13_room_00.h"
#include "data/scene_mission_13_room_01.h"
#include "data/scene_mission_13_room_02.h"
#include "data/scene_mission_13_room_03.h"
#include "data/scene_mission_14_room_00.h"
#include "data/scene_mission_14_room_01.h"
#include "data/scene_mission_14_room_02.h"
#include "data/scene_mission_14_room_03.h"
#include "data/scene_mission_15_room_00.h"
#include "data/scene_mission_15_room_01.h"
#include "data/scene_mission_15_room_02.h"
#include "data/scene_mission_15_room_03.h"
#include "data/scene_mission_16_room_00.h"
#include "data/scene_mission_16_room_01.h"
#include "data/scene_mission_16_room_02.h"
#include "data/scene_mission_16_room_03.h"
#include "data/scene_mission_17_room_00.h"
#include "data/scene_mission_17_room_01.h"
#include "data/scene_mission_17_room_02.h"
#include "data/scene_mission_17_room_03.h"
#include "data/scene_mission_18_room_00.h"
#include "data/scene_mission_18_room_01.h"
#include "data/scene_mission_18_room_02.h"
#include "data/scene_mission_18_room_03.h"
#include "data/scene_room_01.h"
#include "data/scene_room_02.h"
#include "data/scene_room_03.h"
#include "data/scene_room_04.h"
#include "data/scene_room_05.h"
#include "data/scene_room_06.h"
#include "data/scene_room_07.h"
#include "data/scene_room_08.h"
#include "data/scene_room_09.h"
#include "data/scene_room_10.h"
#include "data/scene_room_11.h"
#include "data/scene_room_12.h"
static const sf_room_t rooms[SF_ROOM_COUNT] = {
    {"FREIGHT SPINE", "CROSS FREIGHT BAY", "3 CELLS THEN DOCK",
     0, SF_OBJECTIVE_SALVAGE, SF_ENEMY_CHARGER, SF_HAZARD_NONE, 0, 0, 0, 0, 42, 18, 60, 56, 45, 0, 0, 0},
    {"SIGNAL WORKS", "HOLD B TO REPAIR", "ANY ORDER THEN DOCK",
     0, SF_OBJECTIVE_REPAIR, SF_ENEMY_SWEEPER, SF_HAZARD_VENT, 26, 17, 2, 2, 42, 18, 60, 56, 45, 0, 336, 56},
    {"RESCUE CONCOURSE", "STAY NEAR THE CREW", "GUIDE THEM TO DOCK",
     0, SF_OBJECTIVE_ESCORT, SF_ENEMY_HUNTER, SF_HAZARD_LASER, 12, 25, 12, 1, 42, 18, 60, 56, 45, 14, 336, 64},
    {"BULWARK BAY", "PULSE WHEN CORE OPEN", "THREE HITS THEN DOCK",
     0, SF_OBJECTIVE_CORE, SF_ENEMY_CHARGER, SF_HAZARD_NONE, 0, 0, 0, 0, 42, 18, 96, 56, 45, 0, 0, 0},
    {"CARGO FORK", "GRAB THREE CELLS", "CHOOSE TOP OR BOTTOM",
     0, SF_OBJECTIVE_SALVAGE, SF_ENEMY_CHARGER, SF_HAZARD_NONE, 0, 0, 0, 0, 42, 18, 112, 56, 45, 0, 64, 192},
    {"RELAY LADDER", "HOLD B IN NODE ORDER", "LIT NODE THEN NEXT",
     0, SF_OBJECTIVE_RELAY, SF_ENEMY_SWEEPER, SF_HAZARD_VENT, 27, 25, 2, 2, 42, 24, 112, 52, 45, 0, 344, 256},
    {"PATCH DECK", "HOLD B TO REPAIR", "ANY ORDER THEN DOCK",
     0, SF_OBJECTIVE_REPAIR, SF_ENEMY_HUNTER, SF_HAZARD_LASER, 12, 20, 12, 1, 42, 18, 112, 56, 45, 0, 352, 232},
    {"CIRCUIT SENTINEL", "PULSE WHEN CORE OPEN", "AXIS DASH THEN OPEN",
     0, SF_OBJECTIVE_CORE, SF_ENEMY_SWEEPER, SF_HAZARD_VENT, 16, 25, 2, 2, 48, 24, 112, 52, 45, 0, 344, 56},
    {"DEBRIS HALO", "GRAB THREE CELLS", "LOOP AROUND THE HALO",
     0, SF_OBJECTIVE_SALVAGE, SF_ENEMY_HUNTER, SF_HAZARD_VENT, 23, 24, 2, 2, 42, 18, 112, 56, 45, 0, 328, 64},
    {"TRIAGE HUB", "HOLD B TO REPAIR", "ANY ORDER THEN DOCK",
     0, SF_OBJECTIVE_REPAIR, SF_ENEMY_CHARGER, SF_HAZARD_LASER, 18, 18, 14, 1, 42, 18, 112, 56, 45, 0, 336, 56},
    {"POD CAUSEWAY", "STAY NEAR THE CREW", "GUIDE THEM TO DOCK",
     0, SF_OBJECTIVE_ESCORT, SF_ENEMY_SWEEPER, SF_HAZARD_VENT, 34, 23, 2, 2, 42, 24, 112, 52, 45, 19, 344, 64},
    {"POD WARDEN", "PULSE WHEN CORE OPEN", "THREE HITS THEN DOCK",
     0, SF_OBJECTIVE_CORE, SF_ENEMY_HUNTER, SF_HAZARD_LASER, 20, 24, 12, 1, 48, 18, 112, 56, 45, 0, 344, 56},
    {"PUMP GARDEN", "GRAB THREE CELLS", "3 CELLS THEN DOCK",
     1, SF_OBJECTIVE_SALVAGE, SF_ENEMY_CHARGER, SF_HAZARD_VENT, 24, 22, 2, 2, 42, 18, 112, 56, 45, 0, 336, 56},
    {"VALVE GALLERY", "HOLD B TO REPAIR", "ANY ORDER THEN DOCK",
     1, SF_OBJECTIVE_REPAIR, SF_ENEMY_HUNTER, SF_HAZARD_VENT, 18, 17, 2, 2, 42, 18, 112, 56, 45, 0, 336, 232},
    {"FLOW LADDER", "HOLD B IN NODE ORDER", "LIT NODE THEN NEXT",
     1, SF_OBJECTIVE_RELAY, SF_ENEMY_SWEEPER, SF_HAZARD_LASER, 4, 20, 9, 1, 42, 24, 112, 52, 45, 0, 344, 264},
    {"PRESSURE WARDEN", "PULSE WHEN CORE OPEN", "THREE HITS THEN DOCK",
     1, SF_OBJECTIVE_CORE, SF_ENEMY_CHARGER, SF_HAZARD_VENT, 27, 25, 2, 2, 48, 18, 112, 56, 45, 0, 344, 64},
    {"FROST DEPOT", "GRAB THREE CELLS", "3 CELLS THEN DOCK",
     1, SF_OBJECTIVE_SALVAGE, SF_ENEMY_HUNTER, SF_HAZARD_LASER, 22, 21, 14, 1, 42, 18, 112, 56, 45, 0, 176, 64},
    {"DEFROST WORKS", "HOLD B TO REPAIR", "ANY ORDER THEN DOCK",
     1, SF_OBJECTIVE_REPAIR, SF_ENEMY_SWEEPER, SF_HAZARD_VENT, 12, 18, 2, 2, 42, 24, 112, 52, 45, 0, 344, 64},
    {"EVAC TUNNELS", "STAY NEAR THE CREW", "GUIDE THEM TO DOCK",
     1, SF_OBJECTIVE_ESCORT, SF_ENEMY_CHARGER, SF_HAZARD_VENT, 21, 23, 2, 2, 42, 18, 112, 56, 45, 18, 344, 288},
    {"GLASS GUARDIAN", "PULSE WHEN CORE OPEN", "THREE HITS THEN DOCK",
     1, SF_OBJECTIVE_CORE, SF_ENEMY_HUNTER, SF_HAZARD_LASER, 4, 23, 12, 1, 48, 18, 112, 56, 45, 0, 336, 56},
    {"RESERVOIR CROSS", "GRAB THREE CELLS", "3 CELLS THEN DOCK",
     1, SF_OBJECTIVE_SALVAGE, SF_ENEMY_SWEEPER, SF_HAZARD_VENT, 30, 19, 2, 2, 42, 24, 112, 52, 45, 0, 48, 128},
    {"PRESSURE RELAYS", "HOLD B IN NODE ORDER", "LIT NODE THEN NEXT",
     1, SF_OBJECTIVE_RELAY, SF_ENEMY_CHARGER, SF_HAZARD_LASER, 4, 26, 9, 1, 42, 18, 112, 56, 45, 0, 336, 264},
    {"MANIFOLD PATCH", "HOLD B TO REPAIR", "ANY ORDER THEN DOCK",
     1, SF_OBJECTIVE_REPAIR, SF_ENEMY_HUNTER, SF_HAZARD_VENT, 23, 15, 2, 2, 42, 18, 112, 56, 45, 0, 336, 56},
    {"THERMAL SENTINEL", "PULSE WHEN CORE OPEN", "THREE HITS THEN DOCK",
     1, SF_OBJECTIVE_CORE, SF_ENEMY_SWEEPER, SF_HAZARD_VENT, 12, 23, 2, 2, 48, 24, 112, 52, 45, 0, 336, 56},
    {"ORE SPINE", "GRAB THREE CELLS", "3 CELLS THEN DOCK",
     2, SF_OBJECTIVE_SALVAGE, SF_ENEMY_CHARGER, SF_HAZARD_LASER, 4, 20, 9, 1, 42, 18, 112, 56, 45, 0, 144, 72},
    {"SMELTER PATCH", "HOLD B TO REPAIR", "ANY ORDER THEN DOCK",
     2, SF_OBJECTIVE_REPAIR, SF_ENEMY_HUNTER, SF_HAZARD_VENT, 25, 20, 2, 2, 42, 18, 112, 56, 45, 0, 336, 248},
    {"FURNACE LADDER", "HOLD B IN NODE ORDER", "LIT NODE THEN NEXT",
     2, SF_OBJECTIVE_RELAY, SF_ENEMY_SWEEPER, SF_HAZARD_LASER, 4, 24, 12, 1, 42, 24, 112, 52, 45, 0, 344, 272},
    {"KILN GUARDIAN", "PULSE WHEN CORE OPEN", "THREE HITS THEN DOCK",
     2, SF_OBJECTIVE_CORE, SF_ENEMY_SWEEPER, SF_HAZARD_VENT, 24, 25, 2, 2, 48, 24, 112, 52, 45, 0, 336, 56},
    {"ASH SORTER", "GRAB THREE CELLS", "3 CELLS THEN DOCK",
     2, SF_OBJECTIVE_SALVAGE, SF_ENEMY_HUNTER, SF_HAZARD_VENT, 24, 23, 2, 2, 42, 18, 112, 56, 45, 0, 208, 64},
    {"EXHAUST RELAYS", "HOLD B IN NODE ORDER", "LIT NODE THEN NEXT",
     2, SF_OBJECTIVE_RELAY, SF_ENEMY_CHARGER, SF_HAZARD_LASER, 14, 24, 12, 1, 42, 18, 112, 56, 45, 0, 336, 264},
    {"SHIFT WALKWAY", "STAY NEAR THE CREW", "GUIDE THEM TO DOCK",
     2, SF_OBJECTIVE_ESCORT, SF_ENEMY_HUNTER, SF_HAZARD_LASER, 20, 24, 12, 1, 42, 18, 112, 56, 45, 16, 216, 208},
    {"SHIFT GUARDIAN", "PULSE WHEN CORE OPEN", "THREE HITS THEN DOCK",
     2, SF_OBJECTIVE_CORE, SF_ENEMY_CHARGER, SF_HAZARD_VENT, 11, 23, 2, 2, 48, 18, 112, 56, 45, 0, 344, 56},
    {"SLAG CIRCUIT", "GRAB THREE CELLS", "3 CELLS THEN DOCK",
     2, SF_OBJECTIVE_SALVAGE, SF_ENEMY_SWEEPER, SF_HAZARD_LASER, 12, 21, 14, 1, 42, 24, 112, 52, 45, 0, 336, 56},
    {"KILN REPAIR", "HOLD B TO REPAIR", "ANY ORDER THEN DOCK",
     2, SF_OBJECTIVE_REPAIR, SF_ENEMY_CHARGER, SF_HAZARD_VENT, 23, 17, 2, 2, 42, 18, 112, 56, 45, 0, 344, 72},
    {"HEAT RELAYS", "HOLD B IN NODE ORDER", "LIT NODE THEN NEXT",
     2, SF_OBJECTIVE_RELAY, SF_ENEMY_HUNTER, SF_HAZARD_LASER, 19, 24, 14, 1, 42, 18, 112, 56, 45, 0, 336, 96},
    {"FORGE WARDEN", "PULSE WHEN CORE OPEN", "THREE HITS THEN DOCK",
     2, SF_OBJECTIVE_CORE, SF_ENEMY_HUNTER, SF_HAZARD_VENT, 13, 25, 2, 2, 48, 18, 112, 56, 45, 0, 336, 56},
    {"RECEIVER GALLERY", "GRAB THREE CELLS", "FIND THE COVER GAPS",
     3, SF_OBJECTIVE_SALVAGE, SF_ENEMY_CHARGER, SF_HAZARD_VENT, 22, 27, 2, 2, 44, 18, 112, 60, 45, 0, 0, 0},
    {"DECODER STACK", "HOLD B AT EACH PANEL", "POWER THE NEXT PATH",
     3, SF_OBJECTIVE_REPAIR, SF_ENEMY_HUNTER, SF_HAZARD_LASER, 15, 20, 12, 1, 44, 18, 112, 60, 45, 0, 352, 56},
    {"MEMORY SWITCH", "HOLD B AT LIT RELAY", "ACTIVATE IN ORDER",
     3, SF_OBJECTIVE_RELAY, SF_ENEMY_SWEEPER, SF_HAZARD_VENT, 34, 32, 2, 2, 44, 24, 112, 60, 45, 0, 0, 0},
    {"ARCHIVE GUARDIAN", "PULSE WHEN CORE OPEN", "THREE HITS THEN DOCK",
     3, SF_OBJECTIVE_CORE, SF_ENEMY_SWEEPER, SF_HAZARD_LASER, 21, 25, 10, 1, 48, 24, 120, 60, 45, 0, 0, 0},
    {"PACKET CONCOURSE", "GRAB THREE CELLS", "FIND THE COVER GAPS",
     3, SF_OBJECTIVE_SALVAGE, SF_ENEMY_HUNTER, SF_HAZARD_VENT, 23, 18, 2, 2, 44, 20, 112, 60, 45, 0, 0, 0},
    {"CARRIER REPAIR", "HOLD B AT EACH PANEL", "POWER THE NEXT PATH",
     3, SF_OBJECTIVE_REPAIR, SF_ENEMY_CHARGER, SF_HAZARD_LASER, 17, 24, 12, 1, 44, 20, 112, 60, 45, 0, 344, 56},
    {"CREW TRANSIT", "STAY CLOSE TO CREW", "MARKERS THEN DOCK",
     3, SF_OBJECTIVE_ESCORT, SF_ENEMY_HUNTER, SF_HAZARD_LASER, 16, 24, 12, 1, 44, 20, 112, 60, 45, 16, 0, 0},
    {"SIGNAL WARDEN", "PULSE WHEN CORE OPEN", "THREE HITS THEN DOCK",
     3, SF_OBJECTIVE_CORE, SF_ENEMY_CHARGER, SF_HAZARD_VENT, 28, 25, 2, 2, 48, 20, 120, 60, 45, 0, 0, 0},
    {"LENS STACK", "GRAB THREE CELLS", "FIND THE COVER GAPS",
     3, SF_OBJECTIVE_SALVAGE, SF_ENEMY_CHARGER, SF_HAZARD_VENT, 34, 27, 2, 2, 44, 18, 112, 60, 45, 0, 0, 0},
    {"RELAY PRISM", "HOLD B AT LIT RELAY", "ACTIVATE IN ORDER",
     3, SF_OBJECTIVE_RELAY, SF_ENEMY_SWEEPER, SF_HAZARD_LASER, 18, 18, 14, 1, 44, 24, 112, 60, 45, 0, 344, 64},
    {"SHIELD FEED", "HOLD B AT EACH PANEL", "POWER THE NEXT PATH",
     3, SF_OBJECTIVE_REPAIR, SF_ENEMY_HUNTER, SF_HAZARD_VENT, 35, 17, 2, 2, 44, 18, 112, 60, 45, 0, 0, 0},
    {"LENS SENTINEL", "PULSE WHEN CORE OPEN", "THREE HITS THEN DOCK",
     3, SF_OBJECTIVE_CORE, SF_ENEMY_HUNTER, SF_HAZARD_LASER, 24, 24, 12, 1, 48, 18, 120, 60, 45, 0, 0, 0},
    {"ARRAY FOOT", "GRAB THREE CELLS", "FIND THE COVER GAPS",
     4, SF_OBJECTIVE_SALVAGE, SF_ENEMY_SWEEPER, SF_HAZARD_VENT, 23, 31, 2, 2, 44, 24, 112, 64, 45, 0, 0, 0},
    {"BEACON REPAIR", "HOLD B AT EACH PANEL", "POWER THE NEXT PATH",
     4, SF_OBJECTIVE_REPAIR, SF_ENEMY_HUNTER, SF_HAZARD_LASER, 16, 19, 12, 1, 44, 20, 112, 64, 45, 0, 352, 72},
    {"NAV RELAYS", "HOLD B AT LIT RELAY", "ACTIVATE IN ORDER",
     4, SF_OBJECTIVE_RELAY, SF_ENEMY_CHARGER, SF_HAZARD_VENT, 26, 21, 2, 2, 44, 20, 112, 64, 45, 0, 0, 0},
    {"ARRAY GUARDIAN", "PULSE WHEN CORE OPEN", "THREE HITS THEN DOCK",
     4, SF_OBJECTIVE_CORE, SF_ENEMY_CHARGER, SF_HAZARD_LASER, 23, 25, 12, 1, 48, 20, 120, 64, 45, 0, 0, 0},
    {"ANTENNA WALK", "GRAB THREE CELLS", "FIND THE COVER GAPS",
     4, SF_OBJECTIVE_SALVAGE, SF_ENEMY_HUNTER, SF_HAZARD_VENT, 19, 23, 2, 2, 44, 18, 112, 64, 45, 0, 0, 0},
    {"RETURN BUS", "HOLD B AT EACH PANEL", "POWER THE NEXT PATH",
     4, SF_OBJECTIVE_REPAIR, SF_ENEMY_SWEEPER, SF_HAZARD_LASER, 30, 20, 12, 1, 44, 24, 112, 64, 45, 0, 344, 64},
    {"SURVEYOR ROUTE", "STAY CLOSE TO CREW", "MARKERS THEN DOCK",
     4, SF_OBJECTIVE_ESCORT, SF_ENEMY_SWEEPER, SF_HAZARD_LASER, 19, 15, 14, 1, 44, 24, 112, 64, 45, 14, 0, 0},
    {"SKY WARDEN", "PULSE WHEN CORE OPEN", "THREE HITS THEN DOCK",
     4, SF_OBJECTIVE_CORE, SF_ENEMY_SWEEPER, SF_HAZARD_VENT, 27, 25, 2, 2, 48, 24, 120, 64, 45, 0, 0, 0},
    {"STATIC RIDGE", "GRAB THREE CELLS", "FIND THE COVER GAPS",
     4, SF_OBJECTIVE_SALVAGE, SF_ENEMY_CHARGER, SF_HAZARD_LASER, 26, 29, 12, 1, 44, 20, 112, 64, 45, 0, 0, 0},
    {"GROUND RELAYS", "HOLD B AT LIT RELAY", "ACTIVATE IN ORDER",
     4, SF_OBJECTIVE_RELAY, SF_ENEMY_HUNTER, SF_HAZARD_VENT, 14, 16, 2, 2, 44, 20, 112, 64, 45, 0, 344, 56},
    {"EMITTER REPAIR", "HOLD B AT EACH PANEL", "POWER THE NEXT PATH",
     4, SF_OBJECTIVE_REPAIR, SF_ENEMY_SWEEPER, SF_HAZARD_LASER, 17, 25, 12, 1, 44, 24, 112, 64, 45, 0, 0, 0},
    {"JAMMER CORE", "PULSE WHEN CORE OPEN", "THREE HITS THEN DOCK",
     4, SF_OBJECTIVE_CORE, SF_ENEMY_HUNTER, SF_HAZARD_VENT, 26, 24, 2, 2, 48, 20, 120, 64, 45, 0, 0, 0},
    {"FUSION APPROACH", "THREE IGNITION CELLS", "WEAVE THE HEAT FINS",
     5, SF_OBJECTIVE_SALVAGE, SF_ENEMY_CHARGER, SF_HAZARD_VENT, 26, 25, 2, 2, 48, 18, 100, 60, 45, 0, 0, 0},
    {"LENS GALLERY", "REPAIR THREE LENSES", "BRAKE BEHIND THE FIN",
     5, SF_OBJECTIVE_REPAIR, SF_ENEMY_SWEEPER, SF_HAZARD_LASER, 16, 24, 12, 1, 48, 24, 100, 60, 45, 0, 360, 56},
    {"COOLANT THROAT", "HOLD B AT LIT VALVE", "BRAKE AT BAFFLE ENDS",
     5, SF_OBJECTIVE_RELAY, SF_ENEMY_HUNTER, SF_HAZARD_VENT, 15, 19, 2, 2, 50, 18, 100, 60, 45, 0, 0, 0},
    {"IGNITION WARDEN", "THREE OPENING HITS", "BAIT THE WARDEN WIDE",
     5, SF_OBJECTIVE_CORE, SF_ENEMY_CHARGER, SF_HAZARD_LASER, 22, 27, 12, 1, 52, 20, 108, 62, 45, 0, 0, 0},
    {"ANTENNA ROOT", "LINK THREE BEACONS", "CUT ACROSS THE RIBS",
     5, SF_OBJECTIVE_RELAY, SF_ENEMY_SWEEPER, SF_HAZARD_LASER, 16, 22, 8, 1, 48, 24, 100, 60, 45, 0, 0, 0},
    {"HELIOS CONTROL", "RESTORE THE STAR BUS", "B45 REPAIR ANY ORDER",
     5, SF_OBJECTIVE_REPAIR, SF_ENEMY_CHARGER, SF_HAZARD_VENT, 27, 25, 2, 2, 50, 18, 100, 60, 45, 0, 352, 56},
    {"LIFELINE GANTRY", "STAY NEAR THE CREW", "ESCORT TO THE DOCK",
     5, SF_OBJECTIVE_ESCORT, SF_ENEMY_HUNTER, SF_HAZARD_LASER, 28, 14, 10, 1, 54, 22, 100, 60, 45, 15, 0, 0},
    {"CORONA SENTINEL", "READ THE AXIS LOCK", "THREE CYAN PULSES",
     5, SF_OBJECTIVE_CORE, SF_ENEMY_SWEEPER, SF_HAZARD_VENT, 27, 25, 2, 2, 54, 24, 112, 64, 45, 0, 0, 0},
    {"EVENT SPINE", "RECOVER THREE KEYS", "HUNTER USES THE GAPS",
     5, SF_OBJECTIVE_SALVAGE, SF_ENEMY_HUNTER, SF_HAZARD_LASER, 23, 23, 8, 1, 50, 20, 100, 60, 45, 0, 0, 0},
    {"ENGINE BALANCE", "BALANCE THREE COILS", "REPAIR IN YOUR ORDER",
     5, SF_OBJECTIVE_REPAIR, SF_ENEMY_CHARGER, SF_HAZARD_VENT, 20, 16, 2, 2, 54, 22, 100, 60, 45, 0, 344, 72},
    {"CROWN NETWORK", "LINK THE CROWN NODES", "USE THE AXIS SHELTER",
     5, SF_OBJECTIVE_RELAY, SF_ENEMY_SWEEPER, SF_HAZARD_LASER, 15, 18, 9, 1, 52, 24, 100, 60, 45, 0, 0, 0},
    {"STAR ENGINE HEART", "PULSE THREE OPENINGS", "BRING THE HEART HOME",
     5, SF_OBJECTIVE_CORE, SF_ENEMY_CHARGER, SF_HAZARD_LASER, 19, 28, 14, 1, 56, 24, 120, 64, 45, 0, 0, 0},
    {"AIRLOCK", "GRAB THREE CELLS", "DASH LOCKS ON AMBER",
     0, SF_OBJECTIVE_SALVAGE, SF_ENEMY_CHARGER, SF_HAZARD_NONE, 0, 0, 0, 0, 42, 18, 60, 56, 45, 0, 0, 0},
    {"CARGO SPINE", "BRAKE AROUND CRATES", "CROSS AFTER THE DASH",
     0, SF_OBJECTIVE_SALVAGE, SF_ENEMY_SWEEPER, SF_HAZARD_NONE, 0, 0, 0, 0, 40, 24, 60, 56, 45, 0, 0, 0},
    {"SIGNAL ROOM", "HOLD B AT LIT RELAY", "ACTIVATE IN ORDER",
     0, SF_OBJECTIVE_RELAY, SF_ENEMY_CHARGER, SF_HAZARD_NONE, 0, 0, 0, 0, 38, 18, 60, 56, 45, 0, 0, 0},
    {"DOCK LOCK", "RESTORE THE DOCK", "HUNTER MOVES BETWEEN",
     0, SF_OBJECTIVE_SALVAGE, SF_ENEMY_HUNTER, SF_HAZARD_NONE, 0, 0, 0, 0, 38, 18, 64, 56, 45, 0, 0, 0},
    {"PUMP GARDEN", "COLLECT IN COOLANT", "AMBER VENTS THEN RED",
     1, SF_OBJECTIVE_SALVAGE, SF_ENEMY_HUNTER, SF_HAZARD_VENT, 8, 7, 2, 2, 36, 18, 60, 60, 45, 0, 0, 0},
    {"HEAT EXCHANGE", "HOLD B AT EACH RELAY", "TIME THE VENT CYCLE",
     1, SF_OBJECTIVE_RELAY, SF_ENEMY_SWEEPER, SF_HAZARD_VENT, 8, 9, 2, 2, 36, 24, 60, 60, 45, 0, 0, 0},
    {"PRISM BRIDGE", "RETRIEVE THE SHARDS", "WAIT FOR LASER DIM",
     1, SF_OBJECTIVE_SALVAGE, SF_ENEMY_CHARGER, SF_HAZARD_LASER, 2, 5, 16, 1, 34, 20, 54, 60, 45, 0, 0, 0},
    {"MANIFOLD", "RESTART THREE VALVES", "BRAKE AT LIT VALVE",
     1, SF_OBJECTIVE_RELAY, SF_ENEMY_HUNTER, SF_HAZARD_LASER, 2, 4, 16, 1, 34, 20, 60, 60, 45, 0, 0, 0},
    {"OUTER ARRAY", "GRAB THREE BEACONS", "CROSS BETWEEN BEAMS",
     2, SF_OBJECTIVE_SALVAGE, SF_ENEMY_HUNTER, SF_HAZARD_LASER, 2, 5, 16, 1, 32, 20, 60, 64, 45, 0, 0, 0},
    {"ION GALLERY", "HOLD B AT LIT RELAY", "SWEEPER PICKS A LINE",
     2, SF_OBJECTIVE_RELAY, SF_ENEMY_SWEEPER, SF_HAZARD_LASER, 2, 5, 16, 1, 32, 26, 54, 64, 45, 0, 0, 0},
    {"CAPACITOR HALL", "RECOVER THREE CORES", "VENTS WARN IN AMBER",
     2, SF_OBJECTIVE_SALVAGE, SF_ENEMY_CHARGER, SF_HAZARD_VENT, 8, 9, 2, 2, 30, 22, 52, 64, 45, 0, 0, 0},
    {"WARDEN CORE", "PULSE WHEN CORE OPEN", "THREE HITS THEN DOCK",
     2, SF_OBJECTIVE_CORE, SF_ENEMY_CHARGER, SF_HAZARD_VENT, 13, 9, 2, 2, 45, 24, 96, 64, 45, 0, 0, 0},
};
static const char mission_names[SF_MISSION_COUNT][21] = {
    "SALVAGE SIGNAL",
    "BULKHEAD CIRCUIT",
    "RESCUE PASSAGE",
    "PRESSURE NETWORK",
    "CREW TRANSFER",
    "COOLANT RESTART",
    "FOUNDRY ACCESS",
    "SHIFT EVACUATION",
    "HEAT GRID",
    "ARCHIVE UPLINK",
    "SIGNAL RESCUE",
    "LENS ALIGNMENT",
    "BEACON ARRAY",
    "NAVIGATION RESCUE",
    "GROUND THE JAMMER",
    "IGNITION TRAIL",
    "LAST SIGNAL",
    "STARFALL HEART",
};
static const upoint16_t route_2[14] = {
    {2592u,8864u},
    {10272u,8864u},
    {10272u,7840u},
    {10272u,6560u},
    {8224u,6560u},
    {8224u,3232u},
    {6432u,3232u},
    {3232u,3232u},
    {3232u,1952u},
    {2848u,1952u},
    {3232u,1952u},
    {3232u,8352u},
    {1312u,8352u},
    {1312u,9376u},
};
static const upoint16_t route_10[19] = {
    {2592u,8864u},
    {10272u,8864u},
    {10272u,8352u},
    {11296u,8352u},
    {11296u,6304u},
    {8736u,6304u},
    {8736u,1184u},
    {5664u,1184u},
    {5664u,2976u},
    {5664u,1184u},
    {2848u,1184u},
    {2848u,4512u},
    {1824u,4512u},
    {2848u,4512u},
    {2848u,5280u},
    {800u,5280u},
    {800u,8352u},
    {1312u,8352u},
    {1312u,9376u},
};
static const upoint16_t route_18[18] = {
    {2592u,8864u},
    {5664u,8864u},
    {5664u,6560u},
    {6432u,6560u},
    {5664u,6560u},
    {5664u,5536u},
    {11296u,5536u},
    {11296u,2976u},
    {10528u,2976u},
    {11296u,2976u},
    {11296u,1184u},
    {2336u,1184u},
    {2336u,2976u},
    {2336u,6560u},
    {544u,6560u},
    {544u,8352u},
    {1312u,8352u},
    {1312u,9376u},
};
static const upoint16_t route_30[16] = {
    {2592u,8864u},
    {3872u,8864u},
    {3872u,8096u},
    {10784u,8096u},
    {10784u,8352u},
    {10784u,5536u},
    {5664u,5536u},
    {5664u,3488u},
    {5664u,5536u},
    {2336u,5536u},
    {2336u,5280u},
    {2336u,5536u},
    {544u,5536u},
    {544u,8352u},
    {1312u,8352u},
    {1312u,9376u},
};
static const upoint16_t route_42[16] = {
    {2592u,8864u},
    {10784u,8864u},
    {10784u,7840u},
    {10784u,6816u},
    {8480u,6816u},
    {8480u,2976u},
    {6176u,2976u},
    {3616u,2976u},
    {3616u,1696u},
    {2336u,1696u},
    {3616u,1696u},
    {3616u,7584u},
    {2592u,7584u},
    {2592u,8352u},
    {1312u,8352u},
    {1312u,9376u},
};
static const upoint16_t route_54[14] = {
    {2592u,8864u},
    {2592u,7840u},
    {544u,7840u},
    {544u,5536u},
    {4640u,5536u},
    {4640u,1696u},
    {9248u,1696u},
    {9248u,3488u},
    {11296u,3488u},
    {11296u,7840u},
    {8736u,7840u},
    {8736u,8864u},
    {1312u,8864u},
    {1312u,9376u},
};
static const upoint16_t route_66[15] = {
    {2848u,8864u},
    {6432u,8864u},
    {6432u,7072u},
    {9504u,7072u},
    {9504u,3232u},
    {10528u,3232u},
    {10528u,1696u},
    {6944u,1696u},
    {6944u,4512u},
    {4384u,4512u},
    {4384u,6560u},
    {2336u,6560u},
    {2336u,8352u},
    {1312u,8352u},
    {1312u,9376u},
};
typedef struct { UBYTE opcode, size, exception; far_ptr_t destination; } sf_scene_change_t;
typedef char scene_change_is_six_bytes[(sizeof(sf_scene_change_t)==6u)?1:-1];
BANKREF_EXTERN(sf_room_changes)
BANKREF(sf_room_changes)
static const sf_scene_change_t sf_room_changes[SF_ROOM_COUNT] = {
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_01_room_00)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_01_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_01_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_01_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_02_room_00)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_02_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_02_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_02_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_03_room_00)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_03_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_03_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_03_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_04_room_00)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_04_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_04_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_04_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_05_room_00)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_05_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_05_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_05_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_06_room_00)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_06_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_06_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_06_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_07_room_00)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_07_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_07_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_07_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_08_room_00)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_08_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_08_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_08_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_09_room_00)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_09_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_09_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_09_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_10_room_00)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_10_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_10_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_10_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_11_room_00)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_11_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_11_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_11_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_12_room_00)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_12_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_12_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_12_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_13_room_00)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_13_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_13_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_13_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_14_room_00)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_14_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_14_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_14_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_15_room_00)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_15_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_15_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_15_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_16_room_00)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_16_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_16_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_16_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_17_room_00)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_17_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_17_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_17_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_18_room_00)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_18_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_18_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_mission_18_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_room_01)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_room_02)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_room_03)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_room_04)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_room_05)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_room_06)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_room_07)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_room_08)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_room_09)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_room_10)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_room_11)},
    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(scene_room_12)},
};
void starfall_room_read(UBYTE index, sf_room_t *dest) BANKED {
    if (index>=SF_ROOM_COUNT) index=SF_ROOM_COUNT-1u;
    memcpy(dest,&rooms[index],sizeof(sf_room_t));
}
void starfall_mission_name(UBYTE index, char *dest) BANKED {
    if (index>=SF_MISSION_COUNT) index=SF_MISSION_COUNT-1u;
    memcpy(dest,mission_names[index],21u);
}
UBYTE starfall_room_route(UBYTE index, upoint16_t *dest) BANKED {
    switch(index) {
        case 2u: memcpy(dest,route_2,sizeof(route_2)); return 14u;
        case 10u: memcpy(dest,route_10,sizeof(route_10)); return 19u;
        case 18u: memcpy(dest,route_18,sizeof(route_18)); return 18u;
        case 30u: memcpy(dest,route_30,sizeof(route_30)); return 16u;
        case 42u: memcpy(dest,route_42,sizeof(route_42)); return 16u;
        case 54u: memcpy(dest,route_54,sizeof(route_54)); return 14u;
        case 66u: memcpy(dest,route_66,sizeof(route_66)); return 15u;
        default: return 0;
    }
}
UBYTE starfall_room_change(UBYTE index) BANKED {
    if (index>=SF_ROOM_COUNT) return FALSE;
    if (!script_execute(BANK(sf_room_changes),(UBYTE *)&sf_room_changes[index],0,0)) return FALSE;
    fade_out_modal();
    PLAYER.pos.x = index<SF_STORY_ROOM_COUNT ? 41u*32u : 9u*256u;
    PLAYER.pos.y = index<SF_STORY_ROOM_COUNT ? 293u*32u : 13u*256u;
    PLAYER.dir=DIR_UP; camera_settings=CAMERA_LOCK_FLAG;
    return TRUE;
}

UBYTE starfall_checkpoint_valid(const sf_save_t *saved) BANKED {
    UBYTE index = saved->room;
    UBYTE local = index & 3u;
    if (index >= SF_STORY_ROOM_COUNT || !(saved->mission_flags & 0x80000000UL)) return FALSE;
    switch (saved->checkpoint_stage) {
        case SF_SAVE_STAGE_LAUNCH:
            return (local == 0u && !saved->room_clear_mask) ||
                (local == 1u && (saved->room_clear_mask == 1u || saved->room_clear_mask == 5u)) ||
                (local == 2u && (saved->room_clear_mask == 1u || saved->room_clear_mask == 3u)) ||
                (local == 3u && saved->room_clear_mask == 7u);
        case SF_SAVE_STAGE_RESULT:
            return (local == 1u && (saved->room_clear_mask == 3u || saved->room_clear_mask == 7u)) ||
                (local == 2u && (saved->room_clear_mask == 5u || saved->room_clear_mask == 7u));
        case SF_SAVE_STAGE_BRANCH: return local == 0u && saved->room_clear_mask == 1u;
        case SF_SAVE_STAGE_MISSION_BOARD: return TRUE;
        case SF_SAVE_STAGE_MISSION_COMPLETE: return local == 3u && saved->room_clear_mask == 15u;
        case SF_SAVE_STAGE_ENDING:
            return index == SF_STORY_ROOM_COUNT - 1u && saved->campaign_complete;
        default: return FALSE;
    }
}
