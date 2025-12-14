# Virtual Piano Player

A virtual piano can be found at https://virtualpiano.net. 

This tool presses the keys according to a sheet music and tempo.

## How to use
The `PlaySong.py` file takes the following arguments
  1. `file`: path to the song text file (several listed in the `songs` directory).
  2. `bpm`: beats per minute to play the song at; optional if the file specifies the bpm, else required. 

### Examples
1. `python3 PlaySong.py songs/je_te_laisserai_des_mots_Trans2_bpm133.txt`

2. `python3 PlaySong.py songs/je_te_laisserai_des_mots_Trans2_bpm133.txt 266`

### Tips
   - Use `[` and `]` to decrease and increase the tempo, respectively.
   - Press `f12` to pause/play.
   - Press `ctrl` or `backspace` to exit.
