import streamlit as st
import seaborn as sns
import pandas as pd
from pathlib import Path
import joblib

from models.lgbm.predict import predict

cwd = Path.cwd()

local_price = pd.read_csv(cwd / 'data' / 'local_price_test.csv')
pangoly_price = pd.read_csv(cwd / 'data' / 'pangoly.csv')
pangoly_price['date'] = pd.to_datetime(pangoly_price['date'])

local_price = local_price.dropna(subset=['pangoly_group'])

lgbm = joblib.load('./models/lgbm/lgbm.joblib')

def run():
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

    st.header("Harga")
    lower_limit = f'{q1:,.0f}'.replace(',', '.')
    upper_limit = f'{q3:,.0f}'.replace(',', '.')
    st.write(f'Rentang Harga: Rp. {lower_limit} - Rp. {upper_limit}')

    group_opt = selected_df['pangoly_group'].iloc[0]

    preds = predict(60, group_opt, pangoly_price, lgbm)

    last_historical_price = pangoly_price[pangoly_price['product'] == group_opt].iloc[-1]['avg']
    predicted_price = preds.iloc[-1]['avg']
    change = predicted_price - last_historical_price
    pct_change = (change/last_historical_price) * 100

    st.write(f'Prediksi perubahan harga dalam 2 bulan ke depan: {pct_change:.2f}%')

