#ifndef STARFALL_UI_H
#define STARFALL_UI_H
#include <gbdk/platform.h>
#include <stdint.h>
extern UBYTE sf_hud_valid;
void starfall_ui_load_font(void) BANKED;
void starfall_ui_text_row(UBYTE y,const char *text) NONBANKED;
void starfall_ui_menu_option(UBYTE y,UBYTE selected,const char *text) NONBANKED;
void starfall_ui_two_digits(char *dest,UWORD n) BANKED;
void starfall_ui_five_digits(char *dest,UWORD n) BANKED;
void starfall_ui_elapsed_time(char *dest,uint32_t frames) BANKED;
void starfall_ui_hud_row(UBYTE y,const char *text) NONBANKED;
void starfall_ui_render_text_row(UBYTE y,const char *text) BANKED;
void starfall_ui_render_menu_option(UBYTE y,UBYTE selected,const char *text) BANKED;
void starfall_ui_module_option(UBYTE y,UBYTE selected,UBYTE module) BANKED;
void starfall_ui_exit_card_text(UBYTE arcade) BANKED;
void starfall_ui_new_story_card_text(void) BANKED;
void starfall_ui_render_hud_row(UBYTE y,const char *text) BANKED;
#endif
