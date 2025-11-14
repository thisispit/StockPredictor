import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool
import joblib
import os
import sys

def create_dashboard(symbol='INFY'):
    # Load the model
    model_path = f'models/{symbol}_models.pkl'
    if not os.path.exists(model_path):
        print(f"Model for {symbol} not found. Please run models.py first.")
        return

    models = joblib.load(model_path)
    model = models.get('tuned', models.get('quick'))

    # Load the data
    data_path = f'processed/{symbol}_features.csv'
    if not os.path.exists(data_path):
        print(f"Data for {symbol} not found. Please run features.py first.")
        return

    df = pd.read_csv(data_path, parse_dates=['Date'])

    # Make predictions
    features = ['Close', 'ma_4w', 'ma_16w', 'ma_52w', 'vol_shock', 'price_shock']
    X = df[features].fillna(method='ffill').dropna()
    df['predicted'] = model.predict(X)

    # Predict the next day
    last_X = X.tail(1)
    next_day_pred = model.predict(last_X)[0]
    last_date = df['Date'].iloc[-1]
    next_day_date = last_date + pd.Timedelta(days=1)

    # Create a new DataFrame for the next day's prediction
    next_day_df = pd.DataFrame({'Date': [next_day_date], 'predicted': [next_day_pred], 'Close': [next_day_pred]})


    source = ColumnDataSource(df)
    next_day_source = ColumnDataSource(next_day_df)

    # Create the plot
    p = figure(height=400, width=800, title=f'{symbol} Stock Price Prediction', x_axis_type='datetime')

    p.line(x='Date', y='Close', source=source, legend_label='Actual Close', color='blue', line_width=2)
    p.line(x='Date', y='predicted', source=source, legend_label='Predicted Close', color='orange', line_width=2, line_dash='dashed')
    p.circle(x='Date', y='predicted', source=next_day_source, legend_label='Next Day Prediction', color='red', size=8)


    p.add_tools(HoverTool(
        tooltips=[
            ('Date', '@Date{%F}'),
            ('Actual', '@Close{0.2f}'),
            ('Predicted', '@predicted{0.2f}'),
        ],
        formatters={
            '@Date': 'datetime',
        },
        mode='vline'
    ))

    p.legend.location = 'top_left'
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'

    show(p)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        create_dashboard(sys.argv[1].upper())
    else:
        print("Usage: python dashboard.py <STOCK_SYMBOL>")
        print("Defaulting to INFY.")
        create_dashboard()
