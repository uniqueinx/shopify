import os


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY")
    HOST = os.environ.get("HOST_URI")
    DB = os.environ.get("DB")

    SHOPIFY_CONFIG = {
        "API_KEY": os.environ.get("API_KEY"),
        "API_SECRET": os.environ.get("API_SECRET"),
        "APP_HOME": f"http://{HOST}",
        "CALLBACK_URL": f"http://{HOST}/install",
        "REDIRECT_URI": f"http://{HOST}/auth",
        "SCOPE": ["read_products", "read_orders", "write_orders"],
    }
