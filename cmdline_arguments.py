import argparse, os
def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Command line options')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true", default=False)
    parser.add_argument("-u", "--taxerapi_url", nargs='?', help="set taxer-api URL", default=os.getenv('BSTMT_TAXER_API_URL', 'http://127.0.0.1:7080'))
    parser.add_argument("-a", "--accounts_folder", nargs='?', help="accounts folder", default=os.getenv('BSTMT_ACCOUNTS_DIR', 'data'))

    parser.add_argument('action', help='Action: init - initialize; process - process input files, prepare json output files; push - upload json files to taxer-api')
    return parser