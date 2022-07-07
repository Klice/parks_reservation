from flask import Flask, make_response, jsonify
from flask_cors import CORS

from reservations_api import OntarioReservations

api = Flask(__name__)
park = OntarioReservations()
CORS(api)


@api.route('/', methods=['GET'])
def get_available_parks():
    return make_response(jsonify(park.get_avail()), 200)


if __name__ == "__main__":
    api.run(host="0.0.0.0", port=8111)
