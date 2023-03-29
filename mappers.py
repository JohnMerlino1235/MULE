from database.database_user import DatabaseUserModel
from model.user import User
# user_model_to_database_user_model is a mapper to convert from a model to a database model
def user_model_to_database_user_model(user_model):
    return DatabaseUserModel(user_model.email, user_model.password, user_model.first_name, user_model.last_name)

# database_user_model_to_user_model is a mapper to convert from a database model to model
def database_user_model_to_user_model(database_user_model):
    return User(database_user_model.email, database_user_model.password, database_user_model.first_name, database_user_model.last_name)