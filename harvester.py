from pathlib import Path
import requests
import re
from pytube import YouTube

def download_into_folder(video_id, dir):
    try:
        yt = YouTube(f"https://youtu.be/{video_id}")
        stream = yt.streams.get_by_resolution("360p")
        if stream.filesize_approx > 0.2e6 and stream.filesize_approx < 9e6:
            print(f"\n downloading {video_id}")
            stream.download(dir, filename=video_id)``
        else:
            print(f"skipping {video_id}, file: {stream.filesize_approx/1e6}MB")
        del yt
    except Exception as e:
        print(e)


def get_video_ids(query):
    results_page_src = requests.get(
        f"https://www.youtube.com/results?search_query={query}"
    ).text
    video_ids = re.findall(
        r"https://i.ytimg.com/vi/(.{11})/hqdefault.jpg\?sqp=-", results_page_src
    )
    video_ids = list(set(video_ids))
    print(f"video ids for {query}")
    for video_id in video_ids:
        print(f"\t{video_id}")
    return video_ids[:10]


if __name__ == "__main__":
    videos_dir = Path(__file__).parent / "videos"

    queries = [f"MOV{n:05d}" for n in range(460, 512)]  # 1 - 46, 60 -99

    for query in queries:
        video_ids = get_video_ids(query)
        for video_id in video_ids:
            download_into_folder(video_id, videos_dir)
