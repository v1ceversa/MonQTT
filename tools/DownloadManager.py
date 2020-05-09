import os
import datetime
import paramiko
from threading import Thread

download_path = '/home/v1ceversa/Videos/'


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

    def __init__(self, host, schedule):
        # SFTP server connection
        if not os.path.exists(download_path):
            os.mkdir(download_path)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username='pi', password='cntgfyrbpbv')
        self.sftp = ssh.open_sftp()
        self.is_interrupted = False
        self.schedule = schedule

    def interrupt(self):
        self.is_interrupted = True

    def run(self):
        self.is_interrupted = False
        landing = self.schedule.get_landing()
        for video in landing:
            if self.is_interrupted:
                return
            if os.path.isfile(download_path + video['link']):
                sftp_size = self.sftp.stat('/' + video['link']).st_size
                file_size = os.stat(download_path + video['link']).st_size
                if file_size == sftp_size:
                    self.schedule.release()     # file already downloaded
                    continue
            print(f"Download video {video['link']}")
            self.sftp.get('/' + video['link'], DownloadManager.download_path + video['link'], callback=DownloadVerbose())
            self.schedule.release()
