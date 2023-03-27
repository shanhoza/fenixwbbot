import os

from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("FENIXWBBOT_API_TOKEN")

MONGO_HOST = "clusterfenix.unccemf.mongodb.net/?retryWrites=true&w=majority"
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

WB_API_URL = """https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1& \
curr=rub&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0&reg=0&resultset=catalog& \
sort=popular&spp=0&suppressSpellcheck=false{}&page={}&query={}"""

WB_API_CITIES_QUERIES = {
    'Москва': '&couponsGeo=12,3,18,15,21&dest=-1029256,-102269,-2162196,-2162195&regions=68,64,83,4,38,80,33,70,82,86,75,30,69,22,66,31,40,1,48,71',
    'Санкт-Петербург': '&couponsGeo=12,3,18,15,21&dest=-1029256,-102269,-2162196,-2162195&regions=68,64,83,4,38,80,33,70,82,86,75,30,69,22,66,31,40,1,48,71',
    'Екатеринбург': '&couponsGeo=2,12,7,3,6,13,21&dest=-1113276,-79379,-1104258,-5803327&regions=64,58,83,4,38,80,33,70,82,86,30,69,22,66,31,40,1,48',
    'Казань': '&couponsGeo=12,7,3,6,18,22,21&dest=-1075831,-79374,-367666,-2133462&regions=68,64,83,4,38,80,33,70,82,86,30,69,22,66,31,40,1,48',
    'Новосибирск': '&couponsGeo=2,12,7,3,6,21,16&dest=-1221148,-140294,-1751445,-365341&regions=64,58,83,4,38,80,33,70,82,86,30,69,22,66,31,40,1,48',
    'Хабаровск': '&couponsGeo=2,12,7,6,9,21,11&dest=-1221185,-151223,-1782064,-1785058&regions=64,4,38,80,70,82,86,30,69,22,66,40,1,48',
    'Краснодар': '&couponsGeo=2,7,3,6,19,21,8&dest=-1059500,-108082,-269701,12358062&regions=68,64,83,4,38,80,33,70,82,86,30,69,22,66,31,40,1,48',
    'Калининград': '&couponsGeo=3,21&dest=-1216601,-103906,-331414,-331412&regions=68,82,86,30,69,22,66,1,48'
}

WB_API_NUMBER_OF_PAGES_TO_PARSE = 100
