import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

st.set_page_config(
    page_title="Gauteng Transport Dashboard",
    page_icon="\U0001f68d",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #0f3460;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .metric-value { font-size: 2.2rem; font-weight: 700; color: #e94560; }
    .metric-label { font-size: 0.9rem; color: #a0a0a0; text-transform: uppercase; letter-spacing: 1px; }
    .alert-box {
        padding: 12px; border-radius: 8px; margin: 4px 0;
        border-left: 4px solid;
    }
    .alert-critical { background: #2d1b1b; border-color: #e94560; }
    .alert-warning { background: #2d2b1b; border-color: #f5c518; }
    .alert-info { background: #1b2d2b; border-color: #0ea5e9; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 45px; white-space: pre-wrap;
        background-color: #1a1a2e; border-radius: 6px 6px 0 0;
        padding: 8px 16px; color: #fafafa; font-weight: 500;
    }
    .stTabs [aria-selected="true"] { background-color: #e94560; color: white; }
    .report-card {
        background: #1a1a2e; padding: 16px; border-radius: 8px;
        border: 1px solid #0f3460; margin: 8px 0;
    }
    [data-testid="stSidebar"] { background: #0a0a1a; border-right: 1px solid #0f3460; }
</style>
""",
    unsafe_allow_html=True,
)

GT_HUBS = {
    "Johannesburg Park Station": [-26.1952, 28.0416],
    "Sandton Gautrain": [-26.1076, 28.0567],
    "Pretoria Station": [-25.7592, 28.1883],
    "Soweto (Bara)": [-26.2598, 27.9400],
    "Midrand Gautrain": [-25.9964, 28.1278],
    "Rosebank": [-26.1458, 28.0419],
    "OR Tambo Airport": [-26.1367, 28.2411],
    "Centurion": [-25.8524, 28.1868],
    "Menlyn Park": [-25.7820, 28.2750],
    "Fourways Mall": [-26.0227, 28.0076],
    "Alexandra Township": [-26.1070, 28.0970],
    "Tembisa": [-25.9980, 28.1600],
    "Soshanguve": [-25.5200, 28.1000],
    "Mamelodi": [-25.7100, 28.4100],
    "Vereeniging": [-26.6700, 27.9300],
}

MODES = [
    "Gautrain",
    "Metrobus Joburg",
    "Rea Vaya BRT",
    "Mini-Bus Taxi",
    "Uber/Bolt",
    "Tshwane Bus",
]
MODE_COLORS = {
    "Gautrain": "#e94560",
    "Metrobus Joburg": "#f5c518",
    "Rea Vaya BRT": "#0ea5e9",
    "Mini-Bus Taxi": "#22c55e",
    "Uber/Bolt": "#a855f7",
    "Tshwane Bus": "#f97316",
}


@st.cache_data(ttl=300)
def generate_data():
    dates = pd.date_range(end=datetime.now(), periods=90, freq="D")
    records = []
    np.random.seed(42)

    for date in dates:
        trips_per_day = np.random.poisson(lam=80)
        for _ in range(trips_per_day):
            start = np.random.choice(list(GT_HUBS.keys()))
            end = np.random.choice([h for h in GT_HUBS.keys() if h != start])
            mode = np.random.choice(MODES, p=[0.12, 0.18, 0.15, 0.42, 0.08, 0.05])
            hour = int(np.random.normal(loc=14, scale=5))
            hour = max(5, min(22, hour))
            is_peak = hour in range(6, 9) or hour in range(16, 19)
            passenger_mult = 1.8 if is_peak else 1.0
            passengers = int(np.random.poisson(lam=25 * passenger_mult))

            fare_map = {
                "Gautrain": 72,
                "Metrobus Joburg": 18,
                "Rea Vaya BRT": 15,
                "Mini-Bus Taxi": 17,
                "Uber/Bolt": 110,
                "Tshwane Bus": 16,
            }
            fare = fare_map[mode] * np.random.uniform(0.85, 1.4)

            sat_map = {
                "Gautrain": 4.5,
                "Metrobus Joburg": 3.2,
                "Rea Vaya BRT": 3.8,
                "Mini-Bus Taxi": 3.0,
                "Uber/Bolt": 4.2,
                "Tshwane Bus": 3.1,
            }
            sat = sat_map[mode] + np.random.uniform(-0.5, 0.5)
            sat = max(1, min(5, sat))

            delay_prob = (
                0.05
                if mode == "Gautrain"
                else 0.25
                if mode == "Mini-Bus Taxi"
                else 0.12
            )
            status = np.random.choice(
                ["On Time", "Delayed", "Cancelled"],
                p=[1 - delay_prob - 0.02, delay_prob, 0.02],
            )
            delay_min = 0
            if status == "Delayed":
                delay_min = int(np.random.exponential(scale=15) + 5)
            elif status == "Cancelled":
                delay_min = 0

            weather = np.random.choice(
                ["Clear", "Rain", "Fog", "Cloudy"], p=[0.55, 0.20, 0.05, 0.20]
            )
            day_name = date.strftime("%A")
            is_weekend = day_name in ["Saturday", "Sunday"]

            records.append(
                {
                    "Date": date,
                    "Hour": hour,
                    "DayName": day_name,
                    "IsWeekend": is_weekend,
                    "IsPeak": is_peak,
                    "StartHub": start,
                    "EndHub": end,
                    "StartLat": GT_HUBS[start][0],
                    "StartLon": GT_HUBS[start][1],
                    "EndLat": GT_HUBS[end][0],
                    "EndLon": GT_HUBS[end][1],
                    "Mode": mode,
                    "Passengers": passengers,
                    "Fare": round(fare, 2),
                    "Revenue": round(fare * passengers, 2),
                    "Status": status,
                    "DelayMin": delay_min,
                    "Satisfaction": round(sat, 1),
                    "Weather": weather,
                }
            )

    df = pd.DataFrame(records)
    return df


df = generate_data()

st.sidebar.image("https://img.icons8.com/fluency/96/bus.png", width=50)
st.sidebar.title("Gauteng Transit")
st.sidebar.caption("Provincial Transport Intelligence v3.0")

st.sidebar.divider()
st.sidebar.subheader("Filters")

modes = st.sidebar.multiselect(
    "Transport Modes",
    df["Mode"].unique(),
    default=["Gautrain", "Rea Vaya BRT", "Metrobus Joburg"],
)
date_range = st.sidebar.date_input(
    "Date Range",
    value=(df["Date"].min(), df["Date"].max()),
    min_value=df["Date"].min(),
    max_value=df["Date"].max(),
)
hour_range = st.sidebar.slider("Time of Day", 0, 23, (5, 22))
weather_filter = st.sidebar.multiselect(
    "Weather", df["Weather"].unique(), default=df["Weather"].unique()
)

filtered = df[
    (df["Mode"].isin(modes))
    & (df["Date"].dt.date >= date_range[0])
    & (df["Date"].dt.date <= date_range[1])
    & (df["Hour"] >= hour_range[0])
    & (df["Hour"] <= hour_range[1])
    & (df["Weather"].isin(weather_filter))
]

st.sidebar.divider()
st.sidebar.download_button(
    "Export Data (CSV)",
    filtered.to_csv(index=False).encode("utf-8"),
    "gauteng_transport.csv",
    "text/csv",
    use_container_width=True,
)

st.title("Gauteng Transport Intelligence Dashboard")
total_px = filtered["Passengers"].sum()
avg_sat = filtered["Satisfaction"].mean()
on_time = (
    filtered[filtered["Status"] == "On Time"].shape[0] / max(filtered.shape[0], 1)
) * 100
total_rev = filtered["Revenue"].sum()
avg_delay = filtered[filtered["DelayMin"] > 0]["DelayMin"].mean() or 0

cols = st.columns(5)
metrics = [
    ("Total Passengers", f"{total_px:,.0f}", ""),
    ("Satisfaction", f"{avg_sat:.1f}", "/5.0"),
    ("On-Time Rate", f"{on_time:.1f}", "%"),
    ("Revenue (ZAR)", f"R{total_rev / 1e6:.1f}", "M"),
    ("Avg Delay", f"{avg_delay:.0f}", "min"),
]
for i, (label, value, suffix) in enumerate(metrics):
    with cols[i]:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}{suffix}</div></div>',
            unsafe_allow_html=True,
        )

tabs = st.tabs(
    [
        "Network Overview",
        "Geospatial",
        "Route Analytics",
        "Predictive ML",
        "AI Assistant",
        "Reports",
    ]
)

with tabs[0]:
    st.subheader("Network Activity Overview")
    r1, r2 = st.columns(2)
    with r1:
        hourly = filtered.groupby("Hour")["Passengers"].sum().reset_index()
        fig = px.area(
            hourly,
            x="Hour",
            y="Passengers",
            title="Passenger Volume by Hour",
            color_discrete_sequence=["#e94560"],
        )
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    with r2:
        mode_share = filtered["Mode"].value_counts().reset_index()
        mode_share.columns = ["Mode", "Trips"]
        fig2 = px.pie(
            mode_share,
            values="Trips",
            names="Mode",
            title="Modal Share",
            hole=0.4,
            color_discrete_map=MODE_COLORS,
        )
        fig2.update_layout(template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Daily Trends")
    daily = (
        filtered.groupby("Date")
        .agg(
            Passengers=("Passengers", "sum"),
            Revenue=("Revenue", "sum"),
            OnTime=("Status", lambda x: (x == "On Time").mean()),
        )
        .reset_index()
    )
    daily["OnTime"] *= 100
    fig3 = go.Figure()
    fig3.add_trace(
        go.Bar(
            x=daily["Date"], y=daily["Revenue"], name="Revenue", marker_color="#16213e"
        )
    )
    fig3.add_trace(
        go.Scatter(
            x=daily["Date"],
            y=daily["OnTime"],
            name="On-Time %",
            yaxis="y2",
            line=dict(color="#e94560", width=3),
        )
    )
    fig3.update_layout(
        template="plotly_dark",
        yaxis=dict(title="Revenue (ZAR)"),
        yaxis2=dict(title="On-Time %", overlaying="y", side="right", range=[0, 100]),
    )
    st.plotly_chart(fig3, use_container_width=True)

with tabs[1]:
    st.subheader("Route Map")
    st.pydeck_chart(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/dark-v10",
            initial_view_state=pdk.ViewState(
                latitude=-26.1,
                longitude=28.1,
                zoom=9,
                pitch=45,
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=filtered[["StartLat", "StartLon", "Mode"]]
                    .rename(columns={"StartLat": "lat", "StartLon": "lon"})
                    .head(500),
                    get_position=["lon", "lat"],
                    get_color="[233, 69, 96, 160]",
                    get_radius=200,
                    pickable=True,
                ),
            ],
        )
    )

    r = st.columns(2)
    with r[0]:
        st.subheader("Active Alerts")
        alerts = [
            ("critical", "N1 Midrand southbound: accident, 45-min delay"),
            ("warning", "Rea Vaya route C1 suspended: roadworks until 18:00"),
            ("info", "Gautrain: normal service on all lines"),
            ("warning", "Mini-bus taxi strike possible: Vereeniging route"),
            ("info", "Weather: scattered thunderstorms expected 14:00-17:00"),
        ]
        for severity, msg in alerts:
            cls = f"alert-{severity}"
            icon = {
                "critical": "\U0001f6a8",
                "warning": "\u26a0\ufe0f",
                "info": "\u2139\ufe0f",
            }[severity]
            st.markdown(
                f'<div class="alert-box {cls}">{icon} {msg}</div>',
                unsafe_allow_html=True,
            )
    with r[1]:
        st.subheader("Busiest Hubs")
        hubs = filtered["StartHub"].value_counts().head(8)
        fig4 = px.bar(
            hubs,
            x=hubs.values,
            y=hubs.index,
            orientation="h",
            color_discrete_sequence=["#e94560"],
        )
        fig4.update_layout(template="plotly_dark", xaxis_title="Trips")
        st.plotly_chart(fig4, use_container_width=True)

with tabs[2]:
    st.subheader("Route Performance Analysis")
    route_stats = (
        filtered.groupby(["StartHub", "EndHub", "Mode"])
        .agg(
            Trips=("Passengers", "count"),
            AvgPassengers=("Passengers", "mean"),
            AvgSatisfaction=("Satisfaction", "mean"),
            OnTimeRate=("Status", lambda x: (x == "On Time").mean()),
            AvgDelay=("DelayMin", "mean"),
        )
        .reset_index()
    )
    route_stats["OnTimeRate"] *= 100
    route_stats["Route"] = route_stats["StartHub"] + " \u279d " + route_stats["EndHub"]

    col_d1, col_d2 = st.columns([2, 1])
    with col_d1:
        fig5 = px.scatter(
            route_stats,
            x="AvgSatisfaction",
            y="OnTimeRate",
            size="Trips",
            color="Mode",
            hover_name="Route",
            title="Satisfaction vs Reliability",
            color_discrete_map=MODE_COLORS,
            labels={"AvgSatisfaction": "Avg Satisfaction", "OnTimeRate": "On-Time %"},
        )
        fig5.update_layout(template="plotly_dark")
        st.plotly_chart(fig5, use_container_width=True)
    with col_d2:
        st.subheader("Underperformers")
        bad = route_stats[route_stats["AvgSatisfaction"] < 3.0].sort_values(
            "AvgSatisfaction"
        )
        if not bad.empty:
            st.dataframe(
                bad[["Route", "Mode", "AvgSatisfaction", "OnTimeRate"]].head(8),
                column_config={
                    "AvgSatisfaction": st.column_config.ProgressColumn(
                        "Rating",
                        format="%.1f",
                        min_value=1,
                        max_value=5,
                    ),
                    "OnTimeRate": st.column_config.ProgressColumn(
                        "On-Time",
                        format="%.0f%%",
                        min_value=0,
                        max_value=100,
                    ),
                },
                hide_index=True,
                use_container_width=True,
            )

    st.subheader("Delay Distribution")
    delays = filtered[filtered["DelayMin"] > 0]
    if not delays.empty:
        fig6 = px.histogram(
            delays, x="DelayMin", color="Mode", nbins=30, color_discrete_map=MODE_COLORS
        )
        fig6.update_layout(template="plotly_dark")
        st.plotly_chart(fig6, use_container_width=True)

with tabs[3]:
    st.subheader("Machine Learning Predictions")
    st.caption("Demand forecasting and delay prediction using scikit-learn")

    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, accuracy_score

    ml_df = filtered.copy()
    ml_df["HourSin"] = np.sin(2 * np.pi * ml_df["Hour"] / 24)
    ml_df["HourCos"] = np.cos(2 * np.pi * ml_df["Hour"] / 24)
    ml_df["DayOfWeek"] = pd.Categorical(ml_df["DayName"]).codes
    ml_df["IsWeekend"] = ml_df["IsWeekend"].astype(int)
    ml_df["IsPeak"] = ml_df["IsPeak"].astype(int)
    ml_df["ModeCode"] = pd.Categorical(ml_df["Mode"]).codes

    feature_cols = [
        "HourSin",
        "HourCos",
        "DayOfWeek",
        "IsWeekend",
        "IsPeak",
        "ModeCode",
    ]

    col_ml1, col_ml2 = st.columns(2)

    with col_ml1:
        st.markdown("### Demand Forecast")
        X = ml_df[feature_cols]
        y = ml_df["Passengers"]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)

        future_hours = np.arange(5, 23)
        future = pd.DataFrame(
            {
                "HourSin": np.sin(2 * np.pi * future_hours / 24),
                "HourCos": np.cos(2 * np.pi * future_hours / 24),
                "DayOfWeek": 2,
                "IsWeekend": 0,
                "IsPeak": 0,
                "ModeCode": 0,
            }
        )
        future["IsPeak"] = (
            (future_hours >= 6) & (future_hours <= 9)
            | (future_hours >= 16) & (future_hours <= 19)
        ).astype(int)
        forecast = rf.predict(future)

        fig7 = px.line(
            x=future_hours,
            y=forecast,
            markers=True,
            title=f"Predicted Passengers by Hour (MAE: {mae:.1f})",
            labels={"x": "Hour", "y": "Predicted Passengers"},
            color_discrete_sequence=["#e94560"],
        )
        fig7.update_layout(template="plotly_dark")
        st.plotly_chart(fig7, use_container_width=True)

    with col_ml2:
        st.markdown("### Delay Prediction")
        ml_df["IsDelayed"] = (ml_df["Status"] != "On Time").astype(int)
        Xd = ml_df[feature_cols]
        yd = ml_df["IsDelayed"]
        Xd_train, Xd_test, yd_train, yd_test = train_test_split(
            Xd, yd, test_size=0.2, random_state=42
        )
        clf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
        clf.fit(Xd_train, yd_train)
        yd_pred = clf.predict(Xd_test)
        acc = accuracy_score(yd_test, yd_pred)

        feature_importance = pd.DataFrame(
            {
                "Feature": ["Time", "Time (cos)", "Day", "Weekend", "Peak", "Mode"],
                "Importance": clf.feature_importances_,
            }
        ).sort_values("Importance", ascending=True)

        fig8 = px.bar(
            feature_importance,
            x="Importance",
            y="Feature",
            orientation="h",
            title=f"Delay Prediction Factors (Accuracy: {acc:.1%})",
            color_discrete_sequence=["#0ea5e9"],
        )
        fig8.update_layout(template="plotly_dark")
        st.plotly_chart(fig8, use_container_width=True)

    st.info(
        "Model is trained on filtered data in real-time. Retrains when filters change."
    )

with tabs[4]:
    st.subheader("AI Transport Assistant")
    st.caption("Powered by local LLM (Ollama) or rule-based fallback")

    col_ai1, col_ai2 = st.columns([3, 2])

    with col_ai1:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about the transport network..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            p = prompt.lower()
            response = ""
            if "busiest" in p or "popular" in p:
                top = filtered["EndHub"].mode()
                response = f"The busiest destination is **{top.iloc[0]}** with peak traffic 07:00-09:00."
            elif "delay" in p or "late" in p:
                rate = (
                    filtered[filtered["Status"] != "On Time"].shape[0]
                    / max(filtered.shape[0], 1)
                ) * 100
                response = f"Currently **{rate:.1f}%** of trips are delayed or cancelled. Mini-bus taxis have the highest delay rate."
            elif "gautrain" in p:
                g = filtered[filtered["Mode"] == "Gautrain"]
                sat = g["Satisfaction"].mean() if not g.empty else 4.5
                response = f"Gautrain satisfaction: **{sat:.1f}/5.0**. On-time rate exceeds 95%. Busiest at OR Tambo and Sandton."
            elif "weather" in p or "rain" in p:
                weather_stats = filtered.groupby("Weather")["DelayMin"].mean()
                worst = weather_stats.idxmax() if not weather_stats.empty else "Rain"
                response = f"**{worst}** causes the longest delays. Average delay during rain: **{weather_stats.get('Rain', 0):.0f} min**."
            elif "revenue" in p or "money" in p:
                rev = filtered["Revenue"].sum()
                response = f"Total revenue: **R{rev:,.2f}**. Gautrain contributes the most revenue per trip."
            elif "safety" in p or "crime" in p:
                response = "Safety data is not available in this dataset. Contact SAPS or Gauteng transport authorities for crime statistics."
            else:
                try:
                    import ollama

                    context = f"""
Transport data summary for Gauteng:
- Total trips: {len(filtered)}
- Passengers: {total_px:,.0f}
- Satisfaction: {avg_sat:.1f}/5.0
- On-time rate: {on_time:.1f}%
- Modes: {", ".join(filtered["Mode"].unique())}
Question: {prompt}
Answer concisely based on this data.
"""
                    resp = ollama.generate(model="llama3.2:3b", prompt=context)
                    response = resp["response"]
                except Exception:
                    response = (
                        "I'm analyzing... The network is operating at "
                        f"**{on_time:.0f}%** efficiency. Try asking about "
                        "specific modes, routes, delays, or revenue."
                    )

            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.chat_history.append(
                {"role": "assistant", "content": response}
            )

    with col_ai2:
        st.markdown("### 7-Day Demand Forecast")
        future_dates = pd.date_range(start=df["Date"].max(), periods=7, freq="D")
        base = total_px / max(len(filtered["Date"].unique()), 1)
        trends = [1.1, 1.05, 1.2, 1.25, 0.9, 0.8, 1.15]
        forecast_demand = [base * t * np.random.uniform(0.9, 1.1) for t in trends]
        fdf = pd.DataFrame({"Date": future_dates, "Predicted Demand": forecast_demand})
        fig9 = px.line(
            fdf,
            x="Date",
            y="Predicted Demand",
            markers=True,
            title="Passenger Demand Forecast",
            color_discrete_sequence=["#22c55e"],
        )
        fig9.update_layout(template="plotly_dark")
        st.plotly_chart(fig9, use_container_width=True)
        st.success("Increase capacity by 20% on Friday to meet expected demand.")

with tabs[5]:
    st.subheader("Generate Reports")
    st.caption("Export professional PDF reports for stakeholder meetings")

    report_type = st.selectbox(
        "Report Type",
        [
            "Executive Summary",
            "Route Performance",
            "Mode Analysis",
            "Delay & Reliability",
        ],
    )
    include_charts = st.checkbox("Include visualizations", value=True)

    if st.button("Generate Report", type="primary"):
        with st.spinner("Generating report..."):
            try:
                from fpdf import FPDF

                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Helvetica", "B", 20)
                pdf.cell(
                    0,
                    15,
                    "Gauteng Transport Report",
                    align="C",
                    new_x="LMARGIN",
                    new_y="NEXT",
                )
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(
                    0,
                    8,
                    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    align="C",
                    new_x="LMARGIN",
                    new_y="NEXT",
                )
                pdf.cell(
                    0,
                    8,
                    f"Period: {date_range[0]} to {date_range[1]}",
                    align="C",
                    new_x="LMARGIN",
                    new_y="NEXT",
                )
                pdf.ln(10)

                pdf.set_font("Helvetica", "B", 14)
                pdf.cell(0, 10, "Key Metrics", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", "", 11)
                for label, val in [
                    ("Total Passengers", f"{total_px:,.0f}"),
                    ("Average Satisfaction", f"{avg_sat:.1f}/5.0"),
                    ("On-Time Performance", f"{on_time:.1f}%"),
                    ("Total Revenue", f"R{total_rev:,.2f}"),
                ]:
                    pdf.cell(0, 8, f"  {label}: {val}", new_x="LMARGIN", new_y="NEXT")

                report_path = os.path.join(os.path.dirname(__file__), "report.pdf")
                pdf.output(report_path)

                with open(report_path, "rb") as f:
                    st.download_button(
                        "Download PDF Report",
                        f.read(),
                        f"gauteng_transport_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        "application/pdf",
                    )
                os.remove(report_path)
            except Exception as e:
                csv_report = filtered.describe().to_csv()
                st.download_button(
                    "Download CSV Summary",
                    csv_report.encode("utf-8"),
                    "report_summary.csv",
                    "text/csv",
                )
                st.info(
                    "PDF generation requires fpdf2. Install with: pip install fpdf2"
                )

st.markdown("---")
st.caption(
    "Gauteng Transport Intelligence Dashboard | Developed by Raphasha27 | Data simulated for demonstration"
)

# KDT_WIDGET_INJECTED
import streamlit.components.v1 as st_components_kdt
st_components_kdt.html('''<script>
(function () {
  if (window.__KDT_BRAND__) return;
  window.__KDT_BRAND__ = true;

  var APP_NAME = window.KDT_APP_NAME || document.title || "This application";
  var UPGRADE_EMAIL = "raphashakoketso69@gmail.com";
  var TRIAL_DAYS = 7;
  var STORAGE_KEY = "kdt_trial_start";

  var start = parseInt(localStorage.getItem(STORAGE_KEY), 10);
  if (!start || isNaN(start)) { start = Date.now(); try { localStorage.setItem(STORAGE_KEY, String(start)); } catch (e) {} }

  var daysUsed = Math.floor((Date.now() - start) / 86400000);
  var trialOver = daysUsed >= TRIAL_DAYS;

  var css = [
    "#kdt-widget{position:fixed;bottom:10px;right:10px;z-index:2147483646;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;text-align:left;direction:ltr}",
    "#kdt-badge{display:flex;align-items:center;gap:6px;background:rgba(10,10,20,.85);color:#fff;border:1px solid rgba(255,255,255,.25);border-radius:999px;padding:6px 12px;font-size:12px;font-weight:600;letter-spacing:.4px;cursor:pointer;box-shadow:0 2px 10px rgba(0,0,0,.35);transition:transform .15s ease;backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px)}",
    "#kdt-badge:hover{transform:scale(1.04)}",
    "#kdt-badge .kdt-dot{width:8px;height:8px;border-radius:50%;background:#22c55e;flex:0 0 auto}",
    "#kdt-modal{display:none;position:fixed;inset:0;z-index:2147483647;background:rgba(0,0,0,.55);align-items:center;justify-content:center;padding:16px;backdrop-filter:blur(2px);-webkit-backdrop-filter:blur(2px)}",
    "#kdt-modal.kdt-open{display:flex}",
    "#kdt-card{background:#fff;color:#111;max-width:420px;width:100%;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.4);overflow:hidden;max-height:92vh;overflow-y:auto}",
    "#kdt-card .kdt-head{background:linear-gradient(135deg,#0f172a,#1e293b);color:#fff;padding:20px 22px;display:flex;align-items:center;gap:12px}",
    "#kdt-card .kdt-logo{width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,#22c55e,#0ea5e9);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;color:#fff;flex:0 0 auto}",
    "#kdt-card .kdt-title{font-size:16px;font-weight:800;line-height:1.2}",
    "#kdt-card .kdt-sub{font-size:12px;opacity:.85;margin-top:2px}",
    "#kdt-card .kdt-body{padding:20px 22px 6px;font-size:14px;line-height:1.55;color:#1f2937}",
    "#kdt-card .kdt-body p{margin:0 0 10px}",
    "#kdt-card .kdt-license{background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:12px 14px;font-size:12.5px;color:#334155;margin:0 0 14px}",
    "#kdt-card .kdt-plans{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:0 0 14px}",
    "#kdt-card .kdt-plan{border:2px solid #e2e8f0;border-radius:12px;padding:14px 12px;text-align:center;cursor:pointer;transition:border-color .15s ease;position:relative}",
    "#kdt-card .kdt-plan.kdt-sel{border-color:#16a34a;background:#f0fdf4}",
    "#kdt-card .kdt-plan .kdt-price{font-size:20px;font-weight:800;color:#0f172a}",
    "#kdt-card .kdt-plan .kdt-per{font-size:11px;color:#64748b;margin-top:2px}",
    "#kdt-card .kdt-plan .kdt-save{position:absolute;top:-9px;right:8px;background:#16a34a;color:#fff;font-size:10px;font-weight:700;border-radius:999px;padding:2px 8px}",
    "#kdt-card .kdt-btn{display:block;width:100%;border:0;border-radius:12px;padding:14px;font-size:15px;font-weight:700;cursor:pointer;color:#fff;background:linear-gradient(135deg,#16a34a,#15803d);margin:0 0 10px;transition:filter .15s ease}",
    "#kdt-card .kdt-btn:hover{filter:brightness(1.08)}",
    "#kdt-card .kdt-note{font-size:11.5px;color:#64748b;text-align:center;padding:0 6px 16px}",
    "#kdt-card .kdt-x{position:absolute;top:14px;right:14px;background:rgba(255,255,255,.15);border:0;color:#fff;font-size:16px;width:28px;height:28px;border-radius:50%;cursor:pointer;line-height:1}",
    "@media (max-width:480px){#kdt-card .kdt-plans{grid-template-columns:1fr}#kdt-badge{font-size:11px;padding:5px 10px}#kdt-card .kdt-title{font-size:15px}}",
    "@media (prefers-reduced-motion:reduce){#kdt-badge{transition:none}}"
  ].join("");

  var style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  var el = document.createElement("div");
  el.id = "kdt-widget";
  el.innerHTML = [
    '<div id="kdt-badge" role="button" aria-label="Kirov Dynamics Technology information">',
    '<span class="kdt-dot"></span><span>KDT &middot; Kirov Dynamics Technology</span>',
    "</div>",
    '<div id="kdt-modal" role="dialog" aria-modal="true">',
    '<div id="kdt-card">',
    '<button class="kdt-x" aria-label="Close">&times;</button>',
    '<div class="kdt-head"><div class="kdt-logo">KDT</div><div><div class="kdt-title">Kirov Dynamics Technology</div><div class="kdt-sub">Proudly South African &middot; Built in SA</div></div></div>',
    '<div class="kdt-body">',
    '<p><strong>KDT License Notice</strong></p>',
    '<div class="kdt-license">This application is the property of <strong>Kirov Dynamics Technology (KDT)</strong>. Unauthorised use, copying or redistribution is prohibited. By using this app you agree to the KDT terms of service.</div>',
    '<p id="kdt-trial-text" style="display:none"><strong>Free trial complete!</strong> Your free trial of this app has ended. Upgrade to Pro to continue enjoying all features.</p>',
    '<p><strong>Upgrade to KDT Pro</strong></p>',
    '<div class="kdt-plans">',
    '<div class="kdt-plan kdt-sel" data-plan="monthly"><div class="kdt-price">R49</div><div class="kdt-per">per month</div></div>',
    '<div class="kdt-plan" data-plan="yearly"><div class="kdt-save">Save 16%</div><div class="kdt-price">R490</div><div class="kdt-per">per year</div></div>',
    "</div>",
    '<button class="kdt-btn" id="kdt-upgrade">Upgrade to Pro &rarr;</button>',
    '<div class="kdt-note">On upgrade, an email request is sent to KDT. Once approved, your Pro access will be activated.</div>',
    "</div>",
    "</div>",
    "</div>",
  ].join("");

  document.body.appendChild(el);

  var modal = el.querySelector("#kdt-modal");
  var badge = el.querySelector("#kdt-badge");
  var xBtn = el.querySelector(".kdt-x");
  var upgradeBtn = el.querySelector("#kdt-upgrade");
  var plans = Array.prototype.slice.call(el.querySelectorAll(".kdt-plan"));
  var selectedPlan = "monthly";
  var trialText = el.querySelector("#kdt-trial-text");

  if (trialOver) { trialText.style.display = ""; badge.style.background = "rgba(220,38,38,.9)"; badge.style.borderColor = "rgba(255,255,255,.35)"; }

  function close() { modal.classList.remove("kdt-open"); }
  badge.addEventListener("click", function () { modal.classList.add("kdt-open"); });
  xBtn.addEventListener("click", close);
  modal.addEventListener("click", function (e) { if (e.target === modal) close(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });

  plans.forEach(function (p) {
    p.addEventListener("click", function () {
      plans.forEach(function (q) { q.classList.remove("kdt-sel"); });
      p.classList.add("kdt-sel");
      selectedPlan = p.getAttribute("data-plan");
    });
  });

  upgradeBtn.addEventListener("click", function () {
    var planLabel = selectedPlan === "monthly" ? "Monthly (R49/month)" : "Yearly (R490/year)";
    var subject = encodeURIComponent("[KDT PRO UPGRADE] " + APP_NAME + " - " + planLabel);
    var body = encodeURIComponent(
      "Hello Kirov Dynamics Technology,\n\n" +
      "I would like to upgrade to KDT Pro for the following application:\n\n" +
      "Application: " + APP_NAME + "\n" +
      "Plan: " + planLabel + "\n" +
      "Date: " + new Date().toISOString() + "\n\n" +
      "Please activate my Pro access. Thank you!"
    );
    window.location.href = "mailto:" + UPGRADE_EMAIL + "?subject=" + subject + "&body=" + body;
  });
})();

</script>''', height=0)
