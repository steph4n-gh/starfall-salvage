#ifndef STARFALL_SCREENS_H
#define STARFALL_SCREENS_H

#include <gbdk/platform.h>

enum {
    SF_SCREEN_TITLE,
    SF_SCREEN_LAUNCH,
    SF_SCREEN_PAUSE,
    SF_SCREEN_RESULT,
    SF_SCREEN_ENDING,
    SF_SCREEN_FAILURE,
    SF_SCREEN_UPGRADE
};

/* room is the campaign index; room&3 selects one of four mission bays.
 * zone is 0..5; higher zone values clamp to 5.
 * Hides the window, loads original artwork, and leaves the window hidden.
 * The caller overlays every text row, then reveals the completed card with
 * overlay_cut_scanline = 150 and ui_set_pos(0, 0).
 * Changes bank-1 tiles 00..BF, window maps, and background palettes 0..6.
 * The encounter must restore its room palettes before gameplay resumes.
 * Font C0..E9, hazard EA..EE, background maps, and object palettes are intact.
 */
void starfall_screen_show(UBYTE kind, UBYTE zone, UBYTE room) BANKED;

#endif
