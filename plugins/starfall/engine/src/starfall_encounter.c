#pragma bank 255

#include <gbdk/platform.h>
#include <string.h>
#include "actor.h"
#include "collision.h"
#include "input.h"
#include "interrupts.h"
#include "palette.h"
#include "ui.h"
#include "starfall_audio.h"
#include "starfall_rooms.h"
#include "starfall_screens.h"
#include "starfall_encounter.h"
#include "starfall_save.h"
#include "starfall_world.h"
#include "starfall_objectives.h"
#include "starfall_ui.h"
#include "data_manager.h"
#include "scroll.h"

extern WORD adv_walk_vel, adv_dec, adv_vel_x, adv_vel_y;
extern UBYTE overlay_cut_scanline;

#define CELL_FIRST 1u
#define TERMINAL 4u
#define DRONE 5u
#define PULSE 6u
#define CREW 7u
#define CAMPAIGN_SIGNATURE 0x80000000UL
#define MISSION_BITS 0x0003FFFFUL
#define HAZARD_FIRST 0xEAu
#define HAZARD_ATTR 0x0Eu

enum { DORMANT, WARNING, CHARGING, RECOVERING, STUNNED };
enum { STANDARD, FAST_CAPACITOR, WIDE_COIL, OVERCHARGE, HULL_PATCH };
enum { HAZARD_SAFE, HAZARD_WARNING, HAZARD_ACTIVE };

/* These are genuine state variables, exported solely for read-only QA. */
UWORD sf_gameplay_ticks;
UBYTE sf_room_index, sf_mode_index, sf_objective_progress, sf_boss_hp;
UBYTE sf_hull_value, sf_arcade_sector, sf_drone_phase_value, sf_drone_timer_value;
/*0 no checkpoint,1 successful save/readback,2 failed save/readback. */
UBYTE sf_save_status;
UBYTE sf_crew_hp, sf_branch_order, sf_room_clear_mask, sf_mission_cursor;
#define sf_mode sf_mode_index
#define cargo sf_objective_progress
#define hull sf_hull_value
#define sector sf_arcade_sector
#define drone_phase sf_drone_phase_value
#define drone_timer sf_drone_timer_value

static sf_room_t room;
static UBYTE arcade, collected, pulse_module, pulse_radius, pulse_reload, pulse_stun;
static UBYTE pulse_cooldown, pulse_timer, invulnerable, flash_timer, last_buttons;
static UBYTE hud_dirty, palette_dirty, damage_total, relay_hold, boss_grace;
static UBYTE boss_open, boss_hit_used, choice_a, choice_b, menu_grace;
static UBYTE scene_transition, pending_room, hazard_kind, hazard_phase, hazard_started;
static UBYTE hazard_saved, hazard_valid, large_world;
static UWORD hazard_timer, sortie_score, best_banked_score;
static uint32_t campaign_frames, room_frames;
static sf_save_t persisted_session;
static UBYTE resume_stage;
static UBYTE crew_grace, cache_found, cache_hold;
static UBYTE menu_cursor, exit_return_mode;
/* Transient navigation intent; checkpoint stages and save layout stay unchanged. */
static UBYTE direct_launch;
static sf_objective_state_t objective_state;
static upoint16_t escort_route[20];
static UBYTE escort_count;
#define NO_RESUME_STAGE 255u
static WORD charge_dx, charge_dy;
static upoint16_t initial_positions[8];
static palette_entry_t initial_background[7], initial_drone_palette;
static UBYTE original_hazard_tiles[16], original_hazard_attrs[16];



static const UBYTE hazard_tiles[80] = {
    0xFF,0,0x80,0,0x88,0,0x84,0,0x82,0,0x81,0,0x80,0,0x80,0,
    0xFF,0,0x01,0,0x11,0,0x21,0,0x41,0,0x81,0,0x01,0,0x01,0,
    0x80,0,0x80,0,0x81,0,0x82,0,0x84,0,0x88,0,0x80,0,0xFF,0,
    0x01,0,0x01,0,0x81,0,0x41,0,0x21,0,0x11,0,0x01,0,0xFF,0,
    0,0,0,0,0x3C,0,0x3C,0,0x3C,0,0x3C,0,0,0,0,0
};

static UWORD magnitude(WORD n) { return n < 0 ? -n : n; }
static WORD actor_x(UBYTE n) {
    return ((WORD)actors[n].pos.x + ((actors[n].bounds.left + actors[n].bounds.right) >> 1)) >> 5;
}
static WORD actor_y(UBYTE n) {
    return ((WORD)actors[n].pos.y + ((actors[n].bounds.top + actors[n].bounds.bottom) >> 1)) >> 5;
}
static UBYTE safe_dock(void) {
    return large_world ? starfall_world_dock_contains(actor_x(0),actor_y(0)) : actor_y(0) >= 112;
}
static UBYTE drone_visible(void) {
    WORD x = actor_x(DRONE) - draw_scroll_x, y = actor_y(DRONE) - draw_scroll_y;
    return x >= 8 && x <= 152 && y >= 24 && y <= 136;
}
static UBYTE nearby(UBYTE a, UBYTE b, UBYTE radius) {
    WORD dx = actor_x(a) - actor_x(b), dy = actor_y(a) - actor_y(b);
    if (magnitude(dx) > radius || magnitude(dy) > radius) return FALSE;
    return dx * dx + dy * dy <= (UWORD)radius * radius;
}
static void show_actor(UBYTE n) {
    actors[n].flags &= ~(ACTOR_FLAG_HIDDEN | ACTOR_FLAG_DISABLED | ACTOR_FLAG_COLLISION);
    actors[n].collision_group = COLLISION_GROUP_NONE;
    activate_actor(&actors[n]);
}
static void hide_actor(UBYTE n) {
    actors[n].flags |= ACTOR_FLAG_HIDDEN;
    actors[n].flags &= ~ACTOR_FLAG_COLLISION;
    actors[n].collision_group = COLLISION_GROUP_NONE;
    deactivate_actor(&actors[n]);
}
static void apply_module(UBYTE module) {
    pulse_module = module;
    pulse_radius = 24; pulse_reload = 120; pulse_stun = 60;
    if (module == FAST_CAPACITOR) { pulse_radius = 20; pulse_reload = 72; pulse_stun = 30; }
    else if (module == WIDE_COIL) { pulse_radius = 36; pulse_reload = 180; }
    else if (module == OVERCHARGE) { pulse_reload = 180; pulse_stun = 90; }
    else if (module == HULL_PATCH) { hull = 3; pulse_module = STANDARD; }
}
static void checkpoint(UBYTE stage) {
    if (arcade) return;
    persisted_session.has_checkpoint = TRUE;
    persisted_session.room = sf_room_index;
    persisted_session.checkpoint_stage = stage;
    persisted_session.rig = pulse_module;
    persisted_session.damage_total = damage_total;
    persisted_session.successful_frames = campaign_frames;
    persisted_session.best_banked = best_banked_score;
    persisted_session.room_clear_mask = sf_room_clear_mask;
    persisted_session.branch_order = sf_branch_order;
    persisted_session.hull_value = hull;
    persisted_session.mission_flags |= CAMPAIGN_SIGNATURE;
    if (pulse_module == FAST_CAPACITOR) persisted_session.unlock_flags |= SF_SAVE_UNLOCK_FAST;
    else if (pulse_module == WIDE_COIL) persisted_session.unlock_flags |= SF_SAVE_UNLOCK_WIDE;
    else if (pulse_module == OVERCHARGE) persisted_session.unlock_flags |= SF_SAVE_UNLOCK_OVERCHARGE;
    sf_save_status = starfall_save_write(&persisted_session) ? 1u : 2u;
}

static void hazard_capture(void) {
    /* Core paints the new BG after state init. Capture only on its first update. */
    if (large_world) {
        /* Scrolling repaints the hardware map. Its hazard pixels are authored
         * in palette6, so animate that palette without modifying VRAM tiles. */
        hazard_valid = hazard_kind && room.hazard_w && room.hazard_h &&
            room.hazard_x + room.hazard_w <= image_tile_width &&
            room.hazard_y + room.hazard_h <= image_tile_height;
        hazard_saved = TRUE; return;
    }
    hazard_valid = hazard_kind && room.hazard_w && room.hazard_h &&
        (UWORD)room.hazard_w * room.hazard_h <= 16u &&
        room.hazard_x + room.hazard_w <= 20u && room.hazard_y + room.hazard_h <= 14u;
    if (hazard_valid) {
        VBK_REG = 0;
        get_bkg_tiles(room.hazard_x, room.hazard_y, room.hazard_w, room.hazard_h, original_hazard_tiles);
        VBK_REG = 1;
        get_bkg_tiles(room.hazard_x, room.hazard_y, room.hazard_w, room.hazard_h, original_hazard_attrs);
    }
    VBK_REG = 1; set_bkg_data(HAZARD_FIRST, 5, hazard_tiles); VBK_REG = 0;
    hazard_saved = TRUE;
}
static void hazard_restore(void) {
    if (large_world) return;
    if (!hazard_saved || !hazard_valid) return;
    VBK_REG = 1;
    set_bkg_tiles(room.hazard_x, room.hazard_y, room.hazard_w, room.hazard_h, original_hazard_attrs);
    VBK_REG = 0;
    set_bkg_tiles(room.hazard_x, room.hazard_y, room.hazard_w, room.hazard_h, original_hazard_tiles);
}
static void hazard_stamp(void) {
    UBYTE tiles[16], attrs[16], x, y, i = 0;
    if (large_world) return;
    if (!hazard_valid) return;
    memset(attrs, HAZARD_ATTR, sizeof(attrs));
    for (y = 0; y != room.hazard_h; ++y) for (x = 0; x != room.hazard_w; ++x) {
        tiles[i++] = hazard_kind == SF_HAZARD_LASER ? HAZARD_FIRST + 4u :
            HAZARD_FIRST + (y ? 2u : 0u) + (x ? 1u : 0u);
    }
    VBK_REG = 1;
    set_bkg_tiles(room.hazard_x, room.hazard_y, room.hazard_w, room.hazard_h, attrs);
    VBK_REG = 0;
    set_bkg_tiles(room.hazard_x, room.hazard_y, room.hazard_w, room.hazard_h, tiles);
}
static UWORD hazard_safe_frames(void) {
    UBYTE reduction = arcade ? (sector > 15u ? 30u : sector << 1) : 0;
    return 120u - reduction;
}
static void hazard_activate(void) {
    if (!hazard_valid || hazard_started) return;
    hazard_started = TRUE; hazard_phase = HAZARD_SAFE;
    hazard_timer = hazard_safe_frames() + 1u;
    palette_dirty = TRUE;
}
static void hazard_palette(void) {
    palette_entry_t p;
    p.c0 = CGB_COLOR(2, 4, 7); p.c1 = CGB_COLOR(8, 15, 17);
    p.c2 = CGB_COLOR(3, 8, 10); p.c3 = CGB_COLOR(0, 0, 0);
    if (hazard_started && hazard_phase == HAZARD_WARNING) p.c1 = CGB_COLOR(31, 23, 5);
    else if (hazard_started && hazard_phase == HAZARD_ACTIVE) p.c1 = CGB_COLOR(31, 5, 3);
    BkgPalette[6] = p; set_bkg_palette(6, 1, (UWORD *)&BkgPalette[6]);
}
static void hazard_update(void) {
    UBYTE extra;
    if (!hazard_valid || !hazard_started) return;
    if (hazard_timer) --hazard_timer;
    if (hazard_timer) return;
    if (hazard_phase == HAZARD_SAFE) {
        hazard_phase = HAZARD_WARNING; hazard_timer = 45;
        starfall_audio_sfx(STARFALL_SFX_WARNING);
    } else if (hazard_phase == HAZARD_WARNING) {
        hazard_phase = HAZARD_ACTIVE;
        extra = arcade ? sector / 8u : 0;
        if (extra > 9u) extra = 9u;
        hazard_timer = 36u + extra;
    } else { hazard_phase = HAZARD_SAFE; hazard_timer = hazard_safe_frames(); }
    palette_dirty = TRUE;
}
static UBYTE hazard_hits_actor(UBYTE actor) {
    WORD left, right, top, bottom, hx, hy;
    if (!hazard_valid || !hazard_started || hazard_phase != HAZARD_ACTIVE ||
        starfall_world_dock_contains(actor_x(actor),actor_y(actor))) return FALSE;
    /* Use the native player feet/body bounds, not an assumed sixteen-pixel box. */
    left = ((WORD)actors[actor].pos.x + actors[actor].bounds.left) >> 5;
    right = ((WORD)actors[actor].pos.x + actors[actor].bounds.right) >> 5;
    top = ((WORD)actors[actor].pos.y + actors[actor].bounds.top) >> 5;
    bottom = ((WORD)actors[actor].pos.y + actors[actor].bounds.bottom) >> 5;
    hx = (WORD)room.hazard_x << 3; hy = (WORD)room.hazard_y << 3;
    return right >= hx && left < hx + ((WORD)room.hazard_w << 3) &&
           bottom >= hy && top < hy + ((WORD)room.hazard_h << 3);
}
static UWORD tint(UWORD c, UBYTE red, UBYTE green, UBYTE blue) {
    UBYTE r = (c & 31u) + red, g = ((c >> 5) & 31u) + green, b = ((c >> 10) & 31u) + blue;
    if (r > 31u) r = 31u; if (g > 31u) g = 31u; if (b > 31u) b = 31u;
    return CGB_COLOR(r, g, b);
}
static void lighting(void) {
    UBYTE i, r = cargo, g = cargo, b = cargo;
    palette_entry_t p;
    if (drone_phase == WARNING && (drone_timer & 8u)) r += 5u, g += 2u;
    if (drone_phase == CHARGING || flash_timer) r += 7u;
    if (drone_phase == STUNNED || pulse_timer || boss_open) g += 3u, b += 7u;
    for (i = 0; i != 7; ++i) {
        p.c0 = tint(initial_background[i].c0, r, g, b); p.c1 = tint(initial_background[i].c1, r, g, b);
        p.c2 = tint(initial_background[i].c2, r, g, b); p.c3 = tint(initial_background[i].c3, r, g, b);
        BkgPalette[i] = p; set_bkg_palette(i, 1, (UWORD *)&BkgPalette[i]);
    }
    if (hazard_valid) hazard_palette();
    p = initial_drone_palette;
    if (drone_phase == WARNING) { p.c1 = CGB_COLOR(31,27,9); p.c2 = CGB_COLOR(31,15,3); }
    else if (drone_phase == CHARGING) { p.c1 = CGB_COLOR(31,12,8); p.c2 = CGB_COLOR(25,3,3); }
    else if (drone_phase == STUNNED || boss_open) { p.c1 = CGB_COLOR(11,31,31); p.c2 = CGB_COLOR(5,13,31); }
    SprPalette[1] = p; set_sprite_palette(1, 1, (UWORD *)&SprPalette[1]);
    palette_dirty = FALSE;
}
static void navigation_hud(void) {
    char heading[] = "A READY TARGET NE";
    UBYTE i, target = TERMINAL;
    UWORD best = 65535u, distance;
    WORD dx, dy;
    if (room.objective == SF_OBJECTIVE_ESCORT && !(objective_state.flags & SF_OBJECTIVE_READY)) target = CREW;
    else if (cargo < 3u) for (i = CELL_FIRST; i < CELL_FIRST + 3u; ++i) {
        if (collected & (1u << (i - CELL_FIRST))) continue;
        distance = magnitude(actor_x(i) - actor_x(0)) + magnitude(actor_y(i) - actor_y(0));
        if (distance < best) { best = distance; target = i; }
    }
    if (pulse_cooldown) memcpy(heading + 2,"WAIT ",5);
    if (target == TERMINAL) memcpy(heading + 8,"DOCK  ",6);
    if (target == CREW) memcpy(heading + 8,"CREW  ",6);
    dx = actor_x(target) - actor_x(0); dy = actor_y(target) - actor_y(0);
    if (target == CREW && nearby(0,CREW,24) && objective_state.waypoint < escort_count) {
        /* Route entries are crew anchors, whose actual midpoint is +7,+3. */
        dx = (escort_route[objective_state.waypoint].x >> 5) + 7 - actor_x(0);
        dy = (escort_route[objective_state.waypoint].y >> 5) + 3 - actor_y(0);
    }
    heading[15] = dy < -8 ? 'N' : dy > 8 ? 'S' : ' ';
    heading[16] = dx < -8 ? 'W' : dx > 8 ? 'E' : ' ';
    if (heading[15] == ' ' && heading[16] == ' ') heading[15] = 'O', heading[16] = 'K';
    starfall_ui_hud_row(1,heading);
}
static void hud(void) {
    char first[] = "H3 C0/3 M01 BAY 1/4";
    char arcade_first[] = "H3 C0/3 SECTOR 01";
    char second[] = "A READY S:00000";
    char relay[] = "NODE1 B00/30 A READY";
    char repair[] = "REPAIR B00/45 A OK  ";
    first[1] = arcade_first[1] = '0' + hull;
    first[4] = arcade_first[4] = '0' + cargo;
    starfall_ui_two_digits(first + 9,sf_room_index / 4u + 1u); first[16] = '1' + (sf_room_index & 3u);
    starfall_ui_two_digits(arcade_first + 15, sector);
    if (room.objective == SF_OBJECTIVE_RELAY && cargo < 3u) {
        first[3] = arcade_first[3] = 'N'; first[4] = arcade_first[4] = '1' + cargo;
    } else if (room.objective == SF_OBJECTIVE_REPAIR) {
        first[3] = 'F'; first[4] = '0' + cargo;
    } else if (room.objective == SF_OBJECTIVE_CORE && sf_boss_hp) {
        first[3] = arcade_first[3] = 'W'; first[4] = arcade_first[4] = '0' + sf_boss_hp;
    }
    if (room.objective == SF_OBJECTIVE_ESCORT) first[3] = 'R', first[4] = '0' + sf_crew_hp;
    starfall_ui_hud_row(0, arcade ? arcade_first : first);
    if (room.objective == SF_OBJECTIVE_CORE && sf_boss_hp) {
        if (boss_open) {
            if (boss_hit_used) starfall_ui_hud_row(1,pulse_cooldown ? "HIT LANDED - A WAIT" : "HIT LANDED - A READY");
            else starfall_ui_hud_row(1,pulse_cooldown ? "CORE OPEN - A WAIT" : "CORE OPEN - A PULSE");
        } else starfall_ui_hud_row(1,pulse_cooldown ? "CORE SHIELD A WAIT" : "CORE SHIELD A STUN");
    } else if (room.objective == SF_OBJECTIVE_CORE) starfall_ui_hud_row(1,cargo < 3u ? "CORE DOWN - COLLECT" : "CORES READY - DOCK");
    else if (room.objective == SF_OBJECTIVE_ESCORT && (objective_state.flags & SF_OBJECTIVE_BLOCKED)) starfall_ui_hud_row(1,"CREW BLOCKED - RETRY");
    else if (room.objective == SF_OBJECTIVE_REPAIR && objective_state.hold) {
        starfall_ui_two_digits(repair + 8,objective_state.hold);
        if (pulse_cooldown) memcpy(repair + 14,"WAIT",4);
        starfall_ui_hud_row(1,repair);
    }
    else if (room.objective == SF_OBJECTIVE_RELAY && cargo < 3u) {
        relay[4] = '1' + cargo; starfall_ui_two_digits(relay + 7, relay_hold);
        if (pulse_cooldown) memcpy(relay + 15,"WAIT ",5);
        starfall_ui_hud_row(1, relay);
    } else if (room.objective == SF_OBJECTIVE_RELAY) starfall_ui_hud_row(1, "RELAYS ONLINE - DOCK");
    else if (large_world) navigation_hud();
    else if (cargo == 3u) starfall_ui_hud_row(1,"CARGO READY - DOCK");
    else if (drone_phase == WARNING && room.enemy == SF_ENEMY_SWEEPER)
        starfall_ui_hud_row(1, charge_dx ? "AMBER - X DASH LOCK" : "AMBER - Y DASH LOCK");
    else if (arcade) {
        starfall_ui_five_digits(second + 10, sortie_score);
        if (pulse_cooldown) memcpy(second + 2, "WAIT ", 5);
        starfall_ui_hud_row(1, second);
    } else starfall_ui_hud_row(1, pulse_cooldown ? "A WAIT  B BRAKE" : "A READY B BRAKE");
    hide_sprites = FALSE; overlay_cut_scanline = 16u; ui_set_pos(0,0); hud_dirty = FALSE; sf_hud_valid = TRUE;
}

static void screen(UBYTE kind) {
    sf_hud_valid = FALSE;
    overlay_cut_scanline = 0u; hide_sprites = TRUE; ui_set_pos(0,144);
    starfall_screen_show(kind, room.zone, sf_room_index);
    menu_grace = 20;
}
static void screen_ready(void) {
    if (sf_save_status == 2u) starfall_ui_text_row(17,"SAVE WRITE FAILED");
    overlay_cut_scanline = 150u; ui_set_pos(0,0);
}
static const char *enemy_name(void) {
    if (room.objective == SF_OBJECTIVE_CORE) return "WARDEN - PULSE OPEN";
    if (room.enemy == SF_ENEMY_SWEEPER) return "SWEEPER - AXIS DASH";
    if (room.enemy == SF_ENEMY_HUNTER) return "HUNTER - TRACKS SAFE";
    return "CHARGER LOCKS AMBER";
}
static UBYTE menu_move(UBYTE pressed, UBYTE count) {
    if (pressed & J_UP) menu_cursor = menu_cursor ? menu_cursor - 1u : count - 1u;
    else if (pressed & J_DOWN) menu_cursor = (menu_cursor + 1u) % count;
    else return FALSE;
    return TRUE;
}
static UBYTE mission_available(UBYTE index) {
    UBYTE zone = index / 3u;
    uint32_t done = persisted_session.mission_flags & MISSION_BITS;
    if (index >= SF_MISSION_COUNT) return FALSE;
    if (zone && !(done & (1UL << (zone * 3u - 1u)))) return FALSE;
    if (index % 3u == 2u && (done & (3UL << (zone * 3u))) != (3UL << (zone * 3u))) return FALSE;
    return TRUE;
}
static UBYTE next_room_index(void) {
    UBYTE base = sf_room_index & 252u;
    if (arcade) return sf_room_index + 1u >= SF_ROOM_COUNT ? SF_ARCADE_FIRST : sf_room_index + 1u;
    if (!(sf_room_clear_mask & 2u)) return base + 1u;
    if (!(sf_room_clear_mask & 4u)) return base + 2u;
    return base + 3u;
}
static void mission_board_card(void) {
    char name[21], label[] = "MISSION 01/01";
    sf_room_t first;
    screen(SF_SCREEN_LAUNCH); starfall_mission_name(sf_mission_cursor,name);
    starfall_room_read(sf_mission_cursor * 4u,&first);
    starfall_ui_two_digits(label + 8,sf_mission_cursor + 1u); starfall_ui_two_digits(label + 11,SF_MISSION_COUNT);
    starfall_ui_header("FLIGHT DECK"); starfall_ui_menu_card(3,3,TRUE,label); starfall_ui_centered_row(6,name);
    starfall_ui_centered_row(7,!mission_available(sf_mission_cursor) ? "LOCKED" :
        (persisted_session.mission_flags & (1UL << sf_mission_cursor)) ? "CLEARED / REPLAY" : "READY TO FLY");
    starfall_ui_objective_hint(8,first.objective);
    starfall_ui_module_option(9,FALSE,pulse_module); starfall_ui_module_description(13,pulse_module);
    if (persisted_session.optional_flags & (1UL << sf_mission_cursor)) starfall_ui_centered_row(14,"CACHE BADGE EARNED");
    starfall_ui_centered_row(15,"UP/DOWN JOB L/R RIG");
    starfall_ui_footer(SF_FOOTER_LAUNCH); screen_ready();
}
static void branch_options(void) {
    sf_room_t option;
    starfall_room_read((sf_room_index & 252u) + 1u,&option);
    starfall_ui_route_option(0,menu_cursor == 0u,option.objective);
    starfall_room_read((sf_room_index & 252u) + 2u,&option);
    starfall_ui_route_option(1,menu_cursor == 1u,option.objective);
}
static void branch_card(void) {
    screen(SF_SCREEN_RESULT); starfall_ui_header("CHOOSE YOUR ROUTE");
    starfall_ui_centered_row(4,"BOTH BAYS TO CLEAR"); branch_options();
    starfall_ui_footer(SF_FOOTER_FLY); screen_ready();
}
static void mission_complete_card(void) {
    char name[21], count[] = "MISSIONS CLEARED 00";
    UBYTE i,n=0;
    for(i=0;i<SF_MISSION_COUNT;++i) if(persisted_session.mission_flags & (1UL<<i)) ++n;
    screen(SF_SCREEN_RESULT); starfall_ui_header("MISSION COMPLETE"); starfall_mission_name(sf_room_index / 4u,name);
    starfall_ui_centered_row(5,name); starfall_ui_two_digits(count+17,n); starfall_ui_centered_row(7,count);
    starfall_ui_centered_row(9,cache_found ? "CACHE BADGE EARNED" : "ALL FOUR BAYS CLEAR");
    starfall_ui_menu_card(12,3,TRUE,"FLIGHT DECK");
    starfall_ui_footer(SF_FOOTER_CONTINUE); screen_ready();
}
static void title_options(void) {
    char resume[] = "CONTINUE M01";
    if (persisted_session.has_checkpoint) {
        starfall_ui_two_digits(resume + 10, persisted_session.room / 4u + 1u); starfall_ui_menu_option(11,menu_cursor == 0u,resume);
        starfall_ui_menu_option(13,menu_cursor == 2u,"NEW STORY");
    } else { starfall_ui_menu_option(11,menu_cursor == 0u,"STORY"); starfall_ui_text_row(13,""); }
    starfall_ui_menu_option(12,menu_cursor == 1u,"ARCADE");
}
static void title_card(void) {
    char best[] = "BEST BANKED: 00000";
    hazard_restore(); screen(SF_SCREEN_TITLE); title_options();
    starfall_ui_centered_row(9,"FULL CAMPAIGN 1.2");
    starfall_ui_five_digits(best + 13, best_banked_score); starfall_ui_centered_row(15,best);
    starfall_ui_footer(SF_FOOTER_PLAY);
    screen_ready();
}
static void launch_card(void) {
    char label[] = "M01 BAY 1/4 H3";
    char arcade_label[] = "SECTOR 01 HULL 3";
    starfall_ui_two_digits(label + 1,sf_room_index / 4u + 1u); label[8] = '1' + (sf_room_index & 3u); label[13] = '0' + hull;
    starfall_ui_two_digits(arcade_label+7,sector); arcade_label[15]='0'+hull;
    screen(SF_SCREEN_LAUNCH); starfall_ui_header("READY TO FLY");
    starfall_ui_centered_row(4,room.name); starfall_ui_centered_row(6,arcade ? arcade_label : label);
    starfall_ui_centered_row(8,room.brief1); starfall_ui_centered_row(9,room.brief2); starfall_ui_centered_row(11,enemy_name());
    starfall_ui_centered_row(13,"FINISH THEN DOCK");
    if (!arcade && (sf_room_index & 3u) == 2u && sf_branch_order == 1u) starfall_ui_centered_row(13,"POWERED / HAZARD OFF");
    else if (!arcade && (sf_room_index & 3u) == 1u && sf_branch_order == 2u) starfall_ui_centered_row(13,"FAST RECHARGE");
    if (!arcade) starfall_ui_centered_row(15,"CHECKPOINT SAVED");
    starfall_ui_footer(arcade ? SF_FOOTER_LAUNCH_EXIT : SF_FOOTER_LAUNCH);
    screen_ready();
}
static void pause_options(void) {
    starfall_ui_menu_card(6,3,menu_cursor == 0u,"RESUME");
    starfall_ui_menu_card(9,3,menu_cursor == 1u,arcade ? "FRESH SORTIE" : "RETRY ROOM");
    starfall_ui_menu_card(12,3,menu_cursor == 2u,"EXIT TO TITLE");
}
static void pause_card(void) {
    screen(SF_SCREEN_PAUSE); starfall_ui_header("PAUSED"); starfall_ui_centered_row(4,room.name);
    starfall_ui_objective_hint(5,room.objective);
    pause_options(); starfall_ui_footer(SF_FOOTER_CONFIRM);
    screen_ready();
}
static void exit_card(void) {
    screen(SF_SCREEN_PAUSE); starfall_ui_exit_card_text(arcade); screen_ready();
}
static void new_story_card(void) {
    screen(SF_SCREEN_PAUSE); starfall_ui_new_story_card_text(); screen_ready();
}
static void result_card(void) {
    char time[] = "TIME 00:00:00";
    sf_room_t next;
    starfall_room_read(next_room_index(),&next);
    starfall_ui_elapsed_time(time + 5, room_frames); screen(SF_SCREEN_RESULT); starfall_ui_header("BAY SECURED");
    starfall_ui_centered_row(4,resume_stage == SF_SAVE_STAGE_RESULT ? "CHECKPOINT RESTORED" : time);
    starfall_ui_centered_row(6,"NEXT BAY"); starfall_ui_centered_row(8,next.name);
    starfall_ui_objective_hint(10,next.objective); starfall_ui_menu_card(12,3,TRUE,"FLY ON");
    starfall_ui_footer(SF_FOOTER_CONTINUE);
    screen_ready();
}
static void ending_card(void) {
    char time[] = "CLEAR TIME: 00:00:00";
    starfall_ui_elapsed_time(time + 12, campaign_frames);
    screen(SF_SCREEN_ENDING); starfall_ui_header(SF_MISSION_COUNT == 18u ? "STARFALL SAVED" : "SLICE COMPLETE");
    starfall_ui_centered_row(6,time);
    starfall_ui_centered_row(9,!damage_total ? "RANK S / CLEAN RUN" : damage_total <= 2u ? "RANK A / NICE FLYING" : "RANK B / GOT HOME");
    starfall_ui_menu_card(12,3,TRUE,"BACK TO TITLE"); starfall_ui_footer(SF_FOOTER_CONTINUE);
    screen_ready();
}
static void arcade_dock_options(void) {
    starfall_ui_menu_card(8,3,menu_cursor == 0u,"FLY ON");
    starfall_ui_menu_card(11,3,menu_cursor == 1u,"CHANGE RIG");
    starfall_ui_menu_card(14,3,menu_cursor == 2u,"BANK HAUL");
}
static void arcade_dock_card(void) {
    char score[] = "HAUL 00000  HULL 3";
    sf_room_t next;
    starfall_room_read(next_room_index(),&next);
    starfall_ui_five_digits(score + 5, sortie_score); score[17] = '0' + hull;
    screen(SF_SCREEN_RESULT); starfall_ui_header("SAFE AT DOCK");
    starfall_ui_centered_row(4,score); starfall_ui_centered_row(6,next.name);
    starfall_ui_objective_hint(7,next.objective);
    arcade_dock_options(); starfall_ui_footer(SF_FOOTER_CONFIRM_EXIT);
    screen_ready();
}
static void upgrade_options(void) {
    starfall_ui_menu_card(5,3,menu_cursor == 0u,"KEEP CURRENT");
    starfall_ui_module_option(8,menu_cursor == 1u,choice_a);
    starfall_ui_module_option(11,menu_cursor == 2u,choice_b);
    starfall_ui_module_description(15,!menu_cursor ? pulse_module : menu_cursor == 1u ? choice_a : choice_b);
}
static void upgrade_card(void) {
    switch ((sector - 1u) % 5u) {
        case 0: choice_a = FAST_CAPACITOR; choice_b = WIDE_COIL; break;
        case 1: choice_a = OVERCHARGE; choice_b = HULL_PATCH; break;
        case 2: choice_a = STANDARD; choice_b = FAST_CAPACITOR; break;
        case 3: choice_a = WIDE_COIL; choice_b = OVERCHARGE; break;
        default: choice_a = HULL_PATCH; choice_b = FAST_CAPACITOR; break;
    }
    screen(SF_SCREEN_UPGRADE); starfall_ui_header("CHOOSE YOUR RIG"); starfall_ui_module_name(4,pulse_module);
    upgrade_options(); starfall_ui_footer(SF_FOOTER_FIT);
    screen_ready();
}
static void bank_card(void) {
    char score[] = "BANKED: 00000", best[] = "BEST:   00000";
    if (sortie_score > best_banked_score) best_banked_score = sortie_score;
    /* Banking statistics must retain the committed Story checkpoint, even
     * if an earlier Story save failed and left an uncommitted RAM draft. */
    starfall_save_read(&persisted_session);
    persisted_session.best_banked = best_banked_score;
    sf_save_status = starfall_save_write(&persisted_session) ? 1u : 2u;
    starfall_ui_five_digits(score + 8,sortie_score); starfall_ui_five_digits(best + 8,best_banked_score);
    screen(SF_SCREEN_ENDING); starfall_ui_header(sf_save_status == 2u ? "SAVE WRITE FAILED" : "HAUL BANKED");
    starfall_ui_centered_row(6,score); starfall_ui_centered_row(9,best);
    starfall_ui_menu_card(12,3,TRUE,"BACK TO TITLE"); starfall_ui_footer(SF_FOOTER_CONTINUE);
    screen_ready();
}
static void failure_card(void) {
    char lost[] = "LOST: 00000";
    starfall_ui_five_digits(lost + 6,sortie_score);
    if (arcade) sortie_score = 0;
    screen(SF_SCREEN_FAILURE); starfall_ui_header(room.objective == SF_OBJECTIVE_ESCORT && !sf_crew_hp ? "CREW LOST" : "HULL CRITICAL");
    starfall_ui_centered_row(5,room.name); starfall_ui_centered_row(7,arcade ? "UNBANKED CARGO LOST" : "CHECKPOINT RETAINED");
    if (arcade) starfall_ui_centered_row(9,lost);
    starfall_ui_menu_card(12,3,TRUE,arcade ? "FRESH SORTIE" : "RETRY ROOM"); starfall_ui_footer(SF_FOOTER_RETRY);
    screen_ready();
}
static void to_title(void) {
    direct_launch = 0;
    menu_cursor = 0; sf_mode = SF_MODE_TITLE; title_card();
}
static void request_room(UBYTE index) {
    if (index >= SF_ROOM_COUNT) index = 0;
    pending_room = index;
    if (starfall_room_change(index)) {
        scene_transition = TRUE; sf_room_index = index; sf_mode = SF_MODE_TRANSITION;
        if (resume_stage == NO_RESUME_STAGE) checkpoint(SF_SAVE_STAGE_LAUNCH);
    } else {
        sf_mode = SF_MODE_LOAD_BUSY; screen(SF_SCREEN_FAILURE);
        starfall_ui_text_row(6,"ROOM LOAD BUSY"); starfall_ui_text_row(9,"A TRY AGAIN"); starfall_ui_text_row(12,"B BACK TO TITLE");
        screen_ready();
    }
}
static void start_game(UBYTE is_arcade) {
    arcade = is_arcade; sector = 1; hull = 3; damage_total = 0;
    direct_launch = 0;
    resume_stage = NO_RESUME_STAGE;
    sortie_score = 0; campaign_frames = 0; apply_module(STANDARD);
    if (!arcade) {
        persisted_session.credits = 0; persisted_session.mission_flags = CAMPAIGN_SIGNATURE;
        sf_room_clear_mask = sf_branch_order = sf_mission_cursor = sf_room_index = 0;
        sf_mode = SF_MODE_MISSION_BOARD; checkpoint(SF_SAVE_STAGE_MISSION_BOARD); mission_board_card();
    } else request_room(SF_ARCADE_FIRST);
}
static void continue_story(void) {
    /* Re-read cartridge SRAM so Continue consumes the committed checkpoint,
     * including fallback to the prior valid record after a failed write. */
    if (!starfall_save_read(&persisted_session) || !persisted_session.has_checkpoint || !starfall_checkpoint_valid(&persisted_session)) {
        persisted_session.has_checkpoint = FALSE; sf_save_status = 0;
        to_title(); return;
    }
    sf_save_status = 1;
    direct_launch = 0;
    arcade = FALSE; sector = 1; hull = 3; sortie_score = 0;
    sf_room_clear_mask = persisted_session.room_clear_mask;
    sf_branch_order = persisted_session.branch_order;
    sf_mission_cursor = persisted_session.room / 4u;
    cache_found = !!(persisted_session.optional_flags & (1UL << sf_mission_cursor));
    damage_total = persisted_session.damage_total;
    campaign_frames = persisted_session.successful_frames;
    apply_module(persisted_session.rig);
    resume_stage = persisted_session.checkpoint_stage;
    request_room(persisted_session.room);
}
static void next_room(void) {
    direct_launch = TRUE;
    if (arcade && sector < 99u) ++sector;
    request_room(next_room_index());
}
static void open_mission_board(void) {
    UBYTE i, candidate;
    sf_mission_cursor = sf_room_index / 4u;
    if (sf_mission_cursor >= SF_MISSION_COUNT) sf_mission_cursor = 0;
    for (i = 1u; i <= SF_MISSION_COUNT; ++i) {
        candidate = (sf_mission_cursor + i) % SF_MISSION_COUNT;
        if (mission_available(candidate) && !(persisted_session.mission_flags & (1UL << candidate))) {
            sf_mission_cursor = candidate; break;
        }
    }
    sf_mode = SF_MODE_MISSION_BOARD;
    checkpoint(SF_SAVE_STAGE_MISSION_BOARD); mission_board_card();
}
static void change_rig(UBYTE backwards) {
    UBYTE next = pulse_module, tries = 4;
    while (tries--) {
        next = backwards ? (next ? next - 1u : OVERCHARGE) : (next + 1u) % 4u;
        if (!next || (persisted_session.unlock_flags & (1u << (next - 1u)))) break;
    }
    apply_module(next); checkpoint(SF_SAVE_STAGE_MISSION_BOARD); mission_board_card();
}

static UBYTE enemy_blocked(WORD x, WORD y) {
    if (!large_world && (x < 16 || x > 136 || y < 24 || y > 104)) return TRUE;
    return starfall_world_enemy_blocked(x,y);
}
static UBYTE enemy_move(WORD dx, WORD dy) {
    WORD nx = (WORD)actors[DRONE].pos.x + dx, ny = (WORD)actors[DRONE].pos.y + dy;
    WORD x = (nx + ((actors[DRONE].bounds.left + actors[DRONE].bounds.right) >> 1)) >> 5;
    WORD y = (ny + ((actors[DRONE].bounds.top + actors[DRONE].bounds.bottom) >> 1)) >> 5;
    if (enemy_blocked(x,y)) return FALSE;
    actors[DRONE].pos.x = nx; actors[DRONE].pos.y = ny; return TRUE;
}
static void set_drone_phase(UBYTE phase, UBYTE frames) {
    if (phase != drone_phase) hud_dirty = palette_dirty = TRUE;
    drone_phase = phase; drone_timer = frames;
}
static void begin_recovery(void) {
    UBYTE frames = room.recover_frames;
    if (room.objective == SF_OBJECTIVE_CORE && sf_boss_hp) {
        if (frames < 96u) frames = 96u;
        if (drone_phase != RECOVERING) boss_hit_used = FALSE;
        boss_open = TRUE; starfall_audio_sfx(STARFALL_SFX_CORE_OPEN);
    } else boss_open = FALSE;
    set_drone_phase(RECOVERING,frames);
}
static void begin_warning(void) {
    UBYTE target = room.objective == SF_OBJECTIVE_ESCORT && sf_crew_hp ? CREW : 0u;
    WORD dx = actor_x(target) - actor_x(DRONE), dy = actor_y(target) - actor_y(DRONE);
    UWORD ax = magnitude(dx), ay = magnitude(dy);
    point16_t world_delta;
    UBYTE cycle = arcade ? (sector - 1u) / SF_ARCADE_ROOM_COUNT : 0;
    UBYTE speed, warning;
    if (cycle > 2u) cycle = 2u;
    speed = room.speed + (cycle << 2); if (speed > 64u) speed = 64u;
    warning = room.warning_frames > cycle * 3u ? room.warning_frames - cycle * 3u : 30u;
    if (warning < 30u) warning = 30u;
    if (room.enemy == SF_ENEMY_SWEEPER) {
        charge_dx = ax >= ay ? (dx < 0 ? -(WORD)speed : speed) : 0;
        charge_dy = ax >= ay ? 0 : (dy < 0 ? -(WORD)speed : speed);
    } else {
        starfall_world_target_delta(dx,dy,speed,&world_delta);
        charge_dx = world_delta.x; charge_dy = world_delta.y;
    }
    boss_open = FALSE; set_drone_phase(WARNING,warning); starfall_audio_sfx(STARFALL_SFX_WARNING);
}
static void hunter_step(void) {
    UBYTE target = room.objective == SF_OBJECTIVE_ESCORT && sf_crew_hp ? CREW : 0u;
    WORD dx = actor_x(target) - actor_x(DRONE), dy = actor_y(target) - actor_y(DRONE);
    WORD sx = 0, sy = 0; UBYTE step = arcade && sector > 12u ? 10u : 9u;
    if (safe_dock()) return;
    if (magnitude(dx) > 3u) sx = dx < 0 ? -(WORD)step : step;
    if (magnitude(dy) > 3u) sy = dy < 0 ? -(WORD)step : step;
    if (sx && sy) { step = (step * 181u) >> 8; sx = dx < 0 ? -(WORD)step : step; sy = dy < 0 ? -(WORD)step : step; }
    if (!enemy_move(sx,sy)) { if (!enemy_move(sx,0)) enemy_move(0,sy); }
}
static void drone_update(void) {
    UBYTE dash;
    /* Readable warnings begin and count while the threat is visible. An
     * already telegraphed dash remains committed if the camera moves away. */
    if (large_world && drone_phase != CHARGING && !drone_visible()) return;
    if (drone_phase == DORMANT) {
        if (room.objective == SF_OBJECTIVE_CORE && sf_boss_hp && boss_grace && !safe_dock() && !--boss_grace) begin_warning();
        return;
    }
    if (drone_timer) --drone_timer;
    if (drone_phase == WARNING) {
        if (!(drone_timer & 7u)) palette_dirty = TRUE;
        if (!drone_timer) {
            dash = room.dash_frames; if (dash < 8u) dash = 8u; if (dash > 30u) dash = 30u;
            set_drone_phase(CHARGING,dash);
        }
    } else if (drone_phase == CHARGING) {
        if (!enemy_move(charge_dx,charge_dy) || !drone_timer) begin_recovery();
    } else if (drone_phase == RECOVERING) {
        if (room.enemy == SF_ENEMY_HUNTER && !boss_open) hunter_step();
        if (!drone_timer) {
            boss_open = FALSE;
            if (safe_dock()) {
                if (room.objective == SF_OBJECTIVE_CORE && sf_boss_hp) { boss_grace = 24; set_drone_phase(DORMANT,0); }
                else set_drone_phase(RECOVERING,24);
            }
            else begin_warning();
        }
    } else if (!drone_timer) {
        if (safe_dock()) {
            if (room.objective == SF_OBJECTIVE_CORE && sf_boss_hp) { boss_grace = 24; set_drone_phase(DORMANT,0); }
            else set_drone_phase(RECOVERING,24);
        }
        else begin_warning();
    }
}
static void wake_drone(void) {
    if (drone_phase == DORMANT) { set_drone_phase(RECOVERING,60); hazard_activate(); }
}
static void pulse(void) {
    UBYTE i;
    pulse_cooldown = pulse_reload; pulse_timer = 8;
    actors[PULSE].pos = PLAYER.pos; show_actor(PULSE);
    if (nearby(0,DRONE,pulse_radius)) {
        if (room.objective == SF_OBJECTIVE_CORE && sf_boss_hp) {
            if (boss_open && drone_phase == RECOVERING) {
                if (!boss_hit_used) {
                    boss_hit_used = TRUE; --sf_boss_hp; starfall_audio_sfx(STARFALL_SFX_CORE_HIT);
                    if (!sf_boss_hp) {
                        boss_open = FALSE; set_drone_phase(DORMANT,0); hide_actor(DRONE);
                        for (i = CELL_FIRST; i < CELL_FIRST + 3u; ++i) show_actor(i);
                    }
                }
            } else { boss_open = FALSE; boss_grace = 0; set_drone_phase(STUNNED,pulse_stun); }
        } else if (drone_phase != DORMANT) set_drone_phase(STUNNED,pulse_stun);
    }
    hud_dirty = palette_dirty = TRUE;
    starfall_audio_sfx(STARFALL_SFX_PULSE);
}
static void objectives_update(void) {
    UBYTE i, n, flags, previous_hold;
    if (room.objective == SF_OBJECTIVE_REPAIR || room.objective == SF_OBJECTIVE_ESCORT) {
        previous_hold = objective_state.hold;
        flags = room.objective == SF_OBJECTIVE_REPAIR ?
            starfall_repair_update(&objective_state,joy,room.hold_ticks) :
            starfall_escort_update(&objective_state,escort_route,0,escort_count);
        cargo = objective_state.progress; collected = objective_state.completed_mask;
        if (flags & SF_OBJECTIVE_ADVANCED) {
            wake_drone(); starfall_audio_sfx(STARFALL_SFX_RELAY); hud_dirty = palette_dirty = TRUE;
        }
        if (objective_state.hold && !(objective_state.hold % 5u)) hud_dirty = TRUE;
        else if (previous_hold && !objective_state.hold) hud_dirty = TRUE;
        return;
    }
    if (room.objective == SF_OBJECTIVE_CORE && sf_boss_hp) return;
    if (room.objective == SF_OBJECTIVE_RELAY) {
        /* Completed relays must never fall through into automatic salvage. */
        if (cargo >= 3u) return;
        n = CELL_FIRST + cargo;
        if (sf_gameplay_ticks & 8u) actors[n].flags |= ACTOR_FLAG_HIDDEN;
        else actors[n].flags &= ~ACTOR_FLAG_HIDDEN;
        if (INPUT_B && nearby(0,n,12)) {
            if (relay_hold < 30u) ++relay_hold;
            if (!(relay_hold % 5u)) hud_dirty = TRUE;
            if (relay_hold == 30u) {
                hide_actor(n); ++cargo; relay_hold = 0; wake_drone();
                starfall_audio_sfx(STARFALL_SFX_RELAY); hud_dirty = palette_dirty = TRUE;
            }
        } else if (relay_hold) { relay_hold = 0; hud_dirty = TRUE; }
        return;
    }
    for (i = 0; i != 3; ++i) if (!(collected & (1u << i)) && nearby(0,CELL_FIRST + i,12)) {
        collected |= 1u << i; ++cargo; hide_actor(CELL_FIRST + i);
        if (room.objective != SF_OBJECTIVE_CORE) wake_drone();
        else hazard_activate();
        starfall_audio_sfx(STARFALL_SFX_PICKUP); hud_dirty = palette_dirty = TRUE;
    }
}
static void configure_room(void) {
    UBYTE i;
    sf_hud_valid = FALSE;
    large_world = image_width > 160u || image_height > 144u;
    collected = cargo = relay_hold = 0; room_frames = 0;
    crew_grace = cache_hold = 0; sf_crew_hp = room.objective == SF_OBJECTIVE_ESCORT ? 2u : 0u;
    starfall_objective_init(&objective_state);
    escort_count = starfall_room_route(sf_room_index,escort_route);
    pulse_cooldown = pulse_timer = invulnerable = flash_timer = 0;
    boss_grace = boss_open = boss_hit_used = 0;
    hazard_kind = room.hazard; hazard_started = hazard_saved = hazard_valid = 0;
    if (!arcade && (sf_room_index & 3u) == 2u && sf_branch_order == 1u) hazard_kind = SF_HAZARD_NONE;
    hazard_phase = HAZARD_SAFE; hazard_timer = hazard_safe_frames();
    sf_boss_hp = room.objective == SF_OBJECTIVE_CORE ? 3u : 0;
    adv_vel_x = adv_vel_y = 0; adv_walk_vel = 5120; adv_dec = 128;
    PLAYER.flags &= ~ACTOR_FLAG_HIDDEN;
    for (i = 1; i != 7; ++i) show_actor(i);
    if (actors_len > CREW) {
        if (room.objective == SF_OBJECTIVE_ESCORT) show_actor(CREW); else hide_actor(CREW);
    }
    apply_module(pulse_module);
    if (!arcade && (sf_room_index & 3u) == 1u && sf_branch_order == 2u && pulse_reload > 72u) pulse_reload = 72u;
    hide_actor(PULSE); set_drone_phase(DORMANT,0);
    if (sf_boss_hp) for (i = CELL_FIRST; i < CELL_FIRST + 3u; ++i) hide_actor(i);
}
static void enter_play(void) {
    sf_mode = SF_MODE_PLAY; menu_grace = 0; hazard_stamp();
    /* Consume the confirmation edge while preserving held movement controls. */
    last_buttons = joy;
    if (sf_boss_hp) { boss_grace = 60; hazard_activate(); }
    hud_dirty = palette_dirty = TRUE; lighting(); hud(); starfall_audio_sfx(STARFALL_SFX_LAUNCH);
}
static void resume_play(void) { sf_mode = SF_MODE_PLAY; menu_grace = 0; lighting(); hud(); }

void starfall_encounter_init(void) BANKED {
    UBYTE i;
    if (!scene_transition) {
        arcade = 0; sector = 1; sf_room_index = 0; hull = 3; damage_total = 0;
        sortie_score = 0; campaign_frames = 0; sf_gameplay_ticks = 0;
        resume_stage = NO_RESUME_STAGE;
        sf_room_clear_mask = sf_branch_order = sf_mission_cursor = cache_found = 0;
        starfall_save_read(&persisted_session);
        if (persisted_session.has_checkpoint && !starfall_checkpoint_valid(&persisted_session)) persisted_session.has_checkpoint = FALSE;
        sf_save_status = persisted_session.has_checkpoint ? 1u : 0u;
        best_banked_score = persisted_session.best_banked;
        menu_cursor = 0; exit_return_mode = SF_MODE_PAUSE;
        direct_launch = 0;
        sf_mode = SF_MODE_TITLE; last_buttons = 0; apply_module(STANDARD); starfall_audio_init();
    }
    scene_transition = FALSE;
    starfall_room_read(sf_room_index,&room);
    for (i = 0; i < actors_len && i != 8; ++i) initial_positions[i] = actors[i].pos;
    memcpy(initial_background,BkgPalette,sizeof(initial_background)); initial_drone_palette = SprPalette[1];
    BkgPalette[7].c0 = CGB_COLOR(2,4,7); BkgPalette[7].c1 = CGB_COLOR(25,31,31);
    BkgPalette[7].c2 = CGB_COLOR(7,17,20); BkgPalette[7].c3 = CGB_COLOR(0,0,0);
    set_bkg_palette(7,1,(UWORD *)&BkgPalette[7]); starfall_ui_load_font(); configure_room();
    starfall_audio_zone(room.zone);
    if (sf_mode == SF_MODE_TRANSITION) {
        menu_cursor = 0;
        if (!arcade) hull = 3;
        if (resume_stage == SF_SAVE_STAGE_RESULT) { sf_mode = SF_MODE_RESULT; result_card(); }
        else if (resume_stage == SF_SAVE_STAGE_ENDING) { sf_mode = SF_MODE_ENDING; ending_card(); }
        else if (resume_stage == SF_SAVE_STAGE_BRANCH) { sf_mode = SF_MODE_BRANCH; branch_card(); }
        else if (resume_stage == SF_SAVE_STAGE_MISSION_BOARD) { sf_mode = SF_MODE_MISSION_BOARD; mission_board_card(); }
        else if (resume_stage == SF_SAVE_STAGE_MISSION_COMPLETE) { sf_mode = SF_MODE_MISSION_COMPLETE; mission_complete_card(); }
        else {
            sf_mode = SF_MODE_LAUNCH;
            if (!direct_launch) launch_card();
            else {
                /* Core paints this room after init; launch only after hazard_capture(). */
                overlay_cut_scanline = 0u; ui_set_pos(0,144); hide_sprites = TRUE;
                menu_grace = 0;
            }
        }
        resume_stage = NO_RESUME_STAGE;
    } else { sf_mode = SF_MODE_TITLE; title_card(); }
}

UBYTE starfall_encounter_update(void) BANKED {
    UBYTE pressed = joy & ~last_buttons;
    last_buttons = joy;
    if (!hazard_saved) hazard_capture();
    starfall_audio_title(sf_mode == SF_MODE_TITLE);
    starfall_audio_update(sf_mode != SF_MODE_PLAY);
    if (sf_mode == SF_MODE_TITLE) starfall_title_update();
    if (direct_launch && sf_mode == SF_MODE_LAUNCH) {
        direct_launch = FALSE; enter_play(); return FALSE;
    }
    if (menu_grace) { --menu_grace; return FALSE; }
    if (sf_mode == SF_MODE_TITLE) {
        if (menu_move(pressed,persisted_session.has_checkpoint ? 3u : 2u)) title_options();
        else if (pressed & J_A) {
            if (menu_cursor == 1u) start_game(TRUE);
            else if (menu_cursor == 2u) { sf_mode = SF_MODE_NEW_STORY_CONFIRM; new_story_card(); }
            else if (persisted_session.has_checkpoint) continue_story();
            else start_game(FALSE);
        }
        return FALSE;
    }
    if (sf_mode == SF_MODE_NEW_STORY_CONFIRM) {
        if (pressed & J_A) start_game(FALSE); else if (pressed & J_B) to_title();
        return FALSE;
    }
    if (sf_mode == SF_MODE_MISSION_BOARD) {
        if (pressed & J_B) to_title();
        else if (pressed & J_UP) { if (sf_mission_cursor) --sf_mission_cursor; else sf_mission_cursor = SF_MISSION_COUNT-1u; mission_board_card(); }
        else if (pressed & J_DOWN) { sf_mission_cursor = (sf_mission_cursor+1u)%SF_MISSION_COUNT; mission_board_card(); }
        else if (pressed & J_LEFT) change_rig(TRUE);
        else if (pressed & J_RIGHT) change_rig(FALSE);
        else if ((pressed & J_A) && mission_available(sf_mission_cursor)) {
            sf_room_clear_mask = sf_branch_order = 0; hull = 3;
            cache_found = !!(persisted_session.optional_flags & (1UL << sf_mission_cursor));
            direct_launch = TRUE;
            request_room(sf_mission_cursor * 4u);
        }
        return FALSE;
    }
    if (sf_mode == SF_MODE_BRANCH) {
        if (menu_move(pressed,2u)) branch_options();
        else if (pressed & J_A) {
            sf_branch_order = menu_cursor + 1u;
            direct_launch = TRUE;
            request_room((sf_room_index & 252u) + sf_branch_order);
        } else if (pressed & J_B) to_title();
        return FALSE;
    }
    if (sf_mode == SF_MODE_MISSION_COMPLETE) {
        if (pressed & J_A) open_mission_board(); else if (pressed & J_B) to_title();
        return FALSE;
    }
    if (sf_mode == SF_MODE_TRANSITION) return FALSE;
    if (sf_mode == SF_MODE_LOAD_BUSY) {
        if (pressed & J_A) request_room(pending_room); else if (pressed & J_B) to_title();
        return FALSE;
    }
    if (sf_mode == SF_MODE_LAUNCH) {
        if (pressed & J_A) enter_play();
        else if (pressed & J_B) {
            if (arcade) { exit_return_mode = SF_MODE_LAUNCH; sf_mode = SF_MODE_EXIT_CONFIRM; exit_card(); }
            else to_title();
        }
        return FALSE;
    }
    if (sf_mode == SF_MODE_PAUSE) {
        if (pressed & (J_B | J_START)) resume_play();
        else if (menu_move(pressed,3u)) pause_options();
        else if ((pressed & J_SELECT) || ((pressed & J_A) && menu_cursor == 2u)) {
            exit_return_mode = SF_MODE_PAUSE; sf_mode = SF_MODE_EXIT_CONFIRM; exit_card();
        } else if (pressed & J_A) {
            if (!menu_cursor) resume_play();
            else if (arcade) start_game(TRUE);
            else { hull = 3; request_room(sf_room_index); }
        }
        return FALSE;
    }
    if (sf_mode == SF_MODE_EXIT_CONFIRM) {
        if (pressed & J_A) to_title();
        else if (pressed & J_B) {
            sf_mode = exit_return_mode;
            if (sf_mode == SF_MODE_ARCADE_DOCK) arcade_dock_card();
            else if (sf_mode == SF_MODE_LAUNCH) launch_card();
            else pause_card();
        }
        return FALSE;
    }
    if (sf_mode == SF_MODE_FAILURE) {
        if (pressed & J_A) { if (arcade) start_game(TRUE); else { hull = 3; request_room(sf_room_index); } }
        else if (pressed & J_B) to_title();
        return FALSE;
    }
    if (sf_mode == SF_MODE_ENDING) {
        if (pressed & (J_A | J_B)) to_title();
        return FALSE;
    }
    if (sf_mode == SF_MODE_BANK_RESULT) {
        if (pressed & (J_A | J_B)) to_title();
        return FALSE;
    }
    if (sf_mode == SF_MODE_ARCADE_DOCK) {
        if (menu_move(pressed,3u)) arcade_dock_options();
        else if (pressed & J_A) {
            if (!menu_cursor) next_room();
            else if (menu_cursor == 1u) { menu_cursor = 0; sf_mode = SF_MODE_UPGRADE; upgrade_card(); }
            else { sf_mode = SF_MODE_BANK_RESULT; bank_card(); }
        } else if (pressed & J_B) {
            exit_return_mode = SF_MODE_ARCADE_DOCK; sf_mode = SF_MODE_EXIT_CONFIRM; exit_card();
        }
        return FALSE;
    }
    if (sf_mode == SF_MODE_RESULT) {
        if (pressed & J_A) next_room(); else if (pressed & J_B) to_title();
        return FALSE;
    }
    if (sf_mode == SF_MODE_UPGRADE) {
        if (menu_move(pressed,3u)) upgrade_options();
        else if (pressed & J_B) {
            menu_cursor = 0; sf_mode = SF_MODE_ARCADE_DOCK; arcade_dock_card();
        } else if (pressed & J_A) {
            if (menu_cursor) apply_module(menu_cursor == 1u ? choice_a : choice_b);
            next_room();
        }
        return FALSE;
    }
    if (pressed & J_START) { menu_cursor = 0; sf_mode = SF_MODE_PAUSE; pause_card(); return FALSE; }
    if (pressed & J_SELECT) { menu_cursor = 0; exit_return_mode = SF_MODE_PAUSE; sf_mode = SF_MODE_EXIT_CONFIRM; exit_card(); return FALSE; }

    /* Keep the user-qualified thrust, turning, and brake feel unchanged. */
    adv_walk_vel = INPUT_B ? 1536 : 5120; adv_dec = INPUT_B ? 2048 : 128;
    ++sf_gameplay_ticks; ++room_frames;
    if (large_world && !(sf_gameplay_ticks & 15u)) hud_dirty = TRUE;
    if (pulse_cooldown && !--pulse_cooldown) hud_dirty = TRUE;
    if (flash_timer && !--flash_timer) palette_dirty = TRUE;
    if (invulnerable) {
        --invulnerable;
        if (invulnerable & 4u) PLAYER.flags |= ACTOR_FLAG_HIDDEN; else PLAYER.flags &= ~ACTOR_FLAG_HIDDEN;
    } else PLAYER.flags &= ~ACTOR_FLAG_HIDDEN;
    if (pulse_timer) {
        --pulse_timer; actors[PULSE].pos = PLAYER.pos;
        if (!pulse_timer) { hide_actor(PULSE); palette_dirty = TRUE; }
    }
    if ((pressed & J_A) && !pulse_cooldown) pulse();
    objectives_update(); drone_update(); hazard_update();
    if (crew_grace) --crew_grace;
    if (room.objective == SF_OBJECTIVE_ESCORT && sf_crew_hp && !crew_grace &&
        ((drone_phase == CHARGING && nearby(CREW,DRONE,11) &&
          !starfall_world_dock_contains(actor_x(CREW),actor_y(CREW))) || hazard_hits_actor(CREW))) {
        --sf_crew_hp; crew_grace = 90; flash_timer = 10; hud_dirty = palette_dirty = TRUE;
        starfall_audio_sfx(STARFALL_SFX_HIT);
        if (drone_phase == CHARGING) begin_recovery();
        if (!sf_crew_hp) objective_state.flags |= SF_OBJECTIVE_FAILED;
    }
    if (objective_state.flags & SF_OBJECTIVE_FAILED) {
        sf_mode = SF_MODE_FAILURE; hide_actor(PULSE); checkpoint(SF_SAVE_STAGE_LAUNCH); failure_card(); return FALSE;
    }
    if (!arcade && !cache_found && room.cache_x && magnitude(actor_x(0)-room.cache_x) <= 12u &&
        magnitude(actor_y(0)-room.cache_y) <= 12u && INPUT_B) {
        if (cache_hold < 20u) ++cache_hold;
        if (cache_hold == 20u) {
            cache_found = TRUE; persisted_session.optional_flags |= 1UL << (sf_room_index / 4u);
            starfall_audio_sfx(STARFALL_SFX_PICKUP); hud_dirty = palette_dirty = TRUE;
        }
    } else cache_hold = 0;
    if (!invulnerable && ((drone_phase == CHARGING && !safe_dock() && nearby(0,DRONE,11)) || hazard_hits_actor(0))) {
        --hull; if (damage_total != 255u) ++damage_total;
        invulnerable = 90; flash_timer = 10; adv_vel_x = adv_vel_y = 0;
        if (room.objective == SF_OBJECTIVE_CORE && sf_boss_hp) { if (drone_phase == CHARGING) begin_recovery(); }
        else if (drone_phase != DORMANT) set_drone_phase(RECOVERING,60);
        hud_dirty = palette_dirty = TRUE; starfall_audio_sfx(STARFALL_SFX_HIT);
        if (!hull) {
            sf_mode = SF_MODE_FAILURE; hide_actor(PULSE); PLAYER.flags &= ~ACTOR_FLAG_HIDDEN;
            checkpoint(SF_SAVE_STAGE_LAUNCH);
            failure_card(); return FALSE;
        }
    }
    if (cargo == 3u && (room.objective != SF_OBJECTIVE_ESCORT || (objective_state.flags & SF_OBJECTIVE_READY)) &&
        safe_dock() && magnitude(actor_x(0) - actor_x(TERMINAL)) <= 20u &&
        magnitude(actor_y(0) - actor_y(TERMINAL)) <= 16u) {
        adv_vel_x = adv_vel_y = 0; hide_actor(PULSE); PLAYER.flags &= ~ACTOR_FLAG_HIDDEN;
        starfall_audio_sfx(STARFALL_SFX_WIN);
        if (arcade) {
            UWORD earned = (sector > 10u ? 10u : sector) * 300u;
            sortie_score = sortie_score > 60000u - earned ? 60000u : sortie_score + earned;
            if (hull < 3u) ++hull; menu_cursor = 0; sf_mode = SF_MODE_ARCADE_DOCK; arcade_dock_card();
        } else {
            UBYTE mission = sf_room_index / 4u, local = sf_room_index & 3u;
            campaign_frames += room_frames;
            sf_room_clear_mask |= 1u << local; hull = 3;
            if (local == 3u) {
                if (!(persisted_session.mission_flags & (1UL << mission))) {
                    persisted_session.credits = persisted_session.credits > 59700u ? 60000u : persisted_session.credits + 300u;
                }
                persisted_session.mission_flags |= 1UL << mission;
                if (mission == 0u) persisted_session.unlock_flags |= SF_SAVE_UNLOCK_WIDE;
                if (mission == 1u) persisted_session.unlock_flags |= SF_SAVE_UNLOCK_FAST;
                if (mission == 8u) persisted_session.unlock_flags |= SF_SAVE_UNLOCK_OVERCHARGE;
                if ((persisted_session.mission_flags & MISSION_BITS) == (1UL << SF_MISSION_COUNT)-1UL) {
                    persisted_session.campaign_complete = TRUE;
                    sf_mode = SF_MODE_ENDING; checkpoint(SF_SAVE_STAGE_ENDING); ending_card();
                } else { sf_mode = SF_MODE_MISSION_COMPLETE; checkpoint(SF_SAVE_STAGE_MISSION_COMPLETE); mission_complete_card(); }
            } else if (!local) {
                menu_cursor = 0; sf_mode = SF_MODE_BRANCH; checkpoint(SF_SAVE_STAGE_BRANCH); branch_card();
            } else { sf_mode = SF_MODE_RESULT; checkpoint(SF_SAVE_STAGE_RESULT); result_card(); }
        }
        return FALSE;
    }
    if (hud_dirty) hud(); if (palette_dirty) lighting();
    return TRUE;
}
