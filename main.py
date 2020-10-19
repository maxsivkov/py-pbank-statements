from typing import List, Dict, Tuple
import re
import os
import logging, logging.config
import ujson, yaml
import datetime
from config import configuration
from datadir import DataDir
from stmt_driver_xlsx import XlsxDriver
from utils import list_files, get_config_str, get_config_int
from taxerapi import Profile


def setup_logger(filename:str):
    import yaml
    if os.path.exists(filename):
        with open(filename, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                print(f'Setup logging from {filename}')
                logging.config.dictConfig(config)
            except Exception as e:
                print(e)
                print('Error in Logging Configuration.')
                logging.basicConfig(level=logging.INFO)
    else:
        print(f'logging config file {filename} not found.')
        logging.basicConfig(level=logging.INFO)
setup_logger('logging.yaml')


config = configuration()
d = DataDir(config)
logger = logging.getLogger(__name__)

if config['action'].as_str() == 'init':
    d.UpdateAll()

if config['action'].as_str() == 'process':
    for userid in d.Users():

        if not os.path.exists(d.user_config_path(userid)):
            raise ValueError(f'config file for user {userid} not found')
        user_data = DataDir(config)
        user_data.add_config(d.user_config_path(userid))

        acc = d.UserAccounts(userid)

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

if config['action'].as_str() == 'push':
    for userid in d.Users():
        if not os.path.exists(d.user_config_path(userid)):
            raise ValueError(f'config file for user {userid} not found')
        user_data = DataDir(config)
        user_data.add_config(d.user_config_path(userid))
        output_folder = d.user_folder_output(userid)
        if not os.path.exists(output_folder):
            continue
            #raise ValueError(f'folder does not exist {output_folder}')
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

if config['action'].as_str() == 'test':
    logger.info(f'\nAction {config["action"].as_str()}\n')
    logger.info(f'Requesting Profile from TaxerApi')
    profile: Profile = d.acc_api.get_account_api()
    logger.info(f'Account id: {profile.account_id}')
    logger.info(f'Account name: {profile.account_name}')
    logger.info(f'Account users list')
    for user in profile.users:
        logger.info(f'  user_id: {user.id}')
        logger.info(f'  user_tax: {user.id_key}')
        logger.info(f'  user_title: {user.title_name}')

#https://www.ibancalculator.com/iban_validieren.html