from dataclasses import dataclass
from typing import List, Union, Dict

@dataclass
class Message:
    identifier: str

@dataclass
class PCARequestMessage(Message):
    values: List[float]
    
@dataclass
class OutputMessage(Message):
    result: Dict
    msg: str = ""