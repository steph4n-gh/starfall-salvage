#pragma bank 255

#include <gbdk/platform.h>
#include <string.h>
#include <stdint.h>

#include "system.h"
#include "load_save.h"
#include "starfall_save.h"

/* GB Studio's built-in save slots use banks 0..2. This game's 32 KiB MBC5
 * battery-backed RAM provides bank 3 for these two small records. */
#if SRAM_BANKS_TO_SAVE > 3
#error Starfall checkpoint bank overlaps the configured GB Studio save banks
#endif
#ifdef BATTERYLESS
#error Starfall checkpoints require battery-backed SRAM, not ROM flash saves
#endif

#define SF_SAVE_BANK 3u
#define SF_RECORD_SIZE 40u
#define SF_RECORD_B_OFFSET 64u
#define SF_RECORD_COMMIT 0xA5u
#define SF_RECORD_NONE 2u

/* Version 2 wire layout, independent of C struct padding:
 *  0..3  SFSV magic       4 version=2       5 commit=A5
 *  6     length=40       7 checkpoint stage (0..6)
 *  8..11 generation     12 has_checkpoint 13 room 14 rig 15 unlocks
 * 16     completed      17 rank damage
 * 18..21 successful frames               22..23 best banked
 * 24..25 credits                         26..29 mission flags
 * 30..33 global optional achievements    34 cleared-room mask (0..15)
 * 35     branch order (0..2)              36 hull (0..5), 37 reserved=0
 * 38..39 CRC16-CCITT-FALSE
 * Version 1 accepts stages 0..3 and requires bytes 30..37 to be zero; those
 * fields read as zero except hull defaults to three for an active checkpoint.
 * Multi-byte values and the checksum are little endian. CRC covers 0..37,
 * including the final commit byte. The target commit is invalidated first;
 * all other bytes are written before A5 commits the new record. */

#ifdef STARFALL_SAVE_HOST_TEST
extern volatile UBYTE sf_save_test_sram[SF_RECORD_B_OFFSET + SF_RECORD_SIZE];
extern void sf_save_test_store(UBYTE offset, UBYTE value);
#define SF_SRAM sf_save_test_sram
#else
#define SF_SRAM ((volatile UBYTE *)0xA000u)
#endif

static UWORD read_u16(const UBYTE *p) {
    return (UWORD)p[0] | ((UWORD)p[1] << 8);
}

static uint32_t read_u32(const UBYTE *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static void write_u16(UBYTE *p, UWORD value) {
    p[0] = (UBYTE)value;
    p[1] = (UBYTE)(value >> 8);
}

static void write_u32(UBYTE *p, uint32_t value) {
    p[0] = (UBYTE)value;
    p[1] = (UBYTE)(value >> 8);
    p[2] = (UBYTE)(value >> 16);
    p[3] = (UBYTE)(value >> 24);
}

static UWORD record_crc(const UBYTE *bytes) {
    UBYTE i, bit;
    UWORD crc = 0xFFFFu;
    for (i = 0; i != 38u; ++i) {
        crc ^= (UWORD)bytes[i] << 8;
        for (bit = 0; bit != 8u; ++bit) {
            if (crc & 0x8000u) crc = (UWORD)((crc << 1) ^ 0x1021u);
            else crc = (UWORD)(crc << 1);
        }
    }
    return crc;
}

static UBYTE state_valid(const sf_save_t *state) {
    return state && state->has_checkpoint <= 1u &&
           state->checkpoint_stage <= SF_SAVE_STAGE_MISSION_COMPLETE &&
           state->rig <= 3u && !(state->unlock_flags & 0xF8u) &&
           state->campaign_complete <= 1u && state->room_clear_mask <= 15u &&
           state->branch_order <= 2u && state->hull_value <= 5u;
}

static UBYTE decode_record(const UBYTE *bytes, sf_save_t *dest,
                           uint32_t *generation) {
    UBYTE i;
    if (bytes[0] != 'S' || bytes[1] != 'F' || bytes[2] != 'S' || bytes[3] != 'V' ||
        (bytes[4] != 1u && bytes[4] != 2u) ||
        bytes[5] != SF_RECORD_COMMIT || bytes[6] != SF_RECORD_SIZE)
        return FALSE;
    if (bytes[4] == 1u) {
        if (bytes[7] > SF_SAVE_STAGE_ENDING) return FALSE;
        for (i = 30u; i != 38u; ++i) if (bytes[i]) return FALSE;
    } else if (bytes[37]) return FALSE;
    if (read_u16(bytes + 38) != record_crc(bytes)) return FALSE;

    memset(dest, 0, sizeof(sf_save_t));
    dest->checkpoint_stage = bytes[7];
    dest->has_checkpoint = bytes[12];
    dest->room = bytes[13];
    dest->rig = bytes[14];
    dest->unlock_flags = bytes[15];
    dest->campaign_complete = bytes[16];
    dest->damage_total = bytes[17];
    dest->successful_frames = read_u32(bytes + 18);
    dest->best_banked = read_u16(bytes + 22);
    dest->credits = read_u16(bytes + 24);
    dest->mission_flags = read_u32(bytes + 26);
    if (bytes[4] == 2u) {
        dest->optional_flags = read_u32(bytes + 30);
        dest->room_clear_mask = bytes[34];
        dest->branch_order = bytes[35];
        dest->hull_value = bytes[36];
    } else dest->hull_value = dest->has_checkpoint ? 3u : 0u;
    if (!state_valid(dest)) return FALSE;
    *generation = read_u32(bytes + 8);
    return TRUE;
}

static void encode_record(UBYTE *bytes, const sf_save_t *state,
                          uint32_t generation) {
    memset(bytes, 0, SF_RECORD_SIZE);
    bytes[0] = 'S'; bytes[1] = 'F'; bytes[2] = 'S'; bytes[3] = 'V';
    bytes[4] = 2u; bytes[5] = SF_RECORD_COMMIT; bytes[6] = SF_RECORD_SIZE;
    bytes[7] = state->checkpoint_stage;
    write_u32(bytes + 8, generation);
    bytes[12] = state->has_checkpoint;
    bytes[13] = state->room;
    bytes[14] = state->rig;
    bytes[15] = state->unlock_flags;
    bytes[16] = state->campaign_complete;
    bytes[17] = state->damage_total;
    write_u32(bytes + 18, state->successful_frames);
    write_u16(bytes + 22, state->best_banked);
    write_u16(bytes + 24, state->credits);
    write_u32(bytes + 26, state->mission_flags);
    write_u32(bytes + 30, state->optional_flags);
    bytes[34] = state->room_clear_mask;
    bytes[35] = state->branch_order;
    bytes[36] = state->hull_value;
    write_u16(bytes + 38, record_crc(bytes));
}

static void read_record(UBYTE record, UBYTE *bytes) {
    UBYTE i, prior_bank = _current_ram_bank;
    UBYTE offset = record ? SF_RECORD_B_OFFSET : 0u;
    ENABLE_RAM_MBC5;
    /* MBC5+rumble uses bank bits 0..2; preserve rumble bit 3 and all flags. */
    SWITCH_RAM_BANK(SF_SAVE_BANK, 0x07u);
    for (i = 0; i != SF_RECORD_SIZE; ++i) bytes[i] = SF_SRAM[offset + i];
    SWITCH_RAM_BANK(prior_bank, RAM_BANKS_AND_FLAGS);
}

static void store_byte(UBYTE offset, UBYTE value) {
#ifdef STARFALL_SAVE_HOST_TEST
    sf_save_test_store(offset, value);
#else
    SF_SRAM[offset] = value;
#endif
}

static UBYTE newest_record(const UBYTE *a, const UBYTE *b,
                           uint32_t *generation) {
    sf_save_t scratch;
    uint32_t ga, gb, delta;
    UBYTE valid_a = decode_record(a, &scratch, &ga);
    UBYTE valid_b = decode_record(b, &scratch, &gb);
    if (!valid_a && !valid_b) return SF_RECORD_NONE;
    if (!valid_a) { *generation = gb; return 1u; }
    if (!valid_b) { *generation = ga; return 0u; }
    /* Serial-number arithmetic handles FFFFFFFF -> 0. Equal generations
     * and the unreachable half-range ambiguity deterministically prefer A. */
    delta = gb - ga;
    if (delta && delta < 0x80000000UL) { *generation = gb; return 1u; }
    *generation = ga;
    return 0u;
}

UBYTE starfall_save_read(sf_save_t *dest) BANKED {
    UBYTE a[SF_RECORD_SIZE], b[SF_RECORD_SIZE], selected;
    uint32_t generation;
    if (!dest) return FALSE;
    memset(dest, 0, sizeof(sf_save_t));
    read_record(0, a); read_record(1, b);
    selected = newest_record(a, b, &generation);
    if (selected == SF_RECORD_NONE) return FALSE;
    return decode_record(selected ? b : a, dest, &generation);
}

UBYTE starfall_save_write(const sf_save_t *src) BANKED {
    UBYTE a[SF_RECORD_SIZE], b[SF_RECORD_SIZE], target, i, offset, prior_bank;
    uint32_t generation = 0;
    if (!state_valid(src)) return FALSE;
    read_record(0, a); read_record(1, b);
    target = newest_record(a, b, &generation);
    if (target == SF_RECORD_NONE) target = 0;
    else { target ^= 1u; ++generation; }
    encode_record(a, src, generation);
    offset = target ? SF_RECORD_B_OFFSET : 0u;
    prior_bank = _current_ram_bank;
    ENABLE_RAM_MBC5;
    SWITCH_RAM_BANK(SF_SAVE_BANK, 0x07u);
    store_byte(offset + 5u, 0); /* invalidate before overwriting the older copy */
    for (i = 0; i != SF_RECORD_SIZE; ++i)
        if (i != 5u) store_byte(offset + i, a[i]);
    store_byte(offset + 5u, SF_RECORD_COMMIT); /* commit last */
    for (i = 0; i != SF_RECORD_SIZE; ++i) b[i] = SF_SRAM[offset + i];
    SWITCH_RAM_BANK(prior_bank, RAM_BANKS_AND_FLAGS);
    return memcmp(a, b, SF_RECORD_SIZE) == 0;
}

UBYTE starfall_save_reset_checkpoint(void) BANKED {
    sf_save_t state;
    /* read() supplies zero defaults if neither record is valid. */
    starfall_save_read(&state);
    state.has_checkpoint = FALSE;
    state.room = 0;
    state.checkpoint_stage = SF_SAVE_STAGE_LAUNCH;
    state.rig = 0;
    state.damage_total = 0;
    state.successful_frames = 0;
    state.credits = 0;
    state.mission_flags = 0;
    state.room_clear_mask = 0;
    state.branch_order = 0;
    state.hull_value = 0;
    return starfall_save_write(&state);
}
