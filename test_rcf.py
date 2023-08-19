import boto3
import json

# Create a SageMaker Runtime client using IAM role credentials
sagemaker_runtime = boto3.client('sagemaker-runtime')

# Input data for inference
input_data = {
  "instances": [
    {
      "data": {
        "features": {
          "values": [1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,10,0,0,0]
        }
      }
    }
  ]
}

# Convert input data to JSON format
input_payload = json.dumps(input_data)

# Specify content type and accept type
content_type = "application/json"
accept = "application/json"

# Replace with your SageMaker endpoint name
endpoint_name = 'custom-rcf'

# Invoke the SageMaker endpoint using IAM role credentials
response = sagemaker_runtime.invoke_endpoint(EndpointName=endpoint_name,
                                             ContentType=content_type,
                                             Accept=accept,
                                             Body=input_payload)

# Parse and print the response
response_body = response['Body'].read().decode()
print("Inference response:")
print(response_body)