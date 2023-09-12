import boto3
import json
from abc import ABC, abstractmethod
from typing import Callable, Union
from .message import Message, OutputMessage
from .transform import transform_message
from dataclasses import asdict

class SageMakerProcessor():
    """
    Process the message, send message to endpoint, then modify and return the result
    """
    def __init__(self, 
        endpoint_name: str,
        content_type: str = 'application/json',
        accept: str = 'application/json',
        preprocess: Union[Callable, None] = None, 
        postprocess: Union[Callable, None] = None
    ):
        self.endpoint_name = endpoint_name
        self.content_type = content_type
        self.accept = accept
        
        self.preprocess = preprocess
        self.postprocess = postprocess
        
    """
    This function preprocess the data, send the request to SageMaker, then post process the output
    """
    def process(self, message: Message):
        output_message = OutputMessage(message.identifier, None)
        
        try:
            sagemaker_result = self.send_to_endpoint(
                self.preprocess(message)
            )
            # Return None result if cannot get sagemaker
            if sagemaker_result is not None:
                output_message.result = self.postprocess(sagemaker_result)
        except Exception as e:
            output_message.msg = str(e)
        finally:
            return output_message
    
    @abstractmethod
    def send_to_endpoint(self, processed_message: object):
        raise Exception("Not implemented")



def rcf_pca_preprocess(message: Message):
    return json.dumps({"instances": [{"data": {"features": {"values": message.values}}}]})

def rcf_preprocess(message: Message):
    return json.dumps({"instances": [{"data": {"features": {"values": [message.amt, message.lat, message.lng, message.city_pop, message.merch_lat, message.merch_lng]}}}]})

def rcf_postprocess(response):
    return response["scores"][0]["score"]
    
class RCFProcessor(SageMakerProcessor):
    def __init__(self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.preprocess = rcf_preprocess
        self.postprocess = rcf_postprocess
    
    def send_to_endpoint(self, processed_message: object):
        # Create a SageMaker Runtime client using IAM role credentials
        sagemaker_runtime = boto3.client('sagemaker-runtime')

        # Invoke the SageMaker endpoint using IAM role credentials
        response = sagemaker_runtime.invoke_endpoint(EndpointName=self.endpoint_name,
                                                     ContentType=self.content_type,
                                                     Accept=self.accept,
                                                     Body=processed_message)
        
        # Parse and print the response
        response_body = response['Body'].read().decode()
        return json.loads(response_body)

def xgb_pca_preprocess(message: Message):
    return ','.join([str(v) for v in message.values])

def xgb_preprocess(message: Message):
    transformed_message = transform_message(message)
    dict_message = asdict(transformed_message)

    feature_vector = [
        transformed_message.amt, 
        transformed_message.lat, 
        transformed_message.lng, 
        transformed_message.city_pop, 
        transformed_message.merch_lat, 
        transformed_message.merch_lng,
        transformed_message.age,
        transformed_message.merchant,
        transformed_message.category,
        transformed_message.city,
        transformed_message.state,
        transformed_message.job,
        transformed_message.part_of_day
    ]
    return ','.join([str(v) for v in feature_vector])

def xgb_postprocess(response):
    try:
        return float(response)
    except Exception as e:
        print(str(e))
        return -1

class XGBProcessor(SageMakerProcessor):
    def __init__(self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.preprocess = xgb_preprocess
        self.postprocess = xgb_postprocess
    
    def send_to_endpoint(self, processed_message: object):
        # Create a SageMaker Runtime client using IAM role credentials
        sagemaker_runtime = boto3.client('sagemaker-runtime')

        # Invoke the SageMaker endpoint using IAM role credentials
        response = sagemaker_runtime.invoke_endpoint(EndpointName=self.endpoint_name,
                                                     ContentType=self.content_type,
                                                     Accept=self.accept,
                                                     Body=processed_message)
        
        # Parse and print the response
        response_body = response['Body'].read().decode()
        return response_body