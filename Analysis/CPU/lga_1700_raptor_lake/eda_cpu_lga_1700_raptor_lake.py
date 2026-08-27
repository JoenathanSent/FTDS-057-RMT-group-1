import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimage
import matplotlib.dates as mdates
# library untuk melakukan time series decomposition
from statsmodels.tsa.seasonal import seasonal_decompose
# library untuk mendeteksi data stasioner
from statsmodels.tsa.stattools import adfuller
# library untuk menentukan parameter ARIMA dan SARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import os
CURRENT_PATH = os.getcwd()

def run_lga_1700_raptor_lake():
    # Membuat title 
    st.title('DealSense')

    # Membuat sub header
    st.subheader('Page ini berisi Exploratory Data Analysis (EDA) mengenai dataset harga komponen CPU Socket Merk LGA 1700 Raptor Lake')

    # Menampilkan teks
    st.write('Halaman ini menampilkan eksplorasi data dari data harga komponen komputer CPU Socket LGA 1700 Raptor Lake sejak tanggal 4 Oktober 2022 sampai dengan 21 Agustus 2026.')
    # Menampilkan gambar
    image_path = os.path.join(CURRENT_PATH, 'Analysis', 'CPU', 'lga_1700_raptor_lake', 'intel_processor_intel_core_i9_14900k_box_raptor_lake_socket_lga_1700_full01_glgj77gp.webp')
                              
    data = mpimage.imread(image_path)
    st.image(data, caption='EDA LGA 1700 Raptor Lake')
    df = pd.read_csv('./Analysis/CPU/lga_1700_raptor_lake/lga1700_raptor_lake.csv')
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')

    st.write('# Exploratory Data Analysis untuk komponen socket CPU LGA 1700 Raptor Lake')

    st.subheader('1. Deteksi trend, seasonality, dan residual dengan melakukan dekomposisi')
    st.write('A. Metode Aditif')
    decomposition_a = seasonal_decompose(df['avg'], model='additive', period=30)
    fig = decomposition_a.plot()
    fig.set_size_inches(14, 10) 
    fig.suptitle(
        'Dekomposisi data dengan metode aditif',
        fontsize=16,
        fontweight='bold',
        y=1.02
    )
    fig.axes[0].set_title('Data Rata-rata Harga Socket CPU LGA 1700 Raptor Lake')
    fig.axes[1].set_title('Tren Harga Socket CPU LGA 1700 Raptor Lake')
    fig.subplots_adjust(hspace=1)
    for ax in fig.axes:
        ax.tick_params(axis='x', labelbottom=True)

        # Format tanggal: Tahun-Bulan
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

        # Atur jarak antar label tanggal
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))

        # Rotasi label tanggal
        plt.setp(
            ax.get_xticklabels(),
            rotation=45,
            ha='right'
        )
    st.pyplot(fig)
    st.write('')

    st.write('B. Metode Multiplikatif')
    decomposition_m = seasonal_decompose(df['avg'], model='multiplicative', period=30)
    fig = decomposition_m.plot()
    fig.set_size_inches(14, 10) 
    fig.suptitle(
        'Dekomposisi data dengan metode multiplikatif',
        fontsize=16,
        fontweight='bold',
        y=1.02
    )
    fig.axes[0].set_title('Data Rata-rata Harga Socket CPU LGA 1700 Raptor Lake')
    fig.axes[1].set_title('Tren Harga Socket CPU LGA 1700 Raptor Lake')
    fig.subplots_adjust(hspace=1)
    for ax in fig.axes:
        ax.tick_params(axis='x', labelbottom=True)

        # Format tanggal: Tahun-Bulan
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

        # Atur jarak antar label tanggal
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))

        # Rotasi label tanggal
        plt.setp(
            ax.get_xticklabels(),
            rotation=45,
            ha='right'
        )
    st.pyplot(fig)
    st.write('')
    st.write('Dari 2 visualisasi dekomposisi diatas, dapat kita ambil kesimpulan bahwa:')
    st.write('- Trend dari metode aditif dan multiplikatif menunjukkan bahwa harga CPU untuk LGA 1700 Raptor Lake memiliki kenaikan harga di awal perilisan komponen, kemudian harganya turun kembali ke harga normal setelah sekitar 3 bulan dan menurun secara perlahan hingga sekitar September 2025. Setelah itu harga kembali naik karena terdapat kelangkaan chip untuk komponen komputer dikarenakan banyak perusahaan membeli komponen komputer secara masif untuk membuat Pusat Data (Data Center) untuk pengembangan AI.')
    st.write('- Visualisasi seasonal dari metode aditif tidak menunjukkan nilai maksimum atau minimum yang jauh dari 0, dan untuk metode multiplikatif tidak menunjukkan nilai maksimum atau minimum yang jauh dari 1. Ditambah lagi visualisasi dari tren tidak menunjukkan kesamaan dengan visualisasi dari seasonal. Ini menunjukkan tidak adanya seasonal untuk harga rata-rata Socket CPU LGA 1700 Raptor Lake.')
    st.write('- Untuk nilai residual, bisa dilihat dari visualisasi dari metode aditif dan multiplikatif bahwa metode multiplikatif memiliki nilai residu yang lebih merata dan tidak jauh dari nilai awalnya (untuk metode aditif, nilai awalnya adalah 0, sedangkan untuk metode multiplikatif nilai awalnya adalah 1). Sehingga bisa disimpulkan dekomposisi dengan metode multiplikatif adalah metode terbaik untuk menghitung rata-rata harga Socket CPU LGA 1700 Raptor Lake.')

    st.subheader('2. Analisa Auto Correlation Function (ACF) dan Partial Auto Corellation Function (PACF)')
    len_train = round(len(df) * 0.9)

    df_avg_price_train = df[:len_train]
    df_avg_price_test = df[len_train:]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 11))
    fig.suptitle('Visualisasi ACF dan PACF dari data pelatihan harga rata-rata Socket CPU LGA 1700 Raptor Lake', fontsize=16)
    plot_acf(df_avg_price_train['avg'], ax=ax1, lags=30)
    ax1.set_title('Auto Correlation Function(ACF)')
    plot_pacf(df_avg_price_train['avg'], ax=ax2, lags=30)
    ax2.set_title('Partial Auto Correlation Function(PACF)')
    st.pyplot(fig)

    st.write('Dari visualisasi ACF dan PACF diatas, dapat diketahui bahwa:')
    st.write('- Dari visualisasi diatas, ACF bersifat tails off berarti nilai q = 0 ')
    st.write('- PACF bersifat cuts off setelah lag 3, berarti nilai p = 3, dengan alternatif nilai p adalah 8, 9, 18, dan 23')
    st.write('- Karena data belum melalui diferensiasi, maka nilai d = 0')
    st.write('Dari poin diatas, maka model awal yang bisa digunakan adalah menggunakan parameter ARIMA(3,0,0)')

    st.subheader('3. Pembuktian bahwa data belum stasioner dengan ADF test')
    def perform_adf_test(series: pd.Series, series_name: str = "the series"):
        st.write(f"--- Hasil Tes ADF untuk: {series_name} ---")

        result = adfuller(series.dropna())

        st.write(f'Statistik ADF: {result[0]}')
        st.write(f'p-value: {result[1]}')
        st.write('Nilai Kritikal (Critical Values):')
        for key, value in result[4].items():
            st.write(f'Nilai Signifikansi \t{key}: {value}')

        st.write('\n--- Kesimpulan ---')
        if (result[1] < 0.05) & (result[4]['5%'] > result[0]):
            st.write("Karena nilai statistik ADF lebih kecil daripada nilai signifikansi 5%, maka dapat dinyatakan bahwa data bersifat stasioner. Maka tidak perlu dilakukan tambahan proses differencing")
        elif (result[1] > 0.05) & (result[4]['5%'] > result[0]):
            st.write("Wakaupun nilai statistik ADF lebih kecil daripada nilai signifikansi 5%, belum terdapat bukti yang cukup bahwa data bersifat stasioner karena p-value lebih besar daripada 0,05 (5%). Sehingga belum ada bukti yang cukup untuk menyatatakan bahwa data tidak stasioner. Maka perlu dilakukan tambahan proses differencing sebelum dilakukan pemodelan ARIMA")
        elif (result[1] < 0.05) & (result[4]['5%'] < result[0]):
            st.write("Karena nilai statistik ADF lebih besar daripada nilai signifikansi 5%, dapat dinyatakan bahwa data tidak stasioner. Perlu dilakukan tambahan proses differencing sebelum dilakukan pemodelan ARIMA")
        else:
            st.write("Karena nilai statistik ADF lebih besar daripada nilai signifikansi 5% dan belum terdapat bukti yang cukup bahwa data bersifat stasioner karena p-value lebih besar daripada 0,05 (5%), dapat dinyatakan bahwa data tidak stasioner. Maka perlu dilakukan tambahan proses differencing sebelum dilakukan pemodelan ARIMA")
            
        st.write("-" * 40)

    perform_adf_test(df_avg_price_train['avg'], series_name="Data Harga Rata-rata Socket CPU LGA 1700 Raptor Lake")

    st.subheader('4. Data differencing')

    train_diff = df_avg_price_train.diff().dropna()
    perform_adf_test(train_diff['avg'], series_name="Data Harga Rata-rata Socket CPU LGA 1700 Raptor Lake melalui 1x diferensiasi")
    st.write('Dengan ini, maka model prediksi yang cocok digunakan adalah ARIMA (3,1,0)')


if __name__ == '__main__':
    run_lga_1700_raptor_lake()