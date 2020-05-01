from threading import Thread, Event, Semaphore
from . import DownloadManager
import cv2
import time

default_video = 'test.mp4'

class MediaPlayer(Thread):

    def __init__(self, schedule, new_schedule_event):
        self.new_schedule_event = new_schedule_event
        self.schedule = schedule
        self.download_manager = DownloadManager(self.schedule)

    def run(self):
        self.download_manager.start()
        amount_of_videos = len(self.videos)
        point = 0
        while True:
            slot = time.time()%300+1
            if self.new_schedule_event.is_set():
                self.download_mamnager.join()
                self.download_manager.start()
                schedule = self.schedule.get_schedule()
                self.videos = schedule['videos']
                self.step = schedule['step']

            for i in range(point,len(self.videos)):
                video = self.videos[i]
                if slot in range(video['start'], video['end'] + 1):
                    if slot > self.videos[point]['end']:
                        point += 1
                    file_name = video['link']
                elif slot > video['end']:
                    file_name = default_video
                    break

            cap = cv2.VideoCapture(self.download_path + file_name)
            # play video
            while (True):
                # Capture frame-by-frame
                ret, frame = cap.read()

                # Display the resulting frame
                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()
        self.download_manager.join()





