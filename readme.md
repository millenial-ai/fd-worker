Endpoint trigger command:
- XGB
aws sagemaker-runtime invoke-endpoint --endpoint-name custom-xgb --body '1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,10,0,0,0' --content-type text/csv output.txt
- RCF
aws sagemaker-runtime invoke-endpoint --endpoint-name custom-rcf --body '{"instances": [{"data": {"features": {"values": [1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,10,0,0,0]}}}]}' --content-type application/json output.txt
