#!/usr/bin/env python3

# pylint: disable=C0111     # docstrings are always outdated and wrong
# pylint: disable=W0511     # todo is encouraged
# pylint: disable=R0902     # too many instance attributes
# pylint: disable=C0302     # too many lines in module
# pylint: disable=C0103     # single letter var names
# pylint: disable=R0911     # too many return statements
# pylint: disable=R0912     # too many branches
# pylint: disable=R0915     # too many statements
# pylint: disable=R0913     # too many arguments
# pylint: disable=R1702     # too many nested blocks
# pylint: disable=R0914     # too many local variables
# pylint: disable=R0903     # too few public methods
# pylint: disable=E1101     # no member for base
# pylint: disable=W0201     # attribute defined outside __init__
## pylint: disable=W0703     # catching too general exception

import click
from icecream import ic
from kcl.inputops import input_iterator
from kcl.iterops import randomize_iterator

ic.configureOutput(includeContext=True)
# import IPython; IPython.embed()
# import pdb; pdb.set_trace()
# from pudb import set_trace; set_trace(paused=False)

APP_NAME = 'randompipe'


@click.command()
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.option('--head', type=int)
@click.option('--max-wait-time', type=float, default=1.0)
@click.option('--min-pool-size', type=int, default=2)
@click.option('--not-random', is_flag=True)
@click.option("--printn", is_flag=True)
def cli(verbose,
        debug,
        head,
        not_random,
        printn,
        max_wait_time,
        min_pool_size):

    assert max_wait_time
    assert min_pool_size

    if min_pool_size < 2:
        min_pool_size = 2

    null = not printn
    random = not not_random

    byte = b'\n'
    if null:
        byte = b'\x00'

    iterator = input_iterator(null=null, verbose=verbose, head=head)

    if random:
        iterator = randomize_iterator(iterator,
                                      verbose=verbose,
                                      debug=debug,
                                      max_wait_time=max_wait_time,
                                      min_pool_size=min_pool_size)

    for item in iterator:
        print(item, end=byte.decode('utf8'))

