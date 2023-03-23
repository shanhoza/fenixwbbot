import motor.motor_asyncio

import bot.config as config

cluster = motor.motor_asyncio.AsyncIOMotorClient(
    "mongodb+srv://{}:{}@{}").format(
        config.MONGO_USERNAME,
        config.MONGO_PASSWORD,
        config.MONGO_HOST,
)

collection_users = cluster.FenixDB.USERS
