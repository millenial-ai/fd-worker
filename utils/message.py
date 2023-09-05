from dataclasses import dataclass
from typing import List, Union, Dict

@dataclass
class Message:
    identifier: str

@dataclass
class PCARequestMessage(Message):
    values: List[float]

@dataclass
class BasicInfoRequestMessage(Message):
    amt: float
    lat: float
    lng: float
    city_pop: float
    merch_lat: float
    merch_lng: float
    merch_name: str
    tx_name: str
    tx_date: str
    tx_ending: str
    
@dataclass
class OutputMessage(Message):
    result: Dict
    msg: str = ""