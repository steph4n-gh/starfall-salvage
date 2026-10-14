#ifndef STARFALL_OBJECTIVES_H
#define STARFALL_OBJECTIVES_H

#include <gbdk/platform.h>
#include "math.h"

#define SF_OBJECTIVE_READY    0x01u
#define SF_OBJECTIVE_FAILED   0x02u
#define SF_OBJECTIVE_BLOCKED  0x04u
#define SF_OBJECTIVE_ADVANCED 0x08u

/* Caller-owned, per-room state. progress is the number of completed nodes,
 * hold is eligible repair updates, active_node is 0..2 or 255, and waypoint
 * is the next escort route entry. READY/FAILED latch; other flags last one
 * update. The caller may latch FAILED after an independently verified hit. */
typedef struct {
    UBYTE completed_mask, progress, hold, active_node, waypoint, flags;
} sf_objective_state_t;

/* Reset numeric state only. The scene owner restores authored actors and
 * shows crew actor 7 for escort; this module never resets their positions. */
void starfall_objective_init(sf_objective_state_t *state) BANKED;

/* Call once per PLAY update with sampled joypad bits. Continuous B within
 * 12 pixels of one unfinished station (actors 1..3) completes hold_ticks.
 * Release, leave, or change stations resets dwell; A does not interrupt B.
 * A completed station hides once. Keep hold_ticks stable until the next
 * init; zero hold_ticks is invalid metadata. */
UBYTE starfall_repair_update(sf_objective_state_t *state, UBYTE buttons,
                             UBYTE hold_ticks) BANKED;

/* Authored axis-aligned route entries are native actor-anchor positions:
 * 32 subpixels per pixel, NOT sprite centers. The array may be in banked
 * ROM, fixed-bank ROM, or RAM (bank 0). Crew actor 7 moves at most 20
 * subpixels per PLAY update while the player is within 24 pixels. Every
 * touched collision tile is tested using the crew's actual native bounds.
 * Keep the route pointer, bank and count stable until the next init.
 * BLOCKED stops movement, without inventing a path or failing the mission.
 * Crew proximity completes/hides the three actual markers once. READY
 * requires all three plus exact final route arrival inside terminal safety.
 * FAILED reports missing actors, invalid route/bounds, or an incomplete
 * marker route; crew HP and enemy threat targeting remain caller-owned. */
UBYTE starfall_escort_update(sf_objective_state_t *state,
                             const upoint16_t *waypoints, UBYTE bank,
                             UBYTE count) BANKED;

#endif
