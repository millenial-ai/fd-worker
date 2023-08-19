import boto3

# Create a SageMaker Runtime client using IAM role credentials
sagemaker_runtime = boto3.client('sagemaker-runtime')

# Input data for inference
input_data = '1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,10,0,0,0'

# Specify content type and accept type
content_type = "text/csv"
accept = "text/csv"

# Replace with your SageMaker endpoint name
endpoint_name = 'custom-xgb'

# Invoke the SageMaker endpoint using IAM role credentials
response = sagemaker_runtime.invoke_endpoint(EndpointName=endpoint_name,
                                             ContentType=content_type,
                                             Accept=accept,
                                             Body=input_data)

# Parse and print the response
response_body = response['Body'].read().decode()
print("Inference response:")
print(response_body)