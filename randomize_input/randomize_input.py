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

import secrets
import sys
import time

import click
from asserttool import nevd
from enumerate_input import iterate_input


def eprint(*args, **kwargs):
    if 'file' in kwargs.keys():
        kwargs.pop('file')
    print(*args, file=sys.stderr, **kwargs)


try:
    from icecream import ic  # https://github.com/gruns/icecream
except ImportError:
    ic = eprint


def append_to_set(*,
                  iterator,
                  the_set: set,
                  max_wait_time: float,
                  min_pool_size: float,  # the_set always has 1 item
                  verbose: bool = False,
                  debug: bool = False,
                  ):

    if verbose:
        ic(max_wait_time, min_pool_size)

    assert max_wait_time > 0.01
    assert min_pool_size >= 2

    start_time = time.time()
    time_loops = 0
    while_loops = 0
    while len(the_set) < min_pool_size:
        loop_start_time = time.time()
        time_loops = 0
        while_loops += 1

        # add to the_set for max_wait_time
        while (time.time() - loop_start_time) < max_wait_time:
            time_loops += 1
            try:
                the_set.add(next(iterator))
            except StopIteration:
                pass

            if time_loops == 3:
                ic('Waiting for:', min_pool_size)

        if time_loops > 1:
            ic(min_pool_size, 'was not reached in', max_wait_time, time_loops)
            #{}s so actual wait time was: {}x {}s\n".format(min_pool_size, max_wait_time, time_loops, max_wait_time * time_loops))

        if len(the_set) < min_pool_size:
            ic(len(the_set), 'waiting for', min_pool_size)

    ic(while_loops, len(the_set), time.time() - start_time)
    assert time_loops > 0
    return the_set


# add time-like memory limit
# the longer the max_wait, the larger buffer_set will be,
# resulting in better mixing
def randomize_input(iterator, *,
                    min_pool_size: int,
                    max_wait_time,
                    buffer_set=None,
                    verbose: bool = False,
                    debug: bool = False):

    assert max_wait_time
    assert min_pool_size

    if min_pool_size < 2:
        min_pool_size = 2

    if not buffer_set:
        buffer_set = set()
        try:
            buffer_set.add(next(iterator))
        except StopIteration:
            pass

    buffer_set = append_to_set(iterator=iterator,
                               the_set=buffer_set,
                               min_pool_size=min_pool_size,
                               max_wait_time=max_wait_time,
                               verbose=verbose,
                               debug=debug)

    while buffer_set:
        try:
            buffer_set.add(next(iterator))
            buffer_set.add(next(iterator))
        except StopIteration:
            pass

        buffer_set_length = len(buffer_set)
        random_index = secrets.randbelow(buffer_set_length)
        next_item = list(buffer_set).pop(random_index)
        buffer_set.remove(next_item)
        if debug:
            ic('Chose 1 item out of:', buffer_set_length)

        if verbose or debug:
            ic(len(buffer_set), random_index, next_item)

        yield next_item


@click.command()
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.option('--head', type=int)
@click.option('--max-wait-time', type=float, default=1.0)
@click.option('--min-pool-size', type=int, default=2)
@click.option('--not-random', is_flag=True)
@click.pass_context
def cli(ctx,
        verbose: bool,
        debug: bool,
        head: int,
        not_random: bool,
        max_wait_time: float,
        min_pool_size: int,
        ):

    ctx.ensure_object(dict)
    assert max_wait_time
    assert min_pool_size

    if min_pool_size < 2:
        min_pool_size = 2

    random = not not_random

    null, end, verbose, debug = nevd(ctx=ctx,
                                     printn=False,
                                     ipython=False,
                                     verbose=verbose,
                                     debug=debug,)

    iterator = iterate_input(iterator=None,
                             disable_stdin=False,
                             dont_decode=True,  # stdin is bytes
                             tail=None,
                             skip=None,
                             null=null,
                             input_filter_function=None,
                             verbose=verbose,
                             debug=debug,
                             random=False,
                             loop=None,
                             head=head,)

    if random:
        iterator = randomize_input(iterator,
                                   verbose=verbose,
                                   debug=debug,
                                   max_wait_time=max_wait_time,
                                   min_pool_size=min_pool_size)

    for item in iterator:
        print(item, end=end)

