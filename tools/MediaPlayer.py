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
        self.download_path = '/home/pi/Videos/'

    def __get_init_point(self, slot):
        landing = self.schedule.get_landing()
        videos = landing['videos']
        for i in range(len(videos)):
            if slot <= videos[i]['end']:
                return i
        return len(videos) - 1

    @staticmethod
    def __is_slot_in_point(slot, point_video):
        return slot in range(point_video['start'], point_video['end'] + 1)

    @staticmethod
    def __get_point(videos, slot, cur_point=0):
        if slot > videos[cur_point]['end'] and cur_point != len(videos) - 1:
            cur_point += 1
        return cur_point

    @staticmethod
    def __get_file_name(slot, point_video):
        if MediaPlayer.is_slot_in_point(slot=slot, point_video=point_video):
            return point_video['link']
        else:
            return default_video

    def run(self):
        def play_video():
            global stop
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

        self.download_manager.start()
        landing = self.schedule.get_landing()
        prev_file_name = default_video
        file_name = default_video
        slot = time.time() % landing['step'] + 1
        point = self.get_init_point(slot)

        while True:
            if self.new_schedule_event.is_set():
                self.new_schedule_event.clear()
                self.download_manager.interrupt()
                self.download_manager.join()
                self.download_manager.start()

            videos = landing['videos']
            file_name = MediaPlayer.get_file_name(slot=slot, point_video=videos[point])
            if prev_file_name != file_name:
                Thread.start(target=play_video)
            prev_file_name = file_name

            landing = self.schedule.get_landing()
            slot = time.time() % landing['step'] + 1
            point = MediaPlayer.get_point(slot)

        self.download_manager.join()





