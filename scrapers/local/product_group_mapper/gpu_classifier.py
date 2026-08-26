import re

PANGOLY_GPU_GROUPS = {
    'GeForce RTX 3060', 'GeForce RTX 3060 Ti',
    'GeForce RTX 4070 Ti SUPER', 'GeForce RTX 4080', 'GeForce RTX 4080 SUPER',
    'GeForce RTX 5050', 'GeForce RTX 5060', 'GeForce RTX 5060 Ti',
    'GeForce RTX 5060 Ti 8GB', 'GeForce RTX 5070', 'GeForce RTX 5070 Ti',
    'GeForce RTX 5080', 'GeForce RTX 5090',
    'Radeon RX 7600', 'Radeon RX 7900 XTX',
    'Radeon RX 9060 XT', 'Radeon RX 9070', 'Radeon RX 9070 XT',
}


def classify_gpu_group(name):
    """
    Function untuk mapping product gpu ke pangoly gpu group
    """
    if not isinstance(name, str) or not name.strip():
        return None

    s = name.upper().replace('™', '').replace('®', '')
    s = re.sub(r'\s+', ' ', s).strip()

    # NVIDIA GeForce RTX (skip workstation Quadro / RTX Axxxx cards)
    m = re.search(r'RTX\s*(\d{3,4})(\s*TI)?(\s*SUPER)?', s)
    if m and 'QUADRO' not in s:
        number = m.group(1)
        ti, super_ = bool(m.group(2)), bool(m.group(3))

        # RTX 5060 Ti is split into two pangoly groups by VRAM
        if number == '5060' and ti:
            vram_m = re.search(r'(\d{1,3})\s?G(?:B)?\b', s[m.end():])
            if vram_m and vram_m.group(1) == '8':
                return 'GeForce RTX 5060 Ti 8GB'
            return 'GeForce RTX 5060 Ti'

        candidate = f'GeForce RTX {number}'
        if ti:
            candidate += ' Ti'
        if super_:
            candidate += ' SUPER'
        return candidate if candidate in PANGOLY_GPU_GROUPS else None

    # AMD Radeon RX
    m = re.search(r'\bRX\s*(\d{3,4})\s*(XTX|XT)?', s)
    if m:
        number, suffix = m.group(1), m.group(2) or ''
        candidate = f'Radeon RX {number}' + (f' {suffix}' if suffix else '')
        return candidate if candidate in PANGOLY_GPU_GROUPS else None

    return None


def extract_gpu_type(name):
    """
    Function untuk meng-ekstrak type GPU.
    """
    if not isinstance(name, str) or not name.strip():
        return None

    s = name.upper().replace('™', '').replace('®', '')
    s = re.sub(r'\s+', ' ', s).strip()

    def vram(start_idx):
        m = re.search(r'(\d{1,3})\s?G(?:B)?\b', s[start_idx:])
        return f'{m.group(1)}GB' if m else None

    # NVIDIA Quadro / RTX Axxxx workstation cards
    m = re.search(r'QUADRO\s+(?:RTX\s*)?(A)?(\d{3,5})', s)
    if m:
        prefix = m.group(1) or ''
        parts = [f'Quadro RTX {prefix}{m.group(2)}']
        v = vram(m.end())
        if v:
            parts.append(v)
        return ' '.join(parts)

    # NVIDIA GeForce RTX
    m = re.search(r'\bRTX\s*(\d{3,4})(\s*TI)?(\s*SUPER)?', s)
    if m:
        parts = [f'GeForce RTX {m.group(1)}']
        if m.group(2):
            parts.append('Ti')
        if m.group(3):
            parts.append('SUPER')
        v = vram(m.end())
        if v:
            parts.append(v)
        return ' '.join(parts)

    # NVIDIA GeForce GTX
    m = re.search(r'\bGTX\s*(\d{3,4})(\s*TI)?(\s*SUPER)?', s)
    if m:
        parts = [f'GeForce GTX {m.group(1)}']
        if m.group(2):
            parts.append('Ti')
        if m.group(3):
            parts.append('SUPER')
        v = vram(m.end())
        if v:
            parts.append(v)
        return ' '.join(parts)

    # NVIDIA GeForce GT
    m = re.search(r'\bGT\s*(\d{3,4})\b', s)
    if m:
        parts = [f'GeForce GT {m.group(1)}']
        v = vram(m.end())
        if v:
            parts.append(v)
        return ' '.join(parts)

    # AMD Radeon RX
    m = re.search(r'\bRX\s*(\d{3,4})\s*(XTX|XT)?', s)
    if m:
        suffix = m.group(2) or ''
        parts = [f'Radeon RX {m.group(1)}' + (f' {suffix}' if suffix else '')]
        v = vram(m.end())
        if v:
            parts.append(v)
        return ' '.join(parts)

    return None


def classify_gpu_products(df, column='product', new_column='pangoly_group'):
    """
    Fungsi untuk apply mapping gpu group ke dataframe
    """
    df = df.copy()
    df[new_column] = df[column].apply(classify_gpu_group)
    unmatched = sorted(df.loc[df[new_column].isna(), column].unique().tolist())
    return df, unmatched