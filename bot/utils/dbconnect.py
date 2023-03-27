from datetime import datetime

import motor.motor_asyncio
from aiogram.types.user import User


class Request:
    def __init__(
        self,
        connector: motor.motor_asyncio.AsyncIOMotorClient
    ) -> None:
        self.connector = connector

    async def add_user(
        self,
        user: User
    ):
        await self.connector.F_USERS.USERS.update_one(
            {
                'id': user.id,
            },
            {
                '$setOnInsert': {
                    'CREATED': datetime.now(),
                    'FIRST_NAME': user.first_name,
                    'LAST_NAME': user.last_name,
                    'USERNAME': user.username,
                    # 'BLOCKED': BLOCKED,
                    # 'PHONE': PHONE
                }
            },
            upsert=True
        )

    async def add_parsed_keys(self, vendor_code: int, ):
        collection_name = int(str(vendor_code)[:3])
        await self.connector.PARSED_KEYS.collection_name.update
