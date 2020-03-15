

SECONDS_PER_CLIP = 2

from random import shuffle
from math import floor
import os.path
from glob import glob
from pathlib import Path
import math
import pandas as pd
from cv2 import cv2
from SSIM_PIL import compare_ssim
from PIL import Image
from tqdm import tqdm

def unpack_frames():
    project_dir = Path(__file__).parent
    video_paths = glob(str(project_dir / 'videos' / '*.mp4'))
    for video in video_paths:
        video_id_mp4 = os.path.basename(video)
        video_id = os.path.splitext(video_id_mp4)[0]
        video_frames_folder = project_dir / 'frames' / video_id

        if video_frames_folder.exists():
            print(f"{video_id} already extracted")
        else:
            video_frames_folder.mkdir()
            cap = cv2.VideoCapture(video)
            frame_rate = cap.get(5)
            while(cap.isOpened()):
                frameId = cap.get(1) #current frame number
                retrival, frame = cap.read()
                if not retrival:
                    break
                if (frameId % math.floor(frame_rate*4) == 0):
                    filename = str(video_frames_folder / f'{int(frameId)}.jpg')
                    print(filename)
                    cv2.imwrite(filename, frame)
            cap.release()
            print ("Done!")

def resize_all():
    project_dir = Path(__file__).parent
    video_filenames = [os.path.basename(video) for video in glob(str(project_dir / 'videos' / '*.mp4'))]
    video_ids = [os.path.splitext(video_filename)[0] for video_filename in video_filenames]

    with tqdm(total=len(video_ids)) as pbar:
        for video_id in video_ids:
            frames = glob(str(project_dir / 'frames' / video_id / '*.jpg'))
            for frame in frames:
                image = Image.open(frame).resize((128,128))
                image.save(frame)
            pbar.set_description(f"Processing {video_id}")
            pbar.update(1)
    
def make_connections():
    project_dir = Path(__file__).parent
    video_filenames = [os.path.basename(video) for video in glob(str(project_dir / 'videos' / '*.mp4'))]
    video_ids = [os.path.splitext(video_filename)[0] for video_filename in video_filenames]
    shuffle(video_ids)

    connections = {}

    for i in range(20):
        video_id = video_ids.pop()
        frames = glob(str(project_dir / 'frames' / video_id / '*.jpg'))

        two_thirds = floor(len(frames) * 0.6)
        frame_two_thirds = frames[two_thirds]

        image_1 = Image.open(frame_two_thirds)

        max_ssi = 0.0
        max_meta = ('','')
        with tqdm(total=len(video_ids)) as pbar:
            for other_video_id in video_ids:
                other_frames = glob(str(project_dir / 'frames' / other_video_id / '*.jpg'))
                new_ssi, _ = get_max_ssi(image_1, other_frames, 7)
                if new_ssi > max_ssi:
                    new_ssi, new_frame = get_max_ssi(image_1, other_frames)
                    max_ssi = new_ssi
                    matching_video_id = other_video_id
                    matching_frame = new_frame
                pbar.set_description(f"Comparing {video_id} to {other_video_id}")
                pbar.update(1)

        connections[video_id] = {
            "frame_nr": two_thirds,
            "max_ssi": max_ssi,
            "matching_video_id": matching_video_id,
            "matching_frame": matching_frame,
        }
        print(connections)


def get_max_ssi(image_1, other_frames, grain=1):
    max_ssi = 0.0
    max_frame = ""
    for other_frame in other_frames[::grain]:
        image_2 = Image.open(other_frame)
        ssi = compare_ssim(image_1, image_2)
        if ssi > max_ssi:
            max_ssi = ssi
            max_frame = other_frame
    return max_ssi, max_frame


if __name__ == '__main__':
    #unpack_frames()
    #resize_all()
    make_connections()
