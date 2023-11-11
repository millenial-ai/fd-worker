BIN_PATH = './resource/bin'
# RCF_BIN_PATH = f'{BIN_PATH}/rcf'
# XGB_BIN_PATH = f'{BIN_PATH}/xgb'

# Features for XGB
NUMERICAL_FEATURES = ['amt', 'lat', 'long', 'city_pop', 'merch_lat', 'merch_long', 'age']
CATEGORICAL_FEATURES = ['merchant', 'category', 'city', 'state', 'job', 'part_of_day']

# Features for RCF
RCF_NUMERICAL_FEATURES = ['amt', 'lat', 'long', 'city_pop', 'merch_lat', 'merch_long']

XGB_FRAUD_THRESHOLD = .5
RCF_FRAUD_THRESHOLD = .71

UNKNOWN = -1