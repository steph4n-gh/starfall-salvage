/* SPDX-License-Identifier: MIT
 * "Salvage Orbit": original 32-bar A-minor chiptune for Starfall Salvage.
 * Bronze uses eight frames per sixteenth, about 112 BPM. Coolant uses nine,
 * about 100 BPM; engine uses seven, about 128 BPM. Each zone has four eight-bar
 * arrangements, repeating after 4096/4608/3584 unpaused frames respectively.
 * Main theme -> answering theme -> lower, quieter main -> fuller answer.
 * Signal Archive, Outer Array and Star Engine add distinct original four-bar
 * lead/answer scores, running 16 bars per cycle at ~90/112/128 BPM. Their loops
 * occupy 2560/2048/1792 unpaused frames; all original zones/cues retain timing.
 *
 * Channel 1: articulated square lead. Channel 3: triangle-wave bass.
 * Channel 2: priority-controlled gameplay cues. Channel 4: quiet percussion,
 * temporarily reserved by a pulse/hit cue. The idle GB Studio music ISR is
 * stopped on initialization; this score owns the APU only in this encounter.
 * All pitches and composition are precomputed: no floats, division, sampling,
 * interrupts or per-frame bank switches beyond the caller's BANKED call.
 */
#pragma bank 255

#include "starfall_audio.h"
#include "music_manager.h"

#define HOLD 255u
#define REST 254u
#define C3 0u
#define D3 2u
#define E3 4u
#define F3 5u
#define G3 7u
#define A3 9u
#define B3 11u
#define C4 12u
#define D4 14u
#define E4 16u
#define F4 17u
#define G4 19u
#define A4 21u
#define B4 23u
#define C5 24u
#define D5 26u
#define E5 28u
#define F5 29u
#define G5 31u
#define A5 33u
#define B5 35u
#define C6 36u
#define D6 38u
#define E6 40u
#define G6 43u
#define A6 45u

/* Square pitches C3..B6. The same wave-channel register plays one octave lower. */
static const UWORD pitch[48] = {
    1046u, 1102u, 1155u, 1205u, 1253u, 1297u, 1339u, 1379u, 1417u, 1452u, 1486u, 1517u,
    1547u, 1575u, 1602u, 1627u, 1650u, 1673u, 1694u, 1714u, 1732u, 1750u, 1767u, 1783u,
    1798u, 1812u, 1825u, 1837u, 1849u, 1860u, 1871u, 1881u, 1890u, 1899u, 1907u, 1915u,
    1923u, 1930u, 1936u, 1943u, 1949u, 1954u, 1959u, 1964u, 1969u, 1974u, 1978u, 1982u
};

static const UBYTE lead[128] = {
    E5,HOLD,A5,HOLD,C6,B5,A5,HOLD,E5,HOLD,G5,HOLD,A5,HOLD,HOLD,REST,
    A5,HOLD,C6,HOLD,D6,C6,A5,HOLD,F5,HOLD,G5,HOLD,A5,HOLD,HOLD,REST,
    G5,HOLD,E5,HOLD,G5,HOLD,C6,HOLD,B5,A5,G5,HOLD,E5,HOLD,HOLD,REST,
    D5,HOLD,G5,HOLD,B5,HOLD,A5,HOLD,G5,HOLD,D5,HOLD,E5,F5,G5,HOLD,
    E5,A5,C6,HOLD,B5,A5,E5,HOLD,C6,HOLD,E6,HOLD,D6,C6,B5,A5,
    A5,HOLD,F5,HOLD,A5,C6,D6,HOLD,C6,A5,G5,HOLD,F5,HOLD,HOLD,REST,
    G5,HOLD,C6,HOLD,E6,D6,C6,HOLD,G5,A5,B5,HOLD,C6,HOLD,HOLD,REST,
    B5,HOLD,D6,HOLD,G6,HOLD,D6,HOLD,B5,A5,G5,HOLD,E5,HOLD,B4,HOLD
};

/* A second, coherent answering melody over the same Am-F-C-G harmony. */
static const UBYTE answer[128] = {
    E5,HOLD,C6,B5,A5,HOLD,E5,HOLD,G5,A5,C6,HOLD,B5,A5,E5,HOLD,
    F5,HOLD,A5,HOLD,C6,HOLD,A5,HOLD,G5,A5,C6,D6,C6,HOLD,A5,REST,
    E5,G5,C6,HOLD,E6,HOLD,D6,C6,G5,HOLD,E5,HOLD,D5,E5,G5,HOLD,
    G5,HOLD,B5,HOLD,D6,HOLD,B5,A5,G5,HOLD,D5,HOLD,G5,A5,B5,HOLD,
    A5,HOLD,E6,HOLD,D6,C6,B5,A5,C6,HOLD,A5,HOLD,G5,E5,A5,HOLD,
    C6,HOLD,A5,HOLD,F5,HOLD,A5,C6,D6,C6,A5,HOLD,F5,G5,A5,HOLD,
    E6,HOLD,D6,C6,G5,HOLD,C6,HOLD,B5,A5,G5,E5,G5,HOLD,C6,HOLD,
    D6,HOLD,B5,HOLD,G5,D5,G5,HOLD,A5,B5,D6,HOLD,B5,G5,E5,HOLD
};

static const UBYTE lead_duties[4] = {0x80u,0x40u,0x80u,0x40u};
static const UBYTE lead_envelopes[4] = {0x52u,0x53u,0x43u,0x63u};

static const UBYTE bass[32] = {
    A3,E4,A3,E4, F3,C4,F3,C4, C3,G3,E3,G3, G3,D4,G3,B3,
    A3,E4,C4,E4, F3,C4,A3,C4, C3,G3,E3,G3, G3,D4,B3,E3
};

static const UBYTE triangle[16] = {
    0x01u,0x23u,0x45u,0x67u,0x89u,0xabu,0xcdu,0xefu,
    0xfeu,0xdcu,0xbau,0x98u,0x76u,0x54u,0x32u,0x10u
};

/* Each native 32-sample waveform occupies 16 bytes. Wave writes are restricted
 * to a zone transition with channel 3's DAC disabled, never a per-frame loop. */
static const UBYTE coolant_wave[16] = {
    0x89u,0xbcu,0xdeu,0xffu,0xffu,0xfeu,0xdcu,0xb9u,
    0x86u,0x43u,0x21u,0x00u,0x00u,0x01u,0x23u,0x46u
};
static const UBYTE engine_wave[16] = {
    0x03u,0x69u,0xcfu,0xfeu,0xedu,0xdcu,0xcbu,0xbau,
    0xa9u,0x98u,0x87u,0x76u,0x65u,0x54u,0x43u,0x21u
};
/* Three original four-bar scores for the remaining zones. Each has an
 * answering phrase and its own harmony; the driver retains four arrangements
 * (main, answer, lower main, fuller answer), without changing legacy scores. */
static const UBYTE archive_lead[64] = {
    E5,HOLD,B5,HOLD,D6,B5,G5,HOLD,E5,HOLD,G5,HOLD,B5,HOLD,HOLD,REST,
    C6,HOLD,G5,HOLD,E5,HOLD,G5,HOLD,B5,HOLD,A5,G5,E5,HOLD,HOLD,REST,
    A5,HOLD,E5,HOLD,G5,A5,B5,HOLD,A5,HOLD,G5,HOLD,E5,HOLD,REST,REST,
    B5,HOLD,D6,HOLD,E6,D6,B5,HOLD,A5,HOLD,G5,HOLD,E5,HOLD,B5,REST
};
static const UBYTE archive_answer[64] = {
    E5,HOLD,G5,HOLD,B5,D6,E6,HOLD,D6,HOLD,B5,G5,E5,HOLD,REST,REST,
    C6,HOLD,B5,G5,E5,HOLD,G5,HOLD,A5,HOLD,G5,HOLD,E5,HOLD,HOLD,REST,
    A5,HOLD,C6,HOLD,B5,A5,G5,HOLD,E5,HOLD,G5,A5,B5,HOLD,REST,REST,
    D6,HOLD,B5,HOLD,A5,G5,E5,HOLD,G5,HOLD,B5,HOLD,E6,HOLD,HOLD,REST
};
static const UBYTE archive_bass[16] = {
    E3,B3,E4,B3, C3,G3,E3,G3, A3,E4,C4,E4, B3,D4,B3,A3
};
static const UBYTE array_lead[64] = {
    C6,HOLD,E6,G6,E6,HOLD,D6,C6,G5,HOLD,A5,G5,E5,HOLD,G5,REST,
    A5,HOLD,C6,E6,D6,C6,A5,HOLD,E5,HOLD,G5,A5,C6,HOLD,HOLD,REST,
    F5,HOLD,A5,C6,A5,HOLD,G5,F5,C6,HOLD,D6,C6,A5,HOLD,F5,REST,
    G5,B5,D6,HOLD,G6,HOLD,D6,B5,A5,G5,E5,D5,G5,HOLD,HOLD,REST
};
static const UBYTE array_answer[64] = {
    C6,E6,G6,HOLD,E6,D6,C6,HOLD,G5,A5,C6,HOLD,D6,E6,G6,REST,
    A5,C6,E6,HOLD,C6,A5,E5,HOLD,G5,A5,C6,D6,E6,HOLD,HOLD,REST,
    A5,C6,F5,HOLD,A5,G5,F5,HOLD,C6,D6,C6,A5,G5,F5,A5,REST,
    B5,D6,G6,HOLD,D6,B5,G5,HOLD,A5,B5,D6,HOLD,E6,D6,C6,HOLD
};
static const UBYTE array_bass[16] = {
    C3,G3,E3,G3, A3,E4,C4,E4, F3,C4,A3,C4, G3,D4,B3,D4
};
static const UBYTE star_engine_lead[64] = {
    D5,A5,D6,HOLD,C6,A5,F5,A5,D6,HOLD,E6,D6,A5,HOLD,C6,REST,
    F5,C6,A5,HOLD,C6,D6,E6,HOLD,D6,C6,A5,F5,A5,HOLD,HOLD,REST,
    C6,G5,E5,HOLD,G5,C6,D6,HOLD,E6,D6,C6,G5,E5,HOLD,G5,REST,
    A5,E5,A5,HOLD,C6,A5,G5,E5,A5,HOLD,C6,D6,E6,D6,C6,A5
};
static const UBYTE star_engine_answer[64] = {
    D6,HOLD,A5,F5,A5,C6,D6,HOLD,E6,D6,C6,A5,F5,A5,D6,REST,
    C6,HOLD,A5,F5,A5,C6,D6,HOLD,C6,A5,F5,C5,F5,A5,C6,REST,
    E6,HOLD,D6,C6,G5,E5,G5,HOLD,C6,D6,E6,HOLD,D6,C6,G5,REST,
    A5,C6,E6,HOLD,D6,C6,A5,HOLD,G5,E5,A5,C6,D6,HOLD,A5,HOLD
};
static const UBYTE star_engine_bass[16] = {
    D3,A3,F3,A3, F3,C4,A3,C4, C3,G3,E3,G3, A3,E4,C4,E4
};
static const UBYTE archive_wave[16] = {
    0x08u,0xcdu,0xfeu,0xcbu,0x98u,0x67u,0x45u,0x67u,
    0x89u,0xabu,0xcdu,0xefu,0xdcu,0x98u,0x54u,0x10u
};
static const UBYTE array_wave[16] = {
    0x78u,0x9au,0xbcu,0xdeu,0xefu,0xfeu,0xdcu,0xbau,
    0x98u,0x76u,0x54u,0x32u,0x21u,0x12u,0x34u,0x56u
};
static const UBYTE star_engine_wave[16] = {
    0x0fu,0xfeu,0xdcu,0xbau,0x98u,0x76u,0x54u,0x32u,
    0x10u,0x01u,0x23u,0x45u,0x67u,0x89u,0xabu,0xcdu
};

static const UBYTE zone_steps[6] = {8u,9u,7u,10u,8u,7u};
static const UBYTE zone_transpose[6] = {0u,5u,3u,7u,0u,5u};

static UBYTE song_step, song_wait, song_arrangement, song_zone, music_paused;
static UBYTE lead_note, bass_note, lead_duty, lead_envelope, bass_level;
static UBYTE noise_timer, noise_lock;
static UBYTE fx_effect, fx_age, fx_duration, fx_priority, fx_duck, fx_zone;

static void load_wave(UBYTE zone) {
    UBYTE i;
    const UBYTE *wave = triangle;
    switch (zone) {
        case 1u: wave = coolant_wave; break;
        case 2u: wave = engine_wave; break;
        case 3u: wave = archive_wave; break;
        case 4u: wave = array_wave; break;
        case 5u: wave = star_engine_wave; break;
    }
    NR32_REG = 0u;
    NR30_REG = 0u;
    for (i = 0u; i != 16u; ++i) AUD3WAVE[i] = wave[i];
    NR30_REG = 0x80u;
}

static void play_lead(UBYTE note) {
    UWORD frequency = pitch[note];
    NR10_REG = 0u;
    NR11_REG = lead_duty;
    /* Lead envelopes use initial volumes >=3. Major cues lower music by two
     * volume units while retaining the envelope's decay timing. */
    NR12_REG = fx_duck ? lead_envelope - 0x20u : lead_envelope;
    NR13_REG = (UBYTE)frequency;
    NR14_REG = 0x80u | (UBYTE)(frequency >> 8);
}

static void play_bass(UBYTE note) {
    UWORD frequency = pitch[note];
    NR32_REG = fx_duck ? 0x60u : bass_level;
    NR33_REG = (UBYTE)frequency;
    NR34_REG = 0x80u | (UBYTE)(frequency >> 8);
}

static void play_cue_note(UBYTE note, UBYTE envelope) {
    UWORD frequency;
    /* Cue notes never exceed E6 (40); archive's largest +7 ends at 47. */
    note += zone_transpose[fx_zone];
    frequency = pitch[note];
    NR21_REG = 0x80u;
    NR22_REG = envelope;
    NR23_REG = (UBYTE)frequency;
    NR24_REG = 0x80u | (UBYTE)(frequency >> 8);
}

static void play_noise(UBYTE polynomial, UBYTE envelope, UBYTE frames) {
    NR41_REG = 0u;
    NR42_REG = envelope;
    NR43_REG = polynomial;
    NR44_REG = 0x80u;
    noise_timer = frames;
}

static void restore_music_levels(void) {
    if (!music_paused) {
        if (lead_note != REST) play_lead(lead_note);
        if (bass_note != REST) play_bass(bass_note);
    }
}

static void play_song_step(void) {
    UBYTE note;
    const UBYTE *phrase, *low_phrase;
    if (!song_step) {
        lead_duty = lead_duties[song_arrangement];
        lead_envelope = lead_envelopes[song_arrangement];
        if (song_zone == 1u) {
            lead_duty = 0x80u;
            lead_envelope = (song_arrangement == 2u) ? 0x36u : 0x46u;
        } else if (song_zone == 2u) {
            lead_duty = 0x40u;
            lead_envelope = (song_arrangement == 2u) ? 0x43u : 0x62u;
        } else if (song_zone == 3u) {
            lead_duty = 0x00u;
            lead_envelope = (song_arrangement == 2u) ? 0x35u : 0x45u;
        } else if (song_zone == 4u) {
            lead_duty = 0x80u;
            lead_envelope = (song_arrangement == 2u) ? 0x43u : 0x53u;
        } else if (song_zone == 5u) {
            lead_duty = 0x40u;
            lead_envelope = (song_arrangement == 2u) ? 0x43u : 0x62u;
        }
    }
    if (song_zone < 3u) note = (song_arrangement & 1u) ? answer[song_step] : lead[song_step];
    else {
        if (song_zone == 3u) phrase = (song_arrangement & 1u) ? archive_answer : archive_lead;
        else if (song_zone == 4u) phrase = (song_arrangement & 1u) ? array_answer : array_lead;
        else phrase = (song_arrangement & 1u) ? star_engine_answer : star_engine_lead;
        note = phrase[song_step];
    }
    if (note == REST) {
        lead_note = REST;
        NR12_REG = 0u;
    } else if (note != HOLD) {
        /* Coolant carries the theme seven semitones lower (D minor); engine
         * carries it three higher (C minor). Even after the bridge's extra
         * octave shift, all resulting pitch indices lie in 4..46. */
        if (song_zone == 1u) note -= 7u;
        else if (song_zone == 2u) note += 3u;
        if (song_arrangement == 2u) note -= 12u;
        lead_note = note;
        play_lead(note);
    }
    if (!(song_step & 3u)) {
        if (song_zone < 3u) bass_note = bass[song_step >> 2] + zone_transpose[song_zone];
        else {
            low_phrase = song_zone == 3u ? archive_bass :
                         (song_zone == 4u ? array_bass : star_engine_bass);
            bass_note = low_phrase[song_step >> 2];
        }
        bass_level = ((song_zone == 1u) || (song_zone == 3u) || (song_arrangement == 2u)) ? 0x60u : 0x40u;
        play_bass(bass_note);
    } else if (((song_arrangement & 1u) ||
                (song_zone && song_arrangement != 2u)) && ((song_step & 3u) == 2u)) {
        /* A quiet octave echo adds motion only in the answering arrangements.
         * Legacy bass tops at 33; all newly authored bass/echo notes top at 28. */
        if (song_zone < 3u) bass_note = bass[song_step >> 2] + zone_transpose[song_zone] + 12u;
        else {
            low_phrase = song_zone == 3u ? archive_bass :
                         (song_zone == 4u ? array_bass : star_engine_bass);
            bass_note = low_phrase[song_step >> 2] + 12u;
        }
        bass_level = 0x60u;
        play_bass(bass_note);
    }
    if (!noise_lock && !(song_step & 1u)) {
        if (song_zone == 3u) {
            if (!(song_step & 15u)) play_noise(0x64u,0x21u,4u);
            else if ((song_step & 15u) == 8u) play_noise(0x15u,0x11u,2u);
        } else if (song_zone == 4u) {
            switch (song_step & 15u) {
                case 0u: case 8u: play_noise(0x64u,0x31u,4u); break;
                case 4u: case 12u: play_noise(0x35u,0x21u,3u); break;
                default:
                    if (song_arrangement != 2u) play_noise(0x15u,0x11u,2u);
                    break;
            }
        } else if (song_zone == 5u) {
            switch (song_step & 15u) {
                case 0u: case 6u: case 8u: play_noise(0x64u,0x41u,4u); break;
                case 4u: case 12u: play_noise(0x35u,0x31u,4u); break;
                default:
                    if (song_arrangement != 2u) play_noise(0x15u,0x21u,2u);
                    break;
            }
        } else switch (song_step & 15u) {
            case 0u: case 8u:
                play_noise(0x64u, (song_zone == 1u) ? 0x21u : 0x41u, 5u);
                break;
            case 4u: case 12u:
                play_noise(0x35u, (song_zone == 1u) ? 0x21u : 0x31u, 4u);
                break;
            default:
                if ((song_zone == 2u) && ((song_step & 15u) == 6u))
                    play_noise(0x64u, 0x31u, 4u); /* engine's offbeat kick */
                else if ((song_zone != 1u) && (song_arrangement != 2u))
                    play_noise(0x15u, 0x21u, 2u); /* sparse coolant/bridge */
                break;
        }
    }
    song_step = (song_step + 1u) & ((song_zone < 3u) ? 127u : 63u);
    if (!song_step) song_arrangement = (song_arrangement + 1u) & 3u;
    song_wait = zone_steps[song_zone];
}

/* Cue notes are only written at their boundaries; the hardware envelope does
 * the rest. Priority prevents a pickup from swallowing a damage or win cue. */
static void update_cue(void) {
    if (!fx_effect) return;
    switch (fx_effect) {
        case STARFALL_SFX_PICKUP:
            if (fx_age == 0u) play_cue_note(A5, 0x62u);
            else if (fx_age == 5u) play_cue_note(C6, 0x62u);
            else if (fx_age == 10u) play_cue_note(E6, 0x62u);
            break;
        case STARFALL_SFX_PULSE:
            if (fx_age == 0u) {
                play_cue_note(A5, 0x61u);
                play_noise(0x1au, 0x31u, 4u);
            } else if (fx_age == 3u) play_cue_note(E5, 0x51u);
            else if (fx_age == 6u) play_cue_note(A4, 0x41u);
            else if (fx_age == 9u) play_cue_note(C4, 0x31u);
            break;
        case STARFALL_SFX_HIT:
            if (fx_age == 0u) {
                play_cue_note(E3, 0x62u);
                play_noise(0x35u, 0x62u, 12u);
            } else if (fx_age == 6u) play_cue_note(C3, 0x52u);
            break;
        case STARFALL_SFX_WARNING:
            if ((fx_age == 0u) || (fx_age == 9u)) play_cue_note(G5, 0x51u);
            else if ((fx_age == 5u) || (fx_age == 14u)) NR22_REG = 0u;
            break;
        case STARFALL_SFX_WIN:
            switch (fx_age) {
                case 0u: play_cue_note(A4, 0x73u); break;
                case 6u: play_cue_note(C5, 0x73u); break;
                case 12u: play_cue_note(E5, 0x73u); break;
                case 18u: play_cue_note(A5, 0x73u); break;
                case 24u: play_cue_note(E5, 0x73u); break;
                case 30u: play_cue_note(G5, 0x73u); break;
                case 36u: play_cue_note(A5, 0x75u); break;
            }
            break;
        case STARFALL_SFX_RELAY:
            switch (fx_age) {
                case 0u: play_cue_note(E5, 0x62u); break;
                case 4u: play_cue_note(A5, 0x62u); break;
                case 8u: play_cue_note(E6, 0x62u); break;
                case 16u: play_cue_note(C6, 0x63u); break;
                case 24u: play_cue_note(A5, 0x64u); break;
            }
            break;
        case STARFALL_SFX_CORE_OPEN:
            switch (fx_age) {
                case 0u:
                    play_cue_note(F3, 0x64u);
                    play_noise(0x45u, 0x31u, 14u);
                    break;
                case 6u: play_cue_note(A3, 0x64u); break;
                case 12u: play_cue_note(C4, 0x64u); break;
                case 18u: play_cue_note(F4, 0x64u); break;
                case 24u: play_cue_note(A4, 0x64u); break;
                case 30u: play_cue_note(C5, 0x65u); break;
            }
            break;
        case STARFALL_SFX_CORE_HIT:
            if (fx_age == 0u) {
                play_cue_note(G4, 0x61u);
                play_noise(0x31u, 0x41u, 7u);
            } else if (fx_age == 3u) play_cue_note(E4, 0x51u);
            else if (fx_age == 6u) play_cue_note(C4, 0x41u);
            break;
        case STARFALL_SFX_LAUNCH:
            switch (fx_age) {
                case 0u:
                    play_cue_note(A4, 0x74u);
                    play_noise(0x35u, 0x31u, 22u);
                    break;
                case 6u: play_cue_note(C5, 0x74u); break;
                case 12u: play_cue_note(E5, 0x74u); break;
                case 18u: play_cue_note(A5, 0x74u); break;
                case 24u: play_cue_note(B5, 0x74u); break;
                case 30u: play_cue_note(C6, 0x74u); break;
                case 36u: play_cue_note(E6, 0x76u); break;
            }
            break;
    }
    if (++fx_age >= fx_duration) {
        NR22_REG = 0u;
        fx_effect = fx_priority = 0u;
        if (fx_duck) {
            fx_duck = 0u;
            restore_music_levels();
        }
    }
}

void starfall_audio_init(void) BANKED {
    /* Atomically leave GB Studio's timer-driven song/sample players idle before
     * taking ownership. No timer settings or interrupt handlers are changed. */
    CRITICAL {
        music_stop();
        sfx_reset_sample();
    }
    NR52_REG = 0x80u;
    NR50_REG = 0x44u; /* moderate master volume, no cartridge audio input */
    NR51_REG = 0xffu; /* centered on both speakers/headphone outputs */
    NR12_REG = NR22_REG = NR32_REG = NR42_REG = 0u;
    load_wave(0u);
    NR31_REG = 0u;
    song_step = song_wait = song_arrangement = song_zone = 0u;
    lead_note = bass_note = REST;
    lead_duty = lead_duties[0];
    lead_envelope = lead_envelopes[0];
    bass_level = 0x40u;
    music_paused = 1u;
    fx_effect = fx_age = fx_duration = fx_priority = fx_duck = fx_zone = 0u;
    noise_timer = noise_lock = 0u;
}

void starfall_audio_zone(UBYTE zone) BANKED {
    if (zone > 5u) zone = 5u;
    if (zone == song_zone) return;
    NR12_REG = 0u;
    load_wave(zone);
    song_zone = zone;
    song_step = song_wait = song_arrangement = 0u;
    lead_note = bass_note = REST;
    /* Channel 2's current cue and its priority/age are deliberately retained. */
}

void starfall_audio_update(UBYTE paused) BANKED {
    if (noise_timer && !--noise_timer) NR42_REG = 0u;
    if (noise_lock) --noise_lock;
    update_cue();
    if (paused) {
        if (!music_paused) {
            NR12_REG = NR32_REG = 0u;
            if (!noise_lock) {
                NR42_REG = 0u;
                noise_timer = 0u;
            }
            music_paused = 1u;
        }
        return;
    }
    if (music_paused) {
        music_paused = 0u;
        if (lead_note != REST) play_lead(lead_note);
        if (bass_note != REST) play_bass(bass_note);
    }
    if (!song_wait || !--song_wait) play_song_step();
}

void starfall_audio_sfx(UBYTE effect) BANKED {
    UBYTE priority, duration, was_ducked;
    switch (effect) {
        case STARFALL_SFX_PULSE: priority = 1u; duration = 12u; break;
        case STARFALL_SFX_PICKUP: priority = 2u; duration = 18u; break;
        case STARFALL_SFX_WARNING: priority = 3u; duration = 18u; break;
        case STARFALL_SFX_HIT: priority = 4u; duration = 20u; break;
        case STARFALL_SFX_WIN: priority = 5u; duration = 60u; break;
        case STARFALL_SFX_RELAY: priority = 2u; duration = 36u; break;
        case STARFALL_SFX_CORE_OPEN: priority = 3u; duration = 48u; break;
        case STARFALL_SFX_CORE_HIT: priority = 4u; duration = 16u; break;
        case STARFALL_SFX_LAUNCH: priority = 6u; duration = 84u; break;
        default: return;
    }
    if (fx_effect && priority < fx_priority) return;
    was_ducked = fx_duck;
    if (noise_lock) {
        NR42_REG = 0u;
        noise_timer = noise_lock = 0u;
    }
    NR22_REG = 0u;
    fx_effect = effect;
    fx_age = 0u;
    fx_duration = duration;
    fx_priority = priority;
    fx_zone = song_zone; /* a zone change does not transpose a cue mid-phrase */
    fx_duck = (effect == STARFALL_SFX_CORE_OPEN) || (effect == STARFALL_SFX_LAUNCH);
    if (was_ducked != fx_duck) restore_music_levels();
    if ((effect == STARFALL_SFX_PULSE) || (effect == STARFALL_SFX_HIT) ||
        (effect == STARFALL_SFX_CORE_OPEN) || (effect == STARFALL_SFX_CORE_HIT) ||
        (effect == STARFALL_SFX_LAUNCH))
        noise_lock = duration;
}

