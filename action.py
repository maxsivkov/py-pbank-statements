from typing import List, Dict, Tuple
from datadir import DataDir, UserAccounts, UserAccount
from confuse import Configuration
from logging import Logger
from stmt_driver_xlsx import XlsxDriver
from utils import list_files, get_config_int
from decimal import Decimal
import os, datetime, re, ujson
from bank_api import PbApi

def action_user(d:DataDir, config:Configuration, logger:Logger, f):
    for userid in d.Users(): f(d, config, logger, userid)

def action_init(d:DataDir, config:Configuration, logger:Logger, userid:int):
    d.UpdateAll()

def action_process(d:DataDir, config:Configuration, logger:Logger, userid:int):
    if not os.path.exists(d.user_config_path(userid)):
        raise ValueError(f'config file for user {userid} not found')
    user_data = DataDir(config)
    user_data.add_config(d.user_config_path(userid))

    acc:UserAccounts = d.UserAccounts(userid)

    # try to convert xls to xlsx
    for datafile in d.UserXLSDataFiles(userid):
        try:
            import pyexcel as p

            xlsx_file = datafile + 'x'
            logger.info(f'Trying to convert {datafile} to {xlsx_file}')
            if os.path.exists(xlsx_file):
                logger.info(f'IGNORED (Already exists) {xlsx_file}')
            else:
                p.save_book_as(file_name=datafile,
                           dest_file_name=xlsx_file)
                logger.info(f'Converted')
        except ImportError as e:
            logger.error('Error during xls to xlsx conversion', 'Error', exc_info=e)

    datafiles : List[str] = d.UserDataFiles(userid)
    if len(datafiles) == 0:
        logger.error('No xlsx files')
    import_tag : str = f'IMP-{datetime.date.today().strftime("%Y-%m-%d")}'
    for datafile in d.UserDataFiles(userid):
        #datafile_parts:str = os.path.splitext(os.path.basename(datafile))
        outputfn = os.path.join(user_data.user_folder_output(userid), os.path.basename(datafile))

        stmt_data = XlsxDriver(filepath=datafile, output_file_path=outputfn, first_row=get_config_int(user_data.config, 'datafile.first_row'))
        stmt_data.read()

        from execution_context import ExecutionContext

        ec = ExecutionContext(stmt_data, acc, list_files('rules', r'.*\.yaml'), d.UserTaxNumber(userid), d.user_folder_output(userid))
        (total_rows, rows_processed) = ec.execute(import_tag)
        stmt_data.close()
        logger.info(f'DONE. Processed {total_rows} rows, prepared {rows_processed} statements with tag {import_tag}')


def action_push(d:DataDir, config:Configuration, logger:Logger, userid:int):
    if not os.path.exists(d.user_config_path(userid)):
        raise ValueError(f'config file for user {userid} not found')
    user_data = DataDir(config)
    user_data.add_config(d.user_config_path(userid))
    output_folder = d.user_folder_output(userid)
    if not os.path.exists(output_folder):
        return
        # raise ValueError(f'folder does not exist {output_folder}')
    processed_files = 0
    for f in sorted(os.listdir(output_folder)):
        m = re.match(f'(?P<index>[0-9]+)-(?P<operation>\w+)-(?P<operation_id>\w+).json', f)
        if not m: continue
        index = m.group('index')
        operation = m.group('operation')
        operation_id = m.group('operation_id')
        print(f'{index} : processing {operation} / {operation_id}')
        with open(os.path.join(output_folder, f), encoding='utf8') as json_file:
            data = ujson.load(json_file)
            user_data.ProcessOperation(operation, userid, data)
            processed_files = processed_files + 1
    print(f'DONE. Processed {processed_files} statements')

def action_fetch_statements(d:DataDir, config:Configuration, logger:Logger, userid:int):
    if not os.path.exists(d.user_config_path(userid)):
        raise ValueError(f'config file for user {userid} not found')
    user_data = DataDir(config)
    user_data.add_config(d.user_config_path(userid))
    accounts = user_data.UserAccounts(userid)
    bankApi:PbApi = PbApi(user_data)
    logger.info(f'getting statements for period {bankApi.first_date} - {bankApi.last_date}')
    bankApi.fetch_statements()
    num_entries = bankApi.store(os.path.join(user_data.user_folder_input(userid), f'{bankApi.period_str}.xlsx'), get_config_int(user_data.config, 'datafile.first_row'))
    logger.info(f'{num_entries} statements stored in {bankApi.period_str}.xlsx')

def action_balance(d:DataDir, config:Configuration, logger:Logger, userid:int):
    if not os.path.exists(d.user_config_path(userid)):
        raise ValueError(f'config file for user {userid} not found')
    user_data = DataDir(config)
    user_data.add_config(d.user_config_path(userid))
    accounts = user_data.UserAccounts(userid)
    bankApi:PbApi = PbApi(user_data)
    balance = {}
    for b in bankApi.balance():
        amount = Decimal(b['balanceIn'])
        balance[b["acc"]] = {'bank_balance': Decimal(b['balanceIn']), 'currency': b["currency"]}

    userAccounts = user_data.GetUserAccounts(userid)
    for a in user_data.GetUserAccounts(userid):
        _d = {'taxer_balance': Decimal(a.balance), 'currency': a.currency}
        num = a.num if a.num else a.title
        if num in balance:
            balance[num].update(_d)
        else:
            balance[num] = _d
    logger.info(f'{"Номер счета": <30} {"Банк": >15} {"Taxer": >15} {"Валюта": <3}')
    for acc in balance:
        b = balance[acc]
        bank_balance = b['bank_balance'] if 'bank_balance' in b else Decimal(0)
        taxer_balance = b['taxer_balance'] if 'taxer_balance' in b else Decimal(0)
        currency = b["currency"]
        if bank_balance.is_zero() and taxer_balance.is_zero(): continue
        logger.info(f'{acc: <30} {bank_balance: >15.2f} {taxer_balance: >15.2f} {currency: <3}')