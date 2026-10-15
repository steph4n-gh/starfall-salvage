#pragma bank 0
#include <gbdk/platform.h>
#include "starfall_ui.h"
/* Only this small fixed-bank bridge dereferences caller-bank literals.
 * Rendering then consumes WRAM, preserving genuine banked text pointers. */
sf_ui_request_t sf_ui_request;
static void draw_text(UBYTE operation,const char *text) {
    char *dest = sf_ui_request.text;
    UBYTE remaining = 20u;
    sf_ui_request.operation = operation;
    while (remaining-- && *text) *dest++ = *text++;
    *dest = 0;
    starfall_ui_render_request();
}
void starfall_ui_text_row(UBYTE y,const char *text) NONBANKED {
    sf_ui_request.y = y; draw_text(SF_UI_TEXT,text);
}
void starfall_ui_centered_row(UBYTE y,const char *text) NONBANKED {
    sf_ui_request.y = y; draw_text(SF_UI_CENTERED,text);
}
void starfall_ui_header(const char *text) NONBANKED {
    draw_text(SF_UI_HEADER,text);
}
void starfall_ui_menu_option(UBYTE y,UBYTE selected,const char *text) NONBANKED {
    sf_ui_request.y = y; sf_ui_request.selected = selected;
    draw_text(SF_UI_OPTION,text);
}
void starfall_ui_menu_card(UBYTE y,UBYTE height,UBYTE selected,const char *text) NONBANKED {
    sf_ui_request.y = y; sf_ui_request.height = height; sf_ui_request.selected = selected;
    draw_text(SF_UI_CARD,text);
}
void starfall_ui_hud_row(UBYTE y,const char *text) NONBANKED {
    sf_ui_request.y = y; draw_text(SF_UI_HUD,text);
}
