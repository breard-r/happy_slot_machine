#!/bin/env python
#
# Copyright (c) 2015 Rodolphe Breard
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

"""
Happy Slot Machine

This software is a python slot machine that cheats on the users. The numbers
selection function is designed so it is very unlikely to get three identical
numbers and increases the chances for the two firsts numbers to be the same.
"""

from collections import Counter
from random import randint
import curses
import time
import os


def get_asset(asset_name):
    '''
    Loads an asset in memory.
    '''
    file_name = '{}.txt'.format(asset_name)
    asset_path = os.path.join('assets', file_name)
    with open(asset_path) as f:
        return [l.rstrip('\n') for l in f.readlines()]

slot_asset = get_asset('slot')
numbers_assets = [get_asset(n) for n in range(10)]
results_assets = {
    'success': get_asset('success'),
    'failure': get_asset('failure'),
    'reset': get_asset('reset'),
}


def get_numbers():
    '''
    Returns a list of 3 not-so-random numbers.
    See the attached README.md for more details.
    '''
    nbs = [randint(0, 9) for _ in range(4)]
    set_len = len(set(nbs))
    if set_len in [2, 3]:
        nbs.sort(key=Counter(nbs).get, reverse=True)
        nbs[2], nbs[3] = nbs[3], nbs[2]
        rand_position = randint(1, 100)
        if rand_position < 50:
            nbs[0], nbs[2] = nbs[2], nbs[0]
        elif rand_position < 25:
            nbs[1], nbs[2] = nbs[1], nbs[0]
    return nbs[:3]


def draw_result(stdscr, status):
    '''
    Draws the status of the current round.

    stdscr: curses window object
    status: string, must be either "success", "failure" or "reset"
    '''
    for i, line in enumerate(results_assets[status]):
        stdscr.addstr(i + 13, 1, line)
    stdscr.refresh()


def draw_slot(stdscr, offset):
    '''
    Draws an empty slot.

    stdscr: curses window object
    offset: integer representing the slot's position
    '''
    off = offset * (len(slot_asset[0]) + 3) + 1
    for i, line in enumerate(slot_asset):
        stdscr.addstr(i + 2, off, line)


def draw_slots(stdscr):
    '''
    Draws the 3 empty slots.

    stdscr: curses window object
    '''
    for i in range(3):
        draw_slot(stdscr, i)
    stdscr.refresh()


def draw_raw_number(stdscr, nb, offset):
    '''
    Draws a number in a given slot.

    stdscr: curses window object
    nb: integer representing number to display
    offset: integer representing the slot's position
    '''
    nb = numbers_assets[nb]
    off = offset * (len(nb[0]) + 13) + 6
    for i, line in enumerate(nb):
        stdscr.addstr(i + 4, off, line)
    stdscr.refresh()


def random_excepted(nb):
    '''
    Returns a random number that cannot be the one passed as a parameter.

    nb: integer representing the number to avoid
    '''
    while True:
        n = randint(0, 9)
        if n != nb:
            return n


def numbers_to_display(nb):
    '''
    Yields a series of numbers that should be displayed on a slot.

    nb: integer representing the last number to be yielded
    '''
    n = None
    for _ in range(10):
        time.sleep(0.15)
        n = random_excepted(n)
        yield n
    yield nb


def draw_number(stdscr, nb, offset):
    '''
    Draws a number in a given slot with an animation.

    stdscr: curses window object
    nb: integer representing number to display
    offset: integer representing the slot's position
    '''
    for n in numbers_to_display(nb):
        draw_raw_number(stdscr, n, offset)


def play(stdscr):
    '''
    Plays a new round.

    stdscr: curses window object
    '''
    nbs = get_numbers()
    draw_slots(stdscr)
    draw_result(stdscr, 'reset')
    for i, nb in enumerate(nbs):
        draw_number(stdscr, nb, i)
    draw_result(stdscr, 'success' if len(set(nbs)) == 1 else 'failure')


def clean_input(stdscr):
    '''
    Removes all unread data from the standard input.
    '''
    stdscr.nodelay(1)
    while stdscr.getch() != -1:
        pass
    stdscr.nodelay(0)


def main(stdscr):
    '''
    Initialize the screen and the commands.

    stdscr: curses window object
    '''
    height, width = stdscr.getmaxyx()
    curses.curs_set(0)
    stdscr.clear()

    stdscr.addstr(" SLOT MACHINE", curses.A_REVERSE)
    stdscr.chgat(-1, curses.A_REVERSE)

    h = height - 1
    stdscr.addstr(h, 0, " Press Q to quit, P to play.", curses.A_REVERSE)
    stdscr.chgat(h, 0, -1, curses.A_REVERSE)
    draw_slots(stdscr)

    while True:
        stdscr.refresh()
        clean_input(stdscr)
        key = stdscr.getch()
        if key in [ord('q'), ord('Q')]:
            break
        elif key in [ord('p'), ord('P')]:
            play(stdscr)


if __name__ == '__main__':
    curses.wrapper(main)
