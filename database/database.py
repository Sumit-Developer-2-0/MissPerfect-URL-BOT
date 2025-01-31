import datetime
import motor.motor_asyncio
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Database:

    def __init__(self, uri: str, database_name: str):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.clinton = self._client[database_name]
        self.col = self.clinton.USERS
        self._create_indexes()

    async def _create_indexes(self):
       try:
           await self.col.create_index([("id", 1)], unique=True)
           logging.info("Index on 'id' created.")
       except Exception as e:
           logging.error(f"Failed to create indexes: {e}")

    def new_user(self, id: int) -> Dict[str, Any]:
        """Creates a basic user dictionary."""
        return {
            "id": id,
            "thumbnail": None,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        }

    async def add_user(self, id: int) -> None:
       """Adds a new user to the database."""
       try:
           user = self.new_user(id)
           await self.col.insert_one(user)
           logging.info(f"User with id {id} added successfully.")
       except Exception as e:
           logging.error(f"Failed to add user with id {id}: {e}")

    async def is_user_exist(self, id: int) -> bool:
        """Checks if a user exists with the given id."""
        try:
            user = await self.col.find_one({'id': id})
            return True if user else False
        except Exception as e:
            logging.error(f"Error checking user existance with id {id}: {e}")
            return False

    async def total_users_count(self) -> int:
        """Returns the total count of users."""
        try:
           count = await self.col.count_documents({})
           return count
        except Exception as e:
           logging.error(f"Error getting total user count: {e}")
           return 0


    async def get_all_users(self):
      """Returns a cursor to iterate through all users."""
      try:
        return self.col.find({})
      except Exception as e:
           logging.error(f"Error getting all users: {e}")
           return None
    
    async def delete_user(self, user_id: int) -> None:
        """Deletes a user with the given id."""
        try:
           result = await self.col.delete_one({'id': user_id})
           if result.deleted_count > 0:
               logging.info(f"User with id {user_id} deleted.")
           else:
               logging.info(f"No user found with id {user_id} to delete")

        except Exception as e:
          logging.error(f"Failed to delete user with id {user_id}: {e}")

    async def set_thumbnail(self, id: int, thumbnail: str) -> None:
        """Sets the thumbnail for a user."""
        try:
           await self.col.update_one({'id': id}, {'$set': {'thumbnail': thumbnail, 'updated_at': datetime.datetime.now()}})
           logging.info(f"Thumbnail set for user with id {id}")
        except Exception as e:
           logging.error(f"Failed to set thumbnail for user with id {id}: {e}")
    
    async def update_user(self, id: int, update_data: Dict[str, Any]) -> None:
        """Updates the user's data."""
        try:
            update_data['updated_at'] = datetime.datetime.now()
            await self.col.update_one({'id': id}, {'$set': update_data})
            logging.info(f"User with id {id} updated with data: {update_data}")
        except Exception as e:
            logging.error(f"Failed to update user with id {id}: {e}")

    async def get_thumbnail(self, id: int) -> Optional[str]:
        """Retrieves the thumbnail of a user."""
        try:
           user = await self.col.find_one({'id': id})
           return user.get('thumbnail', None) if user else None
        except Exception as e:
           logging.error(f"Error getting thumbnail for user id {id}: {e}")
           return None