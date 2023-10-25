import os
import pickle
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from dataclasses import asdict
from .message import Message, BasicInfoRequestMessage
from .CONST import BIN_PATH, NUMERICAL_FEATURES, CATEGORICAL_FEATURES

def load_pkl(source_path):
    return pickle.load(open(source_path,'rb'))
    
features_encoders = {
    key: load_pkl(os.path.join(BIN_PATH, f'{key}_encoder.pkl'))
    for key in CATEGORICAL_FEATURES
}

numeric_scaler = load_pkl(os.path.join(BIN_PATH, 'xgb-numerical-std-scaler.pkl'))

def dob_to_age(date_str):
    # Convert the birthdate string to a datetime object
    birthdate = datetime.strptime(date_str, '%Y-%m-%d')

    # Get the current date and time
    current_date = datetime.now()

    # Calculate the difference in years
    age = current_date.year - birthdate.year

    # Adjust the age if the birthdate hasn't occurred yet this year
    if (current_date.month, current_date.day) < (birthdate.month, birthdate.day):
        age -= 1

    return age

# Convert date to one of the values (morning,afternoon,evening,night)
def date_to_part_of_day(date_str):
    hour = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').hour
    if 6 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 18:
        return 'afternoon'
    elif 18 <= hour < 24:
        return 'evening'
    else:
        return 'night'


"""
Transform numerical data for XGB algorithm
Scale numerical value and encode categorical value
"""
def transform_message(
    message: BasicInfoRequestMessage,
    features_encoders=features_encoders,
    numeric_scaler=numeric_scaler
):
    dict_message = asdict(message)
    dict_message['age'] = dob_to_age(dict_message['dob'])
    dict_message['part_of_day'] = date_to_part_of_day(dict_message['tx_date'])
    
    # Convert numerical features
    numerical_features = []
    for feature in NUMERICAL_FEATURES:
        numerical_features.append(dict_message[feature])
    transformed_numerical_features = numeric_scaler.transform([numerical_features])[0]
    for idx, feature in enumerate(NUMERICAL_FEATURES):
        dict_message[feature] = transformed_numerical_features[idx]
    
    # Convert categorical features
    for cat_feature in CATEGORICAL_FEATURES:
        encoder=features_encoders[cat_feature]
        dict_message[cat_feature] = encoder.transform([dict_message[cat_feature]])[0]
    
    return BasicInfoRequestMessage(**dict_message)

"""
Transform numerical data for RCF algorithm
"""
def transform_message_rcf(
    message: BasicInfoRequestMessage,
    features_encoders=features_encoders,
    numeric_scaler=numeric_scaler
):
    dict_message = asdict(message)
    sample_vector = [
        dict_message['amt'],
        dict_message['lat'],
        dict_message['long'],
        dict_message['city_pop'],
        dict_message['merch_lat'],
        dict_message['merch_long']
    ]
    
    # Convert numerical features
    numerical_features = []
    for feature in NUMERICAL_FEATURES:
        numerical_features.append(dict_message[feature])
    transformed_numerical_features = numeric_scaler.transform([numerical_features])[0]
    for idx, feature in enumerate(NUMERICAL_FEATURES):
        dict_message[feature] = transformed_numerical_features[idx]
    
    return BasicInfoRequestMessage(**dict_message)
