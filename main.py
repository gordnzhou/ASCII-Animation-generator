import math
import os
import time

import numpy as np
import cv2
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer

vid_path = "badapple.mp4"
audio_path = "badapple.mp3"

# ascii are darkest to brightest (use if console background is black)
ascii_chars = ".,-~:;=!*#$@"

brightest_rgb_value = 255
b = (len(ascii_chars)-1)/brightest_rgb_value

# to do: add dynamic video scaling
# my area threshold before the frames starts to look choppy: (127 x 127)
size = (160, 80) # (length, height)

clear_console = 'clear' if os.name == 'posix' else 'CLS' # clear console os command

def play_animation(vid, dimensions, f_range=range(1000000)):
    length = int(dimensions[0])
    height = int(dimensions[1])

    # changes console size to match the dimensions of the animation
    os.system(f'mode con: cols={length} lines={height}')

    mixer.music.load(audio_path) # loads audio
    mixer.music.set_volume(0.5) # sets volume of the audio to 50%
 
    # to do: add frame stalling to match video's fps
    current_frame = 1
    while True:
        ret, frame = vid.read() # gets the next frame of the video
        if ret and current_frame in f_range: 
            # audio starts on the first frame
            if current_frame == 1:
               mixer.music.play() 
            
            # adjusts the area of the frame to fit the console dimensions
            frame = cv2.resize(frame, dimensions) 

            # applies greyscale filter to frame to isolate each pixel's brightness
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            # converts each pixel to ascii based on its brightness and joins them to each row
            ascii_rows = ["".join([ascii_chars[math.ceil(pixel*b)] for pixel in line]) for line in frame]
            print('\n'.join(ascii_rows)) # prints each row of ascii to a new line

            current_frame += 1 # increment frame by 1 each iteration
        else:
            break
    
    mixer.music.stop()

def main():
    mixer.init()

    while True:
        frame_count = input(f"({vid_path}) number of frames to play: ")

        if frame_count.isdigit(): #creates range of frames to play
            print(f"playing {frame_count} frames of {vid_path}...")
            frame_range = range(1, int(frame_count)) 

        else: # no valid input
            print(f"playing full video of {vid_path}...")
    
        time.sleep(1)
        vid = cv2.VideoCapture(vid_path) # creates a new object instance from path
        play_animation(vid, size, frame_range) 

        os.system(clear_console)
        print("animation has ended.")

if __name__ == "__main__":
    main()