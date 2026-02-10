#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 20:55:39 2026

@author: paultudes
"""

# ============================================================
# %% IMPORTS
# ============================================================

import streamlit as st
import json
from pathlib import Path
import uuid
from datetime import date
import os

from utilities.styles import style
from utilities.functions import *
from utilities.constants import OPTIONS, IACS_GRAINS, SNOW_HARDNESS, TEMP_UNITS
from version import __version__

# ============================================================
# %% APP HEADER
# ============================================================

st.set_page_config(
    page_title="Glacio-Log",
    page_icon="❄",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:ptudes@mtu.edu',
        'Report a bug': "mailto:ptudes@mtu.edu",
        "About": f"""
                Glacio-Log is an open-source application developed by Paul Tudès
                (Michigan Technological University - Atmospheric sciences program).\n\n 
                This application is designed for managing, visualizing, 
                and analyzing snow profiles and snow pit data. 
                It allows users to create, edit, and visualize snow layers, grain type, density, 
                temperature, and liquid water content (LWC).\n\n
                Glacio-Log — version {__version__}
                  """
    }
)

BASE_DIR = Path.cwd().parent

style()

# === Session_state ===
if st.session_state.get("__force_reset__", False):
    st.session_state.clear()
    st.session_state["__force_reset__"] = False

init_session_state()
init_profile_session_state()

st.title("Glacio-Log ❄")
st.caption("Snow pit acquisition, edition and visualization")
card()

# --- First use ---
config_path = "utilities/user_config.json"
config_exists = os.path.exists(config_path)

if config_exists:
    with open(config_path, "r") as f:
        user_config = json.load(f)

    SITES = user_config["sites"]
    SEASONS = user_config["seasons"]
    init_site_season_state(user_config)

    st.session_state.config_validated = True

if not st.session_state.config_validated:
    st.subheader("New user")
    st.caption("Create your working environment")

    site = st.text_input(
        "Name of the site(s) (separated by commas)",
        key="site_input"
    )

    season = st.text_input(
        "Season e.g. (separated by commas)",
        value="2025-2026",
        key="season_input"
    )

    export_data_folder = "{site}/{season}/clean_data/"
    export_plot_folder = "{site}/{season}/plot/"

    st.caption("""
    We recommend a tree structure with "site" and "season" enclosed in curly braces so that the application 
    can automatically sort your results according to the date and site you chose when creating the Snowpit.
    """)

    st.session_state.mode_locked = True

    if site.strip():
        col_left, col_center, col_right = st.columns([1, 1.12, 0.49])

        with col_center:
            validate = st.button(
                "Validate configuration",
                type="primary"
            )

        if validate:
            user_config = {
                "sites": parse_list(site),
                "seasons": parse_list(season),
            }

            with open(config_path, "w") as f:
                json.dump(user_config, f, indent=2)

            create_file_tree(
                base_dir=BASE_DIR,
                sites=user_config["sites"],
                seasons=user_config["seasons"],
                data_template=export_data_folder,
                plot_template=export_plot_folder,
            )

            st.session_state.config_saved = True
            st.session_state.config_validated = True
            st.rerun()

if st.session_state.config_saved:
    st.success("Configuration saved successfully")

    st.info(
        "Your working environment is ready.\n\n"
        "Click below to continue."
    )

    col_left, col_center, col_right = st.columns([1, 0.76, 1])

    with col_center:
        continue_app = st.button(
            "Continue to application",
            type="primary"
        )

    if continue_app:
        st.session_state.config_validated = True
        st.session_state.config_saved = False
        st.session_state.mode_locked = False
        st.rerun()
  
# --- Modify config ---
if st.session_state.modify_config:
    st.session_state.mode_locked = True
    st.subheader("Modify your user configuration")
    
    for k in ("reset_add_site", "reset_remove_site", "reset_add_season", "reset_remove_season"):
        if k not in st.session_state:
            st.session_state[k] = False
            
    # Add site       
    if st.session_state.reset_add_site:
        st.session_state["add_site"] = ""
        st.session_state.reset_add_site = False

    site_input = st.text_input("Add a new site", key="add_site")

    if st.button("Add site"):
        if site_input and site_input not in SITES:
            SITES.append(site_input)
            user_config["sites"] = SITES
            with open(config_path, "w") as f:
                json.dump(user_config, f, indent=4)
            st.session_state.reset_add_site = True
            st.rerun()
     
    # Remove site
    if st.session_state.reset_remove_site:
        st.session_state["remove_site"] = ""
        st.session_state.reset_remove_site = False
    
    if len(SITES) > 1:
        site_remove = st.text_input("Name of site to be removed", key="remove_site")
        
        if st.button("Remove site"):
            if site_remove in SITES:
                SITES.remove(site_remove)
                user_config["sites"] = SITES
                with open(config_path, "w") as f:
                    json.dump(user_config, f, indent=4)
                st.session_state.reset_remove_site = True
                st.rerun()
    
    st.caption(f"List of your sites: {SITES}")
    
    # Add season
    if st.session_state.reset_add_season:
        st.session_state["add_season"] = ""
        st.session_state.reset_add_season = False
    
    season_input = st.text_input("Add a new season", key="add_season")

    if st.button("Add season"):
        if season_input and season_input not in SEASONS:
            SEASONS.append(season_input)
            user_config["seasons"] = SEASONS
            with open(config_path, "w") as f:
                json.dump(user_config, f, indent=4)
            st.session_state.reset_add_season = True
            st.rerun()
    # Remove season
    if st.session_state.reset_remove_season:
        st.session_state["remove_season"] = ""
        st.session_state.reset_remove_season = False
        
    if len(SEASONS) > 1:
        season_remove = st.text_input("Season to be removed", key="remove_season")

        if st.button("Remove season"):
            if season_remove in SEASONS:
                SEASONS.remove(season_remove)
                user_config["seasons"] = SEASONS
                with open(config_path, "w") as f:
                    json.dump(user_config, f, indent=4)
                st.rerun()
    
    st.caption(f"List of your seasons: {SEASONS}")
    
    col_left, col_center, col_right = st.columns([1, 0.76, 1])

    with col_center:
        if st.button("Return to application", type="primary"):
            st.session_state.clear()
            st.rerun()
    
    soft_divider()
  
# ============================================================
# %% SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("Menu")

st.sidebar.selectbox(
    "Choose an option",
    OPTIONS,
    key="action",
    disabled=st.session_state.mode_locked
)

# --- Welcome page ---
if st.session_state.action == OPTIONS[0]:
    st.image("utilities/Header.jpg")
    st.subheader("About Glacio-Log")
    st.markdown("""
Glacio-Log is an open-source application developed by Paul Tudès (Michigan Technological University - 
                                                                  Atmospheric sciences program). 
This application is designed for managing, visualizing, and analyzing snow profiles and snow pit data.
It allows users to create, edit, and visualize snow layers, grain type, density, 
temperature, and liquid water content (LWC).
""")
    st.caption(f"Glacio-Log — version {__version__}")
        
# --- Creation ---

if st.session_state.action == OPTIONS[1]:
    
    date = st.sidebar.date_input(
        "Snow pit date",
        key="date",
        disabled=st.session_state.mode_locked
    )
    
    season = current_season(st.session_state["date"])
    
    site = st.sidebar.selectbox(
        "Snow pit site",
        SITES,
        key="site",
        disabled=st.session_state.mode_locked
    )
    save_path = (
        BASE_DIR
        / site
        / season
        / "clean_data"
        / f"snowpits_{date}.json"
    )
    
# --- Edition ---

if st.session_state.action == OPTIONS[2] or st.session_state.action == OPTIONS[3]:
    
    date_edit = st.sidebar.date_input(
        "Snow pit date",
        key="date_edit",
        disabled=st.session_state.mode_locked
    )
    
    season_edit = current_season(st.session_state["date_edit"])
    
    site_edit = st.sidebar.selectbox(
        "Snow pit site",
        SITES,
        key="site_edit",
        disabled=st.session_state.mode_locked
    )
    data_path = (
        BASE_DIR
        / site_edit
        / season_edit
        / "clean_data"
        / f"snowpits_{date_edit}.json"
    )
    if not data_path.exists():
        st.warning("No existing snow pit for this day, please select an other date!")
        st.stop()
        
    with open(data_path) as f:
        database = json.load(f)
    
    pit_labels = {
        f"Snow Pit {i+1}: Snow depth = {p['SD (cm)']} cm | Air Temperature = {p['Air_T (K)']} K": p["id"]
        for i, p in enumerate(database)
    }

    label = st.selectbox(
        "Choose the snow pit to edit",
        list(pit_labels.keys()),
        key="pit_to_edit",
        disabled=st.session_state.mode_locked
    )
# --- Snow pit stratigraphy plot ---

if st.session_state.action == OPTIONS[4]:
    
    date_plot = st.sidebar.date_input(
        "Snow pit date",
        key="date_plot",
        disabled=st.session_state.mode_locked
    )
    season_plot = current_season(st.session_state["date_plot"])
    
    site_plot = st.sidebar.selectbox(
        "Snow pit site",
        SITES,
        key="site_plot",
        disabled=st.session_state.mode_locked
    )
    data_path = (
        BASE_DIR
        / site_plot
        / season_plot
        / "clean_data"
        / f"snowpits_{date_plot}.json"
    )
    if not data_path.exists():
        st.warning("No existing snow pit for this day, please select an other date!")
        st.stop()
        
    with open(data_path) as f:
        database = json.load(f)
    
    pit_labels = {
        f"Snow Pit {i+1}: Snow depth = {p['SD (cm)']} cm | Air Temperature = {p['Air_T (K)']} K": p["id"]
        for i, p in enumerate(database)
    }

    label = st.selectbox(
        "Choose the snow pit to plot",
        list(pit_labels.keys()),
        key="pit_to_plot",
        disabled=st.session_state.mode_locked
    )
      
# --- Seasonal stratigraphy plot ---

#if st.session_state.action == OPTIONS[5]:
    
    #st.sidebar.selectbox(
    #    "Season",
    #    SEASONS,
    #    key='seasons'
    #)
    #st.caption('Under construction')
    
# --- User setup ---
if st.session_state.config_validated:
    with st.sidebar:
        soft_divider()
        if st.button("Modify user configuration", disabled=st.session_state.mode_locked):
            st.session_state.modify_config = True
            st.rerun()
            
            #st.session_state.clear()
            #st.rerun()

if st.session_state.config_validated:
    with st.sidebar:
        if st.button("Reset user configuration", disabled=st.session_state.mode_locked):
            os.remove(config_path)
            st.session_state.clear()
            st.rerun()
    
# ============================================================
# %% New snow pit creation
# ============================================================   
    
if st.session_state.action == OPTIONS[1]:
    
    # === Start button ===
    
    if st.session_state.start_button_clicked == False:
        col_left, col_center, col_right = st.columns([1, 1.1, 1])
        with col_center :
            start = st.button("Start new snow pit acquisition", type='primary')
            if start:
                st.session_state.mode_locked = True
                st.session_state.start_button_clicked = True
                st.rerun()
                
    # === New snow pit acquisition ===
    
    else:
        section_title_box(
            "New snow pit acquisition",
            badge_text="READY",
            badge_type="success"
        )
        
        if st.session_state.generated_id == False :
            st.session_state.snowpit_id = str(uuid.uuid4())
            snowpit_id = st.session_state.snowpit_id
            st.session_state.generated_id = True
            
        else :
            snowpit_id = st.session_state.snowpit_id
        st.code(f"Snow pit ID: {snowpit_id}", language="text")
        
        # %%% --- General data ---
        with st.expander("General data"):
            col1, col2 = st.columns(2)
            with col1:
                SD = st.number_input(
                    "Snow depth (cm)", 
                    min_value=0.0,
                    key="SD"
                )
            with col2:
                AT = st.number_input(
                    "Air temperature (°C)",
                    min_value=(-273.15),
                    key="AT"
                    )
             
        # %%% --- Layers ---
        with st.expander("Layers"):
            st.warning("\u26A0\ufe0f Ground level still at 0 cm")
        
            if st.button("Reset table"):
                st.session_state.reset_counter_layers += 1 
                
            key = f"layers_editor_{st.session_state.reset_counter_layers}"
            
            df_layers = st.data_editor(
                st.session_state.layers_df,
                key=key,
                num_rows="dynamic",
                column_config={
                    "grain (IACS)": st.column_config.SelectboxColumn(
                        "grain (IACS)",
                        options=IACS_GRAINS
                    ),
                    "snow hardness": st.column_config.SelectboxColumn(
                        "snow hardness",
                        options=SNOW_HARDNESS
                    )
                }
            ) 
            with st.expander("Reference – Grain types (IACS) & Snow hardness"): 
                st.markdown("[IACS Classification]" 
    "(https://cryosphericsciences.org/wp-content/uploads/2019/02/snowclass_2009-11-23-tagged-highres.pdf)")
                st.markdown("[Snow hardness Classification]"
    "(https://avalanche.org/avalanche-encyclopedia/snowpack/snowpack-observations/snow-pit/snow-hardness/)")
                
        # %%% --- Temperature profile ---
        with st.expander("Temperature profile"):
            # Scale selection
            st.number_input(
                "Vertical temperature range",
                min_value=0.5,
                step=0.5,
                value=st.session_state.temp_custom_step,
                key="temp_custom_step",
                on_change=regenerate_profile(
                    st.session_state.temp_custom_step, 
                    f"temperature ({st.session_state.temp_unit})"
                )
            )
            if st.session_state.temp_custom_step is None or st.session_state.SD==0: 
                locked_df_temp = True
                st.caption("Complete snow depth and vertical temperature range")
            else: locked_df_temp = False
            
            if st.session_state.temp_unit is not None :
                df_temp = st.data_editor(
                    st.session_state.temp_df,
                    key="temp_editor",
                    num_rows="dynamic",
                    disabled=locked_df_temp
                )
            else:
                locked_df_temp = True
                df_temp = st.data_editor(
                    st.session_state.temp_df,
                    key="temp_editor",
                    num_rows="dynamic",
                    disabled=locked_df_temp
                )
                st.warning('Please choose a temperature unit.')
                
            temp_locked = is_temperature_locked(df_temp)
            
            # Unite selection
            st.selectbox(
                "Temperature unit",
                TEMP_UNITS,
                key="temp_unit",
                disabled=temp_locked
            )
            if st.session_state.temp_unit != "K":
                st.caption(f"Temperature displayed in {st.session_state.temp_unit}, stored internally in K")
            st.caption("To reset the table, change the vertical temperature range or the snow depth")
            
        # %%% --- LWC profile ---
        with st.expander("Liquid water content profile"):
            st.number_input(
                "Vertical LWC range",
                min_value=0.5,
                step=0.5,
                value=st.session_state.lwc_custom_step,
                key="lwc_custom_step",
                on_change=regenerate_profile(
                    st.session_state.lwc_custom_step,
                    "LWC (%)"
                )
            )
            
            if st.session_state.lwc_custom_step is None or st.session_state.SD==0: 
                locked_df_lwc = True
                st.caption("Complete snow depth and vertical LWC range")
            else : locked_df_lwc = False
            
            df_lwc = st.data_editor(
                st.session_state.lwc_df,
                key="lwc_editor",
                num_rows="dynamic",
                disabled=locked_df_lwc
            )
        
        # %%% --- Save/Refresh ---
        ivisible_divider()
        if st.session_state.SD != 0:
            col_left, col_center, col_right = st.columns([1, 0.53, 1])
            with col_center :
                if st.button('Save snow pit', type='primary'):
                    st.session_state.save_button = True
            
            if st.session_state.save_button == True:
                
                df_temp_copy = df_temp.copy()
                
                # Temperature conversion
                AT_K = unit_to_K(AT, "°C")
                
                unit = f"temperature ({st.session_state.temp_unit})"
                df_temp_copy[unit] = df_temp_copy[unit].apply(
                    lambda v: unit_to_K(v, st.session_state.temp_unit)
                )
                df_temp_K = df_temp_copy.rename(columns={unit: "temperature (K)"})
                    
                # Snow pit validation    
                error = validate_snowpit(SD, df_layers, df_temp_K, df_lwc)
                if error :
                    st.session_state.save_button = False
                    for e in error:
                        st.error(e)
                    st.stop()
                
                if st.session_state.temp_unit is not None:
                    if df_temp_K["temperature (K)"].min() < 0:
                        st.error('One or more values in temperature profile < 0 K')
                        st.session_state.save_button = False
                        st.stop()
                    
                snowpit = {
                    "id": snowpit_id,
                    "Date": str(date),
                    "SD (cm)": SD,
                    "Air_T (K)": AT_K,
                    "layers": df_layers.dropna().to_dict("records"),
                    "temperature_profile (K)": df_temp_K.dropna().to_dict("records"),
                    "lwc_profile (%)": df_lwc.dropna().to_dict("records")
                }
                action = save_or_update_snowpit(save_path, snowpit)
            
                if action == "updated":
                    st.success(f"Snow pit ID: {snowpit_id} udpated ✅")
                else:
                    st.success(f"Snow pit ID: {snowpit_id} saved ✅")
                
                st.write("Saving to:", save_path.resolve())
        
        # Refresh
        soft_divider()
        col_left, col_center, col_right = st.columns([1, 0.5, 0.519])
        with col_right :
            refresh = st.button("Refresh creation page")
            if refresh:
                st.session_state.clear()
                st.rerun()
            
        
# ============================================================
# %% Existing snow pit edition
# ============================================================  

if st.session_state.action == OPTIONS[2]:
    
    # === Start button ===
    
    if st.session_state.start_button_clicked == False:
        col_left, col_center, col_right = st.columns([1, 1.1, 1])
        if st.session_state.pit_to_edit is not None :
            with col_center :
                start = st.button("Start editing existing snow pit", type='primary')
                if start:
                    st.session_state.mode_locked = True
                    st.session_state.start_button_clicked = True
                    st.rerun()
        else : 
            with col_center : st.button("Start editing existing snow pit", type='primary', disabled=True)
                
    # === New snow pit acquisition ===
    
    else:
        section_title_box(
            "Existing snow pit edition",
            badge_text="READY",
            badge_type="success"
        )
        selected_id = pit_labels[label]
        st.code(f"Snow pit ID: {selected_id}", language="text")
        pit = next(p for p in database if p["id"] == selected_id)
        
        # %%% --- General data edit ---
        with st.expander("General data edition"):
            
            if st.button("Reset modifications on general data"):
                st.session_state.SD_edit=pit["SD (cm)"]
                st.session_state.AT_edit=K_to_unit(pit["Air_T (K)"],"°C")
            
            col1, col2 = st.columns(2)
            with col1:
                SD_edit=st.number_input(
                    "Snow depth (cm)", 
                    min_value=(0.0),
                    value=pit["SD (cm)"],
                    key="SD_edit"
                )
            with col2:
                AT_edit=st.number_input(
                    "Air temperature (°C)",
                    min_value=(-273.15),
                    value=K_to_unit(pit["Air_T (K)"],"°C"),
                    key="AT_edit"
                    ) 
                
        # %%% --- Layers edit ---
        with st.expander("Layers edition"):
            st.warning("\u26A0\ufe0f Ground level still at 0 cm")
            
            if st.button("Reset modifications on layers"):
                st.session_state.reset_counter_layers_edit += 1 
                
            key = f"layers_edit_editor_{st.session_state.reset_counter_layers_edit}"
            
            pit_layers_edit_work = pit["layers"]
            
            if to_df(pit_layers_edit_work).empty: 
                pit_layers_edit_work = st.session_state.layers_df
                
            df_layers_edit = st.data_editor(
                pit_layers_edit_work,
                key=key,
                num_rows="dynamic",
                column_config={
                    "grain (IACS)": st.column_config.SelectboxColumn(
                        "grain (IACS)",
                        options=IACS_GRAINS
                    ),
                    "snow hardness": st.column_config.SelectboxColumn(
                        "snow hardness",
                        options=SNOW_HARDNESS
                    )
                }
            )
            with st.expander("Reference – Grain types (IACS) & Snow hardness"): 
                st.markdown("[IACS Classification]" 
    "(https://cryosphericsciences.org/wp-content/uploads/2019/02/snowclass_2009-11-23-tagged-highres.pdf)")
                st.markdown("[Snow hardness Classification]"
    "(https://avalanche.org/avalanche-encyclopedia/snowpack/snowpack-observations/snow-pit/snow-hardness/)")
                
        # %%% --- Temperature profile edit ---
        with st.expander("Temperature profile edition"):
            # Reset modification
            if st.button("Reset modifications on temperature profile"):
                st.session_state.reset_counter_temp_profile_edit += 1
                st.session_state.temp_locked_edit = False
                st.session_state.temp_unit_edit = None
            
            key = f"temp_profile_edit_editor_{st.session_state.reset_counter_temp_profile_edit}"
            
            df_temp_edit_display=to_df(pit["temperature_profile (K)"])
            
            if df_temp_edit_display.empty:
                df_temp_edit_display = st.session_state.empty_temp_df
            
            df_temp_edit_display['temperature (K)']=df_temp_edit_display['temperature (K)'].apply(
                lambda v: K_to_unit(v, st.session_state.temp_unit_edit)
            )
            df_temp_edit_display=df_temp_edit_display.rename(
                columns={
                    f"temperature (K)": f"temperature ({st.session_state.temp_unit_edit})"
                }
            )
            if st.session_state.temp_unit_edit is not None:
                
                st.session_state.temp_locked_edit = True
                
                df_temp_edit = st.data_editor(
                    df_temp_edit_display,
                    key=key,
                    num_rows="dynamic"
                )
                st.info('Reset changes to switch units. All changes will be lost.')
                
                df_temp_edit = normalize_numeric_df(df_temp_edit)
                
            else :
                df_temp_edit_display = df_temp_edit_display.rename(
                    columns={
                        f"temperature (None)": f"temperature (K)"
                    }
                )
                df_temp_edit = st.data_editor(
                    df_temp_edit_display,
                    key=key,
                    num_rows="dynamic",
                    disabled=True
                )
                df_temp_edit = df_temp_edit.rename(
                    columns={
                        f"temperature (K)": f"temperature (None)"
                    }
                )
                st.info('Choose temperature unit to edit the profile.')
            
            st.selectbox(
                "Temperature unit",
                TEMP_UNITS,
                key="temp_unit_edit",
                disabled=st.session_state.temp_locked_edit
            )
            
            df_temp_edit_final = df_temp_edit.copy()
            unit = f"temperature ({st.session_state.temp_unit_edit})"
            df_temp_edit_final[unit]=df_temp_edit_final[unit].apply(
                lambda v: unit_to_K(v, st.session_state.temp_unit_edit)
            )
            df_temp_edit_final=df_temp_edit_final.rename(
                columns={
                    f"temperature ({st.session_state.temp_unit_edit})" : f"temperature (K)"
                }
            )

        # %%% --- LWC profile edit ---
        with st.expander("LWC profile edition"):
            
            if st.button("Reset modifications on LWC profile"):
                st.session_state.reset_counter_lwc_profile_edit += 1
                
            pit_lwc_edit_work = pit["lwc_profile (%)"]
            
            if to_df(pit_lwc_edit_work).empty: 
                pit_lwc_edit_work = st.session_state.empty_lwc_df
            
            key = f"lwc_profile_edit_editor_{st.session_state.reset_counter_lwc_profile_edit}"
            
            df_lwc_edit = st.data_editor(
                pit_lwc_edit_work,
                key=key,
                num_rows="dynamic"
            )
        
        # %%% --- Save/Refresh ---
        ivisible_divider()
        has_changes = (
            SD_edit != pit["SD (cm)"]
            or AT_edit != K_to_unit(pit["Air_T (K)"],"°C")
            or not to_df(df_layers_edit).equals(to_df(pit["layers"]))
            or not to_df(df_temp_edit_final).equals(to_df(pit["temperature_profile (K)"]))
            or not to_df(df_lwc_edit).equals(to_df(pit["lwc_profile (%)"]))
        )
          
        #locked_save=True
        if has_changes: locked_save=False
        else: locked_save=True
        col_left, col_center, col_right = st.columns([1, 0.65, 1])
        with col_center :
            if st.button("Save modification", type="primary", disabled=locked_save):
                st.session_state.save_button_edit = True
        
        if st.session_state.save_button_edit == True:
            # Temperature conversion
            AT_K_edit = unit_to_K(AT_edit, "°C")
                
            # Snow pit validation    
            error = validate_snowpit(
                SD_edit, 
                to_df(df_layers_edit), 
                to_df(df_temp_edit_final), 
                to_df(df_lwc_edit)
                )
            if error :
                st.session_state.save_button_edit = False
                for e in error:
                    st.error(e)
                st.stop()
            
            if st.session_state.temp_unit_edit is not None:
                if to_df(df_temp_edit_final)["temperature (K)"].min() < 0:
                    st.error('One or more values in temperature profile < 0 K')
                    st.session_state.save_button_edit = False
                    st.stop()
                    
            snowpit = {
                "id": selected_id,
                "Date": str(date_edit),
                "SD (cm)": SD_edit,
                "Air_T (K)": AT_K_edit,
                "layers": to_df(df_layers_edit).dropna().to_dict("records"),
                "temperature_profile (K)": to_df(df_temp_edit_final).dropna().to_dict("records"),
                "lwc_profile (%)": to_df(df_lwc_edit).dropna().to_dict("records")
            }
            
            action = save_or_update_snowpit(data_path, snowpit)
        
            if action == "updated":
                st.success(f"Snow pit ID: {selected_id} udpated ✅")
            else:
                st.success(f"Snow pit ID: {selected_id} saved ✅")
            st.write("Saving to:", data_path.resolve())
    
    # Refresh
    soft_divider()
    col_left, col_center, col_right = st.columns([1, 0.5, 0.49])
    with col_right :
        refresh = st.button("Refresh edition page")
        if refresh:
            st.session_state["__force_reset__"] = True
            st.rerun()
   
# ============================================================
# %% Remove existing snow pit edition
# ============================================================  
if st.session_state.action == OPTIONS[3]:
    if st.session_state.remove_clicked == False and  st.session_state.confirm_remove_clicked == False:
        if st.session_state.pit_to_edit is  not None:
            section_title_box(
                "Removal of existing snow pit",
                badge_text="READY",
                badge_type="success"
            )
            selected_id = pit_labels[label]
            st.code(f"Snow pit ID: {selected_id}", language="text")
            col_left, col_center, col_right = st.columns([1, 0.7, 1])
            with col_center :
                remove = st.button('Remove snow pit', type='primary')
                if remove: 
                    st.session_state.remove_clicked = True
                    st.rerun()
                
    if st.session_state.remove_clicked == True:
        section_title_box(
            "Removal of existing snow pit",
            badge_text="READY",
            badge_type="success"
        )
        selected_id = pit_labels[label]
        st.code(f"Snow pit ID: {selected_id}", language="text")
        st.warning("All deletions are final, please confirm your choice.")
        col_left, col_center, col_right = st.columns([1, 1.4, 1])
        with col_center :
            confirm_remove = st.button('Confirms the removal of the snow pit', type='primary')
            if confirm_remove: 
                st.session_state.confirm_remove_clicked = True
                st.session_state.remove_clicked = False
                st.rerun()
    
    if st.session_state.confirm_remove_clicked == True:
        section_title_box(
            "Removal of existing snow pit",
            badge_text="READY",
            badge_type="success"
        )
        selected_id = pit_labels[label]
        st.code(f"Snow pit ID: {selected_id}", language="text")
        delet_pit = [p for p in database if p["id"] != selected_id]

        if len(delet_pit) == 0:
            if data_path.exists():
                data_path.unlink()
                st.session_state.confirm_remove_clicked  = False
                st.error(f"Snow pit (ID: {selected_id}) deleted ✅")
                st.error("No snow pits left for this date. JSON file removed!")
        else:
            with open(data_path, "w") as f:
                json.dump(delet_pit, f, indent=2)
                st.error(f"Snow pit (ID: {selected_id}) deleted ✅")
                st.session_state.confirm_remove_clicked  = False
            
            
    soft_divider()
    col_left, col_center, col_right = st.columns([1, 0.5, 0.52])
    with col_right :
        refresh = st.button("Refresh removal page")
        if refresh:
            st.session_state.clear()
            st.rerun()
                
# ============================================================
# %% Single snow pit plot 
# ============================================================                            
if st.session_state.action == OPTIONS[4]:
    if st.session_state.pit_to_plot is  not None:
        section_title_box(
            "Single snow pit stratigraphy plot",
            badge_text="READY",
            badge_type="success"
        )
        selected_id = pit_labels[label]
        pit = next(p for p in database if p["id"] == selected_id)
        st.code(f"Snow pit ID: {selected_id}", language="text")
        
        title = st.text_input('Snow pit title', value='Snow pit profile')
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("Snow pit location")
            plot_temp = st.toggle("Plot temperature")
        with col2:
            weather = st.text_input("Weather")
            plot_lwc = st.toggle("Plot LWC")
        
        fig = plot_snowpit_grid_mapped(
            pit,
            plot_temp,
            plot_lwc,
            title=title,
            location=location,
            date=pit["Date"],
            weather=weather,
            air_temperature=K_to_unit(pit["Air_T (K)"], "°C"),
        )
        st.pyplot(fig, use_container_width=True)
        save_plot_path = (
            BASE_DIR
            / site_plot
            / season_plot
            / "plot"
            / f"{title}-{pit['Date']}.png"
        )
        st.caption(f"Your figure will be registered at: {save_plot_path}")
        col_left, col_center, col_right = st.columns([1, 1.1, 0.52])
        with col_center :
            if st.button('Save stratigraphy', type='primary'):
                st.session_state.save_strati = True
                fig.savefig(
                    save_plot_path,
                    dpi=300,
                    bbox_inches="tight",
                    )
        if st.session_state.save_strati == True: st.write("Saving to:", save_plot_path.resolve())
    
    
    
    
    
    
    
    
    
    
    
    
    