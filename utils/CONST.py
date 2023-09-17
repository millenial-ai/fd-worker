BIN_PATH = './resource/bin'

# Features for XGB
NUMERICAL_FEATURES = ['amt', 'lat', 'lng', 'city_pop', 'merch_lat', 'merch_lng', 'age']
CATEGORICAL_FEATURES = ['merchant', 'category', 'city', 'state', 'job', 'part_of_day']

# Features for RCF
RCF_NUMERICAL_FEATURES = ['amt', 'lat', 'lng', 'city_pop', 'merch_lat', 'merch_lng']

XGB_FRAUD_THRESHOLD = .5
RCF_FRAUD_THRESHOLD = .71