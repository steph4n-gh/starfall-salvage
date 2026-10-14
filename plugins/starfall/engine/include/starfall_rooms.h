#ifndef STARFALL_ROOMS_H
#define STARFALL_ROOMS_H
#include <gbdk/platform.h>
#include "math.h"
#include "starfall_save.h"
#define SF_MISSION_COUNT 18u
#define SF_STORY_ROOM_COUNT 72u
#define SF_ARCADE_FIRST SF_STORY_ROOM_COUNT
#define SF_ARCADE_ROOM_COUNT 12u
#define SF_ROOM_COUNT 84u
enum { SF_OBJECTIVE_SALVAGE, SF_OBJECTIVE_RELAY, SF_OBJECTIVE_CORE,
       SF_OBJECTIVE_REPAIR, SF_OBJECTIVE_ESCORT };
enum { SF_ENEMY_CHARGER, SF_ENEMY_SWEEPER, SF_ENEMY_HUNTER };
enum { SF_HAZARD_NONE, SF_HAZARD_VENT, SF_HAZARD_LASER };
typedef struct {
    char name[21], brief1[21], brief2[21];
    UBYTE zone, objective, enemy, hazard;
    UBYTE hazard_x, hazard_y, hazard_w, hazard_h;
    UBYTE warning_frames, dash_frames, recover_frames, speed;
    UBYTE hold_ticks, route_count;
    UWORD cache_x, cache_y;
} sf_room_t;
void starfall_room_read(UBYTE index, sf_room_t *dest) BANKED;
UBYTE starfall_checkpoint_valid(const sf_save_t *saved) BANKED;
void starfall_mission_name(UBYTE index, char *dest) BANKED;
UBYTE starfall_room_route(UBYTE index, upoint16_t *dest) BANKED;
UBYTE starfall_room_change(UBYTE index) BANKED;
#endif
