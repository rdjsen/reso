# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 15:56:14 2020

@author: rdjse
"""

#wrapper for resolution tracker

from class_def import resolutions
from os import path
from os import getcwd

#file location

test = resolutions(path.join(getcwd(), "ryan.csv"))

test.status()

test.update_percentage()

test.status()
