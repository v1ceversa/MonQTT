from threading import Semaphore

class Schedule:
    default_video = 'test.mp4'

    def __init__(self, landing={'step': 300, 'videos': [{'link': default_video, 'start': 1, 'end': 288}]}):
        self.landing = landing
        self.semaphore = Semaphore(len(landing['videos']))

    def get_landing(self):
        return self.landing

    def set_landing(self, landing):
        self.landing = landing
        self.semaphore = Semaphore(len(landing['videos']))
