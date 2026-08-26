import warnings
warnings.filterwarnings('ignore')

import streamlit as st
import seaborn as sns
import pandas as pd
from pathlib import Path
import joblib
import datetime as dt

from models.lgbm.predict import predict

cwd = Path.cwd()

local_price = pd.read_csv(cwd / 'data' / 'local_price_test.csv')
pangoly_price = pd.read_csv(cwd / 'data' / 'pangoly.csv')
pangoly_price['date'] = pd.to_datetime(pangoly_price['date'])

local_price = local_price.dropna(subset=['pangoly_group'])

lgbm = joblib.load('./models/lgbm/lgbm.joblib')

arima_cpu = joblib.load('./models/arima/cpu.joblib')
arima_gpu = joblib.load('./models/arima/gpu.joblib')
arima_ram = joblib.load('./models/arima/ram.joblib')

def run_predict_price():
    st.title('DealSense')

    st.subheader('Dapatkan perkiraan harga part PC mu!')

    cat_opt = st.selectbox(
        "Category: ",
        ("PROCESSORS", "GRAPHICS CARDS", "MEMORY"),
    )

    selected_cat_df = local_price[local_price['pangoly_category'] == cat_opt]

    prod_types = list(selected_cat_df['actual_type'].unique())
    prod_types.sort()

    product_type_opt = st.selectbox(
        "Type: ",
        prod_types
    )

    selected_df = local_price[local_price['actual_type'] == product_type_opt]

    price_col = 'price_idr'
    q1 = selected_df[price_col].quantile(0.25)
    q3 = selected_df[price_col].quantile(0.75)
    median = selected_df[price_col].quantile(0.5)

    st.header("Harga Saat Ini")
    lower_limit = f'{q1:,.0f}'.replace(',', '.')
    upper_limit = f'{q3:,.0f}'.replace(',', '.')
    st.write(f'Rentang Harga: Rp. {lower_limit} - Rp. {upper_limit} dari {len(selected_df)} data')

    group_opt = selected_df['pangoly_group'].iloc[0]


    st.header("Perkiraan Perubahan Harga")

    pred_date = st.date_input("Tanggal:", min_value='today', value=dt.datetime.now() + dt.timedelta(days=7))

    steps = (pred_date - dt.datetime.now().date()).days

    changes = []

    # lightGBM
    lgbm_pct_change = lgbm_predict(group_opt, steps=steps)
    if lgbm_pct_change is not None:
        changes.append(lgbm_pct_change)

    # ARIMA
    arima_pct_change = arima_predict(cat_opt, group_opt, steps=steps)
    if arima_pct_change is not None:
        changes.append(arima_pct_change)

    pct_change = sum(changes)/len(changes)

    
    st.write(f'Prediksi perubahan harga:  {pct_change:.2f}% {"⬆" if pct_change > 0 else "⬇"}')

def lgbm_predict(group_opt, steps = 60):
    preds = predict(steps, group_opt, pangoly_price, lgbm)
    
    last_historical_price = pangoly_price[pangoly_price['product'] == group_opt].iloc[-1]['avg']
    predicted_price = preds.iloc[-1]['avg']
    change = predicted_price - last_historical_price
    pct_change = (change/last_historical_price) * 100

    return pct_change

def arima_predict(cat_opt, group_opt, steps = 60):
    model_group = None
    if cat_opt == 'PROCESSORS':
        model_group = arima_cpu
    elif cat_opt == 'GRAPHICS CARDS':
        model_group = arima_gpu
    elif cat_opt == 'MEMORY':
        model_group = arima_ram
    else:
        return None

    if group_opt not in model_group:
        return None

    model = model_group[group_opt]
    preds = model.predict(n_periods=steps)

    last_price = pangoly_price[pangoly_price['product'] == group_opt].iloc[-1]['avg']
    pred_price = preds.iloc[-1]
    change = pred_price - last_price
    pct_change = (change/last_price)*100

    return pct_change

if __name__ == '__main__':
    run_predict_price()