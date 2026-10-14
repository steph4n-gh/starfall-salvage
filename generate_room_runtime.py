"""Compile authored mission and legacy Arcade metadata into native banked tables.

No geometry or gameplay is generated here. Stable native scene symbols, actual
actor-anchor routes and strings come from the reviewed mission resources.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
missions = [json.loads((ROOT / p).read_text()) for p in
            json.loads((ROOT / 'campaign/active-missions.json').read_text())]
legacy = json.loads((ROOT / 'campaign/rooms.json').read_text())
rooms = [room for mission in missions for room in mission['rooms']] + legacy
story_count = len(missions) * 4
assert len(rooms) == story_count + 12
header = '''#ifndef STARFALL_ROOMS_H
#define STARFALL_ROOMS_H
#include <gbdk/platform.h>
#include "math.h"
#include "starfall_save.h"
#define SF_MISSION_COUNT %du
#define SF_STORY_ROOM_COUNT %du
#define SF_ARCADE_FIRST SF_STORY_ROOM_COUNT
#define SF_ARCADE_ROOM_COUNT 12u
#define SF_ROOM_COUNT %du
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
''' % (len(missions),story_count,len(rooms))
source = '''#pragma bank 255
#include <gbdk/platform.h>
#include <string.h>
#include "actor.h"
#include "bankdata.h"
#include "camera.h"
#include "fade_manager.h"
#include "vm.h"
#include "vm_exceptions.h"
#include "starfall_rooms.h"
'''
for room in rooms:
    source += '#include "data/%s.h"\n' % room['scene_symbol']
source += 'static const sf_room_t rooms[SF_ROOM_COUNT] = {\n'
for room in rooms:
    strings = [room[k] for k in ['name','brief1','brief2']]
    assert all(len(s) <= 20 and s == s.upper() for s in strings), strings
    cache = room.get('optional_cache_marker') or [0,0]
    route = room.get('escort_route') or []
    assert len(route) <= 20
    nums = [str(room['zone']), 'SF_OBJECTIVE_'+room['objective'].upper(),
            'SF_ENEMY_'+room['enemy'].upper(), 'SF_HAZARD_'+room['hazard'].upper()]
    nums += [str(v) for v in room['hazard_rect']]
    nums += [str(room[k]) for k in ['warning_frames','dash_frames','recover_frames','speed']]
    nums += ['45',str(len(route)),str(cache[0]),str(cache[1])]
    source += '    {%s,\n     %s},\n' % (', '.join(json.dumps(s) for s in strings), ', '.join(nums))
source += '};\nstatic const char mission_names[SF_MISSION_COUNT][21] = {\n'
for mission in missions:
    assert len(mission['name']) <= 20
    source += '    '+json.dumps(mission['name'])+',\n'
source += '};\n'
for index,room in enumerate(rooms):
    route = room.get('escort_route') or []
    if route:
        # Astronaut crew's actual inclusive midpoint is +7px x/+3px y.
        source += 'static const upoint16_t route_%d[%d] = {\n' % (index,len(route))
        source += ''.join('    {%du,%du},\n' % ((x-7)*32,(y-3)*32) for x,y in route)
        source += '};\n'
source += '''typedef struct { UBYTE opcode, size, exception; far_ptr_t destination; } sf_scene_change_t;
typedef char scene_change_is_six_bytes[(sizeof(sf_scene_change_t)==6u)?1:-1];
BANKREF_EXTERN(sf_room_changes)
BANKREF(sf_room_changes)
static const sf_scene_change_t sf_room_changes[SF_ROOM_COUNT] = {
'''
source += ''.join('    {0x27,3,EXCEPTION_CHANGE_SCENE,TO_FAR_PTR_T(%s)},\n' % r['scene_symbol'] for r in rooms)
source += '''};
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
'''
for index,room in enumerate(rooms):
    route = room.get('escort_route') or []
    if route:
        source += '        case %du: memcpy(dest,route_%d,sizeof(route_%d)); return %du;\n' % (index,index,index,len(route))
source += '''        default: return 0;
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
'''
source += '\nUBYTE starfall_checkpoint_valid(const sf_save_t *saved) BANKED {\n    UBYTE index = saved->room;\n    UBYTE local = index & 3u;\n    if (index >= SF_STORY_ROOM_COUNT || !(saved->mission_flags & 0x80000000UL)) return FALSE;\n    switch (saved->checkpoint_stage) {\n        case SF_SAVE_STAGE_LAUNCH:\n            return (local == 0u && !saved->room_clear_mask) ||\n                (local == 1u && (saved->room_clear_mask == 1u || saved->room_clear_mask == 5u)) ||\n                (local == 2u && (saved->room_clear_mask == 1u || saved->room_clear_mask == 3u)) ||\n                (local == 3u && saved->room_clear_mask == 7u);\n        case SF_SAVE_STAGE_RESULT:\n            return (local == 1u && (saved->room_clear_mask == 3u || saved->room_clear_mask == 7u)) ||\n                (local == 2u && (saved->room_clear_mask == 5u || saved->room_clear_mask == 7u));\n        case SF_SAVE_STAGE_BRANCH: return local == 0u && saved->room_clear_mask == 1u;\n        case SF_SAVE_STAGE_MISSION_BOARD: return TRUE;\n        case SF_SAVE_STAGE_MISSION_COMPLETE: return local == 3u && saved->room_clear_mask == 15u;\n        case SF_SAVE_STAGE_ENDING:\n            return index == SF_STORY_ROOM_COUNT - 1u && saved->campaign_complete;\n        default: return FALSE;\n    }\n}\n'
(ROOT/'plugins/starfall/engine/include/starfall_rooms.h').write_text(header)
(ROOT/'plugins/starfall/engine/src/starfall_rooms.c').write_text(source)
print(f'{len(missions)} authored missions, {story_count} Story rooms, {len(legacy)} Arcade rooms')
