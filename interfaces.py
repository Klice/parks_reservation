from abc import ABCMeta, abstractmethod


class NotificationService:
    __metaclass__ = ABCMeta

    @abstractmethod
    def send_notification(self, msg: str):
        pass
