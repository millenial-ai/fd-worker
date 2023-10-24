from dataclasses import dataclass, asdict
from typing import List, Union, Dict
import json

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
    long: float
    city_pop: float
    merch_lat: float
    merch_long: float
    merch_name: str
    tx_name: str
    tx_date: str
    tx_ending: str
    merchant: str 
    category: str
    city: str
    state: str
    dob: str
    job: str 
    age: float = None
    part_of_day: str = None
    recipient_email: str = None
    
@dataclass
class OutputMessage(Message):
    result: float
    msg: str = ""