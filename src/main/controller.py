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

from mingus.core import notes, chords
from mingus.containers import *
from mingus.midi import fluidsynth


# soundfont from https://musescore.org/en/handbook/soundfonts-and-sfz-files#specialised
SOUNDFONT_PATH = os.path.join(ROOT_DIR, 'assets', 'soundfont', 'grand-piano-YDP-20160804.sf2').encode('utf-8')
CHANNEL = 8


if __name__ == '__main__':
    # initializing midi synthesizer with soundfont
    if fluidsynth.init(SOUNDFONT_PATH):
        print("Succesfully loaded soundfont: {}".format(SOUNDFONT_PATH))
    else:
        print("Failed to load soundfont: {}".format(SOUNDFONT_PATH))
        sys.exit(1)
    # get instantaneous velocity and height

    # set volume based on height

    # 


    