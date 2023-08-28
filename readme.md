Endpoint trigger command:
- XGB
aws sagemaker-runtime invoke-endpoint --endpoint-name custom-xgb --body '1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,10,0,0,0' --content-type text/csv output.txt
- RCF
aws sagemaker-runtime invoke-endpoint --endpoint-name custom-rcf --body '{"instances": [{"data": {"features": {"values": [1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,10,0,0,0]}}}]}' --content-type application/json output.txt

Send test request to api gateway:
```
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"values": {
        "identifier": "user01",
        "pca": [1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,10,0,0,0]
    }}' \
     https://0m99smdcz1.execute-api.us-east-1.amazonaws.com/fraud/check
```