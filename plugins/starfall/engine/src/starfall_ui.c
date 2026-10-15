#pragma bank 255
#include <gbdk/platform.h>
#include <stdint.h>
#include <string.h>
#include "palette.h"
#include "starfall_ui.h"
#include "starfall_rooms.h"
#define FONT_FIRST 0xC0u
#define FONT_COUNT 42u
#define FONT_ATTR 0x8Fu
#define SELECT_ATTR 0x8Eu
#define HEADER_ATTR 0x8Du
#define CHROME_FIRST 0xB0u
#define CHROME_COUNT 10u
#define UI_DARK CGB_COLOR(2,4,7)
#define UI_MID CGB_COLOR(3,11,14)
#define UI_CYAN CGB_COLOR(9,24,25)
#define UI_LIGHT CGB_COLOR(25,31,31)
static UBYTE map_row[20], attr_row[20], hud_glyphs[2][20];
UBYTE sf_hud_valid;
/* Artwork ends before B0; font C0-E9 and hazards EA-EE stay untouched.
 * Corner pixels use color3 so selected and ordinary frames share one atlas. */
static const UBYTE chrome_tiles[CHROME_COUNT][16] = {
    {0xc0,0xff,0x80,0xc0,0x00,0x80,0x00,0x80,0x00,0x80,0x00,0x80,0x00,0x80,0x00,0x80},
    {0x00,0xff,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00},
    {0x03,0xff,0x01,0x03,0x00,0x01,0x00,0x01,0x00,0x01,0x00,0x01,0x00,0x01,0x00,0x01},
    {0x00,0x80,0x00,0x80,0x00,0x80,0x00,0x80,0x00,0x80,0x00,0x80,0x00,0x80,0x00,0x80},
    {0x00,0x01,0x00,0x01,0x00,0x01,0x00,0x01,0x00,0x01,0x00,0x01,0x00,0x01,0x00,0x01},
    {0x00,0x80,0x00,0x80,0x00,0x80,0x00,0x80,0x00,0x80,0x00,0x80,0x80,0xc0,0xc0,0xff},
    {0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xff},
    {0x00,0x01,0x00,0x01,0x00,0x01,0x00,0x01,0x00,0x01,0x00,0x01,0x01,0x03,0x03,0xff},
    {0x40,0x00,0x60,0x00,0x70,0x00,0x78,0x00,0x70,0x00,0x60,0x00,0x40,0x00,0x00,0x00},
    {0x00,0x00,0x00,0x10,0x00,0x10,0x00,0x7e,0x00,0x18,0x00,0x10,0x00,0x10,0x00,0x00}
};
static const palette_entry_t normal_palette = {UI_DARK,UI_LIGHT,UI_MID,UI_DARK};
static const palette_entry_t selected_palette = {UI_CYAN,UI_DARK,UI_LIGHT,UI_DARK};
static const palette_entry_t header_palette = {UI_MID,UI_LIGHT,UI_CYAN,UI_DARK};
static const char * const module_names[5] = {"STANDARD","FAST CAPACITOR","WIDE COIL","OVERCHARGE","HULL PATCH"};
static const char * const module_descriptions[5] = {"BALANCED","FAST / CLOSE","FAR / SLOW","LONG STUN / SLOW","HEAL / STANDARD"};
static const char * const footer_actions[9] = {"LAUNCH","FLY ON","CONTINUE","PLAY","LAUNCH","CONFIRM","CONFIRM","FIT / FLY","RETRY"};
static const char * const footer_backs[9] = {"TITLE","TITLE","TITLE","","EXIT","BACK","EXIT","BACK","TITLE"};
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

static UBYTE text_length(const char *text, UBYTE maximum) {
    UBYTE length = 0;
    while (length != maximum && text[length]) ++length;
    return length;
}

static void clear_row(UBYTE attr) {
    memset(map_row,FONT_FIRST,sizeof(map_row));
    memset(attr_row,attr,sizeof(attr_row));
}

static void write_row(UBYTE y) {
    VBK_REG = 1;
    set_win_tiles(0,y,20,1,attr_row);
    VBK_REG = 0;
    set_win_tiles(0,y,20,1,map_row);
}

static void put_text(UBYTE x, UBYTE length, const char *text) {
    while (length--) map_row[x++] = font_tile(*text++);
}

static void select_palette(void) {
    /* Gameplay reuses palette6 for hazards. Reinstall it on every menu draw. */
    BkgPalette[6] = selected_palette;
    set_bkg_palette(6,1,(UWORD *)&BkgPalette[6]);
}

static void card_row(UBYTE selected) {
    clear_row(FONT_ATTR);
    memset(attr_row + 1,selected ? SELECT_ATTR : FONT_ATTR,18);
    map_row[1] = CHROME_FIRST + 3u;
    map_row[18] = CHROME_FIRST + 4u;
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
    set_win_data(CHROME_FIRST,CHROME_COUNT,(const UBYTE *)chrome_tiles);
    VBK_REG = 0;
    memset(attr_row, FONT_ATTR, sizeof(attr_row));
    BkgPalette[7] = normal_palette;
    set_bkg_palette(7,1,(UWORD *)&BkgPalette[7]);
    select_palette();
    sf_hud_valid = FALSE;
}

void starfall_ui_render_text_row(UBYTE y, const char *text) BANKED {
    if (y >= 18u) return;
    clear_row(FONT_ATTR);
    put_text(0,text_length(text,20),text);
    write_row(y);
}

void starfall_ui_render_centered_row(UBYTE y, const char *text) BANKED {
    UBYTE length;
    if (y >= 18u) return;
    length = text_length(text,20);
    clear_row(FONT_ATTR);
    put_text((20u - length) >> 1,length,text);
    write_row(y);
}

void starfall_ui_render_header(const char *text) BANKED {
    UBYTE y, length = text_length(text,20);
    BkgPalette[5] = header_palette;
    set_bkg_palette(5,1,(UWORD *)&BkgPalette[5]);
    select_palette();
    sf_hud_valid = FALSE;
    for (y = 0; y != 18u; ++y) {
        clear_row(y < 3u ? HEADER_ATTR : FONT_ATTR);
        if (y == 1u) {
            if (length <= 16u) map_row[1] = CHROME_FIRST + 9u;
            put_text((20u - length) >> 1,length,text);
        } else if (y == 2u) memset(map_row + 1,CHROME_FIRST + 6u,18);
        write_row(y);
    }
}

/* The fixed-bank bridge supplies WRAM text before changing to this bank. */
void starfall_ui_render_menu_option(UBYTE y, UBYTE selected, const char *text) BANKED {
    UBYTE length, x;
    if (y >= 18u) return;
    length = text_length(text,16);
    x = (20u - length) >> 1;
    if (x < 3u) x = 3u;
    clear_row(FONT_ATTR);
    if (selected) {
        select_palette();
        memset(attr_row + 1,SELECT_ATTR,18);
        map_row[1] = CHROME_FIRST + 8u;
    }
    put_text(x,length,text);
    write_row(y);
}

/* Cards occupy x1..18. Their label leaves x2 for the selection pointer.
 * Three rows make a24px choice; five rows leave room for a detail line. */
void starfall_ui_render_menu_card(UBYTE y, UBYTE height, UBYTE selected, const char *text) BANKED {
    UBYTE row, length, x;
    if (y > 15u) return;
    if (height < 3u) height = 3u;
    if (height > 18u - y) height = 18u - y;
    length = text_length(text,15);
    x = (20u - length) >> 1;
    if (x < 4u) x = 4u;
    if (x + length > 18u) x = 18u - length;
    if (selected) select_palette();
    for (row = 0; row != height; ++row) {
        card_row(selected);
        if (!row) {
            map_row[1] = CHROME_FIRST;
            memset(map_row + 2,CHROME_FIRST + 1u,16);
            map_row[18] = CHROME_FIRST + 2u;
        } else if (row == height - 1u) {
            map_row[1] = CHROME_FIRST + 5u;
            memset(map_row + 2,CHROME_FIRST + 6u,16);
            map_row[18] = CHROME_FIRST + 7u;
        } else if (row == 1u) {
            if (selected) map_row[2] = CHROME_FIRST + 8u;
            put_text(x,length,text);
        }
        write_row(y + row);
    }
}

void starfall_ui_render_card_detail(UBYTE y, UBYTE selected, const char *text) BANKED {
    UBYTE length;
    if (y >= 18u) return;
    length = text_length(text,16);
    card_row(selected);
    if (selected) select_palette();
    put_text((20u - length) >> 1,length,text);
    write_row(y);
}

void starfall_ui_render_footer(const char *action, const char *back) BANKED {
    clear_row(FONT_ATTR);
    select_palette();
    map_row[1] = font_tile('A'); attr_row[1] = SELECT_ATTR;
    put_text(3,text_length(action,9),action);
    if (*back) {
        map_row[13] = font_tile('B'); attr_row[13] = SELECT_ATTR;
        put_text(15,text_length(back,5),back);
    }
    write_row(17);
}

void starfall_ui_footer(UBYTE kind) BANKED {
    if (kind > SF_FOOTER_RETRY) return;
    starfall_ui_render_footer(footer_actions[kind],footer_backs[kind]);
}

void starfall_ui_module_option(UBYTE y, UBYTE selected, UBYTE module) BANKED {
    if (module > 4u) module = 0u;
    starfall_ui_render_menu_card(y,3,selected,module_names[module]);
}

void starfall_ui_module_name(UBYTE y, UBYTE module) BANKED {
    if (module > 4u) module = 0u;
    starfall_ui_render_centered_row(y,module_names[module]);
}

void starfall_ui_module_description(UBYTE y, UBYTE module) BANKED {
    if (module > 4u) module = 0u;
    starfall_ui_render_centered_row(y,module_descriptions[module]);
}

void starfall_ui_objective_hint(UBYTE y, UBYTE objective) BANKED {
    const char *text = "COLLECT 3 CELLS";
    if (objective == SF_OBJECTIVE_RELAY) text = "HOLD B: 3 RELAYS";
    else if (objective == SF_OBJECTIVE_REPAIR) text = "HOLD B: 3 REPAIRS";
    else if (objective == SF_OBJECTIVE_ESCORT) text = "ESCORT CREW TO DOCK";
    else if (objective == SF_OBJECTIVE_CORE) text = "PULSE THE OPEN CORE";
    starfall_ui_render_centered_row(y,text);
}

void starfall_ui_route_option(UBYTE branch, UBYTE selected, UBYTE objective) BANKED {
    UBYTE y = branch ? 11u : 6u;
    const char *label = branch ?
        (objective == SF_OBJECTIVE_ESCORT ? "CREW FIRST" : "TOOLS FIRST") :
        (objective == SF_OBJECTIVE_RELAY ? "RELAYS FIRST" : "REPAIR FIRST");
    starfall_ui_render_menu_card(y,5,selected,label);
    starfall_ui_render_card_detail(y + 3u,selected,branch ? "THEN FAST PULSE" : "THEN HAZARD OFF");
}

void starfall_ui_render_request(void) BANKED {
    switch (sf_ui_request.operation) {
        case SF_UI_TEXT: starfall_ui_render_text_row(sf_ui_request.y,sf_ui_request.text); break;
        case SF_UI_CENTERED: starfall_ui_render_centered_row(sf_ui_request.y,sf_ui_request.text); break;
        case SF_UI_HEADER: starfall_ui_render_header(sf_ui_request.text); break;
        case SF_UI_OPTION: starfall_ui_render_menu_option(sf_ui_request.y,sf_ui_request.selected,sf_ui_request.text); break;
        case SF_UI_CARD: starfall_ui_render_menu_card(sf_ui_request.y,sf_ui_request.height,sf_ui_request.selected,sf_ui_request.text); break;
        case SF_UI_HUD: starfall_ui_render_hud_row(sf_ui_request.y,sf_ui_request.text); break;
    }
}

void starfall_ui_exit_card_text(UBYTE arcade) BANKED {
    starfall_ui_render_header("EXIT THIS RUN");
    starfall_ui_render_centered_row(7,arcade ? "UNBANKED LOOT LOST" : "CHECKPOINT RETAINED");
    starfall_ui_render_menu_card(12,3,TRUE,"EXIT TO TITLE");
    starfall_ui_render_footer("CONFIRM","BACK");
}

void starfall_ui_new_story_card_text(void) BANKED {
    starfall_ui_render_header("NEW STORY");
    starfall_ui_render_centered_row(6,"REPLACES CHECKPOINT");
    starfall_ui_render_centered_row(9,"BEST SCORE RETAINED");
    starfall_ui_render_menu_card(12,3,TRUE,"START NEW STORY");
    starfall_ui_render_footer("BEGIN","BACK");
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
    UWORD minutes;
    if (seconds > 359999ul) seconds = 359999ul;
    /* Saturated total minutes fit in 16 bits; avoid the 32-bit modulo runtime. */
    minutes = (UWORD)(seconds / 60u);
    starfall_ui_two_digits(dest, minutes / 60u);
    dest[2] = ':';
    starfall_ui_two_digits(dest + 3, minutes % 60u);
    dest[5] = ':';
    starfall_ui_two_digits(dest + 6, (UWORD)(seconds - (uint32_t)minutes * 60u));
}
/* The two HUD rows share constant attributes. Preserve their actual glyphs
 * separately from menu text, and touch only the smallest changed map span. */
void starfall_ui_render_hud_row(UBYTE y, const char *text) BANKED {
    UBYTE i, first = 0, last = 19, count;
    if (y >= 2u) return;
    for (i = 0; i != 20; ++i) map_row[i] = *text ? font_tile(*text++) : FONT_FIRST;
    if (!sf_hud_valid) {
        memcpy(hud_glyphs[y],map_row,20);
        memset(attr_row,FONT_ATTR,sizeof(attr_row));
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
