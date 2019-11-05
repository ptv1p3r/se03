from flask import Blueprint
import csv
from pathlib import Path
from math import radians, cos, sin, asin, sqrt
from haversine import haversine, Unit

se = Blueprint('se', __name__, template_folder='templates')


@se.route("/se", methods=["GET"])
def get_points():
    serializedData = []
    path = Path(__file__).parent.parent.joinpath('20081026094426.csv')
    with open(path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, fieldnames=("Latitude", "Longitude", "Nr", "Altitude", "DateFrom", "Date", "Time"))
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'\t{" ".join(row)}')
            if line_count >= 6:
                print(f'\t{row["Latitude"]}\t{row["Longitude"]}\t{row["Nr"]}\t{row["Altitude"]}\t{row["DateFrom"]}\t{row["Date"]}\t{row["Time"]}')
                tt = haversine2(116.326982, 40.000595, 116.326983, 40.000595)
                p1 = (40.000595, 116.326982)
                p2 = (40.000595, 116.326983)
                tt2 = haversine(p1,p2)
                print(tt)
                serializedData.append(row)
            line_count += 1
        print(f'Processadas {line_count} linhas.')

    if line_count > 0:
        return jsonify({'ok': True, 'data': serializedData, "count": line_count}), 200
    else:
        return jsonify({'ok': False, 'message': 'No points found'}), 400


def haversine2(lng1, lat1, lng2, lat2):
    # converte decimal graus para radians
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])

    # haversine formula
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # radius da terra em km

    return c * r

