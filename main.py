import argparse
import logging
import sys
import time
from flask import Flask, make_response, jsonify
from flask_cors import CORS
from notifications import Notifications

from reservations_api import OntarioReservations
from telegram import TelegramNotifications

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['api', 'standalone'], required=True)
    parser.add_argument('--weeks', type=int, default=2)
    parser.add_argument('--start-weekday', type=int, default=4)
    parser.add_argument('--nights', type=int, default=2)
    parser.add_argument('--weeks-from-now', type=int, default=0)
    parser.add_argument('--use-holidays', action=argparse.BooleanOptionalAction, default=True)

    args = parser.parse_args()
    park = OntarioReservations(
        args.weeks,
        args.start_weekday,
        args.nights,
        args.use_holidays,
        args.weeks_from_now
    )
    if args.mode == "api":
        api = Flask(__name__)
        CORS(api)

        @api.route('/', methods=['GET'])
        def get_available_parks():
            res = park.get_avail()
            return make_response(jsonify(res), 200)

        api.run(host="0.0.0.0", port=8111)
    if args.mode == "standalone":
        notifications = Notifications(TelegramNotifications)
        while True:
            try:
                notifications.send_available_parks(park.get_avail())
            except Exception as e:
                notifications.send_notification(f"❌ Oops! {e.__class__} occurred: {e}")
                raise e
            time.sleep(60)
