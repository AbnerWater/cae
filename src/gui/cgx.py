#!/usr/bin/env python3
# -*- coding: utf-8 -*-


""" © Ihor Mirzov, April 2020
Distributed under GNU General Public License v3.0

Methods for CGX window. """

import os
import time
import logging
try:
    import psutil
except:
    msg = 'Please, install psutil with command:\n'\
        + 'pip3 install psutil'
    sys.exit(msg)

# Kill all CGX processes
def kill():
    for p in psutil.process_iter():
        if p.name() in ['cgx', 'cgx.exe']:
            pid = p.pid
            count = 1
            while psutil.pid_exists(pid):
                try:
                    p.kill()
                except:
                    pass
                time.sleep(0.1)
                count += 1
                if count > 10:
                    logging.error('Can not kill CGX, PID={}.'.format(pid))
                    break
            if not psutil.pid_exists(pid): 
                logging.info('Killed PID={}.'.format(pid))

# Kill child CGX processes
# def kill(parent=None):
#     if parent is None:
#         parent = psutil.Process()
#     for ch in parent.children(recursive=True):
#         pid = ch.pid
#         ch.terminate()
#         if not pid in psutil.pids():
#             print('Killed PID', pid)

def paint_elsets(w, elsets):
    colors = 'rgbymntk'
    i = 0
    for i in range(len(elsets)):
        if elsets[i].upper() == 'ALL':
            elsets.pop(i)
            break
    if len(elsets) > 1:
        for elset in elsets:
            w.post('plus e {} {}'.format(elset, colors[i]))
            i = (i + 1) % len(colors)
