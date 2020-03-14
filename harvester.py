from pathlib import Path
import requests
import re
from pytube import YouTube

def download_into_folder(video_id, dir):
    try:
        yt = YouTube(f"https://youtu.be/{video_id}")
        stream = yt.streams.first()
        if(stream.filesize_approx < 1e7):
            print(f"\n downloading {video_id}")
            stream.download(dir, filename=video_id)
        else:
            print(f"skipping {video_id}, file: {stream.filesize_approx/1e7}MB")
        del yt
    except Exception as e:
        print(e)

def get_video_ids(query):
    results_page_src = requests.get(f"https://www.youtube.com/results?search_query={query}").text
    video_ids = re.findall(r"https://i.ytimg.com/vi/(.{11})/hqdefault.jpg\?sqp=-", results_page_src)
    print(f"video ids for {query}")
    for video_id in video_ids:
        print(f"\t{video_id}")
    return video_ids

if __name__ == '__main__':
    videos_dir = Path(__file__).parent / 'videos'

    queries = [f"MOV{n:05d}" for n in range(9,10)]

    for query in queries:
        video_ids = get_video_ids(query)
        for video_id in video_ids:
            download_into_folder(video_id, videos_dir)
