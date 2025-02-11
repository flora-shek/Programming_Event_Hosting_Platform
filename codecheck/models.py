from .mongodb import mongo_db

class UserModel:
    collection = mongo_db['user'] 

    @staticmethod
    def create_user(data):
        return UserModel.collection.insert_one(data).inserted_id
    @staticmethod
    def get_all_email():
        email = UserModel.collection.find({"role":"user"},{"email":1,"_id":0})
        e_list = [user["email"] for user in email]
        return e_list
    @staticmethod
    def get_user(email):
        return UserModel.collection.find_one({'email': email})
    @staticmethod
    def get_user_id(user_id):
        cursor = UserModel.collection.find({'user_id': user_id}).limit(1)
        return list(cursor)
    @staticmethod
    def update_user(email, updated_data):
     
        result = UserModel.collection.update_one(
            {'email': email}, {'$set': updated_data}
        )
        return result

    @staticmethod
    def delete_user(email):
       
        return UserModel.collection.delete_one({'email': email})

    @staticmethod
    def count_users():
        
        return UserModel.collection.count_documents({})
    
class EventModel:
    collection = mongo_db['events']
   
    @staticmethod
    def create_event(data):
       
        return EventModel.collection.insert_one(data)
    
    @staticmethod
    def delete(id):
       
        return EventModel.collection.delete_one({'event_id': id})
    @staticmethod
    def count():
       
        return EventModel.collection.count_documents({})
    @staticmethod
    def all_event():
        return list(EventModel.collection.find({}))
    @staticmethod
    def search_event(search_term):
      
        return list(EventModel.collection.find({
            "$or": [
                {"name": {"$regex": search_term, "$options": "i"}},  # Case-insensitive search by event name
                {"description": {"$regex": search_term, "$options": "i"}}  # Case-insensitive search by description
            ]
        }))
    @staticmethod
    def get_event_id(event_id):
        
        cursor = EventModel.collection.find({'event_id': event_id}).limit(1)
        return list(cursor)
    @staticmethod
    def update_event(event_id, updated_data):
      
        result = EventModel.collection.update_one(
            {'event_id': event_id}, {'$set': updated_data}
        )
        return result
    @staticmethod
    def get_user_events(id):
   
        user_events = EventModel.collection.find({"registrations": id})
        
       
        user_events_list = list(user_events)
        return user_events_list
    @staticmethod
    def get_p_events(id):
   
        user_events = EventModel.collection.find({"participations": id})
       
        user_events_list = list(user_events)
        return user_events_list
    @staticmethod
    def get_events(id):
   
        user_events = EventModel.collection.find({"user_id": id})
        
        user_events_list = list(user_events)
        return user_events_list

class ProblemModel:
    collection = mongo_db['problems']
    @staticmethod
    def create(data):
        return ProblemModel.collection.insert_one(data)
    @staticmethod
    def delete(id):
       
        return ProblemModel.collection.delete_one({'problem_id':id})
    @staticmethod
    def all_event():
        return list(EventModel.collection.find({}))
    @staticmethod
    def get_problems_id(event_id):
       
        cursor = ProblemModel.collection.find({'event_id': event_id})
        return list(cursor)
    @staticmethod
    def count():
        return ProblemModel.collection.count_documents({})
    
class SubmissionModel:
    collection = mongo_db['submissions']
   
    @staticmethod
    def insert(data):
        return SubmissionModel.collection.insert_one(data)
    @staticmethod
    def find(problem_id, user_id):
        cursor = SubmissionModel.collection.find({'user_id': user_id, 'problem_id': problem_id})
        return list(cursor)
    @staticmethod
    def find1(problem_id):
        cursor = SubmissionModel.collection.find({'problem_id': problem_id})
        return list(cursor)

    @staticmethod
    def count():
      
        return SubmissionModel.collection.count_documents({})
    @staticmethod
    def delete(user_id,problem_id):
       
        return SubmissionModel.collection.delete_one({'user_id': user_id,'problem_id':problem_id})
    @staticmethod
    def leaderboard(event_id):
        leaderboard_data = list(SubmissionModel.collection.aggregate([
        {"$match": {"event_id": event_id}},  # Get submissions for the event
        {"$group": {"_id": "$user_id", "total_score": {"$sum": "$final_score"}}},  
        {"$sort": {"total_score": -1}}  # Sort descending
    ]))
        return leaderboard_data
class EvaluationModel:
    collection = mongo_db['evaluation']
    @staticmethod
    def count():
        return EvaluationModel.collection.count_documents({})
    @staticmethod
    def insert(data):
        return EvaluationModel.collection.insert_one(data)