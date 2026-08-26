import streamlit as st

from Analysis.CPU.lga_1700_raptor_lake.eda_cpu_lga_1700_raptor_lake import run_lga_1700_raptor_lake as eda_cpu_lga_1700_raptor_lake
from Analysis.CPU.am5_raphael.eda_cpu_am5_raphael import run_cpu_am5_raphael as eda_cpu_am5_raphael

from Analysis.CPU_Cooler.air_cooler.eda_cpu_cooler_air_cooler import run_air_cooler as eda_cpu_cooler_air_cooler

from Analysis.GPU.rtx_5060_ti.eda_gpu_rtx_5060_ti import run_rtx_5060_ti as eda_gpu_rtx_5060_ti
from Analysis.GPU.rx_9060_xt.eda_gpu_rx_9060_xt import run_rx_9060_xt as eda_gpu_rx_9060_xt

from Analysis.Motherboard.am5_amd_a620.eda_mobo_am5_amd_a620 import run_am5_amd_a620 as eda_mobo_am5_amd_a620
from Analysis.Motherboard.lga_1700_intel_b760.eda_mobo_lga_1700_intel_b760 import run_lga_1700_intel_b760 as eda_mobo_lga_1700_intel_b760

from Analysis.PSU.p_650w_80plus_gold.eda_psu_650w_80plus_gold import run_650w_80plus_gold as eda_psu_650w_80plus_gold
from Analysis.PSU.p_750w_80plus_gold.eda_psu_750w_80plus_gold import run_750w_80plus_gold as eda_psu_750w_80plus_gold

from Analysis.RAM.ram_16gb_ddr5.eda_ram_16gb_ddr5 import run_ram_16gb_ddr5 as eda_ram_16gb_ddr5
from Analysis.RAM.ram_32gb_ddr5.eda_ram_32gb_ddr5 import run_ram_32gb_ddr5 as eda_ram_32gb_ddr5

from Analysis.SSD.ssd_1tb_pcie_gen4_x4.eda_ssd_1tb_pcie_gen4_x4 import run_ssd_1tb_pcie_gen4_x4 as eda_ssd_1tb_pcie_gen4_x4
from Analysis.SSD.ssd_2tb_pcie_gen4_x4.eda_ssd_2tb_pcie_gen4_x4 import run_ssd_2tb_pcie_gen4_x4 as eda_ssd_2tb_pcie_gen4_x4

from predict_price import run_predict_price

pages = {
    "EDA": [
        st.Page(eda_cpu_lga_1700_raptor_lake, title="CPU Socket LGA 1700 Raptor Lake"),
        st.Page(eda_cpu_am5_raphael, title="CPU Socket AM5 Raphael"),
        st.Page(eda_cpu_cooler_air_cooler, title="CPU Cooler Air Cooler"),
        st.Page(eda_gpu_rtx_5060_ti, title="GPU RTX 5060 Ti"),
        st.Page(eda_gpu_rx_9060_xt, title="GPU RX 9060 XT"),
        st.Page(eda_mobo_lga_1700_intel_b760, title="Motherboard LGA 1700 Intel B760"),
        st.Page(eda_mobo_am5_amd_a620, title="Motherboard AM5 AMD A620"),
        st.Page(eda_psu_650w_80plus_gold, title="PSU 650W 80 Plus Gold"),
        st.Page(eda_psu_750w_80plus_gold, title="PSU 750W 80 Plus Gold"),
        st.Page(eda_ram_16gb_ddr5, title="RAM 16GB DDR5"),
        st.Page(eda_ram_32gb_ddr5, title="RAM 32GB DDR5"),
        st.Page(eda_ssd_1tb_pcie_gen4_x4, title="SSD 1TB PCIE Gen4 x4"),
        st.Page(eda_ssd_2tb_pcie_gen4_x4, title="SSD 2TB PCIE Gen4 x4"),
    ],
    "Inference": [
        st.Page(run_predict_price, title="Try it out"),
    ],
}

pg = st.navigation(pages)
pg.run()