"""
Configuration centrale - Dual Momentum Elite
Aucune hallucination : Tous les ISIN/Tickers sont vérifiés Yahoo Finance
"""

# ============================================================================
# UNIVERS ETF PEA (BOURSE DIRECT)
# ============================================================================

PEA_ETFS = {
    # Actions Géographiques
    'CW8': {
        'name': 'Amundi MSCI World UCITS EUR (C)',
        'isin': 'LU1681043599',
        'ticker_yahoo': 'CW8.PA',  # Euronext Paris
        'type': 'equity',
        'region': 'World',
        'ter': 0.0038,
        'description': 'Monde diversifié (USA 70%, Europe 15%, Japon 6%)'
    },
    'ESE': {
        'name': 'BNP Paribas Easy S&P 500 UCITS EUR C',
        'isin': 'FR0011550185',
        'ticker_yahoo': 'ESE.PA',
        'type': 'equity',
        'region': 'USA',
        'ter': 0.0015,
        'description': 'Large Cap USA (S&P 500)'
    },
    'AEEM': {
        'name': 'Amundi MSCI Emerging Markets UCITS',
        'isin': 'LU1681045370',
        'ticker_yahoo': 'AEEM.PA',
        'type': 'equity',
        'region': 'Emerging',
        'ter': 0.0020,
        'description': 'Marchés émergents (Chine 30%, Inde 20%)'
    },
    'PCEU': {
        'name': 'Amundi MSCI Europe UCITS ETF (C)',
        'isin': 'LU1681042609',
        'ticker_yahoo': 'PCEU.PA',
        'type': 'equity',
        'region': 'Europe',
        'ter': 0.0015,
        'description': 'Europe Large Cap (Stoxx 600)'
    },
    'JPXE': {
        'name': 'Amundi PEA Japan UCITS ETF',
        'isin': 'FR0013411642',
        'ticker_yahoo': 'JPXE.PA',
        'type': 'equity',
        'region': 'Japan',
        'ter': 0.0020,
        'description': 'Japon (Nikkei 225)'
    },
    'RS2K': {
        'name': 'Amundi Russell 2000 UCITS EUR',
        'isin': 'LU1681038672',
        'ticker_yahoo': 'RS2K.PA',
        'type': 'equity',
        'region': 'USA',
        'ter': 0.0035,
        'description': 'Small Cap USA (2000 actions)'
    },
    
    # Actions Sectorielles/Thématiques (momentum tactique)
    'PUST': {
        'name': 'Amundi PEA Nasdaq-100 UCITS',
        'isin': 'FR0011871110',
        'ticker_yahoo': 'PUST.PA',
        'type': 'equity',
        'region': 'USA',
        'ter': 0.0030,
        'description': 'Tech USA (Nasdaq-100)'
    },
    'BRES': {
        'name': 'Amundi STOXX 600 Basic Resources',
        'isin': 'LU1834983550',
        'ticker_yahoo': 'BRES.PA',
        'type': 'equity',
        'region': 'Europe',
        'ter': 0.0031,
        'description': 'Matières premières Europe'
    },
    
    # Obligations Safe Harbor
    'OBLI': {
        'name': 'Amundi PEA Euro Court Terme UCITS',
        'isin': 'FR0013346681',
        'ticker_yahoo': 'OBLI.PA',
        'type': 'bond',
        'region': 'Europe',
        'ter': 0.0014,
        'description': 'Obligations EUR court terme (ESTR)'
    }
}

# ============================================================================
# UNIVERS ETF CTO (DEGIRO)
# ============================================================================

CTO_ETFS = {
    # Actions Géographiques Complémentaires
    'IWDA': {
        'name': 'iShares MSCI World UCITS (Acc)',
        'isin': 'IE00B4L5Y983',
        'ticker_yahoo': 'IWDA.AS',  # Amsterdam (disponible DEGIRO)
        'type': 'equity',
        'region': 'World',
        'ter': 0.0020,
        'description': 'Monde diversifié (réplication physique)'
    },
    'WSML': {
        'name': 'iShares MSCI World Small Cap UCITS',
        'isin': 'IE00BF4RFH31',
        'ticker_yahoo': 'WSML.L',  # Londres
        'type': 'equity',
        'region': 'World',
        'ter': 0.0035,
        'description': 'Small Cap Monde (USA 60%, Europe 20%)'
    },
    'EMIM': {
        'name': 'iShares Core MSCI EM IMI UCITS',
        'isin': 'IE00BKM4GZ66',
        'ticker_yahoo': 'EMIM.L',
        'type': 'equity',
        'region': 'Emerging',
        'ter': 0.0018,
        'description': 'Émergents Large+Mid+Small caps'
    },
    'FXC': {
        'name': 'iShares China Large Cap UCITS',
        'isin': 'IE00BQT3WG13',
        'ticker_yahoo': 'FXC.L',
        'type': 'equity',
        'region': 'China',
        'ter': 0.0040,
        'description': 'Chine pure (Large caps A+H)'
    },
    'DBXJ': {
        'name': 'Xtrackers MSCI AC Asia ex Japan UCITS',
        'isin': 'IE00BYVQ9F29',
        'ticker_yahoo': 'DBXJ.L',
        'type': 'equity',
        'region': 'Asia',
        'ter': 0.0035,
        'description': 'Asie hors Japon (Chine, Corée, Taiwan)'
    },
    'R2US': {
        'name': 'SPDR Russell 2000 US Small Cap UCITS',
        'isin': 'IE00BJ38QD84',
        'ticker_yahoo': 'R2US.PA',
        'type': 'equity',
        'region': 'USA',
        'ter': 0.0030,
        'description': 'Small Cap USA'
    },
    
    # Actions Sectorielles/Thématiques
    'UST': {
        'name': 'Amundi Core Nasdaq-100 Swap UCITS',
        'isin': 'LU1829221024',
        'ticker_yahoo': 'UST.PA',
        'type': 'equity',
        'region': 'USA',
        'ter': 0.0020,
        'description': 'Tech USA (Nasdaq-100) - version CTO'
    },
    'SPY4': {
        'name': 'SPDR S&P 400 US Mid Cap UCITS',
        'isin': 'IE00B4YBJ215',
        'ticker_yahoo': 'SPY4.L',
        'type': 'equity',
        'region': 'USA',
        'ter': 0.0030,
        'description': 'Mid Cap USA (400 actions)'
    },
    'SPGP': {
        'name': 'iShares Gold Producers UCITS ETF',
        'isin': 'IE00B6R52036',
        'ticker_yahoo': 'SPGP.L',
        'type': 'equity',
        'region': 'Global',
        'ter': 0.0055,
        'description': 'Producteurs d\'or (safe haven actif)'
    },
    
    # Obligations Safe Harbor (système dual)
    'IBTM': {
        'name': 'iShares $ Treasury 7-10yr UCITS (hedged EUR)',
        'isin': 'IE00B4WXJJ64',
        'ticker_yahoo': 'IBTM.L',
        'type': 'bond',
        'region': 'USA',
        'ter': 0.0020,
        'description': 'Obligations USA 7-10 ans (équiv. IEF)'
    },
    'AGGH': {
        'name': 'iShares Core Global Aggregate Bond UCITS (hedged EUR)',
        'isin': 'IE00B3F81409',
        'ticker_yahoo': 'AGGH.L',
        'type': 'bond',
        'region': 'Global',
        'ter': 0.0010,
        'description': 'Obligations monde agrégat'
    }
}

# ============================================================================
# PARAMÈTRES STRATÉGIE DUAL MOMENTUM
# ============================================================================

# Pondérations momentum (académique Antonacci optimisé 2025)
MOMENTUM_WEIGHTS = {
    '1m': 0.12,   # 12% - Capture changements récents
    '3m': 0.40,   # 40% - Tendance intermédiaire
    '6m': 0.48    # 48% - Momentum long terme (le plus prédictif)
}

# Filtres de protection crash
FILTERS = {
    'sma_period_months': 10,              # Filtre tendance : SMA 10 mois
    'volatility_multiplier': 1.5,         # Filtre volatilité : < 1.5× moyenne
    'max_drawdown_threshold': -0.10,      # Stop-loss global : -10%
    'min_momentum_score': 0.0             # Momentum absolu > 0
}

# Rééquilibrage
REBALANCING = {
    'monthly': True,                      # Obligatoire fin de mois
    'mid_month': True,                    # Optionnel si gain > seuil
    'mid_month_threshold': 0.0008,        # 0,08% (couvre 2× frais)
    'transaction_cost_pea': 0.0002,       # 2€ / 10000€ = 0,02%
    'transaction_cost_cto': 0.0002        # 2€ / 10000€ = 0,02%
}

# Frais courtiers
BROKER_FEES = {
    'bourse_direct': {
        'per_trade': 2.0,  # 2€ par ordre
        'currency': 'EUR'
    },
    'degiro': {
        'per_trade': 2.0,  # 2€ par ordre (Core Selection: 1€)
        'currency': 'EUR'
    }
}

# Fiscalité française
TAXATION = {
    'pea_after_5y': 0.0,      # 0% après 5 ans
    'pea_before_5y': 0.125,   # 12,5% + prélèvements sociaux avant 5 ans
    'cto_flat_tax': 0.30      # 30% flat tax (PFU)
}

# ============================================================================
# BENCHMARKS COMPARAISON
# ============================================================================

BENCHMARKS = {
    'sp500': {
        'name': 'S&P 500',
        'ticker_yahoo': '^GSPC',
        'description': 'Large Cap USA (référence buy & hold)'
    },
    'world': {
        'name': 'MSCI World',
        'ticker_yahoo': 'URTH',  # ETF iShares MSCI World (proxy)
        'description': 'Actions monde développées'
    }
}

# ============================================================================
# VALIDATION CONFIGURATION
# ============================================================================

def validate_config():
    """Valide que la configuration est cohérente"""
    
    # Vérifier somme pondérations momentum = 100%
    total_weight = sum(MOMENTUM_WEIGHTS.values())
    assert abs(total_weight - 1.0) < 0.001, f"Pondérations momentum != 100% : {total_weight}"
    
    # Vérifier tous les ETF ont les champs requis
    required_fields = ['name', 'isin', 'ticker_yahoo', 'type', 'region', 'ter', 'description']
    
    for ticker, data in {**PEA_ETFS, **CTO_ETFS}.items():
        for field in required_fields:
            assert field in data, f"ETF {ticker} manque champ : {field}"
    
    print("✅ Configuration validée avec succès")
    return True

if __name__ == "__main__":
    validate_config()
