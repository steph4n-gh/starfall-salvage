#!/usr/bin/env python3
"""Execute the real encounter/save C on a host; compare protected v1.1 mechanics.

Rendering, room loading, and audio are stubs. Assertions exercise production
update/init/save code, not a Python recreation of its state machine. This does
not qualify ROM banking, pixels, collision geometry, sound, or hardware SRAM.
Run from any directory: python3 scripts/test-ui-flow.py [--report receipt.json]
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SRC = "plugins/starfall/engine/src/"
INC = "plugins/starfall/engine/include/"
BASE = "1726211af6fe8b8735b6e357e0dab024f27d21a9"


def masked(text):
    # Keep offsets/lines while excluding braces in comments and string literals.
    pattern = r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
    return re.sub(pattern, lambda m: re.sub(r"[^\n]", " ", m[0]), text)


def block(text, name, array=False):
    clean = masked(text)
    pattern = (r"\b" + re.escape(name) + r"\s*\[[^;=]*=\s*\{" if array else
               r"\b" + re.escape(name) + r"\s*\([^;{}]*\)\s*(?:BANKED|NONBANKED)?\s*\{")
    match = re.search(pattern, clean)
    if not match:
        raise AssertionError(f"Missing C boundary: {name}")
    start = clean.index("{", match.start())
    depth = 1
    end = start + 1
    while depth:
        depth += (clean[end] == "{") - (clean[end] == "}")
        end += 1
    return text[start:end], text.count("\n", 0, start) + 1


def stripped(text):
    return re.sub(r"^\s*#\s*(?:include|pragma)[^\n]*", "", text, flags=re.M)


def digest(data):
    return hashlib.sha256(data.encode() if isinstance(data, str) else data).hexdigest()


def preservation():
    entries = []

    def compare(path, boundary, before, after, line=None):
        entry = dict(path=path, boundary=boundary, baselineSha256=digest(before),
                     currentSha256=digest(after), unchanged=before == after)
        if line is not None:
            entry["currentStartLine"] = line
        entries.append(entry)
        assert entry["unchanged"], f"Protected mechanics changed: {path}:{boundary}"

    def versions(path):
        return (subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT).decode(),
                (ROOT / path).read_text())

    for path in (SRC + "states/adventure.c", SRC + "starfall_world.c",
                 SRC + "starfall_objectives.c", SRC + "starfall_save.c", INC + "starfall_save.h"):
        before, after = versions(path)
        compare(path, "whole file", before, after)
    path = SRC + "starfall_encounter.c"
    before, after = versions(path)
    names = ("apply_module", "hazard_safe_frames", "hazard_activate", "hazard_update",
             "hazard_hits_actor", "tint", "lighting", "enemy_blocked", "enemy_move",
             "set_drone_phase", "begin_recovery", "begin_warning", "hunter_step",
             "drone_update", "wake_drone", "pulse", "objectives_update", "configure_room")
    for name in names:
        old, _ = block(before, name)
        new, line = block(after, name)
        compare(path, name + " body", old, new, line)
    marker = "    /* Keep the user-qualified thrust, turning, and brake feel unchanged. */"
    compare(path, "PLAY mechanics and rewards through update return", before[before.index(marker):],
            after[after.index(marker):], after[:after.index(marker)].count("\n") + 1)
    path = SRC + "starfall_rooms.c"
    before, after = versions(path)
    old, _ = block(before, "starfall_checkpoint_valid")
    new, line = block(after, "starfall_checkpoint_valid")
    compare(path, "checkpoint validity body", old, new, line)
    path = SRC + "starfall_audio.c"
    before, after = versions(path)
    clean = masked(before)
    for name in re.findall(r"static\s+const\s+\w+\s+(\w+)\s*\[", clean):
        old, _ = block(before, name, True)
        new, line = block(after, name, True)
        compare(path, name + " score data", old, new, line)
    for name in ("load_wave", "play_lead", "play_bass", "play_cue_note", "play_noise",
                 "restore_music_levels", "play_song_step", "update_cue", "starfall_audio_sfx"):
        old, _ = block(before, name)
        new, line = block(after, name)
        compare(path, name + " body", old, new, line)
    return entries


PLATFORM = r"""
#ifndef HOST_PLATFORM_H
#define HOST_PLATFORM_H
#include <stdint.h>
typedef uint8_t UBYTE; typedef uint16_t UWORD; typedef int16_t WORD;
#define BANKED
#define NONBANKED
#define TRUE 1
#define FALSE 0
#define CGB_COLOR(r,g,b) ((r)|((g)<<5)|((b)<<10))
typedef struct { UWORD x,y; } upoint16_t;
typedef struct { WORD x,y; } point16_t;
#endif
"""

HOST = r"""
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "gbdk/platform.h"
#include "starfall_audio.h"
#include "starfall_rooms.h"
#include "starfall_screens.h"
#include "starfall_encounter.h"
#include "starfall_save.h"
#include "starfall_world.h"
#include "starfall_objectives.h"
#include "starfall_ui.h"
#define J_A 1u
#define J_B 2u
#define J_SELECT 4u
#define J_START 8u
#define J_RIGHT 16u
#define J_LEFT 32u
#define J_UP 64u
#define J_DOWN 128u
#define INPUT_B (joy & J_B)
#define ACTOR_FLAG_HIDDEN 1u
#define ACTOR_FLAG_DISABLED 2u
#define ACTOR_FLAG_COLLISION 4u
#define COLLISION_GROUP_NONE 0u
typedef struct { upoint16_t pos; struct { WORD left,right,top,bottom; } bounds; UBYTE flags,collision_group; } actor_t;
typedef struct { UWORD c0,c1,c2,c3; } palette_entry_t;
actor_t actors[8];
#define PLAYER actors[0]
UBYTE actors_len=8,joy,VBK_REG,hide_sprites,overlay_cut_scanline,sf_hud_valid;
UWORD image_width=160,image_height=144,image_tile_width=20,image_tile_height=18;
WORD adv_walk_vel,adv_dec,adv_vel_x,adv_vel_y,draw_scroll_x,draw_scroll_y;
palette_entry_t BkgPalette[8],SprPalette[8];
static unsigned stores, room_requests, pulse_sounds, assertions;
static int write_budget=-1;
static UBYTE requested_room;
static UBYTE title_music;
static UBYTE rendered_card_y,rendered_detail_y,rendered_selected;
static char rendered_label[21],rendered_detail[21];
volatile UBYTE sf_save_test_sram[104],_current_ram_bank;
#define STARFALL_SAVE_HOST_TEST
#define SRAM_BANKS_TO_SAVE 3
#define ENABLE_RAM_MBC5 ((void)0)
#define RAM_BANKS_AND_FLAGS 255u
#define SWITCH_RAM_BANK(bank,mask) (_current_ram_bank=(_current_ram_bank & ~(mask))|((bank)&(mask)))
void sf_save_test_store(UBYTE offset,UBYTE value) { assert(offset<104); if(write_budget<0 || stores<(unsigned)write_budget)sf_save_test_sram[offset]=value; ++stores; }
void activate_actor(actor_t *a) {(void)a;}
void deactivate_actor(actor_t *a) {(void)a;}
void get_bkg_tiles(UBYTE x,UBYTE y,UBYTE w,UBYTE h,UBYTE *p) {(void)x;(void)y;memset(p,0,w*h);}
void set_bkg_tiles(UBYTE x,UBYTE y,UBYTE w,UBYTE h,const UBYTE *p) {(void)x;(void)y;(void)w;(void)h;(void)p;}
void set_bkg_data(UBYTE a,UBYTE b,const UBYTE *p) {(void)a;(void)b;(void)p;}
void set_bkg_palette(UBYTE a,UBYTE b,const UWORD *p) {(void)a;(void)b;(void)p;}
void set_sprite_palette(UBYTE a,UBYTE b,const UWORD *p) {(void)a;(void)b;(void)p;}
void ui_set_pos(UBYTE x,UBYTE y) {(void)x;(void)y;}
void starfall_audio_init(void) {title_music=0;}
void starfall_audio_zone(UBYTE z) {(void)z;}
void starfall_audio_title(UBYTE enabled) {title_music=enabled;}
void starfall_audio_update(UBYTE p) {(void)p;}
void starfall_audio_sfx(UBYTE e) {if(e==STARFALL_SFX_PULSE) ++pulse_sounds;}
void starfall_title_update(void) {}
void starfall_screen_show(UBYTE k,UBYTE z,UBYTE r) {(void)k;(void)z;(void)r;}
void starfall_ui_load_font(void) {}
void starfall_ui_text_row(UBYTE y,const char *s) {(void)y;(void)s;}
void starfall_ui_centered_row(UBYTE y,const char *s) {(void)y;(void)s;}
void starfall_ui_header(const char *s) {(void)s;}
void starfall_ui_menu_card(UBYTE y,UBYTE h,UBYTE b,const char *s) {(void)y;(void)h;(void)b;(void)s;}
void starfall_ui_card_detail(UBYTE y,UBYTE b,const char *s) {(void)y;(void)b;(void)s;}
void starfall_ui_footer(UBYTE kind) {(void)kind;}
void starfall_ui_menu_option(UBYTE y,UBYTE b,const char *s) {(void)y;(void)b;(void)s;}
void starfall_ui_module_option(UBYTE y,UBYTE b,UBYTE m) {(void)y;(void)b;(void)m;}
void starfall_ui_module_name(UBYTE y,UBYTE m) {(void)y;(void)m;}
void starfall_ui_module_description(UBYTE y,UBYTE m) {(void)y;(void)m;}
void starfall_ui_objective_hint(UBYTE y,UBYTE objective) {(void)y;(void)objective;}
void starfall_ui_render_menu_card(UBYTE y,UBYTE h,UBYTE selected,const char *s) {(void)h;rendered_card_y=y;rendered_selected=selected;strncpy(rendered_label,s,20);rendered_label[20]=0;}
void starfall_ui_render_card_detail(UBYTE y,UBYTE selected,const char *s) {rendered_detail_y=y;rendered_selected=selected;strncpy(rendered_detail,s,20);rendered_detail[20]=0;}
void starfall_ui_hud_row(UBYTE y,const char *s) {(void)y;(void)s;}
void starfall_ui_two_digits(char *d,UWORD n) {d[0]='0'+n/10%10;d[1]='0'+n%10;}
void starfall_ui_five_digits(char *d,UWORD n) {UBYTE i;for(i=5;i;i--){d[i-1]='0'+n%10;n/=10;}}
void starfall_ui_elapsed_time(char *d,uint32_t n) {(void)n;memcpy(d,"00:00:00",8);}
void starfall_ui_exit_card_text(UBYTE a) {(void)a;}
void starfall_ui_new_story_card_text(void) {}
void starfall_room_read(UBYTE i,sf_room_t *r) {memset(r,0,sizeof(*r));strcpy(r->name,"HOST FIXTURE");r->zone=i/12;r->warning_frames=40;r->dash_frames=20;r->recover_frames=60;r->speed=32;}
void starfall_mission_name(UBYTE i,char *d) {(void)i;strcpy(d,"HOST MISSION");}
UBYTE starfall_room_route(UBYTE i,upoint16_t *d) {(void)i;(void)d;return 0;}
UBYTE starfall_room_change(UBYTE i) {++room_requests;requested_room=i;return TRUE;}
void starfall_world_actor_center(UBYTE i,point16_t *p) {p->x=actors[i].pos.x>>5;p->y=actors[i].pos.y>>5;}
UBYTE starfall_world_dock_contains(WORD x,WORD y) {(void)x;return y>=112;}
UBYTE starfall_world_enemy_blocked(WORD x,WORD y) {(void)x;(void)y;return FALSE;}
void starfall_world_target_delta(WORD x,WORD y,UBYTE s,point16_t *p) {p->x=x? (x<0?-s:s):0;p->y=y?(y<0?-s:s):0;}
void starfall_objective_init(sf_objective_state_t *s) {memset(s,0,sizeof(*s));}
UBYTE starfall_repair_update(sf_objective_state_t *s,UBYTE b,UBYTE t) {(void)b;(void)t;return s->flags;}
UBYTE starfall_escort_update(sf_objective_state_t *s,const upoint16_t *p,UBYTE b,UBYTE n) {(void)p;(void)b;(void)n;return s->flags;}
"""

TESTS = r"""
#define CHECK(c) do {++assertions;if(!(c)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#c);return 1;}}while(0)
static void tick(UBYTE buttons) {joy=buttons;starfall_encounter_update();}
static void settle(void) {UBYTE i;for(i=0;i<22;i++) tick(0);}
static void tap(UBYTE buttons) {tick(0);tick(buttons);}
static void fresh(void) {
    UBYTE i;
    memset((void *)sf_save_test_sram,255,sizeof(sf_save_test_sram));
    memset(actors,0,sizeof(actors));
    for(i=0;i<8;i++){actors[i].pos.x=(20u+i*16u)*32u;actors[i].pos.y=40u*32u;}
    actors[0].pos.x=actors[4].pos.x=80u*32u;actors[0].pos.y=actors[4].pos.y=120u*32u;
    scene_transition=FALSE;joy=0;starfall_encounter_init();settle();
    stores=room_requests=pulse_sounds=0;write_budget=-1;
}
static void dock(UBYTE sec) {
    fresh();arcade=TRUE;sector=sec;sf_room_index=SF_ARCADE_FIRST+sec-1;
    sf_mode=SF_MODE_PLAY;cargo=3;hull=2;sortie_score=700;
    tick(0);settle();
}
static int test_fly_and_held_input(void) {
    unsigned i; UWORD score,ticks;
    dock(1);apply_module(WIDE_COIL);score=sortie_score;
    CHECK(sf_mode==SF_MODE_ARCADE_DOCK && menu_cursor==0 && score==1000 && hull==3);
    tap(J_A);CHECK(sf_mode==SF_MODE_TRANSITION && requested_room==SF_ARCADE_FIRST+1);
    CHECK(sector==2 && pulse_module==WIDE_COIL && sortie_score==score && !stores);
    starfall_encounter_init();tick(J_A);ticks=sf_gameplay_ticks;
    CHECK(sf_mode==SF_MODE_PLAY);
    for(i=0;i<60;i++)tick(J_A|J_RIGHT);
    CHECK(sf_gameplay_ticks==ticks+60 && !pulse_sounds && sortie_score==score);
    tick(J_A|J_RIGHT|J_START);CHECK(sf_mode==SF_MODE_PAUSE);
    settle();tick(J_RIGHT|J_B);CHECK(sf_mode==SF_MODE_PLAY);
    tick(J_RIGHT|J_B);CHECK(adv_walk_vel==1536 && adv_dec==2048);
    tick(0);CHECK(!pulse_sounds);
    tap(J_A);CHECK(pulse_sounds==1);
    puts("PASS default Fly on; retained rig/loot; held A does not pulse; held direction/brake/pause remain responsive");return 0;
}
static int test_route_ui_perks(void) {
    UBYTE objective,branch;
    for(branch=0;branch<2;branch++)for(objective=0;objective<=SF_OBJECTIVE_ESCORT;objective++){
        starfall_ui_route_option(branch,TRUE,objective);
        CHECK(rendered_card_y==(branch?11:6) && rendered_detail_y==(branch?14:9) && rendered_selected);
        CHECK(!strcmp(rendered_detail,branch?"THEN FAST PULSE":"THEN HAZARD OFF"));
        if(branch && (objective==SF_OBJECTIVE_REPAIR || objective==SF_OBJECTIVE_RELAY))CHECK(!strcmp(rendered_label,"TOOLS FIRST"));
    }
    puts("PASS actual route UI helper: perk follows branch for every objective, including repair/relay second bays");return 0;
}
static int test_optional_rigs(void) {
    const UBYTE offers[5][2]={{FAST_CAPACITOR,WIDE_COIL},{OVERCHARGE,HULL_PATCH},{STANDARD,FAST_CAPACITOR},{WIDE_COIL,OVERCHARGE},{HULL_PATCH,FAST_CAPACITOR}};
    UBYTE s,c;UWORD score;
    dock(1);score=sortie_score;tap(J_DOWN);tap(J_A);settle();
    CHECK(sf_mode==SF_MODE_UPGRADE);tap(J_B);settle();
    CHECK(sf_mode==SF_MODE_ARCADE_DOCK && !menu_cursor && sortie_score==score && hull==3 && pulse_module==STANDARD);
    for(s=1;s<=5;s++)for(c=0;c<3;c++){
        dock(s);score=sortie_score;tap(J_DOWN);tap(J_A);settle();
        CHECK(choice_a==offers[s-1][0] && choice_b==offers[s-1][1]);
        if(c)tap(J_DOWN);if(c==2)tap(J_DOWN);
        if(c && offers[s-1][c-1]==HULL_PATCH)hull=1;
        tap(J_A);CHECK(sf_mode==SF_MODE_TRANSITION && sector==s+1 && sortie_score==score);
        CHECK(pulse_module==(c && offers[s-1][c-1]!=HULL_PATCH ? offers[s-1][c-1]:STANDARD));
        CHECK(hull==3 && !stores);
    }
    puts("PASS optional Rig/B back; all five offers and keep/replace/Hull Patch choices");return 0;
}
static int test_bank_and_cancel(void) {
    sf_save_t original,restored;unsigned n,i;UWORD score;
    dock(1);score=sortie_score;memset(&original,0,sizeof(original));
    original.has_checkpoint=1;original.room=1;original.checkpoint_stage=SF_SAVE_STAGE_RESULT;
    original.mission_flags=CAMPAIGN_SIGNATURE;original.room_clear_mask=3;original.branch_order=1;
    original.hull_value=3;original.credits=123;original.optional_flags=9;original.rig=WIDE_COIL;
    CHECK(starfall_save_write(&original));stores=0;
    tap(J_B);settle();CHECK(sf_mode==SF_MODE_EXIT_CONFIRM);tap(J_B);settle();
    CHECK(sf_mode==SF_MODE_ARCADE_DOCK && sortie_score==score && hull==3 && !stores);
    tap(J_DOWN);tap(J_DOWN);tap(J_A);CHECK(sf_mode==SF_MODE_BANK_RESULT);
    n=stores;CHECK(n==41);for(i=0;i<60;i++)tick(J_A);CHECK(stores==n);
    CHECK(starfall_save_read(&restored));original.best_banked=score;
    CHECK(!memcmp(&original,&restored,sizeof(original)));
    CHECK(_current_ram_bank==0);
    puts("PASS Dock exit cancellation; explicit Bank commits once and preserves Story checkpoint");return 0;
}
static int test_interrupted_save_and_arcade_loop(void) {
    sf_save_t original,restored;
    fresh();memset(&original,0,sizeof(original));original.has_checkpoint=1;
    original.mission_flags=CAMPAIGN_SIGNATURE;original.hull_value=3;original.credits=456;
    CHECK(starfall_save_write(&original));persisted_session=original;
    sf_room_index=1;sf_room_clear_mask=1;persisted_session.credits=999;
    stores=0;write_budget=10;checkpoint(SF_SAVE_STAGE_LAUNCH);
    CHECK(sf_save_status==2 && starfall_save_read(&restored));
    CHECK(!memcmp(&original,&restored,sizeof(original)));
    /* Banking must not accidentally commit the failed Story draft. */
    stores=0;write_budget=-1;sortie_score=1000;bank_card();original.best_banked=1000;
    CHECK(sf_save_status==1 && starfall_save_read(&restored));
    CHECK(!memcmp(&original,&restored,sizeof(original)));
    dock(12);sf_room_index=SF_ARCADE_FIRST+11;tap(J_A);
    CHECK(requested_room==SF_ARCADE_FIRST && sector==13);
    puts("PASS interrupted checkpoint fallback; Bank retains committed Story; sector-12 map loop");return 0;
}
static int test_story_rewards_and_board(void) {
    sf_save_t loaded;unsigned n;UBYTE i;
    fresh();sf_room_index=3;sf_mode=SF_MODE_PLAY;cargo=3;sf_room_clear_mask=7;
    persisted_session.mission_flags=CAMPAIGN_SIGNATURE;persisted_session.credits=100;
    tick(0);CHECK(sf_mode==SF_MODE_MISSION_COMPLETE && persisted_session.credits==400);
    n=stores;for(i=0;i<60;i++)tick(0);CHECK(stores==n && persisted_session.credits==400);
    CHECK(starfall_save_read(&loaded) && loaded.credits==400 && (loaded.mission_flags&1u));
    tap(J_A);CHECK(sf_mode==SF_MODE_MISSION_BOARD && sf_mission_cursor==1);
    /* Replay the already-rewarded job through the same production dock check. */
    sf_mode=SF_MODE_PLAY;menu_grace=0;sf_room_index=3;sf_room_clear_mask=7;cargo=3;tick(0);
    CHECK(persisted_session.credits==400 && (persisted_session.unlock_flags&SF_SAVE_UNLOCK_WIDE));
    persisted_session.mission_flags=CAMPAIGN_SIGNATURE|3u;sf_room_index=7;open_mission_board();CHECK(sf_mission_cursor==2);
    persisted_session.mission_flags=CAMPAIGN_SIGNATURE|7u;sf_room_index=11;open_mission_board();CHECK(sf_mission_cursor==3);
    puts("PASS one reward per mission across replay; rig unlock and next available unfinished job");return 0;
}
static int test_checkpoint_stages(void) {
    const UBYTE stages[]={SF_SAVE_STAGE_LAUNCH,SF_SAVE_STAGE_RESULT,SF_SAVE_STAGE_BRANCH,SF_SAVE_STAGE_MISSION_BOARD,SF_SAVE_STAGE_MISSION_COMPLETE,SF_SAVE_STAGE_ENDING};
    const UBYTE rooms[]={0,1,0,0,3,71}, masks[]={0,3,1,0,15,15};
    const UBYTE modes[]={SF_MODE_LAUNCH,SF_MODE_RESULT,SF_MODE_BRANCH,SF_MODE_MISSION_BOARD,SF_MODE_MISSION_COMPLETE,SF_MODE_ENDING};
    UBYTE i,j;sf_save_t old,after;
    for(i=0;i<sizeof(stages);i++){
        fresh();memset(&old,0,sizeof(old));old.has_checkpoint=1;old.room=rooms[i];old.checkpoint_stage=stages[i];
        old.mission_flags=CAMPAIGN_SIGNATURE;old.room_clear_mask=masks[i];old.hull_value=3;
        old.rig=WIDE_COIL;old.branch_order=1;old.credits=321;old.successful_frames=12345;
        old.campaign_complete=stages[i]==SF_SAVE_STAGE_ENDING;
        CHECK(starfall_checkpoint_valid(&old) && starfall_save_write(&old));stores=0;
        scene_transition=FALSE;starfall_encounter_init();settle();tap(J_A);
        CHECK(sf_mode==SF_MODE_TRANSITION);starfall_encounter_init();
        CHECK(sf_mode==modes[i] && pulse_module==WIDE_COIL && !stores);
        for(j=0;j<60;j++)tick(J_A);CHECK(sf_mode==modes[i] && !stores);
        CHECK(starfall_save_read(&after) && !memcmp(&old,&after,sizeof(old)));
    }
    old.checkpoint_stage=SF_SAVE_STAGE_UPGRADE;CHECK(!starfall_checkpoint_valid(&old));
    puts("PASS six valid v1.1 checkpoint stages restore without rewriting; obsolete Story Upgrade rejected");return 0;
}
static int test_both_routes(void) {
    UBYTE order,other;
    for(order=1;order<=2;order++){
        fresh();sf_mode=SF_MODE_BRANCH;sf_room_index=0;sf_room_clear_mask=1;menu_cursor=order-1;
        tap(J_A);CHECK(requested_room==order && sf_branch_order==order);
        starfall_encounter_init();tick(J_A);tick(0);tick(0);
        sf_mode=SF_MODE_RESULT;sf_room_clear_mask=1u|(1u<<order);menu_grace=0;
        other=order==1?2:1;tap(J_A);CHECK(requested_room==other);
        starfall_encounter_init();tick(J_A);tick(0);tick(0);
        if(order==1)CHECK(hazard_kind==SF_HAZARD_NONE);
        if(order==2)CHECK(pulse_reload==72);
        sf_mode=SF_MODE_RESULT;sf_room_clear_mask=7;menu_grace=0;tap(J_A);CHECK(requested_room==3);
    }
    puts("PASS both branch orders reach both middle bays then Guardian; existing route bonuses retained");return 0;
}
int main(void) {
    if(test_fly_and_held_input() || test_route_ui_perks() || test_optional_rigs() || test_bank_and_cancel() ||
       test_interrupted_save_and_arcade_loop() || test_story_rewards_and_board() ||
       test_checkpoint_stages() || test_both_routes())return 1;
    printf("PASS %u production-code assertions\n",assertions);return 0;
}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="optional JSON evidence file")
    parser.add_argument("--negative-controls", action="store_true", help="prove three deliberately broken flows fail")
    args = parser.parse_args()
    compiler = shutil.which("cc") or shutil.which("clang")
    if not compiler:
        raise SystemExit("A host C compiler (cc or clang) is required")
    source = (ROOT / SRC / "starfall_encounter.c").read_text()
    save = (ROOT / SRC / "starfall_save.c").read_text()
    rooms = (ROOT / SRC / "starfall_rooms.c").read_text()
    ui = (ROOT / SRC / "starfall_ui.c").read_text()
    validator, _ = block(rooms, "starfall_checkpoint_valid")
    route_ui, _ = block(ui, "starfall_ui_route_option")
    checks = preservation()
    with tempfile.TemporaryDirectory(prefix="sf-ui-test-") as directory:
        temp = Path(directory)
        for name in ("gbdk/platform.h", "gb/gb.h", "math.h"):
            target = temp / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(PLATFORM if name == "gbdk/platform.h" else '#include "gbdk/platform.h"\n')
        prefix = HOST + "\n" + stripped(save) + "\nUBYTE starfall_checkpoint_valid(const sf_save_t *saved) " + validator
        prefix += "\nvoid starfall_ui_route_option(UBYTE branch,UBYTE selected,UBYTE objective) " + route_ui
        unit = prefix + "\n" + stripped(source) + "\n" + TESTS
        (temp / "flow.c").write_text(unit)
        command = [compiler, "-std=c99", "-Wall", "-Wextra", "-Wno-unused-parameter", "-Wno-misleading-indentation",
                   "-fsanitize=undefined,bounds", "-fno-sanitize-recover=all",
                   "-I", str(temp), "-I", str(ROOT / INC), str(temp / "flow.c"), "-o", str(temp / "flow")]
        subprocess.run(command, check=True)
        result = subprocess.run([str(temp / "flow")], text=True, capture_output=True)
        if result.returncode:
            raise SystemExit(result.stdout + result.stderr)
        controls = []
        if args.negative_controls:
            mutations = (
                ("launch confirmation edge forgotten", block(source,"enter_play")[0], block(source,"enter_play")[0].replace("last_buttons = joy;","last_buttons = 0;")),
                ("default Fly opens Rig", "if (!menu_cursor) next_room();", "if (!menu_cursor) { sf_mode=SF_MODE_UPGRADE; upgrade_card(); }"),
                ("replay rewards duplicated", "if (!(persisted_session.mission_flags & (1UL << mission)))", "if (TRUE)"),
            )
            for name, old, new in mutations:
                assert source.count(old) == 1, f"Negative control boundary changed: {name}"
                (temp / "flow.c").write_text(prefix + "\n" + stripped(source.replace(old, new)) + "\n" + TESTS)
                subprocess.run(command, check=True)
                broken = subprocess.run([str(temp / "flow")], text=True, capture_output=True)
                assert broken.returncode != 0 and "FAIL line" in broken.stderr, f"Undetected negative control: {name}"
                controls.append(dict(mutation=name, rejected=True, assertion=broken.stderr.strip()))
    print(result.stdout, end="")
    print(f"PASS {len(checks)} unchanged mechanics/save/music boundaries against {BASE[:7]}")
    if controls:
        print(f"PASS {len(controls)} deliberately broken flow controls rejected")
    receipt = dict(status="passed", baseline=BASE, sourceSha256=digest(source), saveSourceSha256=digest(save),
                   testScriptSha256=digest(Path(__file__).read_bytes()), routeUiSourceSha256=digest(ui), sanitizers=["undefined", "bounds"],
                   compiler=compiler, hostOutput=result.stdout.splitlines(), preservation=checks, negativeControls=controls,
                   scope="Actual encounter update/init and actual SRAM codec on host with mocked rendering, room changes, geometry and audio. No ROM/hardware or perceived-fun qualification.")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
