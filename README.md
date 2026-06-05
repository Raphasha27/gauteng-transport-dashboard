---
title: Gauteng Transport Dashboard
emoji: 🚍
colorFrom: red
colorTo: blue
sdk: docker
pinned: false
---

# Gauteng Transport Intelligence Dashboard

Interactive transport analytics dashboard for Gauteng province. Real-time tracking, route diagnostics, ML-powered predictions, and AI insights for buses, trains, taxis, and ride-hailing.

## Features

### Network Overview
Real-time KPIs: passenger volume, satisfaction, on-time rate, revenue, delays. Hourly and daily trends with modal share breakdown.

### Geospatial Map
Interactive route map with hub activity visualization and live alert system (accidents, suspensions, weather).

### Route Analytics
Route performance scatter plot, underperformer identification, delay distribution histogram, and detailed route statistics.

### Machine Learning
- **Demand Forecasting**: Random Forest predicts passenger volume by hour (MAE displayed)
- **Delay Prediction**: Classification model identifies key delay factors (peak hour, weather, mode)

### AI Assistant
Chat interface with Ollama integration (local LLM) or rule-based fallback. Answers questions about busiest routes, delays, Gautrain status, weather impact, and revenue.

### Reports
PDF report generation for stakeholder meetings with key metrics and optionally included charts.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deployment

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gauteng-transport-dashboard.streamlit.app)

Deploy on Streamlit Community Cloud:
1. Push to GitHub
2. Go to streamlit.io/cloud → New app
3. Repo: `Raphasha27/gauteng-transport-dashboard`
4. Branch: `main`, File: `streamlit_app.py`
5. Deploy

## Data

Simulated dataset covering 15 major transport hubs across Gauteng with 6 transport modes, 90 days of trip data including weather, delays, satisfaction, and revenue metrics.

## Tech Stack

- **Streamlit** — Frontend & dashboard framework
- **Plotly** — Interactive visualizations
- **scikit-learn** — ML predictions (Random Forest)
- **Ollama** — Local LLM AI assistant
- **PyDeck** — 3D geospatial mapping
- **fpdf2** — PDF report generation

## License

MIT
