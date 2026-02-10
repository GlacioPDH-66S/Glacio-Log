#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 22:24:00 2026

@author: paultudes
"""

OPTIONS = ["---","Create", "Edit", 
           "Remove", "Single Plot"]#,"Seasonal plot"]

OPTIONS_LITE = ["---","Create", "Edit", "Single Plot"]#,"Seasonal plot"]

IACS_GRAINS = ["PP", "DF", "RG", "RGwp", "FC", "DH", "SH", "MF", "IF", "Not measured"]

SNOW_HARDNESS = ["F", "4F", "1F", "P", "K", "I"]

TEMP_UNITS = ["K", "°C", "°F"]

HARDNESS_MAP = {
    "F": 1,
    "4F": 2,
    "1F": 3,
    "P": 4,
    "K": 5,
    "I": 6
}

GRAIN_COLORS = {
    "PP": "#00FF00",
    "DF": "#228B22",
    "RG": "#FFB6C1",
    "RGwp": "#FFB6C1",
    "FC": "#ADD8E6",
    "DH": "#0000FF",
    "SH": "#FF00FF",
    "MF": "#FF0000",
    "IF": "#00FFFF",
    "Not measured":'#FFFFFF'
    
}

IACS_SYMBOLS = {
    "PP": "+",
    "DF": "⁄",
    "RG": "●",
    "RGwp": "●̸",
    "FC": "◻︎",
    "DH": "^",
    "SH": "v",
    "MF": "o",
    "IF": "■",
    "Not measured":' '
}