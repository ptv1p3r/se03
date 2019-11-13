from itertools import cycle

from flask import Blueprint, jsonify
import csv
from pathlib import Path
from haversine import haversine, Unit
import xlsxwriter
import datetime
from config import *
import re

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
        return jsonify(
            {'ok': True, 'data': serializedData, "count": len(serializedData), "total distance": total_distance,
             "total time": total_time}), 200
    else:
        return jsonify({'ok': False, 'message': 'No points found'}), 400


def myFunc(e):
    return e['Time (Sec)']


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
                if p2_timestamp > p1_timestamp:
                    row["Time (Sec)"] = (p2_timestamp - p1_timestamp).total_seconds()
                else:
                    row["Time (Sec)"] = (p1_timestamp - p2_timestamp).total_seconds()

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
                if 0.01 <= float(row["Vel. km/h"]) <= 2.0:
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

                # velocidade media aviao https://www.onaverage.co.uk/speed-averages/24-average-speed-of-a-plane
                if 200.0 <= float(row["Vel. km/h"]) <= 2000.0:
                    row["Mode"] = 'Airplane'
            except:
                row["Mode"] = 'na'

        pos += 1
        total_distance += row["Distance (Mt)"]
        total_time += row["Time (Sec)"]

    return dataGroup, round(total_distance, 2), round(total_time, 2)


# import data from csv file
def importData(fileToImport):
    processedData = []
    path = Path(__file__).parent.parent.joinpath(fileToImport)

    with open(path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, fieldnames=(
        "Latitude", "Longitude", "Nr", "Altitude", "DateFrom", "Date", "Time", "Distance (Km)", "Distance (Mt)",
        "Time (Sec)", "Vel. m/s", "Vel. km/h", "Mode"))
        line_count = 0
        start_line = 0

        index = IMPORT_FILE_INDEX.get(fileToImport, "Invalid index")
        if not index == 'Invalid index':
            start_line = index

        for row in csv_reader:
            if line_count >= start_line:

                itemsGroup = list(row.items())

                row['Latitude'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Latitude')][1] if IMPORT_FILE_HEADER_MAP.get(
                    'Latitude', None) is not None else None
                if row['Latitude'] is not None:
                    # ^(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,6})?))$ com indicador de polaridade inicial (latitude)
                    match = re.search(r'(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,6})?))$',
                                      row['Latitude'])
                    if match is None:
                        row['Latitude'] = None

                row['Longitude'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Longitude')][1] if IMPORT_FILE_HEADER_MAP.get(
                    'Longitude', None) is not None else None
                if row['Longitude'] is not None:
                    # ^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$ com indicador de polaridade inicial (longitude)
                    match = re.search(
                        r'(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$',
                        row['Longitude'])
                    if match is None:
                        row['Longitude'] = None

                row['Nr'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Nr')][1] if IMPORT_FILE_HEADER_MAP.get('Nr',
                                                                                                          None) is not None else None

                row['Altitude'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Altitude')][1] if IMPORT_FILE_HEADER_MAP.get(
                    'Altitude', None) is not None else None
                if row['Altitude'] is not None:
                    if float(row["Altitude"]) <= 0:
                        row['Altitude'] = -777

                row['DateFrom'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('DateFrom')][1] if IMPORT_FILE_HEADER_MAP.get(
                    'DateFrom', None) is not None else None

                row['Date'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Date')][1] if IMPORT_FILE_HEADER_MAP.get('Date',
                                                                                                              None) is not None else None
                if row['Date'] is not None:
                    match = re.search(r'\d{2}-\d{2}-\d{4}', row['Date'])
                    dateFilter = '%d-%m-%Y'
                    if match is None:
                        match = re.search(r'\d{4}-\d{2}-\d{2}', row['Date'])
                        dateFilter = '%Y-%m-%d'
                    if match is not None:
                        date = datetime.datetime.strptime(match.group(), dateFilter).date()
                        row['Date'] = date.strftime('%Y-%m-%d')
                    else:
                        row['Date'] = None

                row['Time'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Time')][1] if IMPORT_FILE_HEADER_MAP.get('Time',
                                                                                                              None) is not None else None
                if row['Time'] is not None:
                    match = re.search(r'\d{2}:\d{2}:\d{2}', row['Time'])
                    if match is not None:
                        time = datetime.datetime.strptime(match.group(), '%H:%M:%S').time()
                        row['Time'] = time.strftime("%H:%M:%S")
                    else:
                        row['Time'] = None

                row['Distance (Km)'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Distance (Km)')][
                    1] if IMPORT_FILE_HEADER_MAP.get('Distance (Km)', None) is not None else None
                row['Distance (Mt)'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Distance (Mt)')][
                    1] if IMPORT_FILE_HEADER_MAP.get('Distance (Mt)', None) is not None else None
                row['Time (Sec)'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Time (Sec)')][
                    1] if IMPORT_FILE_HEADER_MAP.get('Time (Sec)', None) is not None else None
                row['Vel. m/s'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Vel. m/s')][1] if IMPORT_FILE_HEADER_MAP.get(
                    'Vel. m/s', None) is not None else None
                row['Vel. km/h'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Vel. km/h')][1] if IMPORT_FILE_HEADER_MAP.get(
                    'Vel. km/h', None) is not None else None
                row['Mode'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Mode')][1] if IMPORT_FILE_HEADER_MAP.get('Mode',
                                                                                                              None) is not None else None

                if row['Latitude'] is not None and row['Longitude'] is not None and row['Date'] is not None and row[
                    'Time'] is not None:
                    processedData.append(row)

            line_count += 1
    return processedData


# export data to excel file
def exportXLS(dataGroup, total_distance, total_time):
    workbook = xlsxwriter.Workbook(EXPORT_FILE)
    worksheet = workbook.add_worksheet('Data')
    header_format = workbook.add_format({'bold': True, 'font_color': 'black'})
    header_data_format = workbook.add_format({'font_color': 'Gray'})

    # worksheet.write(0, 0, None, header_data_format)
    worksheet.write_blank(0, 0, None, header_data_format)
    worksheet.write(1, 0, None, header_data_format)

    worksheet.set_column(2, 0, 25)
    worksheet.write(2, 0, 'Total distance(mt)', header_format)
    worksheet.write(2, 1, total_distance, header_data_format)
    worksheet.set_column(3, 0, 10)
    worksheet.write(3, 0, 'Total time(s)', header_format)
    worksheet.write(3, 1, total_time, header_data_format)
    worksheet.write(3, 2, 'Delta', header_format)
    worksheet.write(3, 3, str(datetime.timedelta(seconds=total_time)), header_data_format)

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
    lines_format = workbook.add_format({'bg_color': '#ffffff'})
    data_format_odd = workbook.add_format({'bg_color': '#7a6f6f'})
    data_format_even = workbook.add_format({'bg_color': '#c2c0c0'})
    formats = cycle([data_format_odd, data_format_even])

    for row, row_data in enumerate(dataGroup):
        data_format = next(formats)
        # worksheet.set_row(line_number, None, data_format)
        worksheet.write(line_number, 0, row_data["Latitude"], data_format)
        worksheet.write(line_number, 1, row_data["Longitude"], data_format)
        worksheet.write(line_number, 2, row_data["Nr"], data_format)
        worksheet.write(line_number, 3, row_data["Altitude"], data_format)
        worksheet.write(line_number, 4, row_data["Date"], data_format)
        worksheet.write(line_number, 5, row_data["Time"], data_format)
        worksheet.write(line_number, 6, row_data["Distance (Km)"], data_format)
        worksheet.write(line_number, 7, row_data["Distance (Mt)"], data_format)
        worksheet.write(line_number, 8, row_data["Time (Sec)"], data_format)
        worksheet.write(line_number, 9, row_data["Vel. m/s"], data_format)
        worksheet.write(line_number, 10, row_data["Vel. km/h"], data_format)
        worksheet.write(line_number, 11, row_data["Mode"], data_format)
        line_number += 1

    # worksheet.set_column(line_number, 13, None, lines_format)
    # worksheet.write_blank(line_number, 0, None, lines_format)
    workbook.close()
