#ifndef STARFALL_ENCOUNTER_H
#define STARFALL_ENCOUNTER_H

#include <gbdk/platform.h>

/* Project-local adventure hook; checkpoint events use cartridge save RAM. */
void starfall_encounter_init(void) BANKED;
UBYTE starfall_encounter_update(void) BANKED;

/* Count genuine PLAY updates, excluding menus and pause, for frame-budget QA. */
extern UWORD sf_gameplay_ticks;

enum {
    SF_MODE_TITLE, SF_MODE_PLAY, SF_MODE_PAUSE, SF_MODE_RESULT,
    SF_MODE_FAILURE, SF_MODE_ENDING, SF_MODE_ARCADE_DOCK, SF_MODE_UPGRADE,
    SF_MODE_BANK_RESULT, SF_MODE_LAUNCH, SF_MODE_EXIT_CONFIRM,
    SF_MODE_TRANSITION, SF_MODE_LOAD_BUSY, SF_MODE_NEW_STORY_CONFIRM,
    SF_MODE_BRANCH, SF_MODE_MISSION_BOARD, SF_MODE_MISSION_COMPLETE
};
extern UBYTE sf_room_index, sf_mode_index, sf_objective_progress, sf_boss_hp;
extern UBYTE sf_hull_value, sf_arcade_sector;
extern UBYTE sf_drone_phase_value, sf_drone_timer_value;
extern UBYTE sf_save_status;
extern UBYTE sf_crew_hp, sf_branch_order, sf_room_clear_mask, sf_mission_cursor;

#endif
