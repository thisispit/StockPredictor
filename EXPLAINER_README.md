# Explainer README for the Python Stock Predictor Project

This document provides a detailed explanation of the Python Stock Predictor project, covering its concepts, data pipeline, technology stack, and how to use it.

## 1. Introduction

This project is a Python-based stock prediction pipeline that demonstrates a complete end-to-end workflow for a data science project. It includes the following key steps:

1.  **Data Fetching:** Downloading historical stock data from Yahoo Finance.
2.  **Feature Engineering:** Creating additional features from the raw data to improve model performance.
3.  **Model Training:** Training machine learning models on the engineered features.
4.  **Prediction:** Using the trained models to make predictions on new data.
5.  **Visualization:** Creating interactive plots to visualize the data and model performance.
6.  **Dashboard:** An interactive Bokeh dashboard to visualize predictions.

## 2. Technology Stack

The project is built entirely in Python and leverages several popular libraries for data science and machine learning:

*   **`pandas`:** The primary library for data manipulation and analysis. It is used for reading, writing, and transforming data in the form of DataFrames.
*   **`numpy`:** A fundamental library for numerical operations in Python. It is used for efficient array and matrix operations.
*   **`yfinance`:** A library for fetching historical stock data from Yahoo Finance.
*   **`scikit-learn`:** A comprehensive machine learning library that provides tools for model training, evaluation, and selection. The following modules are used:
    *   `LinearRegression`: A simple linear regression model.
    *   `LassoLars`: A linear model that uses L1 regularization to prevent overfitting.
    *   `GridSearchCV`: For finding the best hyperparameters for a model.
    *   `TimeSeriesSplit`: For cross-validation of time series data.
*   **`bokeh`:** A library for creating interactive data visualizations for the web.
*   **`pytest`:** A framework for writing and running tests.
*   **`joblib`:** A library for saving and loading Python objects, used here to save and load trained models.
*   **`argparse`:** A library for parsing command-line arguments, making the scripts easy to run from the terminal.

## 3. Project Structure

The project is organized into the following files and directories:

*   **`data_fetch.py`:** A script for downloading historical stock data.
*   **`features.py`:** A script for generating features from the raw data.
*   **`models.py`:** A script for training and saving machine learning models.
*   **`stockpredictor.py`:** A command-line interface for making predictions.
*   **`visualize_bokeh.py`:** A script for creating visualizations of the data.
*   **`dashboard.py`:** A script for generating an interactive Bokeh dashboard for predictions.
*   **`tests/test_models.py`:** Contains tests for the models.
*   **`requirements.txt`:** Lists the project dependencies.
*   **`data/`:** A directory for storing the raw downloaded data.
*   **`processed/`:** A directory for storing the processed data with engineered features.
*   **`models/`:** A directory for storing the trained models.
*   **`plots/`:** A directory for storing the generated plots.

## 4. Data Pipeline

The project follows a clear and logical data pipeline, with each script responsible for a specific stage of the process.

### 4.1. Data Fetching (`data_fetch.py`)

This script is the entry point for the data pipeline. It uses the `yfinance` library to download historical stock data for specified tickers and an index. The script can be configured with the following command-line arguments:

*   `--tickers`: A list of stock tickers to download (e.g., `INFY.NS`, `TCS.NS`).
*   `--index`: The index to download (e.g., `^NSEI` for the Nifty 50).
*   `--start`: The start date for the data (e.g., `2000-01-01`).
*   `--end`: The end date for the data (e.g., `2023-12-31`).
*   `--out`: The output directory for the downloaded data (defaults to `data/`).

### 4.2. Feature Engineering (`features.py`)

This script takes the raw data from the `data/` directory and generates a set of features that can be used to train the machine learning models. The engineered features are:

*   **Moving Averages (`ma_4w`, `ma_16w`, `ma_52w`):** These features capture the trend of the stock price over different time horizons (4, 16, and 52 weeks).
*   **Rolling Mean (`roll_mean_10`, `roll_mean_75`):** These features smooth out short-term fluctuations in the stock price.
*   **Volume Shocks (`vol_shock`, `vol_shock_dir`):** These features identify days with unusually high or low trading volume, which can be indicative of significant market events.
*   **Price Shocks (`price_shock`, `price_shock_dir`):** These features identify days with significant price movements.
*   **Black Swan Events (`black_swan`):** These features identify extreme price movements that are several standard deviations away from the mean.
*   **Price Shock without Volume (`price_no_vol`):** This feature identifies price movements that are not accompanied by a corresponding change in volume, which can be a sign of market manipulation or other anomalies.

The script saves the processed data with the engineered features to the `processed/` directory.

### 4.3. Model Training (`models.py`)

This script trains two machine learning models on the processed data:

*   **`LinearRegression`:** A simple and fast linear model that serves as a baseline.
*   **`LassoLars`:** A linear model that uses L1 regularization to prevent overfitting and perform feature selection.

The script uses `TimeSeriesSplit` for cross-validation, which is essential for time series data to prevent data leakage from the future to the past. `GridSearchCV` is used to find the best hyperparameters for the `LassoLars` model.

The trained models are saved to the `models/` directory using `joblib`, which allows them to be easily loaded and used for prediction later.

### 4.4. Prediction (`stockpredictor.py`)

This script provides a simple command-line interface for making predictions. It loads a trained model from the `models/` directory and uses it to predict the next day's closing price for a given stock.

### 4.5. Visualization (`visualize_bokeh.py`)

This script uses the `bokeh` library to create interactive visualizations of the data. It generates two types of plots:

*   **Time Series Plots:** These plots show the closing price of the stock over time, along with the moving averages and other features.
*   **PACF Plots:** These plots show the Partial Autocorrelation Function of the stock price, which can be used to identify the order of an autoregressive model.

The generated plots are saved as HTML files in the `plots/` directory.

### 4.6. Dashboard (`dashboard.py`)

This script generates an interactive Bokeh dashboard to visualize the actual stock prices, the model's predictions, and the predicted price for the next day. It provides a quick and intuitive way to assess the model's performance.

## 5. How to Use

To run the project, follow these steps:

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt yfinance
    ```
2.  **Fetch data:**
    ```bash
    python data_fetch.py --tickers INFY.NS TCS.NS --index ^NSEI --start 2000-01-01 --end 2023-12-31
    ```
3.  **Create features:**
    ```bash
    python features.py --input-dir data --output-dir processed
    ```
4.  **Visualize:**
    ```bash
    python visualize_bokeh.py --input processed --out plots
    ```
5.  **Run models:**
    ```bash
    python models.py
    ```
6.  **Run tests:**
    ```bash
    python -m pytest -q
    ```
7.  **Quick prediction CLI:**
    ```bash
    python stockpredictor.py INFY
    ```
8.  **Run Dashboard:**
    ```bash
    python dashboard.py INFY
    ```
    (Replace `INFY` with the desired stock symbol. If no symbol is provided, it defaults to `INFY`.)