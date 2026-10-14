#pragma bank 255

#include <gbdk/platform.h>

#include "bankdata.h"
#include "palette.h"
#include "ui.h"
#include "starfall_screens.h"
#include "sf_screen_title.h"
#include "sf_screen_launch.h"
#include "sf_screen_pause.h"
#include "sf_screen_result.h"
#include "sf_screen_ending.h"
#include "sf_screen_failure.h"
#include "sf_screen_upgrade.h"

extern UBYTE overlay_cut_scanline;

#define DARK CGB_COLOR(2, 4, 7)
static const palette_entry_t screen_palettes[7] = {
    {DARK, CGB_COLOR(4, 8, 13), CGB_COLOR(10, 16, 23), CGB_COLOR(24, 29, 31)},
    {DARK, CGB_COLOR(11, 9, 8), CGB_COLOR(25, 18, 10), CGB_COLOR(31, 29, 22)},
    {DARK, CGB_COLOR(3, 11, 14), CGB_COLOR(9, 24, 25), CGB_COLOR(25, 31, 31)},
    {DARK, CGB_COLOR(10, 8, 17), CGB_COLOR(21, 15, 27), CGB_COLOR(31, 27, 31)},
    {DARK, CGB_COLOR(13, 7, 7), CGB_COLOR(27, 14, 8), CGB_COLOR(31, 27, 15)},
    {DARK, CGB_COLOR(7, 12, 17), CGB_COLOR(16, 23, 26), CGB_COLOR(28, 31, 31)},
    {DARK, CGB_COLOR(12, 5, 7), CGB_COLOR(29, 9, 9), CGB_COLOR(31, 25, 10)}
};
static const palette_entry_t zone_hull[6] = {
    {DARK, CGB_COLOR(11, 9, 8), CGB_COLOR(25, 18, 10), CGB_COLOR(31, 29, 22)},
    {DARK, CGB_COLOR(4, 11, 16), CGB_COLOR(9, 23, 27), CGB_COLOR(26, 31, 31)},
    {DARK, CGB_COLOR(10, 7, 18), CGB_COLOR(22, 14, 29), CGB_COLOR(31, 28, 31)},
    {DARK, CGB_COLOR(4, 12, 10), CGB_COLOR(11, 26, 18), CGB_COLOR(27, 31, 24)},
    {DARK, CGB_COLOR(5, 9, 19), CGB_COLOR(12, 21, 31), CGB_COLOR(30, 31, 31)},
    {DARK, CGB_COLOR(14, 5, 7), CGB_COLOR(31, 12, 9), CGB_COLOR(31, 29, 17)}
};

/* GBVM's NONBANKED helpers restore the caller's ROM bank before returning.
 * Never switch ROM banks from this banked function's own instruction stream.
 * Window and background data share the LCDC-selected tile data address mode.
 */
static void load_art(UBYTE bank, const UBYTE *tiles, UBYTE count,
                     const UBYTE *map, const UBYTE *attrs) {
    VBK_REG = 1;
    SetBankedBkgData(0, count, tiles, bank);
    SetBankedWinTiles(0, 0, 20, 18, attrs, bank);
    VBK_REG = 0;
    SetBankedWinTiles(0, 0, 20, 18, map, bank);
}

#define LOAD_SCREEN(NAME, COUNT) load_art(BANK(sf_screen_##NAME), \
    sf_screen_##NAME##_tiles, COUNT, \
    sf_screen_##NAME##_map, sf_screen_##NAME##_attrs)

void starfall_screen_show(UBYTE kind, UBYTE zone, UBYTE room) BANKED {
    UBYTE i, x, y, active, line, idle;
    /* Atlas and map writes can span multiple PPU frames. Keep the window
     * off-screen until the caller has added every text row to the new card. */
    overlay_cut_scanline = 0u;
    ui_set_pos(0, 144u);
    WY_REG = 144u;
    HIDE_WIN;
    if (zone > 5u) zone = 5u;
    for (i = 0; i != 7; ++i) BkgPalette[i] = screen_palettes[i];
    BkgPalette[1] = zone_hull[zone];
    set_bkg_palette(0, 7, (UWORD *)BkgPalette);

    switch (kind) {
        case SF_SCREEN_LAUNCH: LOAD_SCREEN(launch, SF_SCREEN_LAUNCH_COUNT); break;
        case SF_SCREEN_PAUSE: LOAD_SCREEN(pause, SF_SCREEN_PAUSE_COUNT); break;
        case SF_SCREEN_RESULT: LOAD_SCREEN(result, SF_SCREEN_RESULT_COUNT); break;
        case SF_SCREEN_ENDING: LOAD_SCREEN(ending, SF_SCREEN_ENDING_COUNT); break;
        case SF_SCREEN_FAILURE: LOAD_SCREEN(failure, SF_SCREEN_FAILURE_COUNT); break;
        case SF_SCREEN_UPGRADE: LOAD_SCREEN(upgrade, SF_SCREEN_UPGRADE_COUNT); break;
        default: LOAD_SCREEN(title, SF_SCREEN_TITLE_COUNT); break;
    }
    if (kind == SF_SCREEN_LAUNCH) {
        /* Four bays use the existing corner nodes, clockwise. Tile08 is
         * the atlas's plain track: remove eight intermediate dots without
         * adding tiles or breaking the panel's right-hand border. */
        line = 0x08u;
        VBK_REG = 0;
        for (y = 1u; y <= 3u; y += 2u) {
            for (x = 5u; x <= 11u; x += 2u) set_win_tiles(x,y,1,1,&line);
        }
        idle = 0x09u; /* bank1, the selected zone's hull palette */
        VBK_REG = 1;
        for (i = 0u; i != 4u; ++i) {
            x = (i == 1u || i == 2u) ? 13u : 3u;
            y = i < 2u ? 1u : 3u;
            set_win_tiles(x,y,1,1,&idle);
        }
        i = room & 3u;
        x = (i == 1u || i == 2u) ? 13u : 3u;
        y = i < 2u ? 1u : 3u;
        active = zone == 5u ? 0x0Au : 0x0Eu; /* cyan contrasts with ember hull */
        set_win_tiles(x,y,1,1,&active);
        VBK_REG = 0;
    }
}
