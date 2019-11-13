# api settings
SERVER_MODE_DEV = True
SERVER_PORT = 4000
EXPORT_FILE = 'se.xlsx'
# IMPORT_FILE = '20081026094426.csv'
IMPORT_FILE = '15-07-2017-ap-02738d854419-pml.csv'
# "Latitude", "Longitude", "Nr", "Altitude", "DateFrom", "Date", "Time", "Distance (Km)", "Distance (Mt)", "Time (Sec)", "Vel. m/s", "Vel. km/h", "Mode"
# IMPORT_FILE_HEADER_MAP = {
#         "Latitude": 1,
#         "Longitude": 2,
#         "Nr": 3,
#         "Altitude": 4,
#         "DateFrom": 5,
#         "Date": 6,
#         "Time": 7,
#         "Distance (Km)": None,
#         "Distance (Mt)": None,
#         "Time (Sec)": None,
#         "Vel. m/s": None,
#         "Vel. km/h": None,
#         "Mode": None
#     }

# "_id","bssid","dayoftheweek","ssid","attractiveness","dateTime","latitude","longitude"
IMPORT_FILE_HEADER_MAP = {
        "Latitude": 6,
        "Longitude": 7,
        "Nr": 0,
        "Altitude": None,
        "DateFrom": None,
        "Date": 5,
        "Time": 5,
        "Distance (Km)": None,
        "Distance (Mt)": None,
        "Time (Sec)": None,
        "Vel. m/s": None,
        "Vel. km/h": None,
        "Mode": None
    }