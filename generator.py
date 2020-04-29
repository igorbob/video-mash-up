from collections import OrderedDict
from random import shuffle
from math import floor
import os.path
from glob import glob
from pathlib import Path
import math
import pandas as pd
import json
from cv2 import cv2
from SSIM_PIL import compare_ssim
from PIL import Image
from tqdm import tqdm
from moviepy.editor import VideoFileClip, concatenate_videoclips


def root_dir():
    return Path(__file__).parent


def unpack_frames(new_size):
    video_paths = glob(str(root_dir() / "videos" / "*.mp4"))
    # frame_rates = json.load

    # with open('frame_rates.txt') as json_file:
    #     frame_rates = json.load(json_file)

    frame_rates = {}

    with tqdm(total=len(video_paths)) as pbar:
        for video in video_paths:
            video_id_mp4 = os.path.basename(video)
            video_id = os.path.splitext(video_id_mp4)[0]
            video_frames_folder = root_dir() / "frames" / video_id

            if not video_frames_folder.exists():
                video_frames_folder.mkdir()
                cap = cv2.VideoCapture(video)

                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_rates[video_id] = fps
                while cap.isOpened():
                    frameId = cap.get(1)  # current frame number
                    retrival, frame = cap.read()
                    if not retrival:
                        break
                    if new_size:
                        frame = cv2.resize(frame, new_size)
                    filename = str(video_frames_folder / f"{int(frameId)}.png")
                    cv2.imwrite(filename, frame)
                cap.release()
            pbar.set_description(f"Unpacking {video_id}")
            pbar.update(1)
    return frame_rates


def get_framerates():
    video_paths = glob(str(root_dir() / "videos" / "*.mp4"))

    frame_rates = {}
    with tqdm(total=len(video_paths)) as pbar:
        for video in video_paths:
            video_id_mp4 = os.path.basename(video)
            video_id = os.path.splitext(video_id_mp4)[0]
            cap = cv2.VideoCapture(video)
            frame_rates[video_id] = cap.get(cv2.CAP_PROP_FPS)
            pbar.update(1)
    return frame_rates


def make_connections(frame_rates, num_connections, seconds_per_clip):
    video_filenames = [
        os.path.basename(video) for video in glob(str(root_dir() / "videos" / "*.mp4"))
    ]
    video_ids = [
        os.path.splitext(video_filename)[0] for video_filename in video_filenames
    ]
    shuffle(video_ids)

    current_video_id = video_ids.pop()
    starting_frame = 1
    fps = frame_rates[current_video_id]

    connections = OrderedDict()
    connections[current_video_id] = starting_frame
    for _ in range(num_connections):
        frames = glob(str(root_dir() / "frames" / current_video_id / "*.jpg"))

        max_ssi = 0.0

        with Image.open(frames[starting_frame + (seconds_per_clip * fps)]) as image_1:
            with tqdm(total=len(video_ids)) as pbar:
                for other_video_id in video_ids:
                    other_frames = glob(
                        str(root_dir() / "frames" / other_video_id / "*.jpg")
                    )
                    new_ssi, _ = get_max_ssi(
                        image_1, other_frames[: -(seconds_per_clip * fps)], 5
                    )
                    if new_ssi > max_ssi:
                        new_ssi, matching_frame = get_max_ssi(
                            image_1, other_frames[: -(seconds_per_clip * fps)]
                        )
                        max_ssi = new_ssi
                        matching_video_id = other_video_id
                    pbar.set_description(
                        f"Comparing {current_video_id} to {other_video_id}"
                    )
                    pbar.update(1)

        connections[matching_video_id] = matching_frame

        current_video_id = matching_video_id
        video_ids.remove(current_video_id)
        starting_frame = matching_frame
        fps = frame_rates[current_video_id]

    return connections


def get_max_ssi(image_1, other_frames, grain=1):
    max_ssi = 0.0

    for other_frame in other_frames[::grain]:
        with Image.open(other_frame) as image_2:
            ssi = compare_ssim(image_1, image_2)
            if ssi > max_ssi:
                max_ssi = ssi
                matching_frame = other_frame
    return max_ssi, matching_frame


def stitch_video_together(frame_rates, connections, seconds_per_clip):
    clips = []
    for video_id, starting_frame in connections.items():
        start = starting_frame / frame_rates[video_id]
        video_path = Path(__file__).parent / "videos" / f"{video_id}.mp4"
        clip = (
            VideoFileClip(str(video_path), audio=False, target_resolution=(480, 720))
            .subclip(start, start + seconds_per_clip)
            .set_fps(25)
        )
        clips.append(clip)
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile("my_concatenation.mp4")


if __name__ == "__main__":
    seconds_per_clip = 2
    num_connections = 30

    # frame_rates = unpack_frames(new_size=(64, 64))

    connections = make_connections(frame_rates, num_connections, seconds_per_clip)
    stitch_video_together(frame_rates, connections, seconds_per_clip)
