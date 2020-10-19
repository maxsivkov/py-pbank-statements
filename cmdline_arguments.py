import argparse, os
from datadir import  DataDir
def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Command line options')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true", default=False)
    parser.add_argument("-u", "--taxerapi_url", nargs='?', help="TaxerApi URL", default=os.getenv('BSTMT_TAXER_API_URL', 'http://127.0.0.1:7080'))
    parser.add_argument("-a", "--accounts_folder", nargs='?', help="accounts folder", default=os.getenv('BSTMT_ACCOUNTS_DIR', 'data'))

    parser.add_argument("-i", "--input_folder", nargs='?', help="input folder",
                        default=os.getenv('BSTMT_INPUT_DIR', DataDir.default_input_folder))
    parser.add_argument("-o", "--output_folder", nargs='?', help="output folder",
                        default=os.getenv('BSTMT_OUTPUT_DIR', DataDir.default_output_folder))
    parser.add_argument("-r", "--first_row", nargs='?', help="first row",
                        default=os.getenv('BSTMT_FIRST_ROW', DataDir.default_first_row))
    parser.add_argument('action', help='Action: init - initialize; process - process input files, prepare json output files; push - upload json files to taxer-api, test')
    return parser