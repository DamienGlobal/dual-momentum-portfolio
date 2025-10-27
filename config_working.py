"""
Configuration avec TICKERS YAHOO FINANCE FONCTIONNELS
ETF américains équivalents pour tests système complet
TOUS VALIDÉS : données réelles disponibles
"""

# ============================================================================
# UNIVERS ETF WORKING (100% FONCTIONNELS YAHOO FINANCE)
# ============================================================================

# ETF américains équivalents pour PEA (simulation)
PEA_ETFS_WORKING = {
    'VT': {
        'name': 'Vanguard Total World Stock ETF',
        'isin': 'US9220427424',
        'ticker_yahoo': 'VT',  # ✅ FONCTIONNE
        'type': 'equity',
        'region': 'World',
        'ter': 0.0007,
        'description': 'Équivalent MSCI World (proxy CW8)',
        'pea_equivalent': 'CW8'
    },
    'VOO': {
        'name': 'Vanguard S&P 500 ETF',
        'isin': 'US9229083632',
        'ticker_yahoo': 'VOO',  # ✅ FONCTIONNE
        'type': 'equity',
        'region': 'USA',
        'ter': 0.0003,
        'description': 'S&P 500 (proxy ESE)',
        'pea_equivalent': 'ESE'
    },
    'VWO': {
        'name': 'Vanguard FTSE Emerging Markets ETF',
        'isin': 'US9220428588',
        'ticker_yahoo': 'VWO',  # ✅ FONCTIONNE
        'type': 'equity',
        'region': 'Emerging',
        'ter': 0.0008,
        'description': 'Marchés émergents (proxy AEEM)',
        'pea_equivalent': 'AEEM'
    },
    'VGK': {
        'name': 'Vanguard FTSE Europe ETF',
        'isin': 'US9219107094',
        'ticker_yahoo': 'VGK',  # ✅ FONCTIONNE
        'type': 'equity',
        'region': 'Europe',
        'ter': 0.0008,
        'description': 'Europe (proxy PCEU)',
        'pea_equivalent': 'PCEU'
    },
    'EWJ': {
        'name': 'iShares MSCI Japan ETF',
        'isin': 'US4642872349',
        'ticker_yahoo': 'EWJ',  # ✅ FONCTIONNE
        'type': 'equity',
        'region': 'Japan',
        'ter': 0.0051,
        'description': 'Japon (proxy JPX)',
        'pea_equivalent': 'JPXE'
    },
    'IWM': {
        'name': 'iShares Russell 2000 ETF',
        'isin': 'US4642876555',
        'ticker_yahoo': 'IWM',  # ✅ FONCTIONNE
        'type': 'equity',
        'region': 'USA',
        'ter': 0.0019,
        'description': 'Small Cap USA (proxy RS2K)',
        'pea_equivalent': 'RS2K'
    },
    'QQQ': {
        'name': 'Invesco QQQ Trust',
        'isin': 'US46090E1038',
        'ticker_yahoo': 'QQQ',  # ✅ FONCTIONNE
        'type': 'equity',
        'region': 'USA',
        'ter': 0.0020,
        'description': 'Tech USA Nasdaq-100 (proxy PUST)',
        'pea_equivalent': 'PUST'
    },
    'XLE': {
        'name': 'Energy Select Sector SPDR Fund',
        'isin': 'US81369Y8030',
        'ticker_yahoo': 'XLE',  # ✅ FONCTIONNE
        'type': 'equity',
        'region': 'USA',
        'ter': 0.0010,
        'description': 'Secteur énergie (proxy BRES)',
        'pea_equivalent': 'BRES'
    },
    
    # Obligations Safe Harbor
    'SHY': {
        'name': 'iShares 1-3 Year Treasury Bond ETF',
        'isin': 'US4642872000',
        'ticker_yahoo': 'SHY',  # ✅ FONCTIONNE
        'type': 'bond',
        'region': 'USA',
        'ter': 0.0015,
        'description': 'Obligations USA court terme (proxy OBLI)',
        'pea_equivalent': 'OBLI'
    }
}

# ETF américains pour CTO
CTO_ETFS_WORKING = {
    'ACWI': {
        'name': 'iShares MSCI ACWI ETF',
        'isin': 'US4642872265',
        'ticker_yahoo': 'ACWI',  # ✅ FONCTIONNE
        'type': 'equity',
        'region': 'World',
        'ter': 0.0032,
        'description': 'Monde all countries (proxy IWDA)',
        'cto_equivalent': 'IWDA'
    },
    'VSS': {
        'name': 'Vanguard FTSE All-World ex-US Small-Cap ETF',
        'isin': 'US9219097683',
        'ticker_yahoo': 'VSS',  # ✅ FONCTIONNE
        'type': 'equity',
        'region': 'World',
        'ter': 0.0011,
        'description': 'Small cap monde (proxy WSML)',
        'cto_equivalent': 'WSML'
    },
    'IEMG': {
        'name': 'iShares Core MSCI Emerging Markets ETF',
        'isin': 'US4642874659',
        'ticker_yahoo': 'IEMG',  # ✅ FONCTIONNE
        'type': 'equity',
        'region': 'Emerging',
        'ter': 0.0009,
        'description': 'Émergents large spectre (proxy EMIM)',
        'cto_equivalent': 'EMIM'
    },
    'MCHI': {
        'name': 'iShares MSCI China ETF',
        'isin': 'US4642872687',
        'ticker_yahoo': 'MCHI',  # ✅ FONCTIONNE
        'type': 'equity',
        'region': 'China',
        'ter': 0.0059,
        'description': 'Chine large cap (proxy FXC)',
        'cto_equivalent': 'FXC'
    },
    'AAXJ': {
        'name': 'iShares MSCI All Country Asia ex Japan ETF',
        'isin': 'US4642881175',
        'ticker_yahoo': 'AAXJ',  # ✅ FONCTIONNE
        'type': 'equity',
        'region': 'Asia',
        'ter': 0.0069,
        'description': 'Asie hors Japon (proxy DBXJ)',
        'cto_equivalent': 'DBXJ'
    },
    'VTWO': {
        'name': 'Vanguard Russell 2000 ETF',
        'isin': 'US9229087690',
        'ticker_yahoo': 'VTWO',  # ✅ FONCTIONNE
        'type': 'equity',
        'region': 'USA',
        'ter': 0.0010,
        'description': 'Small Cap USA (proxy R2US)',
        'cto_equivalent': 'R2US'
    },
    'ONEQ': {
        'name': 'Fidelity Nasdaq Composite Index ETF',
        'isin': 'US3160928657',
        'ticker_yahoo': 'ONEQ',  # ✅ FONCTIONNE
        'type': 'equity',
        'region': 'USA',
        'ter': 0.0021,
        'description': 'Nasdaq composite (proxy UST)',
        'cto_equivalent': 'UST'
    },
    'MDY': {
        'name': 'SPDR S&P MidCap 400 ETF Trust',
        'isin': 'US78464A7030',
        'ticker_yahoo': 'MDY',  # ✅ FONCTIONNE
        'type': 'equity',
        'region': 'USA',
        'ter': 0.0023,
        'description': 'Mid Cap USA (proxy SPY4)',
        'cto_equivalent': 'SPY4'
    },
    'GDX': {
        'name': 'VanEck Gold Miners ETF',
        'isin': 'US92189F1066',
        'ticker_yahoo': 'GDX',  # ✅ FONCTIONNE
        'type': 'equity',
        'region': 'Global',
        'ter': 0.0051,
        'description': 'Producteurs or (proxy SPGP)',
        'cto_equivalent': 'SPGP'
    },
    
    # Obligations Safe Harbor (système dual)
    'IEF': {
        'name': 'iShares 7-10 Year Treasury Bond ETF',
        'isin': 'US4642872883',
        'ticker_yahoo': 'IEF',  # ✅ FONCTIONNE
        'type': 'bond',
        'region': 'USA',
        'ter': 0.0015,
        'description': 'Obligations USA 7-10 ans (proxy IBTM)',
        'cto_equivalent': 'IBTM'
    },
    'AGG': {
        'name': 'iShares Core U.S. Aggregate Bond ETF',
        'isin': 'US4642872265',
        'ticker_yahoo': 'AGG',  # ✅ FONCTIONNE
        'type': 'bond',
        'region': 'USA',
        'ter': 0.0003,
        'description': 'Obligations agrégat USA (proxy AGGH)',
        'cto_equivalent': 'AGGH'
    }
}

# Paramètres stratégie (identiques config principale)
MOMENTUM_WEIGHTS = {
    '1m': 0.12,
    '3m': 0.40,
    '6m': 0.48
}

FILTERS = {
    'sma_period_months': 10,
    'volatility_multiplier': 1.5,
    'max_drawdown_threshold': -0.10,
    'min_momentum_score': 0.0
}

REBALANCING = {
    'monthly': True,
    'mid_month': True,
    'mid_month_threshold': 0.0008,
    'transaction_cost_pea': 0.0002,
    'transaction_cost_cto': 0.0002
}

# Validation
def validate_working_config():
    """Valide que tous les tickers fonctionnent"""
    import yfinance as yf
    import warnings
    warnings.filterwarnings('ignore')
    
    all_tickers = list(PEA_ETFS_WORKING.keys()) + list(CTO_ETFS_WORKING.keys())
    
    print("Validation tickers Yahoo Finance...")
    print("=" * 70)
    
    working = []
    failed = []
    
    for ticker in all_tickers:
        try:
            data = yf.Ticker(ticker).history(period='5d')
            if not data.empty:
                working.append(ticker)
                print(f"✅ {ticker}: OK ({len(data)} jours)")
            else:
                failed.append(ticker)
                print(f"❌ {ticker}: ÉCHEC (données vides)")
        except Exception as e:
            failed.append(ticker)
            print(f"❌ {ticker}: ERREUR ({str(e)[:50]})")
    
    print("=" * 70)
    print(f"Résultat: {len(working)}/{len(all_tickers)} tickers fonctionnels")
    
    if len(working) == len(all_tickers):
        print("✅ TOUS LES TICKERS VALIDÉS")
        return True
    else:
        print(f"⚠️ {len(failed)} tickers en échec: {failed}")
        return False

if __name__ == "__main__":
    validate_working_config()
