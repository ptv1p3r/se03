from flask import Blueprint, jsonify
import csv
from pathlib import Path
from haversine import haversine, Unit
import xlsxwriter
import datetime
from config import *

se = Blueprint('se', __name__, template_folder='templates')


@se.route("/se", methods=["GET"])
def get_points():

    # importa dados
    serializedData = importData(IMPORT_FILE)

    # processa informacao
    serializedData, total_distance, total_time = processData(serializedData)

    # exporta dados para excel
    exportXLS(serializedData, total_distance, total_time)

    if len(serializedData) > 0:
        return jsonify({'ok': True, 'data': serializedData, "count": len(serializedData), "total distance": total_distance, "total time": total_time}), 200
    else:
        return jsonify({'ok': False, 'message': 'No points found'}), 400


# process all data
def processData(dataGroup):
    pos = 0
    next_row = None
    total_distance = 0.0
    total_time = 0.0
    distance_mt = 0.0

    for row in dataGroup:
        # calculo de tempo entre pontos
        if row["Time (Sec)"] is None:
            p1_timestamp = datetime.datetime.strptime(row["Date"] + ' ' + row["Time"], '%Y-%m-%d %H:%M:%S')

            # calcula linha de dados seguinte
            if pos + 1 <= len(dataGroup) - 1:
                next_row = dataGroup[pos + 1]

            # calcula dados da linha seguinte
            if next_row is not None:
                p2_timestamp = datetime.datetime.strptime(next_row["Date"] + ' ' + next_row["Time"],
                                                          '%Y-%m-%d %H:%M:%S')
                row["Time (Sec)"] = (p2_timestamp - p1_timestamp).total_seconds()

        # calculo de distancia entre pontos
        if row["Distance (Km)"] is None:
            p1 = (float(row["Latitude"]), float(row["Longitude"]))

            # calcula linha de dados seguinte
            if pos + 1 <= len(dataGroup) - 1:
                next_row = dataGroup[pos + 1]

            # calcula dados da linha seguinte
            if next_row is not None:
                p2 = (float(next_row["Latitude"]), float(next_row["Longitude"]))
                row["Distance (Km)"] = round(haversine(p1, p2, unit=Unit.KILOMETERS), 2)
                row["Distance (Mt)"] = distance_mt = round(haversine(p1, p2, unit=Unit.METERS), 2)

        # calculo de velocidade de deslocação entre pontos
        if row["Vel. m/s"] is None:
            try:
                row["Vel. m/s"] = round(distance_mt / float(row["Time (Sec)"]), 2)
                row["Vel. km/h"] = round(float(row["Vel. m/s"]) * 3.6, 2)
            except:
                row["Vel. m/s"] = 0.0
                row["Vel. km/h"] = 0.0

        # calculo de modo de deslocação entre pontos
        if row["Mode"] is None:
            try:
                row["Mode"] = 'Stop'

                # regra guide Possible transportation modes are: walk, bike, bus, car, subway, train, airplane, boat, run and motorcycle
                if 0.1 <= float(row["Vel. km/h"]) <= 2.0:
                    row["Mode"] = 'Walk'

                # velocidade media de ser humano a andar 2-6 km
                if 2.0 <= float(row["Vel. km/h"]) <= 7.0:
                    row["Mode"] = 'Walk'

                # velocidade media de ser humano a correr 7-10 km
                if 7.0 <= float(row["Vel. km/h"]) <= 11.0:
                    row["Mode"] = 'Run'

                # velocidade media bicicleta 11-19 km
                if 11.0 <= float(row["Vel. km/h"]) <= 20.0:
                    row["Mode"] = 'Bike'

                # velocidade media carro https://en.wikipedia.org/wiki/Medium-speed_vehicle
                if 20.0 <= float(row["Vel. km/h"]) <= 72.9:
                    row["Mode"] = 'Car'

            except:
                row["Mode"] = 'na'

        pos += 1
        total_distance += row["Distance (Km)"]
        total_time += row["Time (Sec)"]

    return dataGroup, round(total_distance, 2), round(total_time, 2)


# import data from csv file
def importData(fileToImport):
    processedData = []
    path = Path(__file__).parent.parent.joinpath(fileToImport)
    with open(path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, fieldnames=("Latitude", "Longitude", "Nr", "Altitude", "DateFrom", "Date", "Time", "Distance (Km)", "Distance (Mt)", "Time (Sec)", "Vel. m/s", "Vel. km/h", "Mode"))
        line_count = 0
        for row in csv_reader:
            if line_count >= 6:

                # Remover os valores negativos da altitude
                a1 = float(row["Altitude"])
                if a1 <= 0:
                    row['Altitude'] = -777

                processedData.append(row)
            line_count += 1
    return processedData


# export data to excel file
def exportXLS(dataGroup, total_distance, total_time):

    workbook = xlsxwriter.Workbook(EXPORT_FILE)
    worksheet = workbook.add_worksheet('Data')
    header_format = workbook.add_format({'bold': True, 'font_color': 'black'})

    worksheet.set_column(2, 0, 25)
    worksheet.write(2, 0, 'Total distance(mt)', header_format)
    worksheet.write(2, 1, total_distance)
    worksheet.set_column(3, 0, 10)
    worksheet.write(3, 0, 'Total time(s)', header_format)
    worksheet.write(3, 1, total_time)
    worksheet.write(3, 2, 'Delta', header_format)
    worksheet.write(3, 3, str(datetime.timedelta(seconds=total_time)))

    line_number = 5
    # headers
    # worksheet.set_column(line_number, 0, 10)
    worksheet.write(line_number, 0, 'Latitude', header_format)
    worksheet.write(line_number, 1, 'Longitude', header_format)
    worksheet.write(line_number, 2, 'Nr', header_format)
    worksheet.write(line_number, 3, 'Altitude', header_format)
    worksheet.set_column(line_number, 4, 10)
    worksheet.write(line_number, 4, 'Date', header_format)
    worksheet.set_column(line_number, 5, 10)
    worksheet.write(line_number, 5, 'Time', header_format)
    worksheet.set_column(line_number, 6, 40)
    worksheet.write(line_number, 6, 'Distance (Km)', header_format)
    worksheet.set_column(line_number, 7, 40)
    worksheet.write(line_number, 7, 'Distance (Mt)', header_format)
    worksheet.set_column(line_number, 8, 10)
    worksheet.write(line_number, 8, 'Time (Sec)', header_format)
    worksheet.write(line_number, 9, 'Vel. m/s', header_format)
    worksheet.write(line_number, 10, 'Vel. km/h', header_format)
    worksheet.write(line_number, 11, 'Mode', header_format)
    line_number += 1

    # lines
    for row in dataGroup:
        worksheet.write(line_number, 0, row["Latitude"])
        worksheet.write(line_number, 1, row["Longitude"])
        worksheet.write(line_number, 2, row["Nr"])
        worksheet.write(line_number, 3, row["Altitude"])
        worksheet.write(line_number, 4, row["Date"])
        worksheet.write(line_number, 5, row["Time"])
        worksheet.write(line_number, 6, row["Distance (Km)"])
        worksheet.write(line_number, 7, row["Distance (Mt)"])
        worksheet.write(line_number, 8, row["Time (Sec)"])
        worksheet.write(line_number, 9, row["Vel. m/s"])
        worksheet.write(line_number, 10, row["Vel. km/h"])
        worksheet.write(line_number, 11, row["Mode"])
        line_number += 1

    workbook.close()
