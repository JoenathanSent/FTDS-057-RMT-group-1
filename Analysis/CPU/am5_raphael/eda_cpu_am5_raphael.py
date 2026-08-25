import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimage
import os
CURRENT_PATH = os.getcwd()

def run():
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

    st.write('# Data Loading')
    df = pd.read_csv('./Analysis/CPU/lga_1700_raptor_lake/lga1700_raptor_lake.csv')
    st.write('Tampilan dataframe')
    st.dataframe(df)
    st.write('# Exploratory Data Analysis')
    st.subheader('1. Tampilan fluktuasi harga komponen')
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df['date'], df['avg'], linestyle='-', color='b')
    ax.set_title('Data fluktuasi harga CPU LGA 1700 Raptor Lake', fontsize=16)
    ax.set_xlabel('Tanggal', fontsize=12)
    ax.set_ylabel('Harga dalam USD', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.show()
    st.write('')
    st.write('Dari visualisasi diatas, diketahui')
    st.write('')

if __name__ == '__main__':
    run()