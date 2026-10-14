#ifndef STARFALL_SAVE_H
#define STARFALL_SAVE_H

#include <gbdk/platform.h>
#include <stdint.h>

#define SF_SAVE_STAGE_LAUNCH 0u
#define SF_SAVE_STAGE_RESULT 1u
#define SF_SAVE_STAGE_UPGRADE 2u
#define SF_SAVE_STAGE_ENDING 3u
#define SF_SAVE_STAGE_BRANCH 4u
#define SF_SAVE_STAGE_MISSION_BOARD 5u
#define SF_SAVE_STAGE_MISSION_COMPLETE 6u

#define SF_SAVE_UNLOCK_FAST 0x01u
#define SF_SAVE_UNLOCK_WIDE 0x02u
#define SF_SAVE_UNLOCK_OVERCHARGE 0x04u

/* Logical checkpoint data, never copied as a compiler-dependent struct blob.
 * room is a full byte; the encounter runtime validates its current manifest.
 * Successful frame time and rank damage survive a resumed Story campaign.
 * optional_flags keeps global achievements across all eighteen missions;
 * room_clear_mask, branch_order and hull_value describe the active campaign.
 * Version 1 records read with new flags zero and checkpoint hull three. */
typedef struct {
    UBYTE has_checkpoint, room, checkpoint_stage, rig, unlock_flags;
    UBYTE campaign_complete, damage_total;
    uint32_t successful_frames, mission_flags, optional_flags;
    UWORD best_banked, credits;
    UBYTE room_clear_mask, branch_order, hull_value;
} sf_save_t;

/* A missing/corrupt save returns FALSE and clears dest to a clean no-save.
 * A valid statistics-only record may have has_checkpoint == FALSE. */
UBYTE starfall_save_read(sf_save_t *dest) BANKED;

/* Event-only checkpoint write. TRUE requires exact SRAM readback. The prior
 * valid record remains available when the replacement is interrupted. */
UBYTE starfall_save_write(const sf_save_t *src) BANKED;

/* Clear the current campaign through a newer logical record; retain the best
 * banked score, rig unlocks, global optional achievements and completion flag. */
UBYTE starfall_save_reset_checkpoint(void) BANKED;

#endif
