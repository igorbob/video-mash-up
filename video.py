from PIL import Image
import os.path
from glob import glob
from pathlib import Path
from cv2 import cv2


class Video:
    _vid_id = None
    _fps = None
    _path = None
    _frame_count = None
    _frames_path = None
    _in_frame = None
    _out_frame = None

    def __init__(self, file_path, fps=None):
        self.file_path = file_path
        self.is_reversed = False
        self.frame_size = (64, 64)

    def __repr__(self):
        return f"< video : {self.vid_id} [fps: {self.fps}; frame_count: {self.frame_count}] >"

    def __len__(self):
        return self._frame_count

    def __eq__(self, other):
        if isinstance(other, Video):
            return self.vid_id == other.vid_id
        if not isinstance(other, str):
            raise TypeError("compare with str")
        if other == self.vid_id:
            return True
        return False

    @property
    def vid_id(self):
        if self._vid_id is None:
            video_id_mp4 = os.path.basename(self.file_path)
            self._vid_id = os.path.splitext(video_id_mp4)[0]
        return self._vid_id

    @property
    def fps(self):
        if self._fps is None:
            cap = cv2.VideoCapture(self.file_path)
            self._fps = cap.get(cv2.CAP_PROP_FPS)
        return self._fps

    @property
    def frame_count(self):
        if self._frame_count is None:
            self._frame_count = len(glob(str(self.frames_path / "*.png")))
        return self._frame_count

    @property
    def path(self):
        if self._path is None:
            self._path = Path(__file__).parent / "videos" / f"{self.vid_id}.mp4"
        return self._path

    @property
    def frames_path(self):
        if self._frames_path is None:
            self._frames_path = Path(__file__).parent / "frames" / self.vid_id
            if not self._frames_path.exists():
                self._frames_path.mkdir()
                self.unpack_frames()
        return self._frames_path
    
    @property
    def in_frame(self):
        return self._in_frame

    @property
    def out_frame(self):
        return self._out_frame
    
    def set_in_and_out_frame(self, in_frame_nr, seconds):
        self._in_frame = in_frame_nr
        frame_count = int(self.fps * seconds)
        
        if self._in_frame + frame_count > self.frame_count:
            self.is_reversed = True
            self._out_frame = self._in_frame - frame_count
        else:
            self._out_frame = self._in_frame + frame_count

    def get_frame_path(self, frame_nr):
        if frame_nr >= self.frame_count:
            print("error handling! frame_nr > frame_count")
            return self.frames_path / f"{self.frame_count}.png"
        return self.frames_path / f"{frame_nr}.png"

    def unpack_frames(self):
        cap = cv2.VideoCapture(self.file_path)

        while cap.isOpened():
            frame_id = cap.get(1)  # current frame number
            retrival, frame = cap.read()
            if retrival:
                frame = cv2.resize(frame, self.frame_size)
                filename = str(self.frames_path / f"{int(frame_id)}.png")
                cv2.imwrite(filename, frame)
            else:
                break
        cap.release()