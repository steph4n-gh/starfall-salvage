#ifndef STARFALL_WORLD_H
#define STARFALL_WORLD_H

#include <gbdk/platform.h>
#include "math.h"

/* Engine actor positions/bounds use 32 subpixels per pixel. Geometry below
 * uses signed pixel centers; target_delta returns signed subpixels per frame. */
void starfall_world_actor_center(UBYTE actor_index, point16_t *center) BANKED;

/* The safe dock follows the real terminal actor (index 4), not a screen row. */
UBYTE starfall_world_dock_contains(WORD center_x, WORD center_y) BANKED;

/* Radius-six enemy AABB against every occupied native collision tile and
 * the real loaded image dimensions. Dock policy remains with the caller. */
UBYTE starfall_world_enemy_blocked(WORD center_x, WORD center_y) BANKED;

/* Acquire a committed target vector once during warning. speed is capped at
 * 64 subpixels/frame; zero target/speed returns zero, with no 16-bit squares. */
void starfall_world_target_delta(WORD dx, WORD dy, UBYTE speed, point16_t *delta) BANKED;

#endif
