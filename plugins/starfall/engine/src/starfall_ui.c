#pragma bank 255
#include <gbdk/platform.h>
#include <stdint.h>
#include <string.h>
#include "starfall_ui.h"
#define FONT_FIRST 0xC0u
#define FONT_COUNT 42u
#define FONT_ATTR 0x8Fu
static UBYTE map_row[20], attr_row[20], hud_glyphs[2][20];
UBYTE sf_hud_valid;
/* Five-by-seven glyphs: blank, A-Z, 0-9, colon, slash, dash, exclamation, period.
 * Font data is generated into the engine's reserved bank-1 text tile range.
 * This avoids per-frame VWF allocation and leaves all artwork tiles intact. */
static const UBYTE glyphs[FONT_COUNT][7] = {
    {0,0,0,0,0,0,0},
    {14,17,17,31,17,17,17}, {30,17,17,30,17,17,30},
    {14,17,16,16,16,17,14}, {30,17,17,17,17,17,30},
    {31,16,16,30,16,16,31}, {31,16,16,30,16,16,16},
    {14,17,16,23,17,17,15}, {17,17,17,31,17,17,17},
    {14,4,4,4,4,4,14}, {7,2,2,2,18,18,12},
    {17,18,20,24,20,18,17}, {16,16,16,16,16,16,31},
    {17,27,21,21,17,17,17}, {17,25,21,19,17,17,17},
    {14,17,17,17,17,17,14}, {30,17,17,30,16,16,16},
    {14,17,17,17,21,18,13}, {30,17,17,30,20,18,17},
    {15,16,16,14,1,1,30}, {31,4,4,4,4,4,4},
    {17,17,17,17,17,17,14}, {17,17,17,17,17,10,4},
    {17,17,17,21,21,21,10}, {17,17,10,4,10,17,17},
    {17,17,10,4,4,4,4}, {31,1,2,4,8,16,31},
    {14,17,19,21,25,17,14}, {4,12,4,4,4,4,14},
    {14,17,1,2,4,8,31}, {30,1,1,14,1,1,30},
    {2,6,10,18,31,2,2}, {31,16,16,30,1,1,30},
    {14,16,16,30,17,17,14}, {31,1,2,4,8,8,8},
    {14,17,17,14,17,17,14}, {14,17,17,15,1,1,14},
    {0,4,4,0,4,4,0}, {1,2,2,4,8,8,16},
    {0,0,0,31,0,0,0}, {4,4,4,4,4,0,4}, {0,0,0,0,0,0,4}
};

static UBYTE font_tile(UBYTE c) {
    if (c >= 'A' && c <= 'Z') return FONT_FIRST + 1u + c - 'A';
    if (c >= '0' && c <= '9') return FONT_FIRST + 27u + c - '0';
    if (c == ':') return FONT_FIRST + 37u;
    if (c == '/') return FONT_FIRST + 38u;
    if (c == '-') return FONT_FIRST + 39u;
    if (c == '!') return FONT_FIRST + 40u;
    if (c == '.') return FONT_FIRST + 41u;
    return FONT_FIRST;
}

void starfall_ui_load_font(void) BANKED {
    UBYTE i, y;
    UBYTE tile[16];
    VBK_REG = 1;
    for (i = 0; i != FONT_COUNT; ++i) {
        for (y = 0; y != 7; ++y) {
            tile[y << 1] = glyphs[i][y] << 2;
            tile[(y << 1) + 1] = 0;
        }
        tile[14] = tile[15] = 0;
        set_win_data(FONT_FIRST + i, 1, tile);
    }
    VBK_REG = 0;
    memset(attr_row, FONT_ATTR, sizeof(attr_row));
}

void starfall_ui_render_text_row(UBYTE y, const char *text) BANKED {
    UBYTE i;
    for (i = 0; i != 20; ++i) {
        if (*text) map_row[i] = font_tile(*text++);
        else map_row[i] = FONT_FIRST;
    }
    VBK_REG = 1;
    set_win_tiles(0, y, 20, 1, attr_row);
    VBK_REG = 0;
    set_win_tiles(0, y, 20, 1, map_row);
}

/* The fixed-bank bridge supplies WRAM text before changing to this bank. */
void starfall_ui_render_menu_option(UBYTE y, UBYTE selected, const char *text) BANKED {
    char label[21]; UBYTE i = 2;
    label[0] = selected ? '-' : ' '; label[1] = ' ';
    while (i != 20u && *text) label[i++] = *text++;
    label[i] = 0; starfall_ui_render_text_row(y,label);
}

void starfall_ui_module_option(UBYTE y, UBYTE selected, UBYTE module) BANKED {
    static const char * const names[5] = {"STANDARD","FAST CAPACITOR","WIDE COIL","OVERCHARGE","HULL PATCH"};
    static const char * const stats[5] = {"24PX 2S 1S","20PX 1.2S 0.5S","36PX 3S 1S","24PX 3S 1.5S","FULL HULL / STANDARD"};
    char heading[21]; UBYTE i; const char *name = names[module];
    heading[0] = selected ? '-' : ' '; heading[1] = heading[2] = ' ';
    for (i = 3; i != 20 && *name; ++i) heading[i] = *name++;
    heading[i] = 0; starfall_ui_render_text_row(y,heading); starfall_ui_render_text_row(y + 1,stats[module]);
}

void starfall_ui_exit_card_text(UBYTE arcade) BANKED {
    starfall_ui_render_text_row(5,"ABANDON THIS RUN?"); starfall_ui_render_text_row(8,"UNBANKED LOOT LOST");
    if (!arcade) starfall_ui_render_text_row(8,"CHECKPOINT RETAINED");
    starfall_ui_render_text_row(11,"A CONFIRM EXIT"); starfall_ui_render_text_row(14,"B CANCEL / GO BACK");
}

void starfall_ui_new_story_card_text(void) BANKED {
    starfall_ui_render_text_row(5,"START A NEW STORY?");
    starfall_ui_render_text_row(8,"REPLACES CHECKPOINT"); starfall_ui_render_text_row(10,"BEST SCORE RETAINED");
    starfall_ui_render_text_row(13,"A BEGIN NEW STORY"); starfall_ui_render_text_row(16,"B CANCEL / GO BACK");
}

void starfall_ui_two_digits(char *dest, UWORD n) BANKED {
    if (n > 99u) n = 99u;
    dest[0] = '0' + n / 10u; dest[1] = '0' + n % 10u;
}
void starfall_ui_five_digits(char *dest, UWORD n) BANKED {
    UBYTE i;
    for (i = 5; i; --i) { dest[i - 1] = '0' + n % 10u; n /= 10u; }
}
/* Long campaigns retain elapsed hours instead of saturating at999 seconds. */
void starfall_ui_elapsed_time(char *dest, uint32_t frames) BANKED {
    uint32_t seconds = frames / 60u;
    if (seconds > 359999ul) seconds = 359999ul;
    starfall_ui_two_digits(dest, (UWORD)(seconds / 3600u));
    dest[2] = ':';
    starfall_ui_two_digits(dest + 3, (UWORD)((seconds / 60u) % 60u));
    dest[5] = ':';
    starfall_ui_two_digits(dest + 6, (UWORD)(seconds % 60u));
}
/* The two HUD rows share constant attributes. Preserve their actual glyphs
 * separately from menu text, and touch only the smallest changed map span. */
void starfall_ui_render_hud_row(UBYTE y, const char *text) BANKED {
    UBYTE i, first = 0, last = 19, count;
    for (i = 0; i != 20; ++i) map_row[i] = *text ? font_tile(*text++) : FONT_FIRST;
    if (!sf_hud_valid) {
        memcpy(hud_glyphs[y],map_row,20);
        VBK_REG = 1; set_win_tiles(0,y,20,1,attr_row);
        VBK_REG = 0; set_win_tiles(0,y,20,1,map_row);
        return;
    }
    while (first != 20 && hud_glyphs[y][first] == map_row[first]) ++first;
    if (first == 20) return;
    while (last > first && hud_glyphs[y][last] == map_row[last]) --last;
    count = last - first + 1u;
    memcpy(hud_glyphs[y] + first,map_row + first,count);
    VBK_REG = 0; set_win_tiles(first,y,count,1,map_row + first);
}
