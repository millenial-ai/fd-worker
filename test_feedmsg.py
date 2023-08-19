from utils.processor import RCFProcessor, XGBProcessor
from utils.message import PCARequestMessage


msg = PCARequestMessage(identifier="xx", values=[1,1,.1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,10,0,0,0])

rcf_processor = RCFProcessor(endpoint_name='custom-rcf')
rcf_result = rcf_processor.process(msg)
print("RCF Result", rcf_result)

xgb_processor = XGBProcessor(endpoint_name='custom-xgb', content_type='text/csv')
xgb_result = xgb_processor.process(msg)
print("XGB Result", xgb_result)