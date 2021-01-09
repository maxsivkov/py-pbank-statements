import logging, logging.config
from config import configuration
from taxerapi import Profile

from action import *

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

def action_test(d:DataDir, config:Configuration, logger:Logger):
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

def main():
    setup_logger('logging.yaml')

    config = configuration()
    d = DataDir(config)
    logger = logging.getLogger(__name__)
    action = config['action'].as_str()
    user_actions = {"init" : action_init
                    , "process": action_process
                    , "push": action_push
                    , "fetch-statements" : action_fetch_statements
                    , "balance" : action_balance
                    }
    if action in user_actions:
        action_user(d, config, logger, user_actions[action])
    else:
        if action == "test":
            action_test(d, config, logger)
        else:
            print(f'Unknown action {action}')

if __name__ == '__main__':
    main()

#https://www.ibancalculator.com/iban_validieren.html