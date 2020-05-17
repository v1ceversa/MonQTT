from threading import Thread
from .DownloadManager import DownloadManager
import time
import cv2

default_video = 'test.mp4'
download_path = '/home/v1ceversa/Videos/'


class MediaPlayer(Thread):
    def __init__(self, file_name=default_video):
        Thread.__init__(self)
        self.file_name = file_name
        self.kill = False

    def interrupt(self):
        self.kill = True

    def run(self):
        self.kill = False
        cap = cv2.VideoCapture(download_path + self.file_name)
        # play video
        while (True):
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret:
                cv2.imshow("Image", frame)
            else:
                print('no video')
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            # Display the resulting frame
            #cv2.imshow('frame', frame)
            if (cv2.waitKey(1) & 0xFF == ord('q')) | self.kill:
                break
        cap.release()
        cv2.destroyAllWindows()


class TaskManager(Thread):

    def __init__(self, schedule):
        Thread.__init__(self)
        self.schedule = schedule

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
        if TaskManager.__is_slot_in_point(slot=slot, point_video=point_video):
            return point_video['link']
        else:
            return default_video

    def run(self):
        #download_manager = DownloadManager(schedule=self.schedule)
        #download_manager.start()
        landing = self.schedule.get_landing()
        prev_file_name = default_video
        slot = int(time.time() / landing['step']) + 1
        point = self.__get_init_point(slot)
        player = MediaPlayer()
        player.start()
        is_stand_by = True
        while True:
            if self.schedule.is_new_schedule():
                download_manager.interrupt()
                download_manager.join()
                download_manager = DownloadManager(schedule=self.schedule)
                download_manager.start()

                landing = self.schedule.get_landing()
                slot = int(time.time() / landing['step']) + 1
                point = self.get_init_point(slot)

                player.interrupt()
                player.join()
                player = MediaPlayer()
                player.start()

            file_name = TaskManager.__get_file_name(slot=slot, point_video=landing['videos'][point])

            if prev_file_name != file_name:
                is_acquire = self.schedule.acquire()

                if is_acquire:
                    is_stand_by = False
                    player.interrupt()
                    player.join()
                    player = MediaPlayer(file_name=file_name)
                    player.start()
                    prev_file_name = file_name
                elif not is_stand_by:
                    is_stand_by = True
                    player.interrupt()
                    player.join()
                    player = MediaPlayer()
                    player.start()

            slot = int(time.time() / landing['step']) + 1
            point = TaskManager.__get_point(slot=slot, cur_point=point)

        download_manager.interrupt()
        download_manager.join()





