import confuse
import os
from cmdline_arguments import parser
def configuration() -> confuse.Configuration:
    conf = confuse.Configuration('taxer-statements')
    if os.path.exists('config.yaml'):
        conf.set_file('config.yaml')
    args = parser().parse_args()
    conf.set_args(args)
    return conf