import re

PANGOLY_CPU_GROUPS = {
    'AM3+ Vishera', 'AM4 Cezanne', 'AM4 Matisse', 'AM4 Pinnacle Ridge',
    'AM4 Summit Ridge', 'AM4 Vermeer', 'AM5 Granite Ridge', 'AM5 Phoenix',
    'AM5 Raphael', 'LGA1150 Haswell', 'LGA1151 Coffee Lake',
    'LGA1151 Kaby Lake', 'LGA1151 Skylake', 'LGA1200 Comet Lake',
    'LGA1200 Rocket Lake', 'LGA1700 Alder Lake', 'LGA1700 Raptor Lake',
    'LGA1851 Arrow Lake', 'LGA2066 Skylake X', 'sTR5 Storm Peak',
}

_INTEL_GEN_TO_GROUP = {
    4: 'LGA1150 Haswell',
    6: 'LGA1151 Skylake',
    7: 'LGA1151 Kaby Lake',
    8: 'LGA1151 Coffee Lake',
    9: 'LGA1151 Coffee Lake',
    10: 'LGA1200 Comet Lake',
    11: 'LGA1200 Rocket Lake',
    12: 'LGA1700 Alder Lake',
    13: 'LGA1700 Raptor Lake',
    14: 'LGA1700 Raptor Lake',
}


def classify_cpu_group(name):
    """
    Function untuk mapping nama product ke pangoly group.
    """
    if not isinstance(name, str) or not name.strip():
        return None

    s = name.upper()

    # AMD Storm Peak
    if 'THREADRIPPER' in s or re.search(r'\bTR\b', s):
        m = re.search(r'(\d{4})\s*WX', s) or re.search(r'\b(\d{4})X\b', s)
        if m and m.group(1)[0] == '7':
            return 'sTR5 Storm Peak'
        return None

    # AMD FX (AM3+)
    if re.search(r'\bFX[-\s]?\d{4}', s):
        return 'AM3+ Vishera'

    # AMD Ryzen
    if 'RYZEN' in s:
        m = re.search(
            r'RYZEN\s*(?:\d\s*)?(?:PRO\s*)?(\d{3,4})\s*(X3D|XT|GE|GT|G|X|F)?', s
        )
        if not m:
            return None

        digits, suffix = m.group(1), (m.group(2) or '')
        gen = digits[0]
        is_apu = suffix in ('G', 'GE', 'GT')

        if digits == '7500' and suffix == 'F':
            return 'AM4 Vermeer'
        if gen in ('2', '3', '4') and is_apu:
            return None

        if gen == '1':
            return 'AM4 Summit Ridge'
        if gen == '2':
            return 'AM4 Pinnacle Ridge'
        if gen == '3':
            return 'AM4 Matisse'
        if gen == '5':
            return 'AM4 Cezanne' if is_apu else 'AM4 Vermeer'
        if gen == '7':
            return 'AM5 Phoenix' if is_apu else 'AM5 Raphael'
        if gen == '8':
            return 'AM5 Phoenix' if is_apu else None
        if gen == '9':
            return 'AM5 Granite Ridge'
        return None

    # Intel Core Ultra
    m = re.search(r'CORE\s*ULTRA\s*\d\s*(\d)\d{2}', s)
    if m:
        return 'LGA1851 Arrow Lake' if m.group(1) == '2' else None

    # Intel Core i3/i5/i7/i9
    m = re.search(r'I[3579][-\s](\d{4,5})([A-Z]*)', s)
    if m:
        digits, suffix = m.group(1), m.group(2)
        gen = int(digits[:2]) if len(digits) == 5 else int(digits[0])

        # X-series
        if suffix == 'X' and gen in (7, 9, 10):
            return 'LGA2066 Skylake X'

        return _INTEL_GEN_TO_GROUP.get(gen)

    return None

_START_KEYWORD_RE = re.compile(
    r'\b(INTEL|AMD|RYZEN|CORE|PENTIUM|THREADRIPPER|EPYC)\b', re.I
)

_AMD_LINE_RE = re.compile(
    r'RYZEN\s+THREADRIPPER\s+PRO|RYZEN\s+THREADRIPPER'
    r'|THREADRIPPER\s+PRO|THREADRIPPER'
    r'|RYZEN\s+TR\s+PRO|RYZEN\s+TR'
    r'|RYZEN\s+\d\s+PRO|RYZEN\s+PRO\s+\d|RYZEN\s+\d|RYZEN'
    r'|EPYC',
    re.I
)

_INTEL_LINE_RE = re.compile(
    r'CORE\s+ULTRA\s+\d|CORE\s+I[3579]|PENTIUM\s+GOLD|PENTIUM',
    re.I
)

_MODEL_NUM_RE = re.compile(r'\d{3,5}[A-Z0-9]{0,4}\b', re.I)
_PENTIUM_MODEL_RE = re.compile(r'G\d{3,5}\b', re.I)
_BARE_I_SERIES_RE = re.compile(r'\bI[3579]\s*-?\s*\d{3,5}[A-Z]{0,3}\b', re.I)


def _clean_infix(core):
    core = re.sub(r'\s*\bPROCESSOR\b\s*', ' ', core, flags=re.I)
    return re.sub(r'\s+', ' ', core).strip()

def extract_cpu_type(name):
    """
    Function untuk mengextract type CPU
    """
    if not isinstance(name, str) or not name.strip():
        return None

    su = name.upper()
    start_kw = _START_KEYWORD_RE.search(su)
    if not start_kw:
        return None
    start = start_kw.start()
    rest = su[start:]

    amd_m = _AMD_LINE_RE.search(rest[:20])
    if amd_m:
        model_m = _MODEL_NUM_RE.search(rest, amd_m.end())
        if not model_m:
            return None
        core = name[start + amd_m.start():start + model_m.end()]
        if not core.upper().lstrip().startswith('AMD'):
            core = 'AMD ' + core
        return _clean_infix(core)

    intel_m = _INTEL_LINE_RE.search(rest[:20])
    if intel_m:
        model_m = _MODEL_NUM_RE.search(rest, intel_m.end())
        if not model_m:
            return None
        core = name[start + intel_m.start():start + model_m.end()]
        if not core.upper().lstrip().startswith('INTEL'):
            core = 'Intel ' + core
        return _clean_infix(core)

    # bare "INTEL <G####>"
    if rest.startswith('INTEL'):
        model_m = _PENTIUM_MODEL_RE.search(rest)
        if model_m:
            core = name[start:start + model_m.end()]
            return _clean_infix(core)

    # bare "i3/i5/i7/i9 ####"
    bare_m = _BARE_I_SERIES_RE.search(name)
    if bare_m:
        return _clean_infix('Intel Core ' + bare_m.group(0))

    return None


def classify_cpu_products(df, column='product', new_column='pangoly_group'):
    """
    Fungsi untuk apply mapping cpu group ke dataframe
    """
    df = df.copy()
    df[new_column] = df[column].apply(classify_cpu_group)
    unmatched = sorted(df.loc[df[new_column].isna(), column].unique().tolist())
    return df, unmatched
