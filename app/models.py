from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

client = MongoClient('mongodb://localhost:27017/')
db = client.ExamBank

class User:
    def __init__(self, email, full_name, password_hash=None, role='Member', is_active=False):
        self.email = email
        self.full_name = full_name
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active
        
    def save(self):
        user_data = {
            'email': self.email,
            'full_name': self.full_name,
            'password_hash': self.password_hash,
            'role': self.role,
            'is_active': self.is_active
        }
        return db.users.insert_one(user_data)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def find_by_email(email):
        print(f"Searching for email: {email}")
        user_data = db.users.find_one({'email': email})
        print(f"Found user data: {user_data}")
        
        if user_data:
            return User(
                email=user_data['email'],
                full_name=user_data.get('full_name', ''),
                password_hash=user_data.get('password_hash'),
                role=user_data.get('role', 'Member'),
                is_active=user_data.get('is_active', False)
            )
        return None
    
    @staticmethod
    def update_active_status(email, status):
        db.users.update_one(
            {'email': email},
            {'$set': {'is_active': status}}
        )
    
    @staticmethod
    def update_password(email, new_password_hash):
        db.users.update_one(
            {'email': email},
            {'$set': {'password_hash': new_password_hash}}
        )
    
    @staticmethod
    def clear_all():
        result = db.users.delete_many({})
        print(f"Deleted {result.deleted_count} documents") 