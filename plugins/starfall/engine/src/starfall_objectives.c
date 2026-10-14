#pragma bank 255

#include <gbdk/platform.h>
#include <stdint.h>
#include "actor.h"
#include "bankdata.h"
#include "collision.h"
#include "data_manager.h"
#include "starfall_objectives.h"
#include "starfall_world.h"

#define FIRST_NODE 1u
#define NODE_COUNT 3u
#define CREW_ACTOR 7u
#define NO_NODE 255u
#define NODE_RADIUS 12u
#define CREW_RADIUS 24u
#define CREW_SPEED 20u
#define ALL_NODES 0x07u
#define TERMINAL_FLAGS (SF_OBJECTIVE_READY | SF_OBJECTIVE_FAILED)

static UBYTE actors_near(UBYTE a, UBYTE b, UBYTE radius) {
    point16_t first, second;
    WORD dx, dy;
    starfall_world_actor_center(a, &first);
    starfall_world_actor_center(b, &second);
    dx = first.x - second.x;
    dy = first.y - second.y;
    /* Reject far world coordinates before multiplying signed WORDs. */
    if (dx < -(WORD)radius || dx > radius || dy < -(WORD)radius || dy > radius) return FALSE;
    return dx * dx + dy * dy <= (UWORD)radius * radius;
}

static void complete_node(sf_objective_state_t *state, UBYTE node) {
    actor_t *actor = &actors[FIRST_NODE + node];
    state->completed_mask |= 1u << node;
    if (state->progress < NODE_COUNT) ++state->progress;
    state->flags |= SF_OBJECTIVE_ADVANCED;
    actor->flags |= ACTOR_FLAG_HIDDEN;
    actor->flags &= ~ACTOR_FLAG_COLLISION;
    actor->collision_group = COLLISION_GROUP_NONE;
    deactivate_actor(actor);
}

static UBYTE crew_blocked(const upoint16_t *position) {
    actor_t *crew = &actors[CREW_ACTOR];
    WORD left, right, top, bottom;
    UBYTE tx, ty, first_x, last_x, first_y, last_y;
    /* Widen before adding signed bounds to unsigned actor positions. Foot
     * bounds are the resource's real bounds, including fractional offsets. */
    left = ((int32_t)position->x + crew->bounds.left) >> 5;
    right = ((int32_t)position->x + crew->bounds.right) >> 5;
    top = ((int32_t)position->y + crew->bounds.top) >> 5;
    bottom = ((int32_t)position->y + crew->bounds.bottom) >> 5;
    if (left < 0 || top < 0 || (UWORD)right >= image_width ||
        (UWORD)bottom >= image_height) return TRUE;
    first_x = left >> 3; last_x = right >> 3;
    first_y = top >> 3; last_y = bottom >> 3;
    /* A normal 16x8 footprint touches at most six tiles. Test all touched
     * tiles, including an internal wall between opposite corners. */
    for (ty = first_y; ty <= last_y; ++ty) {
        for (tx = first_x; tx <= last_x; ++tx) {
            if (tile_at(tx,ty) & COLLISION_ALL) return TRUE;
        }
    }
    return FALSE;
}

static void crew_markers(sf_objective_state_t *state) {
    UBYTE node;
    for (node = 0; node != NODE_COUNT; ++node) {
        if (!(state->completed_mask & (1u << node)) &&
            actors_near(CREW_ACTOR,FIRST_NODE + node,NODE_RADIUS)) complete_node(state,node);
    }
}

static void escort_goal(sf_objective_state_t *state) {
    point16_t center;
    starfall_world_actor_center(CREW_ACTOR,&center);
    if ((state->completed_mask & ALL_NODES) == ALL_NODES &&
        starfall_world_dock_contains(center.x,center.y)) state->flags |= SF_OBJECTIVE_READY;
    else state->flags |= SF_OBJECTIVE_FAILED;
}

void starfall_objective_init(sf_objective_state_t *state) BANKED {
    state->completed_mask = state->progress = state->hold = state->waypoint = state->flags = 0;
    state->active_node = NO_NODE;
}

UBYTE starfall_repair_update(sf_objective_state_t *state, UBYTE buttons,
                             UBYTE hold_ticks) BANKED {
    UBYTE node, chosen = NO_NODE;
    state->flags &= TERMINAL_FLAGS;
    if (state->flags) return state->flags;
    /* actors_len includes the player: scene.n_actors + 1, in data_manager. */
    if (actors_len < FIRST_NODE + NODE_COUNT || !hold_ticks) {
        state->flags = SF_OBJECTIVE_FAILED;
        return state->flags;
    }
    if (buttons & J_B) {
        for (node = 0; node != NODE_COUNT; ++node) {
            if (!(state->completed_mask & (1u << node)) && actors_near(0,FIRST_NODE + node,NODE_RADIUS)) {
                chosen = node;
                break;
            }
        }
    }
    if (chosen == NO_NODE) {
        state->hold = 0;
        state->active_node = NO_NODE;
        return state->flags;
    }
    if (state->active_node != chosen) {
        state->active_node = chosen;
        state->hold = 0;
    }
    if (state->hold < hold_ticks) ++state->hold;
    if (state->hold == hold_ticks) {
        complete_node(state,chosen);
        state->hold = 0;
        state->active_node = NO_NODE;
        if ((state->completed_mask & ALL_NODES) == ALL_NODES) state->flags |= SF_OBJECTIVE_READY;
    }
    return state->flags;
}

UBYTE starfall_escort_update(sf_objective_state_t *state,
                             const upoint16_t *waypoints, UBYTE bank,
                             UBYTE count) BANKED {
    actor_t *crew = &actors[CREW_ACTOR];
    upoint16_t target, candidate;
    UWORD remaining;
    state->flags &= TERMINAL_FLAGS;
    if (state->flags) return state->flags;
    if (actors_len <= CREW_ACTOR || !waypoints || !count || state->waypoint > count ||
        crew->bounds.left > crew->bounds.right || crew->bounds.top > crew->bounds.bottom) {
        state->flags = SF_OBJECTIVE_FAILED;
        return state->flags;
    }
    crew_markers(state);
    if (state->waypoint == count) {
        escort_goal(state);
        return state->flags;
    }
    if (bank) MemcpyBanked(&target,&waypoints[state->waypoint],sizeof(target),bank);
    else target = waypoints[state->waypoint];
    if (target.x >= image_width_subpx || target.y >= image_height_subpx ||
        (crew->pos.x != target.x && crew->pos.y != target.y)) {
        /* An authored axis route never chooses an unvalidated diagonal or
         * invents an L-shaped shortcut around a wall. */
        state->flags |= SF_OBJECTIVE_FAILED;
        return state->flags;
    }
    if (crew->pos.x == target.x && crew->pos.y == target.y) {
        ++state->waypoint;
        if (state->waypoint == count) escort_goal(state);
        return state->flags;
    }
    if (!actors_near(0,CREW_ACTOR,CREW_RADIUS)) return state->flags;
    candidate = crew->pos;
    if (candidate.x != target.x) {
        remaining = candidate.x < target.x ? target.x - candidate.x : candidate.x - target.x;
        if (remaining > CREW_SPEED) remaining = CREW_SPEED;
        if (candidate.x < target.x) candidate.x += remaining; else candidate.x -= remaining;
    } else {
        remaining = candidate.y < target.y ? target.y - candidate.y : candidate.y - target.y;
        if (remaining > CREW_SPEED) remaining = CREW_SPEED;
        if (candidate.y < target.y) candidate.y += remaining; else candidate.y -= remaining;
    }
    if (crew_blocked(&candidate)) {
        state->flags |= SF_OBJECTIVE_BLOCKED;
        return state->flags;
    }
    /* The only position write is one checked axis step, at most20/32px.
     * Clamp the final step to remaining distance; never teleport or lerp. */
    crew->pos = candidate;
    crew_markers(state);
    if (candidate.x == target.x && candidate.y == target.y) {
        ++state->waypoint;
        if (state->waypoint == count) escort_goal(state);
    }
    return state->flags;
}
