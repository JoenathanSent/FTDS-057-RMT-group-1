import pandas as pd
import datetime as dt

lags = [1,2,3,7,14,30]
rolling = [3, 7, 30]

def predict(steps: int, product: str, df: pd.DataFrame, lgb_model):
    df_prod_original = df[df['product'] == product].copy()

    df_prod = df_prod_original.copy()
    df_prod = df_prod.sort_values(by=['date'], ascending=True)

    latest_known_date = df_prod['date'].max()
    cat = df_prod['category'].iloc[0]

    preds = []
    for _ in range(steps):
        new_date = latest_known_date + dt.timedelta(days=1)
        data = {
            'date': [new_date],
            'product': [product],
            'category': [cat]
        }
        current_df = pd.DataFrame(data)

        for col in ['product', 'category']:
            current_df[col] = current_df[col].astype('category')
        
        current_df['day_of_week'] = current_df['date'].dt.dayofweek
        current_df['day_of_month'] = current_df['date'].dt.day
        current_df['month'] = current_df['date'].dt.month
        current_df['year'] = current_df['date'].dt.year
        current_df['is_weekend'] = current_df['day_of_week'].isin([5,6]).astype(int)
        current_df['is_month_end'] = current_df['date'].dt.is_month_end.astype(int)

        for lag in lags:
            current_df[f'lag_{lag}d'] = df_prod['avg'].iloc[-lag]

        for window in rolling:
            current_df[f'mean_{window}d'] = df_prod['avg'].iloc[-window:].mean()
            current_df[f'max_{window}d'] = df_prod['avg'].iloc[-window:].max()
            current_df[f'min_{window}d'] = df_prod['avg'].iloc[-window:].min()
            current_df[f'std_{window}d'] = df_prod['avg'].iloc[-window:].std()

        X = current_df.drop(columns=['date'])
        pred = lgb_model.predict(X)

        current_df['pct_change'] = pred
        current_df['avg'] = current_df['lag_1d'] * (1 + (pred/100))
        df_prod = pd.concat([df_prod, current_df])
        latest_known_date = df_prod['date'].max()
        preds.append(current_df)

    df_prod_original['is_pred'] = False
    df_preds = pd.concat(preds)
    df_preds['is_pred'] = True
    return pd.concat([df_prod_original, df_preds])