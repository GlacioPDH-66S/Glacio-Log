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
import io

from utilities.styles import style
from utilities.functions import *
from utilities.constants import OPTIONS_LITE, IACS_GRAINS, SNOW_HARDNESS, TEMP_UNITS
from lite_version import __version__

# ============================================================
# %% APP HEADER
# ============================================================

st.set_page_config(
    page_title="Glacio-Log-Lite",
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

BASE_DIR = Path(__file__).resolve().parent

style()

# === Session_state ===
if st.session_state.get("__force_reset__", False):
    st.session_state.clear()
    st.session_state["__force_reset__"] = False

init_session_state()
init_profile_session_state()

st.title("Glacio-Log Lite ❄")
st.caption("Snow pit acquisition, edition and visualization")
card()
  
# ============================================================
# %% SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("Menu")

st.sidebar.selectbox(
    "Choose an option",
    OPTIONS_LITE,
    key="action",
    disabled=st.session_state.mode_locked
)

# --- Welcome page ---
if st.session_state.action == OPTIONS_LITE[0]:
    img_path = BASE_DIR / "utilities" / "Header.JPG"
    st.image(img_path)
    st.subheader("About Glacio-Log")
    st.markdown("""
Glacio-Log is an open-source application developed by Paul Tudès (Michigan Technological University - 
                                                                  Atmospheric sciences program). 
This application is designed for managing, visualizing, and analyzing snow profiles and snow pit data.
It allows users to create, edit, and visualize snow layers, grain type, density, 
temperature, and liquid water content (LWC).
""")
    st.caption(f"Glacio-Log — Lite version {__version__}")
        
# --- Creation ---

if st.session_state.action == OPTIONS_LITE[1]:
    
    date = st.sidebar.date_input(
        "Snow pit date",
        key="date",
        disabled=st.session_state.mode_locked
    )
    
# --- Edition ---

if st.session_state.action == OPTIONS_LITE[2]:
    uploaded_file = st.file_uploader(
        "Open Glacio-Log file (.json)",
        key="pit_to_edit",
        type=["json"],
        disabled=st.session_state.mode_locked
    )
    
# --- Snow pit stratigraphy plot ---

if st.session_state.action == OPTIONS_LITE[3]:   
    uploaded_file = st.file_uploader(
        "Open Glacio-Log file (.json)",
        key="pit_to_plot",
        type=["json"]
    )
# --- Seasonal stratigraphy plot ---

#if st.session_state.action == OPTIONS[5]:
    
    #st.sidebar.selectbox(
    #    "Season",
    #    SEASONS,
    #    key='seasons'
    #)
    #st.caption('Under construction')
    
# ============================================================
# %% New snow pit creation
# ============================================================   
    
if st.session_state.action == OPTIONS_LITE[1]:
    
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
            
            json_str = json.dumps(
                snowpit,
                indent=2,
                ensure_ascii=False
            )   

            col_left, col_center, col_right = st.columns([1, 0.6, 1])
            with col_center :
                if st.download_button(
                    label="Download snowpit",
                    data=json_str,
                    file_name=f"Snowpit_{date}.JSON",
                    type='primary'
                ):
                    st.session_state.save_button = True
            
            if st.session_state.save_button == True:             
                st.success(f"Snow pit ID: {snowpit_id} download ✅")
        
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

if st.session_state.action == OPTIONS_LITE[2]:
    
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
        pit = json.load(uploaded_file)
        st.success("File loaded successfully")
        selected_id = pit["id"]
        st.code(f"Snow pit ID: {selected_id}", language="text")
        
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
        date_edit=pit['Date']
        
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
        
        json_str = json.dumps(
            snowpit,
            indent=2,
            ensure_ascii=False
        )   

        col_left, col_center, col_right = st.columns([1, 0.6, 1])
        with col_center :
            if st.download_button(
                label="Download snowpit",
                data=json_str,
                file_name=f"Edited_snowpit_{date_edit}.JSON",
                type='primary', 
                disabled=locked_save
            ):
                st.session_state.save_button = True
        
        if st.session_state.save_button == True:             
            st.success(f"Snow pit ID: {selected_id} download ✅")
    
    # Refresh
    soft_divider()
    col_left, col_center, col_right = st.columns([1, 0.5, 0.49])
    with col_right :
        refresh = st.button("Refresh edition page")
        if refresh:
            st.session_state["__force_reset__"] = True
            st.rerun()
                
# ============================================================
# %% Single snow pit plot 
# ============================================================                            
if st.session_state.action == OPTIONS_LITE[3]:
    if st.session_state.pit_to_plot is  not None:
        section_title_box(
            "Single snow pit stratigraphy plot",
            badge_text="READY",
            badge_type="success"
        )
        pit = json.load(uploaded_file)
        st.success("File loaded successfully")
        selected_id = pit["id"]
        st.code(f"Snow pit ID: {selected_id}", language="text")
        date_plot = pit['Date']
        
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
        col_left, col_center, col_right = st.columns([1, 1.5, 0.52])
        
        with col_center :
            buf = io.BytesIO()
            fig.savefig(buf, format="pdf", dpi=300, bbox_inches="tight")
            buf.seek(0) 
            
            if st.download_button(
                label="Download snowpit stratigraphy",
                data=buf,
                file_name=f"Stratigraphic_plot_{date_plot}.pdf",
                type='primary'
            ):
                st.session_state.save_strati = True
        if st.session_state.save_strati == True: st.write("Saving to:", f"Stratigraphic_plot_{date_plot}.pdf")
 