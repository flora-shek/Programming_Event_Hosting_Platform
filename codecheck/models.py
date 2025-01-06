# models.py (Custom Python model for MongoDB)

from .mongodb import mongo_db

class UserModel:
    collection = mongo_db['user']  # Reference the "users" collection

    @staticmethod
    def create_user(data):
        """
        Inserts a new user document into the 'users' collection.
        """
        return UserModel.collection.insert_one(data).inserted_id

    @staticmethod
    def get_user(email):
        """
        Retrieves a user document based on email.
        """
        return UserModel.collection.find_one({'email': email})
    @staticmethod
    def get_user_id(user_id):
        """
        Retrieves a user document based on email.
        """
        return UserModel.collection.find_one({'user_id': user_id})

    @staticmethod
    def update_user(email, updated_data):
        """
        Updates a user document based on email.
        """
        return UserModel.collection.update_one(
            {'email': email}, {'$set': updated_data}
        )

    @staticmethod
    def delete_user(email):
        """
        Deletes a user document based on email.
        """
        return UserModel.collection.delete_one({'email': email})

    @staticmethod
    def count_users():
        """
        Returns all users.
        """
        return UserModel.collection.count_documents({})
    
   