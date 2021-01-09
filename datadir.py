from typing import List, Dict
from dataclasses import dataclass, field
from marshmallow import Schema, fields, post_dump
from marshmallow.utils import EXCLUDE, INCLUDE, RAISE
import marshmallow_dataclass
from decimal import *
from utils import list_files
import confuse
import os, re
import ujson, yaml
import logging
from taxerapi import Configuration as TaxerConfig, ApiClient as TaxerClient, AccountApi as TaxerAccountApi, AccountsApi as TaxerAccountsApi, OperationApi as TaxerOperationApi \
    , Profile, User, UserBankAccount as ApiBankAccount
from utils import get_config_str, get_config_int, get_config_v

@dataclass
class UserAccount:
    id:int = field(default=None)
    balance: Decimal = field(default=None)
    title: str = field(default=None)
    currency: str = field(default=None)
    num: str = field(default=None)
    bank: str = field(default=None)
    mfo: str = field(default=None)
    comment: str = field(default=None)
    tf_bank_place: str = field(default=None)
    tf_bank_swift: str = field(default=None)
    tf_bank_corr: str = field(default=None)
    tf_bank_corr_place: str = field(default=None)
    tf_bank_corr_swift: str = field(default=None)
    tf_bank_corr_account: str = field(default=None)

    class Meta:
        unknown=EXCLUDE
        render_module = ujson

class UserAccounts:
    def __init__(self, accounts:List[UserAccount]):
        self.accounts = accounts

    def find_by_number(self, number:str) -> UserAccount:
        for a in self.accounts:
            if a is not None and a.num is not None and number is not None and a.num.lower() == number.lower():
                return a
        return None

    def find_by_number_exc(self, number: str) -> UserAccount:
        acc:UserAccount = self.find_by_number(number)
        if acc == None: raise Exception(f'account {number} not found')
        return acc

    def exists(self, number:str) -> bool: return self.find_by_number(number) is not None

class DataDir(object):
    accounts_fn:str = "accounts.json"
    config_fn: str = "config.yaml"
    default_rules_folder:str = 'rules'
    default_input_folder:str = 'data_in'
    default_output_folder: str = 'data_out'
    default_first_row: int = 6

    def __init__(self, config:confuse.Configuration):
        self.logger = logging.getLogger(__name__)
        self.__config = config
        self.accounts_folder = self.get_config_str('accounts_folder')
        if self.accounts_folder is None:
            raise ValueError("accounts_folder must be set")
        self.users_root = self.accounts_folder
        if not os.path.exists(self.accounts_folder):
            os.mkdir(self.accounts_folder)
        self.url = self.get_config_str('taxerapi_url', 'http://127.0.0.1:7080')

        self.update_conf()

        self.verbose = config['verbose'].as_number()
        taxer_config: TaxerConfig = TaxerConfig()
        taxer_config.host = self.url
        taxer_config.debug = True if self.verbose else False
        cli: TaxerClient = TaxerClient(configuration=taxer_config)
        self.acc_api = TaxerAccountApi(api_client=cli)
        self.accs_api = TaxerAccountsApi(api_client=cli)
        self.operation_api = TaxerOperationApi(api_client=cli)

        self.logger.info(f'config_dir {config.config_dir()}')
        self.logger.info(f'user_config_path {config.user_config_path()}')
        self.logger.info(f'accounts_folder \'{self.accounts_folder}\'')
        self.logger.info(f'taxer-api url \'{self.url}\'')

    def data_path(self, p:str): return os.path.join(self.accounts_folder, p)

    def update_conf(self):
        self.rules_folder:str = self.get_config_str('rules_folder', DataDir.default_rules_folder)
        self.input_folder: str = self.get_config_str('input_folder', DataDir.default_input_folder)
        self.output_folder: str = self.get_config_str('output_folder', DataDir.default_output_folder)

    def add_config(self, configfn):
        self.__config.add(confuse.ConfigSource(confuse.load_yaml(configfn), configfn))
        self.update_conf()

    def create_folder_not_exists(self, path:str):
        if not os.path.exists(path):
            self.logger.debug(f'Creating folder {path}')
            os.mkdir(path)

    def user_folder(self, userid:int) -> str:
        for user_folder in os.listdir(self.users_root):
            if re.match(f'{userid} \[.*\]', user_folder):
                return user_folder
        raise ValueError(f'folder for {userid} not found')

    def user_folder_path(self, userid:int) -> str: return os.path.join(self.accounts_folder, self.user_folder(userid))
    def user_folder_rules(self, userid: int) -> str: return os.path.join(self.user_folder_path(userid), self.rules_folder)
    def user_folder_input(self, userid: int) -> str: return os.path.join(self.user_folder_path(userid), self.input_folder)

    def user_folder_output(self, userid: int) -> str: return os.path.join(self.user_folder_path(userid), self.output_folder)

    def user_config_path(self, userid: int) -> str: return os.path.join(self.user_folder_path(userid), DataDir.config_fn)

    @property
    def config(self):
        return self.__config

    def get_config_v(self, name: str, default: str = None) -> str: return get_config_v(self.config, name, default)
    def get_config_str(self, name: str, default: str = None) -> str: return get_config_str(self.config, name, default)
    def get_config_int(self, name: str, default: int = None) -> int: return get_config_int(self.config, name, default)

    def Users(self) -> List[int]:
        users:List[int] = []
        for user_folder in os.listdir(self.users_root):
            m = re.match(f'(?P<userid>[0-9]+) \[.*\]', user_folder)
            if m:
                users.append(int(m.group('userid')))
        return users

    def UserAccounts(self, userid:int) -> UserAccounts:
        schema = marshmallow_dataclass.class_schema(UserAccount)
        accounts_path = os.path.join(self.user_folder_path(userid), DataDir.accounts_fn)
        with open(accounts_path, 'r', encoding='utf-8') as f:
            accounts_json = ujson.load(f)
        return UserAccounts(schema().load(accounts_json, many=True, partial=True, unknown=RAISE))

    def UserDataFiles(self, userid:int) -> List[str]: return list_files(self.user_folder_input(userid), r'.*\.xlsx$')

    def UserXLSDataFiles(self, userid: int) -> List[str]:
        return list_files(self.user_folder_input(userid), r'.*\.xls$')

    def UserRules(self, userid: int) -> List[str]: return [f for f in os.listdir(self.user_folder_rules(userid)) if re.match(r'.*\.yaml$', f)]

    def UserTaxNumber(self, userid:int) -> str:
        m = re.match(f'{userid} \[.*;(?P<taxnumber>[0-9]+)\]', self.user_folder(userid))
        return m.group('taxnumber') if m else None

    def UpdateUsers(self):
        # call profile
        self.logger.debug(f'Getting profile...')
        profile: Profile = self.acc_api.get_account_api()
        u: User
        for u in profile.users:
            # user_folder = os.path.join(account_folder, f'{u.id} [{u.title_name}]')
            user_folder = self.data_path(f'{u.id} [{u.title_name};{u.id_key}]')
            if not os.path.exists(user_folder):
                self.logger.debug(f'Creating folder {user_folder}')
                os.mkdir(user_folder)
                # Store default config
                user_config: Dict = {
                    'datafile': {
                        'first_row': self.get_config_int('first_row', DataDir.default_first_row)
                    },
                    'input_folder': self.get_config_str('input_folder', DataDir.default_input_folder),
                    'output_folder': self.get_config_str('output_folder', DataDir.default_output_folder),
                }
                with open(self.user_config_path(u.id), encoding='utf8', mode='w') as f:
                    yaml.dump(user_config, f)
            self.create_folder_not_exists(self.user_folder_rules(u.id))
            self.create_folder_not_exists(self.user_folder_input(u.id))
            self.create_folder_not_exists(self.user_folder_output(u.id))

    def GetUserAccounts(self, userid:int) -> List[ApiBankAccount]: return self.accs_api.get_user_accounts_all(userid)

    def UpdateUserAccounts(self, userid:int):
        accounts_path = os.path.join(self.user_folder_path(userid), DataDir.accounts_fn)
        self.logger.debug(f'Getting accounts for {userid}...')
        accounts: List[ApiBankAccount] = self.GetUserAccounts(userid)
        with open(accounts_path, mode='w', encoding='utf-8') as outfile:
            ujson.dump([a.to_dict() for a in accounts], outfile, ensure_ascii=False, sort_keys=True, indent=4)

    def UpdateAll(self):
        self.UpdateUsers()
        for userid in self.Users():
            self.UpdateUserAccounts(userid)

    def UpdateUsers1(self):

        # call profile
        self.logger.debug(f'Getting profile...')
        profile:Profile = self.acc_api.get_account_api()
        u:User
        for u in profile.users:
            #user_folder = os.path.join(account_folder, f'{u.id} [{u.title_name}]')
            user_folder = self.data_path(f'{u.id} [{u.title_name}]')
            self.logger.debug(f'Getting accounts for {u.id}...')
            accounts:List[ApiBankAccount] = self.accs_api.get_user_accounts_all(u.id)
            self.create_folder_not_exists(user_folder)
            rules_folder:str=os.path.join(user_folder, 'rules')
            if not os.path.exists(user_folder):
                self.logger.debug(f'Creating folder {user_folder}')
                os.mkdir(user_folder)
            # dump account
            accounts_file:str=os.path.join(user_folder, 'accounts.json')
            with open(accounts_file, mode='w', encoding='utf-8') as outfile:
                a:Dict = {}
                for acc in accounts:
                    a[acc.id] = {
                        'title' : acc.title,
                        'id': acc.id,
                        'currency': acc.currency,
                        'num': acc.num,
                        'bank': acc.bank,
                        'mfo': acc.mfo
                    }
                ujson.dump(a, outfile, ensure_ascii=False, sort_keys=True, indent=4)
                self.logger.debug(f'Saving accounts \'{accounts_file}\'')

    def GetBankAccounts(self, userid:int) -> List[ApiBankAccount]: return self.accs_api.get_user_accounts_all(userid)

    def ProcessOperation(self, operation:str, userid, payload):
        ops = {
            'flowoutgo' : self.operation_api.post_add_flow_outgo_operation
            , 'flowincome' : self.operation_api.post_add_flow_income_operation
            , 'withdrawal': self.operation_api.post_add_withdrawal_operation
            , 'currencyexchange': self.operation_api.post_add_currency_exchange_operation
        }
        f = ops.get(operation.lower())
        if not f: raise ValueError(f'operation {operation.lower()} not registered')
        f(userid, payload)

