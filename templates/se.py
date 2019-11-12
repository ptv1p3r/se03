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
    exportXLS(serializedData)

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
                if 0.0 <= float(row["Vel. km/h"]) <= 1.9:
                    row["Mode"] = 'Walk'

                # velocidade media de ser humano a andar 2-6 km
                if 2.0 <= float(row["Vel. km/h"]) <= 6.9:
                    row["Mode"] = 'Walk'

                # velocidade media de ser humano a correr 7-10 km
                if 7.0 <= float(row["Vel. km/h"]) <= 10.9:
                    row["Mode"] = 'Run'

                # velocidade media bicicleta 11-19 km
                if 11.0 <= float(row["Vel. km/h"]) <= 19.9:
                    row["Mode"] = 'Bike'

                # velocidade media carro https://en.wikipedia.org/wiki/Medium-speed_vehicle
                if 20.0 <= float(row["Vel. km/h"]) <= 72.9:
                    row["Mode"] = 'Car'

            except:
                row["Mode"] = 'na'

        pos += 1
        total_distance += row["Distance (Km)"]
        total_time += row["Time (Sec)"]

    return dataGroup, total_distance, total_time


# import data from csv file
def importData(fileToImport):
    processedData = []
    path = Path(__file__).parent.parent.joinpath(fileToImport)
    with open(path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, fieldnames=("Latitude", "Longitude", "Nr", "Altitude", "DateFrom", "Date", "Time", "Distance (Km)", "Distance (Mt)", "Time (Sec)", "Vel. m/s", "Vel. km/h", "Mode"))
        line_count = 0
        for row in csv_reader:
            # if line_count == 0:
            #     print(f'\t{" ".join(row)}')

            if line_count >= 6:
                # print(f'\t{row["Latitude"]}\t{row["Longitude"]}\t{row["Nr"]}\t{row["Altitude"]}\t{row["DateFrom"]}\t{row["Date"]}\t{row["Time"]}')

                # Remover os valores negativos da altitude
                a1 = float(row["Altitude"])
                if a1 <= 0:
                    row['Altitude'] = -777

                print(f'\t{row["Altitude"]}')

                processedData.append(row)
            line_count += 1
        # print(f'Processadas {line_count} linhas.')
    return processedData


# export data to excel file
def exportXLS(dataGroup):
    workbook = xlsxwriter.Workbook(EXPORT_FILE)
    worksheet = workbook.add_worksheet('Data')

    # headers
    worksheet.write('A1', 'Latitude')
    worksheet.write('B1', 'Longitude')
    worksheet.write('C1', 'Nr')
    worksheet.write('D1', 'Altitude')
    worksheet.write('E1', 'Date')
    worksheet.write('F1', 'Time')
    worksheet.write('G1', 'Distance (Km)')
    worksheet.write('H1', 'Distance (Mt)')
    worksheet.write('I1', 'Time (Sec)')

    # lines
    line_number = 5
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
        line_number += 1

    workbook.close()
