import re

PANGOLY_RAM_GROUPS = {
    '8GB DDR4', '8GB DDR5', '16GB DDR4', '16GB DDR5', '32GB DDR4',
    '32GB DDR5', '48GB DDR5', '64GB DDR4', '64GB DDR5', '96GB DDR5',
    '128GB DDR5',
}


def classify_ram_group(name):
    """
    Function untuk mapping product memory ke pangoly group
    """
    if not isinstance(name, str) or not name.strip():
        return None

    s = name.upper()

    ddr_m = re.search(r'DDR\s?(3L|3|4|5)\b', s)
    if not ddr_m:
        return None
    ddr_digit = ddr_m.group(1)[0]
    if ddr_digit not in ('4', '5'):
        return None  # DDR3/DDR3L has no pangoly group

    # multiplier-before-capacity, e.g. "2 X 4 GB" (total not stated separately)
    mult_m = re.search(r'\b(\d{1,2})\s*X\s*(\d{1,3})\s*GB\b', s)
    if mult_m:
        total = int(mult_m.group(1)) * int(mult_m.group(2))
    else:
        cap_m = re.search(r'\b(\d{1,3})\s*GB\b', s)
        if cap_m:
            total = int(cap_m.group(1))
        else:
            # G.Skill compact part-number naming, e.g. F5-6400R3239G32GQ4-ZR5NK
            # -> per-module capacity 32, quantity 4 -> 128GB kit
            gskill_m = re.search(r'G(\d{1,3})GQ(\d)\b', s)
            if not gskill_m:
                return None
            total = int(gskill_m.group(1)) * int(gskill_m.group(2))

    candidate = f'{total}GB DDR{ddr_digit}'
    return candidate if candidate in PANGOLY_RAM_GROUPS else None


def classify_ram_products(df, column='product', new_column='pangoly_group'):
    """
    Funtion untuk apply mapping memory ke dataframe
    """
    df = df.copy()
    df[new_column] = df[column].apply(classify_ram_group)
    unmatched = sorted(df.loc[df[new_column].isna(), column].unique().tolist())
    return df, unmatched

