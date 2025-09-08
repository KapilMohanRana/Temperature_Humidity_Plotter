import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Temperature & Humidity Data Plotter")

# ✅ Cached CSV loader
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    return df

# Upload CSV
uploaded_file = st.file_uploader("Choose CSV file", type=["csv"])
if uploaded_file:
    try:
        df = load_data(uploaded_file)
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        st.stop()

    # Parameter & grouping selection
    parameter = st.selectbox("Select parameter", ["Temperature", "Humidity"])
    grouping = st.selectbox("Select grouping", ["Day-wise", "Month-wise"])
    month_filter = st.text_input("Filter by month (YYYY-MM, only for Day-wise)")

    # Filter / group data
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

    if grouped.empty:
        st.warning("No data found for the selection")
    else:
        # Plot
        fig, ax = plt.subplots(figsize=(10,6))
        ax.plot(grouped.index.astype(str), grouped['min'], marker='o', label=f"Min {parameter}")
        ax.plot(grouped.index.astype(str), grouped['max'], marker='o', label=f"Max {parameter}")
        ax.set_title(f"{parameter} ({grouping})")
        ax.set_xlabel("Date" if grouping=="Day-wise" else "Month")
        ax.set_ylabel("Temperature (°C)" if parameter=="Temperature" else "Humidity (%)")
        ax.legend()
        ax.set_ylim(0, grouped['max'].max()+5)
        ax.grid(True)
        plt.xticks(rotation=90)
        st.pyplot(fig)
