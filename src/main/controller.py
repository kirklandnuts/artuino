# This script produces music based on continuous serial input from an Arduino device.
# A) continuously read input from Arduino serial output
# B) event loop
#   1) check user input for QUIT command
#   2) get instantaneous velocity and height
#   3) select note based on height
#   4) play note
#   5) sleep for a time period calculated based on velocity

# to do:
#   - change notes based on height
#   - use magenta to generate notes


import os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))

import sys
import time
import pygame
from random import random, choice, randrange
from mingus.core import progressions, intervals
from mingus.core import chords as ch
from mingus.containers import NoteContainer, Note
from mingus.midi import fluidsynth
from device import Device
import numpy as np
import scipy.stats


SOUNDFONT_PATH = '/Users/timmy/Documents/projects/artuino/assets/soundfont/grand-piano-YDP-20160804.sf2'

# progression = ['I', 'bVdim7']
# progression = ["I", "vi", "ii", "iii7", "I7", "viidom7", "iii7","V7"]
# progression = ["I", 'vi', 'IV', 'V']
PROGRESSIONS = [
    {
        'progression' : ['i','VI','III','VII'],
        'key' : 'Ab'
    },
    {
        'progression' : ["I", 'vi', 'IV', 'V'],
        'key' : 'C'
    },
    {
        'progression' : ["I", 'vi', 'IV', 'V'],
        'key' : 'C'
    }
]
SD = 1
p = 2
DRIVER = 'coreaudio'

double_time = True
orchestrate_second = True
swing = True
play_solo = True
play_drums = False
play_bass = True
play_chords = True
bar_length = 1.75
song_end = 24

# Control beginning of solos and chords

solo_start = 2
solo_end = 12
chord_start = 6
chord_end = 14

# Channels

chord_channel = 2
chord_channel2 = 7
chord_channel3 = 3
bass_channel = 4
solo_channel = 13

# generating chords
progression = PROGRESSIONS[p]['progression']
key = PROGRESSIONS[p]['key']
chords = progressions.to_chords(progression, key)


# soundfont from https://musescore.org/en/handbook/soundfonts-and-sfz-files#specialised
SOUNDFONT_PATH = os.path.join(ROOT_DIR, 'assets', 'soundfont', 'grand-piano-YDP-20160804.sf2').encode('utf-8')
CHANNEL = 8


def threshold_value(val, low, high):
    if val > high:
        val = high
    elif val < low:
        val = low
    return val



if __name__ == '__main__':
    # initializing midi synthesizer with soundfont
    time.sleep(1)
    if not fluidsynth.init(SOUNDFONT_PATH, driver=DRIVER):
        print("Failed to load soundfont: {}".format(SOUNDFONT_PATH))
        sys.exit(1)
    print('\nTesting audio driver...')
    for i in range(4):
        fluidsynth.play_Note(Note('C-4'), solo_channel, 110)
        time.sleep(0.5)
    
    print('\nInitializing device...')
    device = Device()
    print('Device initialized\n')

    print('\n\n ======================')
    print('| Press ENTER to begin |')
    print(' ======================\n\n')
    if input() == 'q':
        sys.exit(1)

    # initialize device connection
    time.sleep(2)
    print('\nCalibrating device... (move your hand around)')

    loop = 1
    while loop < song_end:
        i = 0
        if loop == 2:
            min_d, max_d = device.define_range()
            print('Calibration complete: defined range [{},{}]'.format(min_d, max_d))
            print('\nGet ready to play!\n')

        for chord in chords:
            if loop == 1:
                print('...')
            if loop == 2:
                print(4 - i)
                if 4 - i == 1:
                    print('\nHave fun!\n\n{}\n\n'.format('='*20))
            c = NoteContainer(chords[i])
            l = Note(c[0].name)
            n = Note('C')
            l.octave_down()
            l.octave_down()
            
            # print(ch.determine(chords[i])[0])

            if not swing and play_chords and loop > chord_start and loop\
                < chord_end:
                fluidsynth.play_NoteContainer(c, chord_channel, randrange(50, 75))
            if play_chords and loop > chord_start and loop < chord_end:
                
                if orchestrate_second:
                    if loop % 2 == 0:
                        fluidsynth.play_NoteContainer(c, chord_channel2,
                                randrange(50, 75))
                else:
                    fluidsynth.play_NoteContainer(c, chord_channel2, randrange(50,
                            75))

            if double_time:
                beats = [random() > 0.5 for x in range((loop % 2 + 1) * 8)]
            else:
                beats = [random() > 0.5 for x in range(8)]
            
            t = 0

            # constructing extended note selection
            c_lower = NoteContainer(([n.name, n.octave-1] for n in c)) 
            c_upper = NoteContainer(([n.name, n.octave+1] for n in c))
            c_extended = c_lower + c + c_upper
            c_extended = c_extended.remove_duplicate_notes()

            for beat in beats:
                # Play random note
                if beat and play_solo and loop > solo_start and loop < solo_end:
                    distance = device.distance()
                    scaled_distance = distance * (len(c_extended) - 1)
                    rounded_probability_draw = round(np.random.normal(scaled_distance, SD))
                    note_selection = threshold_value(rounded_probability_draw, 0, len(c_extended) - 1)
                    n = c_extended[note_selection]

                    fluidsynth.stop_Note(n)
                    if t % 2 == 0:
                        pass
                    elif random() > 0.5:
                        if random() < 0.46:
                            n = Note(intervals.second(n.name, key))
                        elif random() < 0.46:
                            n = Note(intervals.seventh(n.name, key))
                        else:
                            pass
                        if t > 0 and t < len(beats) - 1:
                            if beats[t - 1] and not beats[t + 1]:
                                pass
                    print('playing note: {}'.format(n))
                    fluidsynth.play_Note(n, solo_channel, randrange(80, 110))

                # Repeat chord on half of the bar
                if play_chords and t != 0 and loop > chord_start and loop\
                    < chord_end:
                    if swing and random() > 0.95:
                        fluidsynth.play_NoteContainer(c, chord_channel3,
                                randrange(20, 75))
                    elif t % (len(beats) / 2) == 0 and t != 0:
                        fluidsynth.play_NoteContainer(c, chord_channel3,
                                randrange(20, 75))

                # Play bass note

                if play_bass and t % 4 == 0 and t != 0:
                    l = Note(choice(c).name)
                    l.octave_down()
                    l.octave_down()
                    fluidsynth.play_Note(l, bass_channel, randrange(50, 75))
                elif play_bass and t == 0:
                    fluidsynth.play_Note(l, bass_channel, randrange(50, 75))

                # Drums

                if swing:
                    if t % 2 == 0:
                        sleep_time = (bar_length / (len(beats) * 3)) * 4
                        
                    else:
                        sleep_time = (bar_length / (len(beats) * 3)) * 2
                else:
                    sleep_time = bar_length / len(beats)
                time.sleep(sleep_time)
                t += 1
            fluidsynth.stop_NoteContainer(c, chord_channel)
            fluidsynth.stop_NoteContainer(c, chord_channel2)
            fluidsynth.stop_NoteContainer(c, chord_channel3)
            fluidsynth.stop_Note(l, bass_channel)
            fluidsynth.stop_Note(n, solo_channel)
            i += 1
        loop += 1
