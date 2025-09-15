import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.title("Temperature & Humidity Data Plotter")

# ✅ Cached CSV loader
@st.cache_data
def load_data(file):
    ext = os.path.splitext(file.name)[1].lower()

    if ext == ".csv":
        df = pd.read_csv(file)
    elif ext == ".xlsx":
        df = pd.read_excel(file, engine="openpyxl")
    elif ext == ".xls":
        df = pd.read_excel(file, engine="xlrd")
    elif ext == ".ods":
        df = pd.read_excel(file, engine="odf")
    else:
        raise ValueError("Unsupported File Format")
    
    df.columns = df.columns.str.strip()

    if 'Time' in df.columns and 'Value' in df.columns:
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        return df
    else:
        raise ValueError("No Value and Time Column find.Please rename the columns to Time and Value")

@st.cache_data
def group_data(df, grouping, month_filter):
    data = df.copy()
    if grouping == "Day-wise" and month_filter:
        try:
            month_period = pd.Period(month_filter, freq="M")
            data = data[data['Time'].dt.to_period("M") == month_period]
        except Exception:
            st.warning("Invalid month format. Use YYYY-MM (e.g. 2025-06).")

    if grouping == "Day-wise":
        grouped = data.groupby(data['Time'].dt.date)['Value'].agg(['min','max'])
    else:
        grouped = data.groupby(data['Time'].dt.to_period("M"))['Value'].agg(['min','max'])
    
    return grouped

# Upload CSV
uploaded_file = st.file_uploader("Choose CSV file", type=["csv","xls", "xlsx", "ods"])
if uploaded_file:
    try:
        df = load_data(uploaded_file)
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        st.stop()

    # st.subheader("Preview of uploaded file")
    # st.dataframe(df.head())

    # User selection Column
    # time_col = st.selectbox("Select the time column", df.columns)
    # value_col = st.selectbox("Select the value column", df.columns)

    # if time_col and value_col and time_col != value_col:
        # Changing the columns name for the rest of the code
        # df = df.rename(columns={time_col: "Time", value_col: "Value"})
    # df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
    # df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

        # Parameter & grouping selection
    parameter = st.selectbox("Select parameter", ["Temperature", "Humidity"])
    grouping = st.selectbox("Select grouping", ["Day-wise", "Month-wise"])
    month_filter = st.text_input("Filter by month (YYYY-MM, only for Day-wise)")

        # Filter / group data
    grouped = group_data(df, grouping, month_filter)

    if grouped.empty:
        st.warning("No data found for the selection")
    else:
        # Plot
        fig, ax = plt.subplots(figsize=(10,6))
        ax.plot(grouped.index.astype(str), grouped['min'], marker='o', label=f"Min {parameter}")
        ax.plot(grouped.index.astype(str), grouped['max'], marker='o', label=f"Max {parameter}")
        ax.set_title(f"{parameter} ({grouping}) ({uploaded_file.name})")
        ax.set_xlabel("Date" if grouping=="Day-wise" else "Month")
        ax.set_ylabel("Temperature (°C)" if parameter=="Temperature" else "Humidity (%)")
        ax.legend()
        ax.set_ylim(0, grouped['max'].max()+5)
        ax.grid(True)
        plt.xticks(rotation=90)
        st.pyplot(fig)

        st.subheader("Tabluar Form")
        table = grouped.reset_index()
        st.dataframe(table)
        csv = table.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Table as CSV",
            data=csv,
            file_name=f"{parameter}_{grouping}.csv",
            mime="text/csv"
        )