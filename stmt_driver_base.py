from typing import Dict, List, Callable
from abc import ABC, abstractmethod
from decimal import Decimal
from datetime import datetime
from utils import *
import re, yaml

class StatementRow(object):
    def __init__(self, transaction_id:str = None, row_index:int = None, comment:str = None, name_other:str= None, acount_other:str= None, account_my:str= None, amount:Decimal= None, currency:str= None, date:datetime= None):
        self.transaction_id: str = transaction_id
        self.row_index:int = row_index
        self.comment:str = comment
        self.name_other: str = name_other
        self.account_other:str = acount_other
        self.account_my: str = account_my
        self.amount: Decimal = amount
        self.currency: str = currency
        self.date: datetime = date
        self.dict:Dict = {}

        self.processed:bool = False
        self.processed_info = ()
        self.result_:Callable[[str, str], None] = None
        self.drvid:str  = None

    def re_extract(self, rx:str, s:str):
        m = re.search(rx, s)
        if m:
            self.dict.update(m.groupdict())
        return m

    def re_match(self, rx:str, s:str):
        return re.search(rx, s)

    def set_result(self, op_type, text):
        self.processed = True
        self.processed_info = (op_type, text)
        if self.result_:
            self.result_(op_type, text)

    def is_processed(self):
        return self.processed

class StatementsDriverBase(ABC):

    def __init__(self, filepath:str):
        self.filepath = filepath
        self.max_rows = 0
        self.rows:List[StatementRow] = []
        with open('row_init.yaml', encoding="utf-8") as f:
            self.row_initializer = yaml.load(f, Loader=yaml.FullLoader)

        super().__init__()



    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def close(self):
        pass


    def get_row(self, name, value_getter):
        _globals = {
            **globals(),
            'name': name,
            'value': value_getter
        }
        return eval(self.row_initializer[name], _globals)

    """
    
    """
    def instantinate_row(self, row_index, value_getter):
        return StatementRow(
                transaction_id=self.get_row('transaction_id', value_getter)
              , row_index=row_index
              , comment=self.get_row('comment', value_getter)
              , name_other=self.get_row('name_other', value_getter)
              , acount_other=self.get_row('acount_other', value_getter)
              , account_my=self.get_row('account_my', value_getter)
              , amount=self.get_row('amount', value_getter)
              , currency=self.get_row('currency', value_getter)
              , date=self.get_row('date', value_getter)
            )