#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 21:47:08 2026

@author: paultudes
"""
import json
import streamlit as st
from datetime import date
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from itertools import product

from utilities.constants import OPTIONS, IACS_GRAINS, SNOW_HARDNESS, HARDNESS_MAP, GRAIN_COLORS, IACS_SYMBOLS

plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
})
# ============================================================
# %% Functions style
# ============================================================

def card():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
def section_title_box(title, badge_text=None, badge_type="info", rgb_font=(0,31,60), rgb_border=(0,104,201)):
    """Title with optional badge inside a colored box."""
    r_f, g_f, b_f = rgb_font
    r_b, g_b, b_b = rgb_border
    badge_class = f"badge-{badge_type}"
    badge_html = f'<span class="badge {badge_class}">{badge_text}</span>' if badge_text else ""
    st.markdown(
        f"""
        <div class="section-box" style="
            border-left: 6px solid rgb({r_b},{g_b},{b_b});
            background-color: rgb({r_f},{g_f},{b_f});
        ">
            <h2>{title}{badge_html}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

def soft_divider():
    st.markdown('<div class="card-divider">', unsafe_allow_html=True)
    
def ivisible_divider():
    st.markdown('<div class="card-invisible">', unsafe_allow_html=True)
# ============================================================
# %% Functions streamlit
# ============================================================    

def init_session_state():
    defaults = {
        "action": OPTIONS[0],
        "date": date.today(),
        "date_edit": date.today(),
        "date_plot": date.today(),
        "mode_locked": False,
        "start_button_clicked": False,
        "SD": 0.0,
        "AT": None,
        "reset_table": False,
        "temp_unit": None,
        "temp_unit_edit": None,
        "temp_custom_step": None,
        "lwc_custom_step": None,
        "generated_id": False,
        "snowpit_id": None,
        "save_button": False,
        "save_button_edit": False,
        "remove_clicked": False,
        "confirm_remove_clicked": False,
        "pit_to_edit": None,
        "pit_to_plot": None,
        "reset_counter_layers": 0,
        "reset_counter_layers_edit": 0,
        "reset_counter_temp_profile_edit": 0,
        "reset_counter_lwc_profile_edit": 0,
        "temp_locked_edit": False,
        "save_strati": False,
        "config_validated": False,
        "config_saved": False,
        "modify_config": False,
        "add_site": "",
        "remove_site": "",
        "add_season": "",
        "remove_season": "",
        "layers_df": pd.DataFrame(
            columns=[
                "bottom (cm)",
                "top (cm)",
                "grain (IACS)",
                "density (g cm⁻³)",
                "snow hardness",
            ]
        ),
        "empty_temp_df": pd.DataFrame(
            columns=[
                "z (cm)",
                "temperature (K)",
            ],
            dtype=float
        ),
        "empty_lwc_df": pd.DataFrame(
            columns=[
                "z (cm)",
                "LWC (%)",
            ],
            dtype=float
        )
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def init_profile_session_state():
    defaults = {
        "temp_df": generate_profile_df(
                        st.session_state.SD, 
                        st.session_state.temp_custom_step, 
                        f"temperature ({st.session_state.temp_unit})"
                 ),
        "lwc_df": generate_profile_df(
                        st.session_state.SD, 
                        st.session_state.lwc_custom_step, 
                        "LWC (%)"
                 )
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
def init_site_season_state(user_config: dict):

    if "site" not in st.session_state:
        st.session_state.site = user_config["sites"][0]
    
    if "site_edit" not in st.session_state:
        st.session_state.site_edit = user_config["sites"][0]
        
    if "site_plot" not in st.session_state:
        st.session_state.site_plot = user_config["sites"][0]

    if "season" not in st.session_state:
        st.session_state.season = user_config["seasons"][0]
# ============================================================
# %% Current functions 
# ============================================================             

def current_season(d):
    y = d.year
    return f"{y}-{y+1}" if d.month >= 10 else f"{y-1}-{y}"

def generate_profile_df(SD, step, name_col):
    if SD == None or SD == 0 or step == None or step == np.nan:
        return pd.DataFrame(
            columns=["z (cm)", name_col]
            )
    else:
        z_values = np.arange(0, SD, step)
        return pd.DataFrame({
            "z (cm)": z_values,
            name_col: np.nan
            })

def regenerate_profile(step, name_col):
    SD = st.session_state.SD
    if name_col == f"temperature ({st.session_state.temp_unit})":
        st.session_state.temp_df = generate_profile_df(SD, step, name_col)
    if name_col == "LWC (%)":
        st.session_state.lwc_df = generate_profile_df(SD, step, name_col)
    
def K_to_unit(v, unit):
    if pd.isna(v):
        return v
    if unit == "K" or unit is None or unit == 'None':
        return v
    if unit == "°C":
        return v - 273.15
    if unit == "°F":
        return (v - 273.15) * 9/5 + 32

def unit_to_K(v, unit):
    if pd.isna(v):
        return v
    if unit == "K" or unit is None or unit == 'None':
        return v
    if unit == "°C":
        return v + 273.15
    if unit == "°F":
        return (v - 32) * 5/9 + 273.15

def is_temperature_locked(df):
    
    for value in df[f"temperature ({st.session_state.temp_unit})"]:
        if not np.isnan(value):
            return True   # at least one value was find
    return False

def save_or_update_snowpit(save_path: Path, new_snowpit: dict):
    if save_path.exists():
        with open(save_path) as f:
            database = json.load(f)
    else:
        database = []
        save_path.parent.mkdir(parents=True, exist_ok=True)

    snowpit_id = new_snowpit["id"]

    # Search for an existing snowpit with the same ID
    existing_index = next(
        (i for i, sp in enumerate(database) if sp.get("id") == snowpit_id),
        None
    )

    if existing_index is not None:
        # Replace
        database[existing_index] = new_snowpit
        action = "updated"
    else:
        # Add
        database.append(new_snowpit)
        action = "created"

    with open(save_path, "w") as f:
        json.dump(database, f, indent=2)

    return action

def validate_snowpit(SD, layers_df, temp_df, lwc_df):

    errors = []
    total_thickness = 0.0
    TOL = 0.0  # tolerance for total thickness check

    # --- 1. Validate layers row by row ---
    valid_layers = []
    for i, row in layers_df.iterrows():
        # Convert numeric values
        try:
            top = float(row["top (cm)"])
            bottom = float(row["bottom (cm)"])
        except (ValueError, TypeError):
            errors.append(f"Layer {i}: invalid numeric values")
            continue

        thickness = top - bottom
        grain = row.get("grain (IACS)")
        hardness = row.get("snow hardness")

        # Basic checks
        if top <= bottom:
            errors.append(f"Layer {i}: top ({top}) <= bottom ({bottom})")
        if top > SD:
            errors.append(f"Layer {i}: top ({top}) > SD ({SD})")
        if bottom < 0:
            errors.append(f"Layer {i}: bottom ({bottom}) < 0")
        if grain not in IACS_GRAINS:
            errors.append(f"Layer {i}: invalid grain ({grain})")
        if hardness not in SNOW_HARDNESS:
            errors.append(f"Layer {i}: invalid snow hardness ({hardness})")

        total_thickness += thickness
        valid_layers.append((bottom, top))

    # --- 2. Check total thickness against SD ---
    if layers_df.dropna().shape[0] > 0 and abs(total_thickness - SD) > TOL:
        errors.append(f"Layer thickness sum ({total_thickness:.1f} cm) ≠ SD ({SD} cm)")

    # --- 3. Check for overlaps ---
    valid_layers.sort()  # sort by bottom
    for i in range(1, len(valid_layers)):
        prev_top = valid_layers[i-1][1]
        curr_bottom = valid_layers[i][0]
        if curr_bottom < prev_top:
            errors.append(f"Layer {i}: overlap detected with previous layer")

    # --- 4. Validate profile DataFrames (Temperature and LWC) ---
    for name, df in {"Temperature": temp_df, "LWC": lwc_df}.items():
        if df.empty:
            continue

        # Ensure numeric z
        df["z (cm)"] = pd.to_numeric(df["z (cm)"], errors="coerce")

        # Check bounds
        if df["z (cm)"].min() < 0:
            errors.append(f"{name}: z < 0")
        if df["z (cm)"].max() > SD:
            errors.append(f"{name}: z > SD")

        # Check duplicates
        if df["z (cm)"].duplicated().any():
            errors.append(f"{name}: duplicated depths")

    return errors

def to_df(obj):
    if isinstance(obj, pd.DataFrame):
        return obj
    return pd.DataFrame(obj)

def normalize_numeric_df(df):
    df = df.copy()
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def parse_list(text):
    return [x.strip() for x in text.split(",") if x.strip()]

def create_file_tree(
    base_dir: Path,
    sites: list[str],
    seasons: list[str],
    data_template: str,
    plot_template: str,
):
    for site, season in product(sites, seasons):
        data_path = base_dir / data_template.format(
            site=site,
            season=season
        )
        plot_path = base_dir / plot_template.format(
            site=site,
            season=season
        )

        data_path.mkdir(parents=True, exist_ok=True)
        plot_path.mkdir(parents=True, exist_ok=True)

# ============================================================
# %% Plot functions 
# ============================================================     
def plot_snowpit_grid_mapped(
    pit,
    plot_temp,
    plot_lwc,
    hardness_categories=HARDNESS_MAP,
    grain_colors=GRAIN_COLORS,
    title="Snow pit profile",
    location=None,
    weather=None,
    date=None,
    air_temperature=None,
):
    layers = pit["layers"]
    temp_profile = pit["temperature_profile (K)"]

    SD = int(pit["SD (cm)"])
    grid_cols = SD

    hardness_categories = list(hardness_categories)
    n_hardness = len(hardness_categories)
    
    step = grid_cols // n_hardness
    hardness_positions = [(i + 1) * step for i in range(n_hardness)]
    
    hardness_lookup = dict(zip(hardness_categories, hardness_positions))
    
    fig_height = max(6, SD / 6)
    fig = plt.figure(figsize=(8, fig_height), dpi=300)
    ax = fig.add_subplot(111)

    for layer in layers:
        bottom = float(layer["bottom (cm)"])
        top = float(layer["top (cm)"])
        height = top - bottom

        h_label = layer["snow hardness"]
        hardness_value = hardness_lookup[h_label]

        grain = layer["grain (IACS)"]
        grain_symbol = IACS_SYMBOLS.get(grain, "")
        density = layer["density (g cm\u207b\u00b3)"]

        ax.barh(
            y=bottom,
            width=hardness_value,
            height=height,
            left=0,
            align="edge",
            color=grain_colors.get(grain, "grey"),
            edgecolor="black",
            linewidth=0.6,
        )

        y_center = bottom + height / 2
        label_text = f"Grain: {grain} - [{grain_symbol}]\nDensity: {density} g cm⁻³"
        
        if height < 5:
            y_center = bottom + height / 2
            
            # Vertical offset of the annotation
            if bottom == 0:
                y_arrow = bottom + height / 3
                y_text = top + 1.0
                va = "bottom"
            else:
                y_arrow = bottom + 2 * height / 3
                y_text = bottom - 1.0
                va = "top"
            
            ax.annotate(
                label_text,
                xy=(hardness_value, y_arrow),
                xytext=(hardness_value + step * 0.1, y_text),
                ha="left",
                va=va,
                fontsize=8,
                arrowprops=dict(
                    arrowstyle="-",
                    linewidth=0.8,
                ),
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    fc="white",
                    ec="black",
                    linewidth=0.5,
                ),
            )
        else:
            ax.text(
                hardness_value / 2,
                y_center,
                label_text,
                ha="center",
                va="center",
                fontsize=8,
                clip_on=True,
            )
    
    ax.set_ylim(0, SD)
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    ax.set_ylabel("Depth (cm)")

    ax.set_xlim(0, max(hardness_positions) + 1)
    ax.set_xlabel("Snow hardness")
    ax.invert_xaxis()

    ax.set_xticks(hardness_positions)
    ax.set_xticklabels(hardness_categories)

    ax.set_xticks(np.arange(0, grid_cols + 1, 1), minor=True)
    ax.set_yticks(np.arange(0, SD + 1, 1), minor=True)

    ax.grid(which="minor", axis="both", linewidth=0.3, alpha=0.35)
    ax.grid(which="major", axis="both", linewidth=0.6, alpha=0.5)

    if plot_temp:
        K_to_C = lambda v: K_to_unit(v, "°C")
        z = [p["z (cm)"] for p in temp_profile]
        T = [K_to_C(p["temperature (K)"]) for p in temp_profile]
        z.append(SD)
        T.append(K_to_C(pit["Air_T (K)"]))

        ax_top = ax.twiny()
        ax_top.plot(T, z, color="darkred", linewidth=2, label='Temperature (°C)')
        ax_top.set_xlim(0,-30)
        ax_top.invert_xaxis()
        ax_top.set_xlabel("Temperature (°C)")
    
    if plot_lwc:
        z_lwc = [p["z (cm)"] for p in pit["lwc_profile (%)"]]
        lwc = [p["LWC (%)"] for p in pit["lwc_profile (%)"]]
    
        ax_lwc = ax.twiny()
        ax_lwc.plot(lwc,z_lwc,color="royalblue",linewidth=2,linestyle="--",label='LWC (%)')
        ax_lwc.set_xlabel("LWC (%)")
        ax_lwc.set_xlim(0,3)
        ax_lwc.invert_xaxis()
        
        if plot_temp == True:
            ax_lwc.spines["top"].set_position(("axes", 1.12))
            ax_lwc.xaxis.set_label_position("top")
            ax_lwc.xaxis.set_ticks_position("top")
    
    info_lines = []
    
    if date is not None:
        info_lines.append(f"Date: {date}   |   ")
        
    if location:
        info_lines.append(f"Location: {location}\n")
    
    if weather:
        info_lines.append(f"Weather: {weather}   |   ")
    
    if air_temperature is not None:
        info_lines.append(f"Air temperature: {np.round(air_temperature,2)} °C")
    
    info_text = "".join(info_lines)

    fig.legend(bbox_to_anchor=(0.99, 0.89),)
    fig.suptitle(
        title,
        fontweight="bold",
        y=0.98,
    )
    fig.text(
        0.5,
        0.91,
        info_text,
        ha="center",
        va="center",
        bbox=dict(
            boxstyle="round,pad=0.35",
            fc="#f5f5f5",
            ec="black",
            linewidth=0.6,
        ),
    )


    plt.tight_layout(rect=[0, 0, 1, 0.91])
    return fig