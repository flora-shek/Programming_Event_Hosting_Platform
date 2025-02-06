from .mongodb import mongo_db

class UserModel:
    collection = mongo_db['user'] 

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
        Retrieves a user document based on id
        """
        cursor = EventModel.collection.find({'user_id': user_id}).limit(1)
        return list(cursor)
    @staticmethod
    def update_user(email, updated_data):
        """
        Updates a user document based on email.
        """
        result = UserModel.collection.update_one(
            {'email': email}, {'$set': updated_data}
        )
        return result

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
    
class EventModel:
    collection = mongo_db['events']
    @staticmethod
    def create_user(data):
        """
        Inserts a new event document into the 'events' collection.
        """
        return EventModel.collection.insert_one(data).inserted_id
    
    @staticmethod
    def delete_user(email):
        """
        Deletes a event document based on email.
        """
        return EventModel.collection.delete_one({'email': email})
    @staticmethod
    def count_users():
        """
        Returns all events.
        """
        return EventModel.collection.count_documents({})
    @staticmethod
    def all_event():
        return list(EventModel.collection.find({}))
    @staticmethod
    def search_event(search_term):
        """
        Searches for events based on a search term (e.g., event name or description).
        """
        return list(EventModel.collection.find({
            "$or": [
                {"name": {"$regex": search_term, "$options": "i"}},  # Case-insensitive search by event name
                {"description": {"$regex": search_term, "$options": "i"}}  # Case-insensitive search by description
            ]
        }))
    @staticmethod
    def get_event_id(event_id):
        """
        Retrieves a user document based on id.
        """
        cursor = EventModel.collection.find({'event_id': event_id}).limit(1)
        return list(cursor)
    @staticmethod
    def update_event(event_id, updated_data):
        """
        Updates a user document based on email.
        """
        result = EventModel.collection.update_one(
            {'event_id': event_id}, {'$set': updated_data}
        )
        return result
    @staticmethod
    def get_user_events(id):
   
        user_events = EventModel.collection.find({"registrations": id})
        
       
        user_events_list = list(user_events)
        return user_events_list

class ProblemModel:
    collection = mongo_db['problems']

    @staticmethod
    def all_event():
        return list(EventModel.collection.find({}))
    @staticmethod
    def get_problems_id(event_id):
        """
        Retrieves a problem document based on event id
        """
        cursor = ProblemModel.collection.find({'event_id': event_id})
        return list(cursor)
    
class SubmissionModel:
    collection = mongo_db['problems']
    @staticmethod
    def insert(data):
       
        return SubmissionModel.collection.insert_one(data).inserted_id
    @staticmethod
    def find(problem_id,user_id):
        pass
    @staticmethod
    def count():
      
        return SubmissionModel.collection.count_documents({})
    