
#%%


# if __name__ == '__main__':
#     project_dir = Path(__file__).parent
#     videos = glob(str(project_dir / 'videos' / '*.mp4'))
    # for i, video in enumerate(videos):
    #     cap = cv2.VideoCapture(video)
    #     frameRate = cap.get(5)
    #     while(cap.isOpened()):
    #         frameId = cap.get(1) #current frame number
    #         retrival, frame = cap.read()
    #         if not retrival:
    #             break
    #         if (frameId % math.floor(frameRate*4) == 0):
    #             filename = str(project_dir / 'frames' / f'{i}_{int(frameId)}.jpg')
    #             print(filename)
    #             cv2.imwrite(filename, frame)
    #     cap.release()
    #     print ("Done!")

#%%
project_dir = Path(__file__).parent
comparisons = {}


frame_1 = Image.open('/Volumes/HDD/ytrip/frames/1_2040.jpg').resize((128,128))
display(frame_1)

for i in range(2,24):
    print(i, end=" ")
    frames_2 = glob(str(project_dir / 'frames' / f'{i}_*.jpg'))
    for frame in frames_2:
        frame_2 = Image.open(frame).resize((128,128))
        value = compare_ssim(frame_1, frame_2)
        comparisons[frame] = value

min_value = min(comparisons.values())
result = [key for key, value in comparisons.items() if value == min_value]
final_frame = Image.open(result[0]).resize((128,128))
#%%


# %%
