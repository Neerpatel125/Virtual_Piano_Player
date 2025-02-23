from music21 import converter, note, chord, tempo, meter
import sys

piano_scale = "1!2@34$5%6^78*9(0qQwWeErtTyYuiIoOpPasSdDfgGhHjJklLzZxcCvVbBnm"
scale_length = len(piano_scale)
SILENCE_LIMIT = None    # Maximum beat size of silence (1, .5, .25, .125, ...)
bpm = None              # Beats Per Minute 

def get_virtual_key(midi_number):
    global piano_scale, scale_length
    index = (midi_number - 21) % scale_length
    return piano_scale[index]

def extract_bpm(midi):
    bpm = None
    for element in midi.flat.getElementsByClass(tempo.MetronomeMark):
        bpm = element.number
    return bpm

def midi_to_virtual_sheet(midi_file, output_file, bpm):
    midi = converter.parse(midi_file)
    if bpm is None:
        bpm = extract_bpm(midi)
    # Calculate beats per second and the actual hold limit in beats
    beats_per_second = bpm / 60
    space_delay = .075 / beats_per_second
    dash_delay = 2 * space_delay

    sheet_music = []
    prev_time = None
    prev_duration = None
    global SILENCE_LIMIT
    if SILENCE_LIMIT is not None:
        # Convert it into seconds
        SILENCE_LIMIT = SILENCE_LIMIT / beats_per_second

    for element in midi.flat.notes:
        current_time = element.offset
        # Timing between notes adjusted using BPM-based delays
        if prev_time is not None:
            gap = None
            if prev_time + prev_duration > current_time:
                # The note is being held, use just the offsets
                gap = current_time - prev_time
            else:
                # Consider how long it was held
                gap = current_time - (prev_time + prev_duration)
            # Adjust the gap to match my beats timers 
            gap = gap / beats_per_second
            # Cap the gap to avoid long, awkward silences. 
            if SILENCE_LIMIT is not None:
                if gap > SILENCE_LIMIT: gap = SILENCE_LIMIT
            while gap >= dash_delay:
                sheet_music.append("|")
                gap -= dash_delay
            while gap >= space_delay:
                sheet_music.append(" ")
                gap -= space_delay

        if isinstance(element, note.Note):
            key = get_virtual_key(element.pitch.midi)
            sheet_music.append(key)
        elif isinstance(element, chord.Chord):
            keys = [get_virtual_key(n.pitch.midi) for n in element.notes]
            sheet_music.append(f"[{''.join(keys)}]")

        prev_duration = element.quarterLength
        prev_time = current_time
    # Save the sheet music
    with open(output_file+f"_MIDI_space{space_delay}_dash{dash_delay}_bpm{bpm}.txt", "w") as f:
        f.write("".join(sheet_music))

    print(f"Virtual sheet music saved to ./songs")

if len(sys.argv) < 3:
    print("Please enter the correct parameters:")
    print("\t1. The MIDI file name (without '.mid'), and make sure it's in the download's folder!")
    print("\t2. The name of the song (code will add bpm and bpb to the file name).")
    print("\t3. [Optional] The BPM of the song.")
    print("\t4. [OPTIONAL] Limit the time period of silence (seconds). Used to avoid awkward pauses when a note is held for a long time.")
    exit()

fileName = sys.argv[1]
if len(sys.argv) > 3:
    if sys.argv[3].isnumeric(): bpm = int(sys.argv[3])
if len(sys.argv) > 4:
    SILENCE_LIMIT = float(sys.argv[4])    #seconds
midi_to_virtual_sheet(f"~/Downloads/{fileName}.mid", f"./songs/{sys.argv[2]}", bpm)


