# api settings
SERVER_MODE_DEV = True
SERVER_PORT = 4000
MAILSYSTEM_USES_MAILJET = False

# smtp email settings
SMTP_USES_SSL = True
SMTP_USES_TLS = False
SMTP_HOST = 'smtp.gmail.com'
SMTP_USER = 'pedro.roldan@gmail.com'
SMTP_PASSWORD = 'nadlor290228'
SMTP_PORT = 465
SMTP_TLS_PORT = 587
SMTP_SENDER = 'no_reply@city-guide.com'

# mailjet
MAILJET_APIKEY = '17a7fdf8dc35676b8453cd1e3bdb6dca'
MAILJET_SECRETKEY = 'ad244291a2df08bd86c2df6670fc2e14'
MAILJET_SENDER = 'pedro.roldan@gmail.com'

# token settings
TOKEN_SUBJECT = 'City Guide Security'
TOKEN_ISSUER = 'CityGuide.pt'
TOKEN_SECRET = 'cityguide_api'
TOKEN_ALGORITHM = 'HS256'
TOKEN_VERSION = '1.0'
TOKEN_EXP_DELTA_SECONDS = 20
TOKEN_EXP_MINUTES = 60  # valido por uma hora

# database settings
DATABASE_HOST = '192.168.88.254'
DATABASE_PORT = 3306
DATABASE_NAME = 'CityGuide'
DATABASE_USER = 'admin'
DATABASE_PASSWORD = 'admin'

# slack
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"
