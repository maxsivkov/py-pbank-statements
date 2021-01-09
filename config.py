import confuse
import os
from cmdline_arguments import parser
def configuration() -> confuse.Configuration:
    conf = confuse.Configuration('taxer-statements')
    if os.path.exists('config.yaml'):
        conf.set_file('config.yaml')
    #args, unknown_args = parser().parse_known_args()
    args = parser().parse_args()
    conf.set_args(args, dots=True)
    return conf