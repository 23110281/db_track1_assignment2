import os

MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'root')
MYSQL_DB = os.environ.get('MYSQL_DB', 'iitgn_connect')

JWT_SECRET_KEY = 'iitgn-connect-jwt-secret-cs432-2026'
JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours in seconds
