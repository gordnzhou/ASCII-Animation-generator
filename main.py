import math
import os
import time

import fpstimer
import numpy as np
import cv2
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer
from moviepy.editor import VideoFileClip

CHARS = " .:-=+*#%@"

# for when chars in cmd are not displayed as "perfect squares"
# for no extra scaling, make it equal to 1
W_SCALE_FACTOR = 1.8

# to keep rendering from overwhelming frame rate
MAX_FRAME_AREA =  12000
MAX_FPS = 30

# clear console command
clear_console = 'clear' if os.name == 'posix' else 'CLS'

def play_animation(vid: cv2.VideoCapture, dimensions: tuple, seconds=None):
    fps = min(MAX_FPS, vid.get(cv2.CAP_PROP_FPS))

    # number of frames to play, plays all if no duration specified
    frame_count = vid.get(cv2.CAP_PROP_FRAME_COUNT) if not seconds else seconds*fps

    length, height = dimensions

    #  match console size with dimensions of the animation
    os.system(f'mode con: cols={length} lines={height}')

    current_frame = 1
    timer = fpstimer.FPSTimer(fps)
    while True:
        try:
            ret, frame = vid.read() # gets next frame
            if ret and current_frame <= frame_count:
                if current_frame == 1:
                    mixer.music.play()
                    
                ascii_frame = render_ascii(frame, dimensions)
                print(ascii_frame)
                current_frame += 1
            else:
                break

            # stalls each frame loop to help maintain frame rate
            timer.sleep()
        except KeyboardInterrupt:
            mixer.music.pause()
            os.system(clear_console)
            
            if input("Animation paused. Continue? (y) ") == "y":
                mixer.music.unpause()
                continue
            else:
                break
        
    mixer.music.stop()
    os.system(clear_console)
    print(f"animation has ended. ({round(current_frame/fps, 2)} secs)")

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

# extra calculations done here to speed up rendering
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

def select_video():
    vid_folder = "videos/"
    videos = [ file for file in os.listdir(vid_folder) if file.endswith(".mp4")]

    if not videos:
        print(f"no videos found! in {videos}!")
        exit()
    elif len(videos) == 1:
        return vid_folder + videos[0]

    for i, v in enumerate(videos):
        print(f"{i+1} - {v}")
    while True:
        index = input("respond with the # of the file you would like to play: ")

        if index.isdigit() and int(index) in range(1, len(videos)+1):
            return vid_folder + videos[int(index)-1]

def main():
    vid_path = select_video()
    load_audio(vid_path)
    os.system(clear_console)

    vid = cv2.VideoCapture(vid_path)

    vid_width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    vid_height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    size = scale_frame_size(vid_width, vid_height, MAX_FRAME_AREA)
    fps =  vid.get(cv2.CAP_PROP_FPS)

    length = int(vid.get(cv2.CAP_PROP_FRAME_COUNT)/fps)
    print(f"({vid_path}): length: {length} secs  width, height {size} fps: {min(MAX_FPS, int(fps))}")

    secs = input(f"how many seconds would you like to play? (or play the full video) ")

    try:
        secs = float(secs)
        print(f"playing {secs} seconds of {vid_path}...")
    except ValueError:
        secs = None
        print(f"no number specified, playing full video of {vid_path}...")

    time.sleep(1)
    play_animation(vid, size, secs) 

if __name__ == "__main__":
    main()