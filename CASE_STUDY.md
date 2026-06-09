# Case Study: Gauteng Transport Intelligence Dashboard

## Overview
An interactive transport analytics dashboard for South Africa's most populous province, providing real-time tracking, ML-powered predictions, and AI-driven insights for buses, trains, taxis, and ride-hailing services.

## The Problem
Gauteng's transport network — the economic heart of South Africa — lacks a unified view of its multi-modal system. Disparate data sources, limited predictive capability, and no centralized intelligence mean delays compound and commuters bear the cost.

## The Solution
A Streamlit-based dashboard that ingests simulated multi-modal transport data, applies machine learning for demand forecasting and delay prediction, and visualizes everything on an interactive geospatial map with an AI assistant for natural language queries.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                       │
│  ┌─────────────┐  ┌──────────┐  ┌────────┐  ┌──────────┐  │
│  │ Network      │  │ Geo      │  │ ML      │  │ AI       │  │
│  │ Overview     │  │ Map      │  │ Engine  │  │ Assistant│  │
│  └─────────────┘  └──────────┘  └────────┘  └──────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Plotly Charts   │  PyDeck 3D     │  scikit-learn  │ Ollama │
├─────────────────────────────────────────────────────────────┤
│                Simulated Gauteng Transport Dataset            │
│  15 hubs · 6 modes · 90 days · Weather · Delays · Revenue   │
└─────────────────────────────────────────────────────────────┘
```

## Key Results

| Metric | Value |
|--------|-------|
| Transport modes covered | 6 (bus, train, taxi, BRT, Gautrain, ride-hailing) |
| Hubs monitored | 15 major transport hubs |
| ML models deployed | 2 (demand forecasting + delay prediction) |
| Forecast accuracy | MAE displayed per model run |
| Report generation | PDF export for stakeholder meetings |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend/Dashboard | Streamlit |
| Visualizations | Plotly, PyDeck |
| Machine Learning | scikit-learn (Random Forest) |
| AI Assistant | Ollama (local LLM) + rule-based fallback |
| Reports | fpdf2 |
| Deployment | Streamlit Community Cloud, Docker |

## Impact
Provides transport authorities and commuters with a prototype for data-driven decision making — demonstrating how South African transport data can be unified, analyzed, and acted upon in real time.

## Links
- **GitHub:** https://github.com/Raphasha27/gauteng-transport-dashboard
- **Live Demo:** https://gauteng-transport-dashboard.streamlit.app
- **Portfolio:** https://raphasha27.github.io/raphasha-dev-portfolio
- **Author:** Koketso Raphasha — Practical AI for Africa