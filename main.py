import math
import os
import time

import numpy as np
import cv2
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer
from moviepy.editor import VideoFileClip

vid_path = "badapple.mp4"

fps = 30
ms_per_frame = 1/fps

# assumes console BG is darker than text
chars = [".", ",", "-", "~", ":", ";", "=", "!", "*", "#", "$", "@"]

# to do: add dynamic video scaling
size = (160, 80) # (length, height)
#size = (128, 72)

b = math.floor(255/(len(chars)-1))  

# clear console command
clear_console = 'clear' if os.name == 'posix' else 'CLS'

def play_animation(vid: cv2.VideoCapture, dimensions: tuple, f_range=range(1000000)):
    
    length = int(dimensions[0])
    height = int(dimensions[1])

    #  match console size with dimensions of the animation
    os.system(f'mode con: cols={length} lines={height}')

    load_audio(vid_path)
    
    current_frame = 1
    start = time.time()
    while True:
        ret, frame = vid.read()
        if ret and current_frame in f_range:
            if current_frame == 1:
                mixer.music.play()
                
            ascii_frame = render_ascii(frame, dimensions)
            print(ascii_frame)
            current_frame += 1
            now = time.time()
            time.sleep((max(0, ms_per_frame-(now-start))))
            start = now
        else:
            break
        
    mixer.music.stop()
    os.system(clear_console)
    print("animation has ended.")

def load_audio(video_path):
    vid_name = os.path.splitext(video_path)[-2]
    audio_path = f"./audio/{vid_name}.mp3"

    mixer.init()
    mixer.music.set_volume(0.5)

    # downloads audio if video's audio file is not found
    if not os.path.isfile(audio_path): 
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)

    mixer.music.load(audio_path)

def render_ascii(frame, dimensions: tuple):
    # resize frame >> apply grayscale
    frame = cv2.resize(frame, dimensions) 
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # assigns each pixel's grayscale value (0-255) to a character
    # in every row
    ascii_rows = ["".join([chars[pixel//b] for pixel in ln]) for ln in frame]
    # join 
    return '\n'.join(ascii_rows)

def main():
    vid = cv2.VideoCapture(vid_path)
    print(vid.get(cv2.CAP_PROP_FPS))

    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    frame_count = input(f"({vid_path}) number of frames to play: ")
    if frame_count.isdigit():
        print(f"playing {frame_count} frames of {vid_path}...")
        frame_range = range(1, int(frame_count))
        time.sleep(1)
        vid = cv2.VideoCapture(vid_path)
        play_animation(vid, size, frame_range) 

    else: 
        print(f"playing full video of {vid_path}...")
        time.sleep(1)
        vid = cv2.VideoCapture(vid_path)
        play_animation(vid, size) 

if __name__ == "__main__":
    main()