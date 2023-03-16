from pymongo import MongoClient
from pymongo.errors import BulkWriteError, DuplicateKeyError

from config import MONGO_DB, MONGO_USERNAME, MONGO_PASSWORD, MONGO_HOST
from config import MONGO_HOST_2, MONGO_DB_2


class Client:
    instance = None
    instances = {}

    def __init__(self, is_second_server=False) -> None:
        self.is_second_server = is_second_server
        self.client = None

        self.connect()

    def connect(self):
        if self.is_second_server:
            self.client = MongoClient(
                MONGO_DB_2, username=MONGO_USERNAME, password=MONGO_PASSWORD,
                authSource='admin', authMechanism='SCRAM-SHA-256', maxPoolSize=None
            )
        else:
            self.client = MongoClient(
                MONGO_DB, username=MONGO_USERNAME, password=MONGO_PASSWORD,
                authSource='admin', authMechanism='SCRAM-SHA-256', maxPoolSize=None
            )

    def reconnect(self):
        self.close()
        self.connect()

    def get_client(self):
        return self.client

    def close(self):
        """
        Don't close at all, but if you want be very careful))
        """
        try:
            self.client.close()
        except Exception as e:
            pass

    def __del__(self):
        try:
            self.client.close()
        except Exception as e:
            pass

    @classmethod
    def get_instance(cls, name=None, is_new=False, is_second_server=False):
        if is_new:
            return cls(is_second_server=is_second_server)

        if name is not None:
            if name not in cls.instances or cls.instances[name] is None:
                cls.instances[name] = cls(is_second_server=is_second_server)

            return cls.instances[name]

        if cls.instance is None:
            cls.instance = cls(is_second_server=is_second_server)

        return cls.instance


class ClientMotor:
    instance = None
    instances = {}

    def __init__(self, is_debug=False, is_second_server=False) -> None:
        self.client = None
        self.is_second_server = is_second_server

        if self.client is None:
            self.connect()

        self.is_debug = is_debug

    def connect(self):
        from motor.motor_asyncio import AsyncIOMotorClient
        # import traceback
        # traceback.print_stack()

        connect_string = self.get_connect_string()

        self.client = AsyncIOMotorClient(connect_string, maxPoolSize=None)

    def get_connect_string(self):
        if self.is_second_server:
            return "mongodb://{}:{}@{}/".format(
                MONGO_USERNAME, MONGO_PASSWORD, MONGO_HOST_2
            )
        else:
            return "mongodb://{}:{}@{}/".format(
                MONGO_USERNAME, MONGO_PASSWORD, MONGO_HOST
            )

    def reconnect(self):
        self.close()
        self.connect()

    async def list_collection_names(self, table_name):
        return await self.client[table_name].list_collection_names()

    async def db_collection(self, table_name, collection_name, create_index=None):
        res = self.client[table_name][collection_name]
        if create_index is not None:
            if type(create_index) == list:
                for item in create_index:
                    await self.db_create_index(res, item)
            else:
                await self.db_create_index(res, create_index)

        collection = ClientMotorCollection(self, res)
        return await collection.get()

    async def db_create_index(self, collection, item):
        if type(item) == dict:
            collection.create_index(item['key'], unique=item['unique'])
        else:
            collection.create_index(item)

    async def db_find(self, collection, query=None, sort=None, projection=None, limit=0):
        if query is None:
            query = {}

        cursor = collection.find(query, sort=sort, projection=projection, limit=limit)

        result = []
        async for document in cursor:
            result.append(document)

        return result

    async def db_find_one(self, collection, query=None, sort=None, projection=None):
        if query is None:
            query = {}

        return await collection.find_one(query, sort=sort, projection=projection)

    async def db_update_one(self, collection, query, fields, upsert=False):
        if '$set' in fields:
            return await collection.update_one(query, fields, upsert=upsert)
        else:
            return await collection.update_one(query, {'$set': fields}, upsert=upsert)

    async def db_update_many(self, collection, query, fields, upsert=False):
        if '$set' in fields:
            return await collection.update_many(query, fields, upsert=upsert)
        else:
            return await collection.update_many(query, {'$set': fields}, upsert=upsert)

    async def db_insert_one(self, collection, document):
        return await collection.insert_one(document)

    async def db_insert_many(self, collection, documents, ordered=True):
        return await collection.insert_many(documents, ordered=ordered)

    async def db_delete_one(self, collection, query):
        return await collection.delete_one(query)

    async def db_delete_many(self, collection, query):
        return await collection.delete_many(query)

    async def db_count_documents(self, collection, query):
        return await collection.count_documents(query)

    async def db_distinct(self, collection, key, query=None):
        return await collection.distinct(key, query)

    async def db_aggregate(self, collection, pipeline):
        return await collection.aggregate(pipeline)

    async def db_drop(self, collection):
        return await collection.drop()

    def close(self):
        """
        Don't close at all, but if you want be very careful))
        """
        try:
            self.client.close()
        except Exception as e:
            pass

    @classmethod
    def get_instance(cls, name=None, is_new=False, is_second_server=False):
        if is_new:
            return cls(is_second_server=is_second_server)

        if name is not None:
            if name not in cls.instances or cls.instances[name] is None:
                cls.instances[name] = cls(is_second_server=is_second_server)

            return cls.instances[name]

        if cls.instance is None:
            cls.instance = cls(is_second_server=is_second_server)

        return cls.instance


class ClientMotorCollection:
    def __init__(self, client_motor: ClientMotor, collection):
        self.client_motor = client_motor
        self.collection = collection

    async def find(self, query=None, sort=None, projection=None, limit=0):
        return await self.client_motor.db_find(
            self.collection, query=query, sort=sort, projection=projection, limit=limit
        )

    async def find_one(self, query, sort=None, projection=None):
        return await self.client_motor.db_find_one(self.collection, query=query, sort=sort, projection=projection)

    async def update_one(self, query, fields, upsert=False):
        return await self.client_motor.db_update_one(self.collection, query, fields, upsert=upsert)

    async def update_many(self, query, fields):
        return await self.client_motor.db_update_many(self.collection, query, fields)

    async def insert_one(self, document):
        return await self.client_motor.db_insert_one(self.collection, document)

    async def insert_many(self, documents, ordered=True):
        return await self.client_motor.db_insert_many(self.collection, documents, ordered=ordered)

    async def delete_one(self, query):
        return await self.client_motor.db_delete_one(self.collection, query)

    async def delete_many(self, query):
        return await self.client_motor.db_delete_many(self.collection, query)

    async def count_documents(self, query):
        return await self.client_motor.db_count_documents(self.collection, query)

    async def get(self):
        return self

    async def distinct(self, key, query=None):
        return await self.client_motor.db_distinct(self.collection, key, query=query)

    async def aggregate(self, pipeline):
        return await self.client_motor.db_aggregate(self.collection, pipeline)

    async def drop(self):
        return await self.client_motor.db_drop(self.collection)
