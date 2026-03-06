import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SmartContainer Risk Dashboard", layout="wide")

st.title("🚢 SmartContainer Risk Intelligence Dashboard")

# -------- LOAD DATA -------- #

@st.cache_data
def load_data():
    df = pd.read_csv("container_results.csv")
    return df

df = load_data()

# -------- SIDEBAR -------- #

st.sidebar.header("Controls")
enable_search = st.sidebar.checkbox("Enable Container Search")

# -------- OVERVIEW METRICS -------- #

st.subheader("📊 Overview Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Containers", len(df))

col2.metric(
    "Critical Risk Containers",
    (df["Risk_Level"] == "Critical").sum()
)

col3.metric(
    "Low Risk Containers",
    (df["Risk_Level"] == "Low").sum()
)

col4.metric(
    "Average Risk Score",
    round(df["Final_Risk_Score"].mean(),3)
)

# -------- RISK DISTRIBUTION -------- #

st.subheader("📈 Risk Distribution")

fig = px.histogram(df, x="Final_Risk_Score", nbins=30)

st.plotly_chart(fig, use_container_width=True)

# -------- ANOMALY DETECTION -------- #

st.subheader("⚠ Anomaly Detection")

anomalies = df[df["Anomaly_Flag"] == 1]

st.write("Total Anomalous Containers:", len(anomalies))

st.dataframe(anomalies)

# -------- TOP RISKY CONTAINERS -------- #

st.subheader("🚨 Top Risky Containers")

top_risk = df.sort_values(
    "Final_Risk_Score",
    ascending=False
).head(10)

st.dataframe(top_risk)

# -------- CONTAINER SEARCH -------- #

if enable_search:

    st.subheader("🔎 Container Search")

    container_id = st.text_input("Enter Container ID")

    if container_id:

        result = df[df["Container_ID"] == container_id]

        if len(result) > 0:

            row = result.iloc[0]

            st.write("### Container Details")

            st.write("Container ID:", row["Container_ID"])
            st.write("Risk Score:", row["Final_Risk_Score"])
            st.write("Risk Level:", row["Risk_Level"])

            st.write("Explanation:")
            st.info(row["Explanation"])

        else:

            st.warning("Container not found")