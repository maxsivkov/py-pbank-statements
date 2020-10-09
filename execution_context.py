from typing import Dict, Tuple
import ujson, logging
from utils import *
import yaml
from stmt_driver_base import StatementsDriverBase, StatementRow
from datadir import UserAccounts

class ExecutionContext(object):
    def __init__(self, stmts:StatementsDriverBase, accounts:UserAccounts, rules:List[str], tax_number:str, output_folder:str):
        self.rules:Dict = {}
        self.accounts = accounts
        self.tax_number = tax_number
        self.output_folder = output_folder
        for filepath in rules:
            with open(filepath, encoding="utf-8") as f:
                y = yaml.load(f, Loader=yaml.FullLoader)
                self.rules[y['id'] if 'id' in y else os.path.splitext(os.path.basename(filepath))[0]] = y
        self.stmts = stmts

    def execute_row(self, row_index, row:StatementRow, rule_id:str, rule, logger, tag:str) -> bool:
        re_extract = lambda rx, s: row.re_extract(rx, s)
        re_match = lambda rx, s: row.re_match(rx, s)
        find_prev_record = lambda idx, f: self.find_prev_record(idx, f)
        find_next_record = lambda idx, f: self.find_next_record(idx, f)

        _globals = {
            **globals(),
            'rule_id': rule_id,
            'logger': logger,
            'row': row,
            'row_index': row_index,
            'find_prev_record': find_prev_record,
            'find_next_record': find_next_record,
            're_extract': re_extract,
            're_match': re_match,
            'accounts' : self.accounts,
            'taxno' : self.tax_number,
            'import_tag': tag
        }
        run_rule = lambda n, r, g=None, l=None: r(rule[n], _globals if g is None else g, l) if n in rule else None
        exec_rule = lambda n, g=None, l=None: run_rule(n, exec, g, l)
        eval_rule = lambda n, g=None, l=None: run_rule(n, eval, g, l)

        operation_id = eval_rule('operation-id') or 'unknown'
        operation_type = eval_rule('operation-type') or 'unknown'

        exec_rule('before-condition')
        condition_result = eval_rule('condition')
        if condition_result and row.processed:
            raise Exception(f'row {row.drvid} already processed. check logic')
        exec_rule('after-condition')
        exec_rule(f'condition-{condition_result}')

        if condition_result:
            output = eval_rule('output')
            row.set_result(operation_type, f'{rule_id}\n{operation_type}')

            json_content = ujson.dumps(output, ensure_ascii=False)
            file_name = f'{row.row_index:03d}-{operation_type}-{row.transaction_id}.json'
            logger.debug('output [%s] %s %s', operation_type, file_name, json_content)
            with open(os.path.join(self.output_folder, file_name), mode='w', encoding="utf-8") as f:
                f.write(json_content)
        return condition_result

    def execute(self, tag:str) -> Tuple[int, int] :
        rows = self.stmts.rows
        processed_rows = 0
        for row_index, row in enumerate(rows):
            for rule_id, rule in self.rules.items():
                logger = logging.getLogger(f'{rule_id}/{row.drvid}')
                processed_rows += 1 if self.execute_row(row_index, row, rule_id, rule, logger, tag) else 0
        return (len(rows), processed_rows)

    def find_prev_record(self, record_index: int, f) -> Tuple:
        if record_index is None: raise Exception(f'record_index is not defined')
        for idx in reversed(range(0, record_index)):
            if f(self.stmts.rows[idx]): return (idx, self.stmts.rows[idx])
        return (None, None)

    def find_next_record(self, record_index: int, f) -> Tuple:
        for idx in range(record_index + 1, self.stmts.max_rows):
            if f(self.stmts.rows[idx]): return (idx, self.stmts.rows[idx])
        return (None, None)
