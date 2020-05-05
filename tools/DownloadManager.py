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

    def __init__(self, host):
        # SFTP server connection
        if not os.path.exists(download_path):
            os.mkdir(download_path)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username='pi', password='cntgfyrbpbv')
        self.sftp = ssh.open_sftp()
        self.is_interrupted = False

    def interrupt(self):
        self.is_interrupted = True

    def run(self):
        self.is_interrupted = False
        while(True):
            if self.is_interrupted:
                break

    def download_file(self, file_name):
        if os.path.isfile(download_path + file_name):
            sftp_size = self.sftp.stat('/' + file_name).st_size
            file_size = os.stat(download_path + file_name).st_size
            if file_size == sftp_size:
                return  # file already downloaded

        print("Download video {0}".format(file_name))
        self.sftp.get('/' + file_name, DownloadManager.download_path + file_name, callback=DownloadVerbose())
