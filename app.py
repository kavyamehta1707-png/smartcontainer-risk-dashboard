import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# PAGE CONFIG


st.set_page_config(
    page_title="SmartContainer Risk Intelligence Dashboard",
    page_icon="🚢",
    layout="wide"
)


# CSS


st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #0D1117; }
[data-testid="stSidebar"] { background-color: #161B22; }

.dashboard-title {
    font-size: 32px;
    font-weight: 700;
    color: #E6EDF3;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}
.dashboard-sub {
    font-size: 14px;
    color: #8B949E;
    margin-bottom: 28px;
}
.section-title {
    font-size: 18px;
    font-weight: 600;
    color: #C9D1D9;
    margin-top: 36px;
    margin-bottom: 12px;
    border-left: 3px solid #238636;
    padding-left: 10px;
}
.metric-card {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 10px;
    padding: 18px 20px;
    text-align: center;
}
.metric-value {
    font-size: 30px;
    font-weight: 700;
    color: #58A6FF;
}
.metric-label {
    font-size: 12px;
    color: #8B949E;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
.critical { color: #F85149 !important; }
.low      { color: #E3B341 !important; }
.minimal  { color: #3FB950 !important; }
</style>
""", unsafe_allow_html=True)

# LOAD DATA

@st.cache_data
def load_data():
    df = pd.read_csv("realtime_explanations_1 (1).zip")
    return df

df = load_data()

# SIDEBAR

st.sidebar.image("https://img.icons8.com/fluency/96/container-ship.png", width=60)
st.sidebar.markdown("## Dashboard Controls")
st.sidebar.markdown("---")

risk_filter = st.sidebar.multiselect(
    "Filter by Risk Level",
    options=["Critical Risk", "Low Risk", "Minimal Risk"],
    default=["Critical Risk", "Low Risk", "Minimal Risk"]
)

anomaly_only = st.sidebar.checkbox("Show Anomalies Only", value=False)
enable_search = st.sidebar.checkbox("Enable Container Search", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Total Records:** {len(df):,}")
st.sidebar.markdown(f"**Last Updated:** Real-Time Feed")

# Apply filters
filtered_df = df[df["Risk_Level"].isin(risk_filter)]
if anomaly_only:
    filtered_df = filtered_df[filtered_df["Anomaly_Flag"] == 1]

# TITLE

st.markdown('<div class="dashboard-title">🚢 SmartContainer Risk Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-sub">AI-powered container risk scoring for global port security — Real-Time Feed</div>', unsafe_allow_html=True)

# OVERVIEW METRICS

st.markdown('<div class="section-title">Overview Metrics</div>', unsafe_allow_html=True)

total       = len(filtered_df)
critical    = (filtered_df["Risk_Level"] == "Critical Risk").sum()
low         = (filtered_df["Risk_Level"] == "Low Risk").sum()
minimal     = (filtered_df["Risk_Level"] == "Minimal Risk").sum()
anomalies_n = (filtered_df["Anomaly_Flag"] == 1).sum()
avg_risk    = round(filtered_df["Final_Risk_Score"].mean(), 4)

col1, col2, col3, col4, col5, col6 = st.columns(6)

def metric_card(col, label, value, css_class=""):
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-value {css_class}">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

metric_card(col1, "Total Containers", f"{total:,}")
metric_card(col2, "Critical Risk",    f"{critical:,}",  "critical")
metric_card(col3, "Low Risk",         f"{low:,}",       "low")
metric_card(col4, "Minimal Risk",     f"{minimal:,}",   "minimal")
metric_card(col5, "Anomalies",        f"{anomalies_n:,}")
metric_card(col6, "Avg Risk Score",   f"{avg_risk}")

# RISK DISTRIBUTION + PIE SIDE BY SIDE


st.markdown('<div class="section-title">Risk Distribution</div>', unsafe_allow_html=True)

c1, c2 = st.columns([2, 1])

with c1:
    fig = px.histogram(
        filtered_df,
        x="Final_Risk_Score",
        nbins=40,
        template="plotly_dark",
        color_discrete_sequence=["#58A6FF"],
        labels={"Final_Risk_Score": "Final Risk Score", "count": "Number of Containers"}
    )
    fig.update_layout(
        plot_bgcolor="#0D1117",
        paper_bgcolor="#0D1117",
        font_color="#C9D1D9",
        margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    risk_counts = filtered_df["Risk_Level"].value_counts().reset_index()
    risk_counts.columns = ["Risk_Level", "Count"]
    color_map = {"Critical Risk": "#F85149", "Low Risk": "#E3B341", "Minimal Risk": "#3FB950"}
    fig2 = px.pie(
        risk_counts,
        names="Risk_Level",
        values="Count",
        template="plotly_dark",
        color="Risk_Level",
        color_discrete_map=color_map,
        hole=0.45
    )
    fig2.update_layout(
        plot_bgcolor="#0D1117",
        paper_bgcolor="#0D1117",
        font_color="#C9D1D9",
        margin=dict(t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )
    st.plotly_chart(fig2, use_container_width=True)

# RISK BY ORIGIN COUNTRY

st.markdown('<div class="section-title">Risk by Origin Country</div>', unsafe_allow_html=True)

country_risk = (
    filtered_df.groupby("Origin_Country")["Final_Risk_Score"]
    .mean()
    .reset_index()
    .sort_values("Final_Risk_Score", ascending=False)
)

fig = px.bar(
    country_risk,
    x="Origin_Country",
    y="Final_Risk_Score",
    template="plotly_dark",
    color="Final_Risk_Score",
    color_continuous_scale="Reds",
    labels={"Final_Risk_Score": "Avg Risk Score", "Origin_Country": "Country"}
)
fig.update_layout(
    plot_bgcolor="#0D1117",
    paper_bgcolor="#0D1117",
    font_color="#C9D1D9",
    coloraxis_showscale=False,
    margin=dict(t=20, b=20)
)
st.plotly_chart(fig, use_container_width=True)

# RISK BY SHIPPING LINE + PORT SIDE BY SIDE

st.markdown('<div class="section-title">Risk by Shipping Line & Destination Port</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    ship_risk = (
        filtered_df.groupby("Shipping_Line")["Final_Risk_Score"]
        .mean()
        .reset_index()
        .sort_values("Final_Risk_Score", ascending=False)
    )
    fig = px.bar(
        ship_risk,
        x="Shipping_Line",
        y="Final_Risk_Score",
        template="plotly_dark",
        color="Final_Risk_Score",
        color_continuous_scale="Blues",
        labels={"Final_Risk_Score": "Avg Risk Score"}
    )
    fig.update_layout(
        plot_bgcolor="#0D1117", paper_bgcolor="#0D1117",
        font_color="#C9D1D9", coloraxis_showscale=False,
        margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    port_risk = (
        filtered_df.groupby("Destination_Port")["Final_Risk_Score"]
        .mean()
        .reset_index()
        .sort_values("Final_Risk_Score", ascending=False)
    )
    fig = px.bar(
        port_risk,
        x="Destination_Port",
        y="Final_Risk_Score",
        template="plotly_dark",
        color="Final_Risk_Score",
        color_continuous_scale="Oranges",
        labels={"Final_Risk_Score": "Avg Risk Score"}
    )
    fig.update_layout(
        plot_bgcolor="#0D1117", paper_bgcolor="#0D1117",
        font_color="#C9D1D9", coloraxis_showscale=False,
        margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

# ANOMALY DETECTION TABLE

st.markdown('<div class="section-title">Anomaly Detection</div>', unsafe_allow_html=True)

anomalies_df = filtered_df[filtered_df["Anomaly_Flag"] == 1]
st.write(f"**{len(anomalies_df):,}** anomalous containers detected")

display_cols = ["Container_ID", "Origin_Country", "Destination_Port",
                "Shipping_Line", "Final_Risk_Score", "Risk_Level", "Explanation"]
st.dataframe(
    anomalies_df[display_cols].sort_values("Final_Risk_Score", ascending=False),
    use_container_width=True,
    height=300
)

# TOP RISKY CONTAINERS

st.markdown('<div class="section-title">Top 10 Risky Containers</div>', unsafe_allow_html=True)

top_risk = filtered_df.sort_values("Final_Risk_Score", ascending=False).head(10)

st.dataframe(
    top_risk[display_cols],
    use_container_width=True,
    height=400
)

# CONTAINER SEARCH

if enable_search:

    st.markdown('<div class="section-title">Container Investigation</div>', unsafe_allow_html=True)

    container_id = st.text_input("🔍 Enter Container ID", placeholder="e.g. 41256141")

    if container_id:
        # Support both int and string IDs
        try:
            result = df[df["Container_ID"] == int(container_id)]
        except ValueError:
            result = df[df["Container_ID"] == container_id]

        if len(result) > 0:
            row = result.iloc[0]

            c1, c2, c3 = st.columns(3)
            c1.metric("Container ID",  row["Container_ID"])
            c2.metric("Risk Score",    round(row["Final_Risk_Score"], 4))
            c3.metric("Risk Level",    row["Risk_Level"])

            st.markdown("**Additional Details**")
            detail_cols = ["Origin_Country", "Destination_Country", "Destination_Port",
                           "Shipping_Line", "Declared_Value", "Declared_Weight",
                           "Measured_Weight", "Dwell_Time_Hours", "Anomaly_Flag"]
            st.dataframe(
                row[detail_cols].to_frame().T,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("**🤖 AI Explanation**")
            explanation = row["Explanation"]
            if pd.isna(explanation) or explanation == "":
                st.warning("No explanation available for this container.")
            else:
                st.info(explanation)

        else:
            st.warning(f"Container `{container_id}` not found in the dataset.")
