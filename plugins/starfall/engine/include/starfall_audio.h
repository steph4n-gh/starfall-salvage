/* SPDX-License-Identifier: MIT
 * Original Starfall Salvage score and effects; no sampled or third-party audio.
 * Call update exactly once per displayed game frame (about 59.7 Hz).
 */
#ifndef STARFALL_AUDIO_H
#define STARFALL_AUDIO_H

#include <gb/gb.h>

enum {
    STARFALL_SFX_PICKUP = 1u,
    STARFALL_SFX_PULSE = 2u,
    STARFALL_SFX_HIT = 3u,
    STARFALL_SFX_WARNING = 4u,
    STARFALL_SFX_WIN = 5u,
    STARFALL_SFX_RELAY = 6u,
    STARFALL_SFX_CORE_OPEN = 7u,
    STARFALL_SFX_CORE_HIT = 8u,
    STARFALL_SFX_LAUNCH = 9u
};

void starfall_audio_init(void) BANKED;
/* 0: bronze expedition; 1: cyan coolant; 2: violet engine; 3: Signal Archive;
 * 4: Outer Array; 5: Star Engine. Same-zone calls are harmless. A change
 * restarts the local arrangement without cutting an ongoing cue. */
void starfall_audio_zone(UBYTE zone) BANKED;
/* Pausing freezes and silences music; queued channel-2 cues still finish. */
void starfall_audio_update(UBYTE paused) BANKED;
void starfall_audio_sfx(UBYTE effect) BANKED;

#endif

