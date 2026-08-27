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

local_price = pd.read_csv(cwd / 'data' / 'local_price_ssd.csv')
pangoly_price = pd.read_csv(cwd / 'data' / 'pangoly.csv')
pangoly_price['date'] = pd.to_datetime(pangoly_price['date'])

local_price = local_price.dropna(subset=['pangoly_group'])

lgbm = joblib.load('./models/lgbm/lgbm.joblib')

arima_cpu = joblib.load('./models/arima/cpu.joblib')
arima_gpu = joblib.load('./models/arima/gpu.joblib')
arima_ram = joblib.load('./models/arima/ram.joblib')
arima_ssd = joblib.load('./models/arima/ssd.joblib')

def run_predict_price():
    st.title('DealSense')

    st.image("DealSense.jpg", caption="DealSense", width=300)

    st.subheader('Dapatkan perkiraan harga part PC mu!')

    cat_opt = st.selectbox(
        "Category: ",
        ("PROCESSORS", "GRAPHICS CARDS", "MEMORY", "SOLID STATE DRIVES"),
    )

    # filter product by category
    selected_cat_df = local_price[local_price['pangoly_category'] == cat_opt]

    sub_cat_maps = {
        "PROCESSORS": ["INTEL", "AMD"],
        "GRAPHICS CARDS": ["NVIDIA", "AMD"],
        "MEMORY": ["DDR4", "DDR5"],
        "SOLID STATE DRIVES": ["SATA", "PCIe Gen3", "PCIe Gen4", "PCIe Gen5"],
    }

    sub_cat_opt = st.selectbox(
        "Sub Category: ",
        sub_cat_maps[cat_opt]
    )

    # filter products by sub category
    if cat_opt == 'GRAPHICS CARDS' and sub_cat_opt == 'NVIDIA':
        sub_cat_df = selected_cat_df[selected_cat_df['pangoly_group'].str.contains('GeForce', na=False)]
    elif cat_opt == 'SOLID STATE DRIVES':
        sub_cat_df = selected_cat_df[selected_cat_df['pangoly_group'].str.contains(sub_cat_opt)]
    else:    
        sub_cat_df = selected_cat_df[selected_cat_df['product_name'].str.contains(sub_cat_opt)]

    prod_types = list(sub_cat_df['actual_type'].unique())
    prod_types.sort()

    product_type_opt = st.selectbox(
        "Type: ",
        prod_types
    )

    # filter product by type
    selected_df = local_price[local_price['actual_type'] == product_type_opt]

    # calculate lower and upper boundary
    price_col = 'price_idr'
    q1 = selected_df[price_col].quantile(0.25)
    q2 = selected_df[price_col].quantile(0.5)
    q3 = selected_df[price_col].quantile(0.75)
    

    st.header("Harga Saat Ini")
    lower_limit = f'{q1:,.0f}'.replace(',', '.')
    median = f'{q2:,.0f}'.replace(',', '.')
    upper_limit = f'{q3:,.0f}'.replace(',', '.')
    st.write(f'Harga berdasarkan {len(selected_df)} data')

    local_price_col1, local_price_col2, local_price_col3 = st.columns(3)

    with local_price_col1:
        with st.container(border=True):
            st.markdown("##### Batas Bawah")
            st.markdown(f"#### Rp. {lower_limit}")

    with local_price_col2:
        with st.container(border=True):
            st.markdown("##### Nilai Tengah")
            st.markdown(f"#### Rp. {median}")

    with local_price_col3:
        with st.container(border=True):
            st.markdown("##### Batas Atas")
            st.markdown(f"#### Rp. {upper_limit}")

    group_opt = selected_df['pangoly_group'].iloc[0]

    st.header("Perkiraan Perubahan Harga")

    pred_date = st.date_input("Tanggal:", min_value='today', value=dt.datetime.now() + dt.timedelta(days=7))

    steps = (pred_date - dt.datetime.now().date()).days

    changes = []

    # lightGBM
    # lgbm_pct_change = lgbm_predict(group_opt, steps=steps)
    # if lgbm_pct_change is not None:
    #     changes.append(lgbm_pct_change)

    # ARIMA
    arima_pct_change = arima_predict(cat_opt, group_opt, steps=steps)
    if arima_pct_change is not None:
        changes.append(arima_pct_change)

    pct_change = sum(changes)/len(changes)
    is_rising = pct_change > 0

    price_change_col1, price_change_col2 = st.columns(2)

    pred_price = q2 * (1 +(pct_change/100))
    pred_median = f'{pred_price:,.0f}'.replace(',', '.')

    with price_change_col1:
        with st.container(border=True):
            st.markdown("##### Harga")
            st.markdown(f"#### Rp. {pred_median}")

    pct_color = 'red' if is_rising else 'green'
    with price_change_col2:
        with st.container(border=True):
            st.markdown("##### Prediksi")
            st.markdown(f"#### :{pct_color}[{'⬆' if is_rising else '⬇'} {pct_change:.2f}%]")

    st.caption("Harga berdasarkan prediksi model tidak dijamin tepat, harga di masa depan bisa berbeda.")


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
    elif cat_opt == 'SOLID STATE DRIVES':
        model_group = arima_ssd
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