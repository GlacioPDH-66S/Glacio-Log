#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 21:47:38 2026

@author: paultudes
"""

import streamlit as st 

css = """
<style>

/* ---------- SECTION TITLES ---------- */
.section-box {
    padding: 0.8rem 1rem;
    margin: 1.2rem 0 0.8rem 0;
    border-radius: 10px;
}
.section-box h2 {
    margin: 0;
    font-size: 2rem;
    font-weight: 600;
    color: var(--text-color);
}

/* ---------- CARDS ---------- */
.card {
    background-color: #0068C9;
    padding: 0.5rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
}
.card-divider {
    background-color: rgba(0, 104, 201, 1);
    height: 2px;
    border-radius: 10px;
    margin: 1.5rem 1;
}
.card-invisible {
    background-color: rgba(0, 104, 201, 0);
    height: 2px;
    border-radius: 10px;
    margin: 0.2rem 0;
}

/* ---------- BADGES ---------- */
.badge {
    font-size: 0.7rem;
    padding: 0.2em 0.6em;
    border-radius: 999px;
    margin-left: 0.6rem;
    vertical-align: middle;
}
.badge-success { background-color: #4CAF50; }
.badge-warning { background-color: #FBC02D; color: #222; }
.badge-info    { background-color: #1E88E5; color: #fff; }

<style>
"""

def style():
    st.markdown(css, unsafe_allow_html=True)
    
