#!/bin/bash

export RCF_ENDPOINT=custom-nopca-datacamp-rcf
export XGB_ENDPOINT=custom-nopca-datacamp-xgbsmote
export SQS_NAME=FraudRequestQueue
python3 main.py --env production