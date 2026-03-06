import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="SmartContainer Risk Intelligence Dashboard",
    layout="wide"
)

# --------------------------------------------------
# PROFESSIONAL CSS
# --------------------------------------------------

st.markdown("""
<style>

body {
    font-family: sans-serif;
}

.dashboard-title{
    font-size:34px;
    font-weight:600;
    margin-bottom:20px;
}

.section-title{
    font-size:22px;
    font-weight:500;
    margin-top:30px;
    margin-bottom:10px;
}

.metric-card{
    background-color:#1C1F26;
    padding:15px;
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.markdown(
'<div class="dashboard-title">SmartContainer Risk Intelligence Dashboard</div>',
unsafe_allow_html=True
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("container_results.zip")
    return df

df = load_data()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Dashboard Controls")

enable_search = st.sidebar.checkbox("Enable Container Search")

# --------------------------------------------------
# OVERVIEW METRICS
# --------------------------------------------------

st.markdown('<div class="section-title">Overview Metrics</div>', unsafe_allow_html=True)

total_containers = len(df)
critical_containers = (df["Risk_Level"] == "Critical").sum()
low_containers = (df["Risk_Level"] == "Low").sum()
avg_risk = round(df["Final_Risk_Score"].mean(),3)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Containers", total_containers)
col2.metric("Critical Risk Containers", critical_containers)
col3.metric("Low Risk Containers", low_containers)
col4.metric("Average Risk Score", avg_risk)

# --------------------------------------------------
# RISK DISTRIBUTION
# --------------------------------------------------

st.markdown('<div class="section-title">Risk Distribution</div>', unsafe_allow_html=True)

fig = px.histogram(
    df,
    x="Final_Risk_Score",
    nbins=30,
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# RISK BY ORIGIN COUNTRY
# --------------------------------------------------

if "Origin_Country" in df.columns:

    st.markdown('<div class="section-title">Risk by Origin Country</div>', unsafe_allow_html=True)

    country_risk = df.groupby("Origin_Country")["Final_Risk_Score"].mean().reset_index()

    fig = px.bar(
        country_risk,
        x="Origin_Country",
        y="Final_Risk_Score",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# RISK BY SHIPPING LINE
# --------------------------------------------------

if "Shipping_Line" in df.columns:

    st.markdown('<div class="section-title">Risk by Shipping Line</div>', unsafe_allow_html=True)

    ship_risk = df.groupby("Shipping_Line")["Final_Risk_Score"].mean().reset_index()

    fig = px.bar(
        ship_risk,
        x="Shipping_Line",
        y="Final_Risk_Score",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# RISK BY PORT
# --------------------------------------------------

if "Destination_Port" in df.columns:

    st.markdown('<div class="section-title">Risk by Port</div>', unsafe_allow_html=True)

    port_risk = df.groupby("Destination_Port")["Final_Risk_Score"].mean().reset_index()

    fig = px.bar(
        port_risk,
        x="Destination_Port",
        y="Final_Risk_Score",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# CONTAINER MAP
# --------------------------------------------------

if "Latitude" in df.columns and "Longitude" in df.columns:

    st.markdown('<div class="section-title">Container Map</div>', unsafe_allow_html=True)

    st.map(df[["Latitude","Longitude"]])

# --------------------------------------------------
# ANOMALY DETECTION
# --------------------------------------------------

st.markdown('<div class="section-title">Anomaly Detection</div>', unsafe_allow_html=True)

anomalies = df[df["Anomaly_Flag"] == 1]

st.write("Total Anomalous Containers:", len(anomalies))

st.dataframe(anomalies, use_container_width=True)

# --------------------------------------------------
# TOP RISKY CONTAINERS
# --------------------------------------------------

st.markdown('<div class="section-title">Top Risky Containers</div>', unsafe_allow_html=True)

top_risk = df.sort_values(
    "Final_Risk_Score",
    ascending=False
).head(10)

st.dataframe(top_risk, use_container_width=True)

# --------------------------------------------------
# CONTAINER SEARCH
# --------------------------------------------------

if enable_search:

    st.markdown('<div class="section-title">Container Investigation</div>', unsafe_allow_html=True)

    container_id = st.text_input("Container ID")

    if container_id:

        result = df[df["Container_ID"] == container_id]

        if len(result) > 0:

            row = result.iloc[0]

            st.write("Container ID:", row["Container_ID"])
            st.write("Risk Score:", row["Final_Risk_Score"])
            st.write("Risk Level:", row["Risk_Level"])

            st.write("AI Explanation")

            st.info(row["Explanation"])

        else:


            st.warning("Container not found")
