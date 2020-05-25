import os
import psutil
import datetime
import paramiko
from threading import Thread

download_path = '/home/v1ceversa/Videos/'
host='127.0.0.1'

class DownloadVerbose:
    def __init__(self):
        self.prev_downloaded = 0
        self.prev_time = datetime.datetime.now()

    def __call__(self, downloaded, total):
        percent = 100.0 * (downloaded / total)
        time = datetime.datetime.now()
        speed_bps = (downloaded - self.prev_downloaded) / (time - self.prev_time).total_seconds()
        speed_mbps = speed_bps / 2 ** 17
        print('Transferred: {0:3.2f}%, {1:3.2f} Mbps'.format(percent, speed_mbps), end='\r')
        self.prev_downloaded = downloaded
        self.prev_time = time


class DownloadManager(Thread):

    def __init__(self, schedule, init_point=0):
        Thread.__init__(self)
        # SFTP server connection
        if not os.path.exists(download_path):
            os.mkdir(download_path)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username='v1ceversa', password='an000829')
        self.sftp = ssh.open_sftp()
        self.is_interrupted = False
        self.schedule = schedule
        self.init_point = init_point

    def interrupt(self):
        self.is_interrupted = True

    def free_disk_space(self,point = 0):
        downloaded_files = os.walk(download_path)[0][3]
        videos = self.schedule.get_landing()['videos']
        rest_videos = reversed([video['link'] for video in videos[point+1:len(videos)]])
        for file in downloaded_files:
            if file not in rest_videos:
                 os.remove(download_path + '/' + file)

    def run(self):
        self.is_interrupted = False
        landing = self.schedule.get_landing()
        for i in range(self.init_point, len(landing)):
            if self.is_interrupted:
                return
            if os.path.isfile(download_path + landing[i]['link']):
                disk_info = psutil.disk_usage('/')
                free_ration = disk_info.free/disk_info.total
                sftp_size = self.sftp.stat('/' + landing[i]['link']).st_size
                if free_ration < 0.05 or free_ration <= sftp_size:
                    self.free_disk_space(i)
                file_size = os.stat(download_path + landing[i]['link']).st_size
                if file_size == sftp_size:
                    self.schedule.release()     # file already downloaded
                    continue
            print(f"Download video {landing[i]['link']}")
            self.sftp.get('/' + landing[i]['link'], DownloadManager.download_path + landing[i]['link'], callback=DownloadVerbose())
            self.schedule.release()
