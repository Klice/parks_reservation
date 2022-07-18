from typing import List
from interfaces import NotificationService
from reservations_api import ReservationPark, ReservationWeekend


class Notifications:

    prev_notifications = None
    cur_notifications = None

    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def send_notification(self, msg):
        if msg:
            self.notification_service.send_notification(msg)

    def send_available_parks(self, results: List[ReservationWeekend]):
        self.cur_notifications = []
        msg = self._build_weekends_notification(results)
        self.send_notification(msg)
        self.prev_notifications = self.cur_notifications

    def _build_weekends_notification(self, weekends: List[ReservationWeekend]):
        return ''.join([self._build_weekend_notification(w) for w in weekends])

    def _build_weekend_notification(self, weekend: ReservationWeekend):
        msg = ''.join([self._build_park_notification(p)
                      for p in weekend.parks])
        return self._format_parks_msg(weekend.start_date, msg)

    def _build_park_notification(self, park: ReservationPark):
        msg = ''
        for c in park.campgrounds:
            if not self._is_reported_last_time(c.key):
                msg += self._format_campground_msg(c.name, c.url)
        return self._format_campgrounds_msg(park.name, msg)

    def _is_reported_last_time(self, key):
        self.cur_notifications.append(key)
        return self.prev_notifications and key in self.prev_notifications

    def _format_parks_msg(self, start_date, parks):
        if parks:
            return f"*📅 {start_date}*\n{parks}\n\n"
        return ''

    def _format_campgrounds_msg(self, park_name, campgrounds):
        if campgrounds:
            return f"{park_name}{campgrounds}"
        return ''

    def _format_campground_msg(self, campground_name, url):
        return f"\n- [{campground_name}]({url})"
