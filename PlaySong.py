import pyautogui as pg
import time
from threading import Thread
from pynput import keyboard
import sys

stop_playing = False
pause = False
dashDelay = None	# Delay between '-' or '|'
spaceDelay = None	# Delay between spaces 

def readSong(file):
	song = None
	with open(file, "r") as f:
		song = f.read()
	return song.replace('\n', " ")

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
		elif c == "-" or c == "|":
			time.sleep(dashDelay)
		elif c == " ":
			time.sleep(spaceDelay)
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
			spaceDelay *= 2 
			dashDelay *= 2
		if key == keyboard.KeyCode.from_char(']'): 
			spaceDelay /= 2
			dashDelay /= 2
		if key == keyboard.Key.f12: 
			pause = not pause 
	except Exception as e:
		print(f"Error: {e}")


if len(sys.argv) < 2:
	print("Please enter valid parameters:")
	print("\t1. File Name for the sheet music. Must be in the songs folder, exclude '.txt'.")
	print("\t2. [Optional if specified in file] Tempo of the music (BPM)")
	print("\n")
	print("Tips:")
	print("\t - Use '[' and ']' to adjust the tempo.")
	print("\t - Press f12 to pause/play.")
	print("\n")
	exit()

filePath = f"songs/{sys.argv[1]}.txt" 
song = readSong(filePath)
bpm = None 			# Beats per minute, tempo of the song.
isMidi = False 		# MIDI converter handles dash delay differently.
if len(sys.argv) == 2:
	# Get tempo info from the file name. 
	split = sys.argv[1].split('_')
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
	beats_per_second = bpm / 60
	spaceDelay = .25 / beats_per_second			
	dashDelay = 0.75 * spaceDelay

print("Starting...")
thread = Thread(target=playSong, args=(song,))
time.sleep(3)
thread.start()

# Start the key listener
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()  # Keep listening until backspace is pressed

print("Exiting...")
