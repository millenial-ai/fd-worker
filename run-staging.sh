#!/bin/bash

export RCF_ENDPOINT=fd-endpoint-rcf
export XGB_ENDPOINT=fd-endpoint-xgb
export SQS_NAME=FraudRequestQueue-Staging
python3 main.py --env staging