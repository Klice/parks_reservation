import argparse
import logging
import sys
import time
from flask import Flask, make_response, jsonify
from flask_cors import CORS

from reservations_api import OntarioReservations
from telegram import TelegramNotifications

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def send_notification(results):
    msg = ""
    for w in results:
        if len(w["parks"]) == 0:
            continue
        msg += f"*📅 {w['start_date']}*\n"
        for p in w["parks"]:
            msg += f"{p['name']}"
            for c in p["campgrounds"]:
                msg += f"\n- [{c['name']}]({c['url']})"
            msg += "\n\n"
    if msg:
        TelegramNotifications.send_notification(msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['api', 'standalone'], required=True)
    parser.add_argument('--weeks', type=int, default=2)
    args = parser.parse_args()
    park = OntarioReservations(args.weeks)
    if args.mode == "api":
        api = Flask(__name__)
        CORS(api)

        @api.route('/', methods=['GET'])
        def get_available_parks():
            res = park.get_avail()
            return make_response(jsonify(res), 200)

        api.run(host="0.0.0.0", port=8111)
    if args.mode == "standalone":
        while True:
            try:
                send_notification(park.get_avail())
            except Exception as e:
                TelegramNotifications.send_notification(f"❌ Oops! {e.__class__} occurred: {e}")
                break
            time.sleep(60)
