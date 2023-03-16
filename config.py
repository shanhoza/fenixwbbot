API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
PROXY_URL = os.getnev("TELEGRAM_PROXY_URL")
PROXY_AUTH = aiohttp.BasicAuth(
    login=os.getenv("TELEGRAM_PROXY_LOGIN")
    password=os.getenv("TELEGRAM_PROXY_PASSWORD")
)
MONGO_DB = 
