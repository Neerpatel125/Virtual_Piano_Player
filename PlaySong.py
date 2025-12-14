import pyautogui as pg
import time
from threading import Thread
from pynput import keyboard
import sys
import re

stop_playing = False
pause = False
dashDelay = None	# Delay between '-'
pipeDelay = None	# Delay between '|'
spaceDelay = None	# Delay between spaces 

def readSong(file):
	def strip_around_separators(s):
		return re.sub(r'\s+([\-|]+)\s+', r'\1', s)
	song = ""
	with open(file, "r") as f:
		for line in f.readlines():
			line = strip_around_separators(line)
			song += line.strip() + " "
	return song

def playNote(c):
	if c.isupper():
		pg.hotkey("shift", c)
	else:
		pg.press(c)

def playSong(song):
	atOnce = False
	multiKeys = []
	global dashDelay, spaceDelay, pause
	for c in song:
		# Stop when signaled to. 
		if stop_playing: return
		# Pause when signalled to.
		while pause: 
			time.sleep(.001) 
			if stop_playing: return 

		# Play the song 
		if c == "[":
			atOnce = True
		elif c == "]":
			atOnce = False
			pg.hotkey(*multiKeys) 
			multiKeys = []
		elif atOnce:
			multiKeys.append(c)
		elif c == "-":
			time.sleep(dashDelay)
		elif c == " ":
			time.sleep(spaceDelay)
		elif c == "|":
			time.sleep(pipeDelay)
		else:
			playNote(c)
	# Exit when done playing. 
	pg.press('ctrl')

def on_press(key):
    # Stops the playback when backspace is pressed.
	global stop_playing, dashDelay, spaceDelay, noteDelay, pause
	try:
		if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r or key == keyboard.Key.backspace:
			stop_playing = True
			return False  # Stop the listener after key is pressed
		if key == keyboard.KeyCode.from_char('['): 
			spaceDelay *= 1.1
			dashDelay *= 1.1
		if key == keyboard.KeyCode.from_char(']'): 
			spaceDelay /= 1.1
			dashDelay /= 1.1
		if key == keyboard.Key.f12: 
			pause = not pause 
	except Exception as e:
		print(f"Error: {e}")


if len(sys.argv) < 2:
	print("Please enter valid parameters:")
	print("\t1. File path for the sheet music.")
	print("\t2. Tempo of the music (BPM) (optional if specified in file).")
	print("Tips:")
	print("\t - Use '[' and ']' to adjust the tempo.")
	print("\t - Press f12 to pause/play.")
	print("\t - Press ctrl or backspace to exit.")
	exit()

filePath = sys.argv[1]
song = readSong(filePath)
bpm = None 			# Beats per minute, tempo of the song.
isMidi = False 		# MIDI converter handles dash delay differently.
if len(sys.argv) == 2:
	# Get tempo info from the file name. 
	fileName = sys.argv[1].split('.txt')[0]	# Remove file extension
	split = fileName.split('_')
	for token in split:
		if token.lower() == 'midi':
			isMidi == True
		if token[0:3].lower() == 'bpm':
			bpm = float(token[3:])
		if token[0:5].lower() == 'space':
			spaceDelay = float(token[5:])
			dashDelay = 2 * spaceDelay
if len(sys.argv) > 2:
	bpm = float(sys.argv[2])


# Calculate time delays based on BPM if not found in file.
if not isMidi or spaceDelay is None or dashDelay is None:
	seconds_per_beat = 60.0 / bpm
	spaceDelay = seconds_per_beat / 4			
	dashDelay = seconds_per_beat / 2
	pipeDelay = seconds_per_beat / 2

print("Starting...")
thread = Thread(target=playSong, args=(song,))
time.sleep(2)
thread.start()

# Start the key listener
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()  # Keep listening until backspace is pressed

print("Exiting...")
