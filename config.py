import os

SLID_TOKEN_KEY = "slid_token"
APP_ID_KEY = "app_id"
APP_SECRET_KEY = "app_secret"
USER_LOGIN_KEY = "user_login"
USER_PASSWORD_KEY = "user_password"

REDIS_HOST="localhost" if os.environ.get('FLASK_ENV') == 'development' else "redis"