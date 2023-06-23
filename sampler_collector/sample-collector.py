import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy.io.wavfile import write

import pyaudio
import wave

import time
import itertools
from pprint import pprint


import argparse

#from recorder import Recorder

# Audio stuff

# Notes stuff

def get_oct_note(note):
    return int(note[-1]),note[0:-1]

scale12notes = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]

# like on piano
scale88notes = \
    [f"{n}0" for n in scale12notes[-3:]] + \
    [f"{n}{o}" for o,n in itertools.product(range(1,8),scale12notes)] + \
    ["C8"]

ipE3 = scale88notes.index("E3")
ipE5 = scale88notes.index("E5")

# 19th thread last on our guitar
guitar_all_notes = scale88notes[ipE3:ipE5+1+19]

# notes of interest
guitar_notes = scale88notes[ipE3:ipE5+1+5]

notes_on_neck = {
    1:"E5",
    2:"B4",
    3:"G4",
    4:"D4",
    5:"A3",
    6:"E3"
}

def sample_collector(sound_filename="sample.wav", annotation_filename="sample.csv", record_time=10.0):
    """
    rec_dev_id list of record indexes
    :param record_time:
    :param filename:
    :return:
    """

    # notes of interest
    guitar_notes = scale88notes[ipE3:ipE5 + 1 + 5]

    notes_on_string = {k:[] for k in range(6,0,-1)}

    for istr in notes_on_string.keys():
        for i in range(6):
            if istr != 1 and i == 5:
                break

            if istr == 3 and i == 4:
                break

            notes_on_string[istr].append(guitar_all_notes[guitar_all_notes.index(notes_on_neck[istr])+i])

    string_thread_to_play = []
    for istr in notes_on_string.keys():
        for ithread, note in enumerate(notes_on_string[istr]):
            string_thread_to_play.append([istr,ithread,note])



    #0     1     2     3
    #      Ready Set   Go

    # format [time,message,note played]
    #screent_play
    fout = open(annotation_filename, "wt")
    fout.write("note,istr,ithread,t_start,tend\n")
    sp = []
    def get_screent_play(t0, istr, ithread, note):
        "Should always finished with word Done"
        m_sp = []
        m_sp.append([t0, f"\rGet ready to play {note} on {istr}-th string {ithread}-th note\n", None])
        m_sp.append([t0 + 1.0, f"\rReady", None])
        m_sp.append([t0 + 2.0, f"\rSet", None])
        m_sp.append([t0 + 3.0, f"\rGo\n", note])
        for i in np.arange(0,record_time,0.1):
            m_sp.append([t0 + 3.0 + i, f"\r{record_time - i:3.1f} seconds left", note])
        m_sp.append([t0 + 3.0 + i, f"\r{0.0:3.1f} seconds left\n", note])
        m_sp.append([t0 + 3.0 + record_time, f"\rDone\n\n", None])

        fout.write(f"{note:5},{istr:5},{ithread:5},{t0 + 3.0:10.3f},{t0 + 3.0 + record_time:10.3f}\n")
        return m_sp

    t0 = 0.0
    for istr,ithread,note in string_thread_to_play:
        sp += get_screent_play(t0, istr, ithread, note)
        t0 = sp[-1][0]

    fout.close()

    next_event = 0
    all_events = len(sp)

    # Start audio recording
    hornsound = 'truck-horn.wav'
    sound_data, fs = sf.read(hornsound, dtype='float32')
    seconds = sp[-1][0]
    print(f"The session will be {seconds} seconds")
    time.sleep(3)

    sound_data = np.pad(sound_data, [(0, int(seconds * fs) - sound_data.shape[0]), (0, 0)], mode='constant',
                        constant_values=0)

    print("\nLets' play!!!\n")
    t0 = time.time()
    myrecording = sd.playrec(sound_data, samplerate=fs, channels=2)

    t = time.time()-t0
    while next_event < all_events:
        t = time.time() - t0
        while sp[next_event][0] < t:
            print(f"{sp[next_event][1]}", end='', flush=True)
            #if sp[next_event][1][-1]=="\n":
            #    print(f"{t:12.6f} {sp[next_event][1]}", end='', flush=True) #{t:12.6f}
            #else:
            #    print(f"\r{t:12.6f} {sp[next_event][1]}", end='', flush=True)
            next_event += 1
            if next_event >= all_events:
                break
            t = time.time() - t0

    write(sound_filename, fs, myrecording)  # Save as WAV file


def set_cli():
    parser = argparse.ArgumentParser(description='Sample Collector')
    #subparsers = parent_parser.add_subparsers(title='commands')

    # # list_rec_dev
    # parser = subparsers.add_parser('list_rec_dev', description="list record devices")
    #
    # def handler1(_):
    #     list_rec_device()
    #
    # parser.set_defaults(func=handler1)


    # do rec
    #parser = subparsers.add_parser('rec', description="do recording")
    #parser.add_argument('--rec-dev-id', help="id of record device, run 'python -m sounddevice' to see options", action='append',required=True, type=int)

    def handler2(args):
        print(args)
        sample_collector()
        #

    parser.set_defaults(func=handler2)


    cli_args = parser.parse_args()

    if hasattr(cli_args, "func"):
        return cli_args.func(cli_args)


if __name__ == '__main__':
    set_cli()
    #sample_collector()