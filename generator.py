from collections import OrderedDict
from random import shuffle

import time
import os.path
from glob import glob
from pathlib import Path

import json
from cv2 import cv2
from SSIM_PIL import compare_ssim
from PIL import Image
from tqdm import tqdm
from moviepy.editor import VideoFileClip, concatenate_videoclips
import moviepy.video.fx.all as vfx

from video import Video

SECONDS_PER_CLIP = 3
NUM_CONNECTIONS = 7
STARTING_FRAME = 45

def root_dir():
    return Path(__file__).parent


def find_connections(videos, num_connections, seconds_per_clip):

    shuffle(videos)

    current_video = videos.pop()
    current_video.set_in_and_out_frame(STARTING_FRAME, SECONDS_PER_CLIP)

    # #---
    # current_video = Video(f"videos/8kFEZ3q1Uvo.mp4")
    # current_video.set_in_and_out_frame(2199, SECONDS_PER_CLIP)
    # videos.pop(videos.index(current_video))
    # #---

    connections = [current_video]

    for _ in range(num_connections):
        max_ssi = -1.0

        with Image.open(current_video.get_frame_path(current_video.out_frame)) as image_1:
            with tqdm(total=len(videos)) as pbar:
                for other_video in videos:

                    new_ssi, _ = get_max_ssi(image_1, other_video, skip=5)
                    if new_ssi > max_ssi:
                        max_ssi, matching_frame = get_max_ssi(image_1, other_video)
                        matching_video = other_video
                        matching_video.set_in_and_out_frame(matching_frame, SECONDS_PER_CLIP)

                    pbar.set_description(
                        f"{current_video.vid_id} x {other_video.vid_id}"
                    )
                    pbar.update(1)
        
        connections.append(matching_video)

        current_video = videos.pop(videos.index(matching_video))

    return connections

def get_max_ssi(image_1, video, skip=1):
    max_ssi = -1.0

    for frame in range(0, video.frame_count, skip):
        with Image.open(video.get_frame_path(frame)) as image_2:
            ssi = compare_ssim(image_1, image_2)
            if ssi > max_ssi:
                max_ssi = ssi
                matching_frame = frame
    return max_ssi, matching_frame

def stitch_video_together(connections, seconds_per_clip):
    clips = []
    for video in connections:
        if video.is_reversed:
            start = video.out_frame / video.fps
            print(video.fps)
            clip = (
                VideoFileClip(str(video.path), audio=False, target_resolution=(480, 720))
                .subclip(start, start + seconds_per_clip)
                .fx(vfx.time_mirror)
                .set_fps(25)
            )
        else:
            start = video.in_frame / video.fps
            clip = (
                VideoFileClip(str(video.path), audio=False, target_resolution=(480, 720))
                .subclip(start, start + seconds_per_clip)
                .set_fps(25)
            )
        clips.append(clip)
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(f"test_{time.strftime(r'%H:%M')}.mp4")


if __name__ == "__main__":

    videos = [Video(path) for path in glob(str(root_dir() / "videos" / "*.mp4"))]
    connections = find_connections(videos, NUM_CONNECTIONS, SECONDS_PER_CLIP)

    # conn = {"_o76YUyNl0s":45,
    #         "ooIONZJ8VWA":1950,
    #         "DP-JWjAIYK8":3911,
    #         "cO5snUzoVv0":3055,
    #         "HP7iIKcMLvo":2234,
    #         "8kFEZ3q1Uvo":3531,
    #         "5qxWdN5kFOI":42,
    #         "Nk33m_oJuPg":1436,
    #         "yclx0NnvdBU":1625,
    #         "MapXib82Mtc":2509,}
    # connections = []
    # for key, value in conn.items():
    #     video = Video(f"videos/{key}.mp4")
    #     video.set_in_and_out_frame(value, SECONDS_PER_CLIP)
    #     print(video.is_reversed)
    #     connections.append(video)

    for connection in connections:
        print(connection.vid_id)
        print(connection.in_frame)

    stitch_video_together(connections, SECONDS_PER_CLIP)




