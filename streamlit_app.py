import streamlit as st

from Analysis.CPU.lga_1700_raptor_lake.eda_cpu_lga_1700_raptor_lake import run_lga_1700_raptor_lake
from Analysis.CPU.am5_raphael.eda_cpu_am5_raphael import run_cpu_am5_raphael

from Analysis.CPU_Cooler.air_cooler.eda_cpu_cooler_air_cooler import run_air_cooler

from Analysis.GPU.rtx_5060_ti.eda_gpu_rtx_5060_ti import run_rtx_5060_ti
from Analysis.GPU.rx_9060_xt.eda_gpu_rx_9060_xt import run_rx_9060_xt

from Analysis.Motherboard.am5_amd_a620.eda_mobo_am5_amd_a620 import run_am5_amd_a620
from Analysis.Motherboard.lga_1700_intel_b760.eda_mobo_lga_1700_intel_b760 import run_lga_1700_intel_b760

from Analysis.PSU.p_650w_80plus_gold.eda_psu_650w_80plus_gold import run_650w_80plus_gold
from Analysis.PSU.p_750w_80plus_gold.eda_psu_750w_80plus_gold import run_750w_80plus_gold

from Analysis.RAM.ram_16gb_ddr5.eda_ram_16gb_ddr5 import run_ram_16gb_ddr5
from Analysis.RAM.ram_32gb_ddr5.eda_ram_32gb_ddr5 import run_ram_32gb_ddr5

from Analysis.SSD.ssd_1tb_pcie_gen4_x4.eda_ssd_1tb_pcie_gen4_x4 import run_ssd_1tb_pcie_gen4_x4
from Analysis.SSD.ssd_2tb_pcie_gen4_x4.eda_ssd_2tb_pcie_gen4_x4 import run_ssd_2tb_pcie_gen4_x4

from predict_price import run_predict_price
from streamlit_option_menu import option_menu

# 1. as sidebar menu
with st.sidebar:
    selected = option_menu(
        "EDA",
        [
            "CPU Socket LGA 1700 Raptor Lake",
            "CPU Socket AM5 Raphael",
            "CPU Cooler Air Cooler",
            "GPU RTX 5060 Ti",
            "GPU RX 9060 XT",
            "Motherboard LGA 1700 Intel B760",
            "Motherboard AM5 AMD A620",
            "PSU 650W 80 Plus Gold",
            "PSU 750W 80 Plus Gold",
            "RAM 16GB DDR5",
            "RAM 32GB DDR5",
            "SSD 1TB PCIE Gen4 x4",
            "SSD 2TB PCIE Gen4 x4",
            "Inference",
        ],
        icons=[
            "cpu",
            "cpu",
            "fan",
            "gpu-card",
            "gpu-card",
            "motherboard",
            "motherboard",
            "plug",
            "plug",
            "memory",
            "memory",
            "device-ssd",
            "device-ssd",
            "magic",
        ],
        menu_icon="cast",
        default_index=0
    )

if selected == "CPU Socket LGA 1700 Raptor Lake":
    run_lga_1700_raptor_lake()
elif selected == "CPU Socket AM5 Raphael":
    run_cpu_am5_raphael()
elif selected == "CPU Cooler Air Cooler":
    run_air_cooler()
elif selected == "GPU RTX 5060 Ti":
    run_rtx_5060_ti()
elif selected == "GPU RX 9060 XT":
    run_rx_9060_xt()
elif selected == "Motherboard LGA 1700 Intel B760":
    run_lga_1700_intel_b760()
elif selected == "Motherboard AM5 AMD A620":
    run_am5_amd_a620()
elif selected == "PSU 650W 80 Plus Gold":
    run_650w_80plus_gold()
elif selected == "PSU 750W 80 Plus Gold":
    run_750w_80plus_gold()
elif selected == "RAM 16GB DDR5":
    run_ram_16gb_ddr5()
elif selected == "RAM 32GB DDR5":
    run_ram_32gb_ddr5()
elif selected == "SSD 1TB PCIE Gen4 x4":
    run_ssd_1tb_pcie_gen4_x4()
elif selected == "SSD 2TB PCIE Gen4 x4":
    run_ssd_2tb_pcie_gen4_x4()
elif selected == "Inference":
    run_predict_price()