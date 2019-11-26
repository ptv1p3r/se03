# api settings
SERVER_MODE_DEV = True
SERVER_PORT = 4000
EXPORT_FILE = 'se.xlsx'
# "Latitude", "Longitude", "Nr", "Altitude", "DateFrom", "Date", "Time", "Distance (Km)", "Distance (Mt)", "Time (Sec)", "Vel. m/s", "Vel. km/h", "Mode"
# IMPORT_FILE_HEADER_MAP = {
#         "Latitude": 0,
#         "Longitude": 1,
#         "Nr": 2,
#         "Altitude": 3,
#         "DateFrom": 4,
#         "Date": 5,
#         "Time": 6,
#         "Distance (Km)": None,
#         "Distance (Mt)": None,
#         "Time (Sec)": None,
#         "Vel. m/s": None,
#         "Vel. km/h": None,
#         "Mode": None
#     }

IMPORT_FILE_HEADER_MAP = {}

# "_id","bssid","dayoftheweek","ssid","attractiveness","dateTime","latitude","longitude"
# IMPORT_FILE_HEADER_MAP = {
#         "Latitude": 6,
#         "Longitude": 7,
#         "Nr": 0,
#         "Altitude": None,
#         "DateFrom": None,
#         "Date": 5,
#         "Time": 5,
#         "Distance (Km)": None,
#         "Distance (Mt)": None,
#         "Time (Sec)": None,
#         "Vel. m/s": None,
#         "Vel. km/h": None,
#         "Mode": None
#     }
UPLOAD_ALLOWED_EXTENSIONS = set(['txt', 'csv'])
UPLOAD_FOLDER = 'downloads'
FILEPATH = ''
