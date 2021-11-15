import math
import os
import time

import fpstimer
import numpy as np
import cv2
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer
from moviepy.editor import VideoFileClip

# video to convert to ascii animation
VID_PATH = "./videos/badapple.mp4"

CHARS = " .:-=+*#%@"

# for when chars in cmd are not displayed as "perfect squares"
# for no extra scaling, make it equal to 1
W_SCALE_FACTOR = 1.8

# to help keep renders quick
MAX_FRAME_AREA =  12000
MAX_FPS = 30

# clear console command
clear_console = 'clear' if os.name == 'posix' else 'CLS'

def play_animation(vid: cv2.VideoCapture, dimensions: tuple, seconds=None):
    fps = min(MAX_FPS, vid.get(cv2.CAP_PROP_FPS))

    # number of frames to play, plays all if no duration specified
    if seconds == None:
        frame_count = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
        seconds = int(vid.get(cv2.CAP_PROP_FRAME_COUNT)/60)
    else:
        frame_count = int(seconds*fps)

    length = int(dimensions[0])
    height = int(dimensions[1])

    #  match console size with dimensions of the animation
    os.system(f'mode con: cols={length} lines={height}')

    current_frame = 1
    
    load_audio(VID_PATH)
    timer = fpstimer.FPSTimer(fps)
    while True:
        ret, frame = vid.read() # gets next frame
        if ret and current_frame <= frame_count:
            if current_frame == 1:
                mixer.music.play()
                
            ascii_frame = render_ascii(frame, dimensions)
            print(ascii_frame)
            current_frame += 1
        else:
            break

        # stalls each iteration to help maintain frame rate
        timer.sleep()
        
    mixer.music.stop()
    os.system(clear_console)
    print(f"animation has ended. ({seconds} secs)")

def load_audio(video_path):
    vid_name = os.path.basename(video_path).split(".")[0]

    audio_path = f"./audio/{vid_name}.mp3"

    mixer.init()
    mixer.music.set_volume(0.5)

    # downloads audio if video's audio file is not found
    if not os.path.isfile(audio_path): 
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)

    mixer.music.load(audio_path)

# extra calculations done here to spped up rendering
b = math.ceil(255/(len(CHARS)-1))

def render_ascii(frame, dimensions: tuple):
    # resize frame >> apply grayscale
    frame = cv2.resize(frame, dimensions) 
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # converts each pixel's grayscale value (0-255) to a character index
    # appends each row of ascii characters to a list
    ascii_rows = ["".join([CHARS[pixel//b] for pixel in ln]) for ln in frame]
 
    return '\n'.join(ascii_rows)

def scale_frame_size(width, height, target_area):
    w_to_h_ratio = (width*W_SCALE_FACTOR)/height

    # scale to target area while mainting aspect ratio
    scaled_width = math.sqrt((target_area*w_to_h_ratio))
    scaled_height = math.sqrt((target_area/w_to_h_ratio))

    # tuple of (width, height) as int
    return (math.floor(scaled_width), math.floor(scaled_height))

def main():
    vid = cv2.VideoCapture(VID_PATH)

    vid_width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    vid_height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    size = scale_frame_size(vid_width, vid_height, MAX_FRAME_AREA)
    fps =  vid.get(cv2.CAP_PROP_FPS)

    length = vid.get(cv2.CAP_PROP_FRAME_COUNT)/fps
    print(f"({VID_PATH}): length: {int(length)} secs  width: {size[0]} height: {size[1]}, fps: {min(30, int(fps))}")

    secs = input(f"how many seconds would you like to play? (or play the full video) ")

    try:
        secs = float(secs)
        print(f"playing {secs} seconds of {VID_PATH}...")
        time.sleep(1)

        play_animation(vid, size, secs) 
    except ValueError:
        print(f"no number specified, playing full video of {VID_PATH}...")
        time.sleep(1)

        play_animation(vid, size) 

if __name__ == "__main__":
    main()