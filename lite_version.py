#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 15:43:29 2026

@author: paultudes
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Version:
    number: str
    release_date: str
    description: str


# Version historic
VERSION_HISTORY = [
    Version(
        number="0.1.0",
        release_date="2026-01-24",
        description="Initial internal prototype"
    ),
    Version(
        number="0.2.0",
        release_date="2026-01-30",
        description="Complete reorganization of the interface and various menus, clarification of the algorithm."
    ),
    Version(
        number="0.3.0",
        release_date="2026-02-04",
        description="User configuration and interactive viewer"
    ),
    Version(
        number="0.4.0-beta",
        release_date="2026-02-04",
        description="Beta testing"
    ),
    Version(
        number="1.0.1",
        release_date="2026-02-04",
        description="Path midification"
    ),
    Version(
        number="1.1.1",
        release_date="2026-02-04",
        description="Temperature and LWC in stratigraphic plot"
    ),
    Version(
        number="1.1.2",
        release_date="2026-02-07",
        description="Modify user config"
    ),
    Version(
        number="1.2.2",
        release_date="2026-02-07",
        description="Lite version for Streamlit Cloud"
    ),
]

# Actual version 
CURRENT_VERSION = VERSION_HISTORY[-1]

__version__ = CURRENT_VERSION.number