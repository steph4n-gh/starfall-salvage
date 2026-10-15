#ifndef STARFALL_UI_H
#define STARFALL_UI_H
#include <gbdk/platform.h>
#include <stdint.h>
extern UBYTE sf_hud_valid;
/* One WRAM request lets fixed-bank callers share the banked rendering handoff. */
enum { SF_UI_TEXT, SF_UI_CENTERED, SF_UI_HEADER, SF_UI_OPTION, SF_UI_CARD, SF_UI_HUD };
enum { SF_FOOTER_LAUNCH, SF_FOOTER_FLY, SF_FOOTER_CONTINUE, SF_FOOTER_PLAY,
       SF_FOOTER_LAUNCH_EXIT, SF_FOOTER_CONFIRM, SF_FOOTER_CONFIRM_EXIT, SF_FOOTER_FIT, SF_FOOTER_RETRY };
typedef struct {
    UBYTE operation, y, height, selected;
    char text[21];
} sf_ui_request_t;
extern sf_ui_request_t sf_ui_request;
void starfall_ui_render_request(void) BANKED;
void starfall_ui_load_font(void) BANKED;
void starfall_ui_text_row(UBYTE y,const char *text) NONBANKED;
void starfall_ui_centered_row(UBYTE y,const char *text) NONBANKED;
void starfall_ui_header(const char *text) NONBANKED;
void starfall_ui_menu_option(UBYTE y,UBYTE selected,const char *text) NONBANKED;
void starfall_ui_menu_card(UBYTE y,UBYTE height,UBYTE selected,const char *text) NONBANKED;
void starfall_ui_footer(UBYTE kind) BANKED;
void starfall_ui_two_digits(char *dest,UWORD n) BANKED;
void starfall_ui_five_digits(char *dest,UWORD n) BANKED;
void starfall_ui_elapsed_time(char *dest,uint32_t frames) BANKED;
void starfall_ui_hud_row(UBYTE y,const char *text) NONBANKED;
void starfall_ui_render_text_row(UBYTE y,const char *text) BANKED;
void starfall_ui_render_centered_row(UBYTE y,const char *text) BANKED;
void starfall_ui_render_header(const char *text) BANKED;
void starfall_ui_render_menu_option(UBYTE y,UBYTE selected,const char *text) BANKED;
void starfall_ui_render_menu_card(UBYTE y,UBYTE height,UBYTE selected,const char *text) BANKED;
void starfall_ui_render_card_detail(UBYTE y,UBYTE selected,const char *text) BANKED;
void starfall_ui_render_footer(const char *action,const char *back) BANKED;
void starfall_ui_module_option(UBYTE y,UBYTE selected,UBYTE module) BANKED;
void starfall_ui_module_name(UBYTE y,UBYTE module) BANKED;
void starfall_ui_module_description(UBYTE y,UBYTE module) BANKED;
void starfall_ui_objective_hint(UBYTE y,UBYTE objective) BANKED;
void starfall_ui_route_option(UBYTE branch,UBYTE selected,UBYTE objective) BANKED;
void starfall_ui_exit_card_text(UBYTE arcade) BANKED;
void starfall_ui_new_story_card_text(void) BANKED;
void starfall_ui_render_hud_row(UBYTE y,const char *text) BANKED;
#endif
