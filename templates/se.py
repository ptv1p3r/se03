from flask import Blueprint, jsonify
import csv
from pathlib import Path
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
                p1 = (40.000595, 116.326982)
                p2 = (40.000595, 116.326983)
                tt2 = haversine(p1,p2)
                serializedData.append(row)
            line_count += 1
        print(f'Processadas {line_count} linhas.')

    if line_count > 0:
        return jsonify({'ok': True, 'data': serializedData, "count": line_count}), 200
    else:
        return jsonify({'ok': False, 'message': 'No points found'}), 400

