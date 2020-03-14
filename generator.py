

SECONDS_PER_CLIP = 2

import os.path
from glob import glob
from pathlib import Path
import math
import pandas as pd
import cv2
from SSIM_PIL import compare_ssim
from IPython.display import Image
from cv2 import VideoCapture, imwrite

if __name__ == '__main__':
    project_dir = Path(__file__).parent
    video_paths = glob(str(project_dir / 'videos' / '*.mp4'))
    video_ids = [os.path.splitext(path)[0] for path in video_paths]
    for i, video in enumerate(video_paths):
        cap = VideoCapture(video)
        frame_rate = cap.get(5)
        while(cap.isOpened()):
            frameId = cap.get(1) #current frame number
            retrival, frame = cap.read()
            if not retrival:
                break
            if (frameId % math.floor(frame_rate*4) == 0):
                filename = str(project_dir / 'frames' / f'{i}_{int(frameId)}.jpg')
                print(filename)
                imwrite(filename, frame)
        cap.release()
        print ("Done!")