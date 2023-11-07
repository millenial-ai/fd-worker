export RCF_ENDPOINT=custom-nopca-datacamp-rcf
export XGB_ENDPOINT=custom-nopca-datacamp-xgbsmote
# export RCF_ENDPOINT=custom-nopca-datacamp-rcf
# export XGB_ENDPOINT=custom-nopca-datacamp-xgbsmote
export SQS_NAME=FraudRequestQueue
aws configure set region $(aws configure list | grep region | awk '{print $2}')

cd ~/fd-worker

echo "Starting app"

nohup python3 main.py > /dev/null 2>&1 &