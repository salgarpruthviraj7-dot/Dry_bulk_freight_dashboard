# 🚢 Dry Bulk Freight Dashboard

An interactive dashboard to analyse the **Baltic Dry Index (BDI)** and freight trends of different dry bulk vessel classes (Capesize, Panamax, Supramax).

🔗 **Live app:** https://YOUR-APP-LINK.streamlit.app

---

## 📌 Overview

The Baltic Dry Index is a benchmark for the cost of shipping dry bulk cargo such as iron ore, coal and grain. It is widely followed as an indicator of global trade activity.

This project turns freight data into an easy-to-use dashboard. Users can filter by date, pick a freight series, compare vessel classes, and study trends and volatility without writing any code.

## ✨ Features

- **Overview cards:** latest value, weekly change, monthly change, period high and period low
- **Trend tab:** line chart with 7-day and 30-day moving averages
- **Vessel comparison tab:** compare Capesize, Panamax and Supramax side by side
- **Volatility tab:** see how much freight rates fluctuate
- **Data tab:** view the cleaned dataset
- **Sidebar filters:** date range, main series, vessel classes and moving-average windows
- **CSV upload:** analyse your own freight data

> **Note:** By default the app shows **synthetic demo data** (not real market data). Upload a real CSV from the sidebar to analyse actual freight rates.

## 🛠️ Tech Stack

| Tool | Use |
|------|-----|
| Python | Core language |
| Pandas | Data cleaning and calculations |
| Plotly | Interactive charts |
| Streamlit | Web app interface |

## 📁 Project Structure

```
Dry_bulk_freight_dashboard/
├── app.py            # Streamlit app (UI, charts, tabs)
├── data_utils.py     # Data cleaning, moving averages, indicators, volatility
├── requirements.txt  # Python dependencies
└── README.md
```

## ▶️ Run Locally

1. Clone the repository
```bash
   git clone https://github.com/salgarpruthviraj7-dot/Dry_bulk_freight_dashboard.git
   cd Dry_bulk_freight_dashboard
```
2. Install the dependencies
```bash
   pip install -r requirements.txt
```
3. Start the app
```bash
   streamlit run app.py
```
4. Open `http://localhost:8501` in your browser.

## 📄 CSV Format

Upload a CSV with a date column and one column for each freight series (for example BDI, Capesize, Panamax, Supramax). Check `data_utils.py` for the exact column names expected.

## 📸 Screenshots

Add your screenshots here (upload them to the repository, then link them):

```
![Dashboard overview](screenshots/overview.png)
```

## 👥 Team

- Pruthviraj Salgar
- Paras Rachannavar

**Project guide:** Mrs. P. S. Bahulekar
B.Tech CSE (AI & ML), Sanjay Bhokare Group of Institutes, Faculty of Engineering, Miraj

## 🔮 Future Improvements

- Connect to live BDI data sources
- Add forecasting models for freight rates
- Export charts and reports
