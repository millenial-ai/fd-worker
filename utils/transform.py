import os
import pickle
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from dataclasses import asdict
from .message import Message, BasicInfoRequestMessage
from .CONST import BIN_PATH, XGB_BIN_PATH, RCF_BIN_PATH, NUMERICAL_FEATURES, CATEGORICAL_FEATURES, UNKNOWN
import logging

def load_pkl(source_path):
    return pickle.load(open(source_path,'rb'))
    
def get_feature_encoder_name(feature_name):
    return f'LabelEncoder_{feature_name}.pkl'

def get_numerical_scaler_name(feature_name):
    return f'StandardScaler_{feature_name}.pkl'

xgb_features_encoders = {
    key: load_pkl(os.path.join(XGB_BIN_PATH, get_feature_encoder_name(key)))
    for key in CATEGORICAL_FEATURES
}
xgb_numerical_scalers = {
    key: load_pkl(os.path.join(XGB_BIN_PATH, get_numerical_scaler_name(key)))
    for key in NUMERICAL_FEATURES
}

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

def aggregate_message(
    message: BasicInfoRequestMessage
):
    dict_message = asdict(message)
    dict_message['age'] = dob_to_age(dict_message['dob'])
    dict_message['part_of_day'] = date_to_part_of_day(dict_message['tx_date'])
    return dict_message

"""
Transform numerical data for XGB algorithm
Scale numerical value and encode categorical value
"""
def transform_message_xgb(
    message: BasicInfoRequestMessage,
    features_encoders=xgb_features_encoders,
    numerical_scalers=xgb_numerical_scalers
):
    dict_message = aggregate_message(message)
    
    # Convert numerical features
    numerical_features = []
    for numerical_feature in NUMERICAL_FEATURES:
        try:
            scaler = numerical_scalers[numerical_feature]
            # print(numerical_feature, dict_message[numerical_feature], scaler.transform([dict_message[numerical_feature]]))
            dict_message[numerical_feature] = scaler.transform([[dict_message[numerical_feature]]])[0][0]
        except Exception as e:
            logging.warn(f"{str(e)} ; Setting {numerical_feature} to -1")
            dict_message[numerical_feature] = UNKNOWN

    # Convert categorical features
    for cat_feature in CATEGORICAL_FEATURES:
        try:
            encoder = features_encoders[cat_feature]
            logging.info(f"{cat_feature} -> {encoder.transform([dict_message[cat_feature]])}")
            dict_message[cat_feature] = encoder.transform([dict_message[cat_feature]])[0]
        except Exception as e:
            logging.warn(f"{str(e)} ; Setting {cat_feature} to -1")
            dict_message[cat_feature] = UNKNOWN
    logging.info(dict_message)

    logging.info(f"XGB dict_message {dict_message}")

    return BasicInfoRequestMessage(**dict_message)

"""
Transform numerical data for RCF algorithm
"""
def transform_message_rcf(
    message: BasicInfoRequestMessage,
    numerical_scalers=xgb_numerical_scalers,
):
    dict_message = asdict(message)
    
    # Convert numerical features
    numerical_features = []
    for numerical_feature in NUMERICAL_FEATURES:
        try:
            scaler = numerical_scalers[numerical_feature]
            # print(numerical_feature, dict_message[numerical_feature], scaler.transform([dict_message[numerical_feature]]))
            dict_message[numerical_feature] = scaler.transform([[dict_message[numerical_feature]]])[0][0]
        except Exception as e:
            logging.warn(f"{str(e)} ; Setting {numerical_feature} to -1")
            dict_message[numerical_feature] = -1
    logging.info(f"RCF dict_message {dict_message}")
    return BasicInfoRequestMessage(**dict_message)
