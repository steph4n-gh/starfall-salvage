#pragma bank 255

#include <gbdk/platform.h>
#include <stdint.h>
#include "actor.h"
#include "collision.h"
#include "data_manager.h"
#include "starfall_world.h"

#define WORLD_TERMINAL_ACTOR 4u
#define ENEMY_RADIUS 6u

/* Integer restoring square root needs at most sixteen iterations. It runs
 * only at target acquisition, never in the per-frame movement/collision path. */
static uint32_t world_isqrt32(uint32_t n) {
    uint32_t result = 0, bit = 0x40000000UL;
    while (bit > n) bit >>= 2;
    while (bit) {
        if (n >= result + bit) {
            n -= result + bit;
            result = (result >> 1) + bit;
        } else result >>= 1;
        bit >>= 2;
    }
    return result;
}

void starfall_world_actor_center(UBYTE actor_index, point16_t *center) BANKED {
    actor_t *actor = &actors[actor_index];
    /* Preserve the existing signed midpoint rounding, including a -1 bounds
     * midpoint. Widen before adding so unsigned positions cannot wrap a WORD. */
    center->x = ((int32_t)actor->pos.x + (((int32_t)actor->bounds.left + actor->bounds.right) >> 1)) >> 5;
    center->y = ((int32_t)actor->pos.y + (((int32_t)actor->bounds.top + actor->bounds.bottom) >> 1)) >> 5;
}

UBYTE starfall_world_dock_contains(WORD center_x, WORD center_y) BANKED {
    point16_t dock;
    WORD dx, dy;
    starfall_world_actor_center(WORLD_TERMINAL_ACTOR, &dock);
    dx = center_x - dock.x;
    dy = center_y - dock.y;
    return dx >= -24 && dx <= 24 && dy >= -20 && dy <= 20;
}

UBYTE starfall_world_enemy_blocked(WORD center_x, WORD center_y) BANKED {
    UBYTE tx, ty, left, right, top, bottom;
    /* Pixel dimensions come from the actual scene, including scrolling maps.
     * A radius-six inclusive box cannot touch pixels beyond width-1/height-1. */
    if (image_width <= ENEMY_RADIUS * 2u || image_height <= ENEMY_RADIUS * 2u ||
        center_x < ENEMY_RADIUS || center_y < ENEMY_RADIUS ||
        (UWORD)center_x >= image_width - ENEMY_RADIUS ||
        (UWORD)center_y >= image_height - ENEMY_RADIUS) return TRUE;
    left = (center_x - ENEMY_RADIUS) >> 3;
    right = (center_x + ENEMY_RADIUS) >> 3;
    top = (center_y - ENEMY_RADIUS) >> 3;
    bottom = (center_y + ENEMY_RADIUS) >> 3;
    /* Thirteen pixels span at most three tiles per axis; inspect all nine,
     * rather than only corners, so a thin internal wall cannot be skipped. */
    for (ty = top; ty <= bottom; ++ty) {
        for (tx = left; tx <= right; ++tx) {
            if (tile_at(tx, ty) & COLLISION_ALL) return TRUE;
        }
    }
    return FALSE;
}

void starfall_world_target_delta(WORD dx, WORD dy, UBYTE speed, point16_t *delta) BANKED {
    int32_t x = dx, y = dy;
    uint32_t ax, ay, squared, length;
    delta->x = delta->y = 0;
    if (!speed || (!dx && !dy)) return;
    if (speed > 64u) speed = 64u;
    ax = x < 0 ? (uint32_t)-x : (uint32_t)x;
    ay = y < 0 ? (uint32_t)-y : (uint32_t)y;
    /* A 384x320 target can exceed 65535 squared pixels. WORD endpoints also
     * permit -32768; widening before absolute value handles that endpoint. */
    squared = ax * ax + ay * ay;
    length = world_isqrt32(squared);
    if (length * length < squared) ++length;
    /* Ceil length and signed truncation keep diagonal speed at or below the
     * requested magnitude. Reuse this fixed vector throughout the charge. */
    delta->x = (x * speed) / (int32_t)length;
    delta->y = (y * speed) / (int32_t)length;
}
