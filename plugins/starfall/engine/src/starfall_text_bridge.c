#pragma bank 0
#include <gbdk/platform.h>
#include "starfall_ui.h"
/* Only this small fixed-bank bridge dereferences caller-bank literals.
 * Rendering then consumes WRAM, preserving genuine banked text pointers. */
static char text_buffer[21];
static void copy_text(const char *text) {
    UBYTE i;
    for (i=0;i<20u;++i) {
        text_buffer[i]=*text;
        if (*text) ++text;
    }
    text_buffer[20]=0;
}
void starfall_ui_text_row(UBYTE y,const char *text) NONBANKED {
    copy_text(text); starfall_ui_render_text_row(y,text_buffer);
}
void starfall_ui_menu_option(UBYTE y,UBYTE selected,const char *text) NONBANKED {
    copy_text(text); starfall_ui_render_menu_option(y,selected,text_buffer);
}
void starfall_ui_hud_row(UBYTE y,const char *text) NONBANKED {
    copy_text(text); starfall_ui_render_hud_row(y,text_buffer);
}
