"""
Configuration complète 20 ETF (9 PEA + 11 CTO).

Structure : Liste de dictionnaires
Chaque ETF est un dict avec : name, ticker, isin, category, expense_ratio, description

Utilisé par :
- portfolio_engine.py (orchestration analyse)
- app.py (interface Streamlit)
"""

# =============================================================================
# ETF ÉLIGIBLES PEA (9 ETF)
# =============================================================================

PEA_ETFS = [
    {
        "name": "Vanguard Total World Stock ETF",
        "ticker": "VT",
        "isin": "US9220427424",
        "category": "World Equity",
        "expense_ratio": 0.07,
        "description": "Exposition mondiale diversifiée (actions développés + émergents)"
    },
    {
        "name": "Vanguard S&P 500 ETF",
        "ticker": "VOO",
        "isin": "US9229087690",
        "category": "US Large Cap",
        "expense_ratio": 0.03,
        "description": "500 plus grandes capitalisations américaines"
    },
    {
        "name": "Vanguard FTSE Emerging Markets ETF",
        "ticker": "VWO",
        "isin": "US9220428588",
        "category": "Emerging Markets",
        "expense_ratio": 0.08,
        "description": "Actions marchés émergents (Chine, Inde, Brésil)"
    },
    {
        "name": "Vanguard FTSE Europe ETF",
        "ticker": "VGK",
        "isin": "US9219097683",
        "category": "Europe Equity",
        "expense_ratio": 0.08,
        "description": "Actions européennes développées"
    },
    {
        "name": "iShares MSCI Japan ETF",
        "ticker": "EWJ",
        "isin": "US4642872349",
        "category": "Japan Equity",
        "expense_ratio": 0.50,
        "description": "Actions japonaises"
    },
    {
        "name": "iShares Russell 2000 ETF",
        "ticker": "IWM",
        "isin": "US4642872414",
        "category": "US Small Cap",
        "expense_ratio": 0.19,
        "description": "Petites capitalisations américaines"
    },
    {
        "name": "Invesco QQQ Trust",
        "ticker": "QQQ",
        "isin": "US46090E1038",
        "category": "US Tech",
        "expense_ratio": 0.20,
        "description": "100 plus grandes entreprises Nasdaq (tech-heavy)"
    },
    {
        "name": "Energy Select Sector SPDR Fund",
        "ticker": "XLE",
        "isin": "US81369Y8030",
        "category": "Energy Sector",
        "expense_ratio": 0.10,
        "description": "Secteur énergétique américain"
    },
    {
        "name": "iShares 1-3 Year Treasury Bond ETF",
        "ticker": "SHY",
        "isin": "US4642874329",
        "category": "Short-Term Bonds",
        "expense_ratio": 0.15,
        "description": "Obligations d'État américaines court terme (protection)"
    }
]


# =============================================================================
# ETF COMPTE-TITRES ORDINAIRE (11 ETF)
# =============================================================================

CTO_ETFS = [
    {
        "name": "iShares MSCI ACWI ETF",
        "ticker": "ACWI",
        "isin": "US4642874576",
        "category": "World Equity",
        "expense_ratio": 0.32,
        "description": "Actions mondiales (développés + émergents)"
    },
    {
        "name": "Vanguard FTSE All-World Small-Cap ETF",
        "ticker": "VSS",
        "isin": "US9219097848",
        "category": "Global Small Cap",
        "expense_ratio": 0.11,
        "description": "Petites capitalisations mondiales"
    },
    {
        "name": "iShares Core MSCI Emerging Markets ETF",
        "ticker": "IEMG",
        "isin": "US4642874220",
        "category": "Emerging Markets",
        "expense_ratio": 0.09,
        "description": "Actions marchés émergents diversifiés"
    },
    {
        "name": "iShares MSCI China ETF",
        "ticker": "MCHI",
        "isin": "US4642874238",
        "category": "China Equity",
        "expense_ratio": 0.59,
        "description": "Actions chinoises large/mid cap"
    },
    {
        "name": "iShares MSCI All Country Asia ex Japan ETF",
        "ticker": "AAXJ",
        "isin": "US4642863926",
        "category": "Asia ex-Japan",
        "expense_ratio": 0.68,
        "description": "Actions asiatiques hors Japon"
    },
    {
        "name": "Vanguard Russell 2000 ETF",
        "ticker": "VTWO",
        "isin": "US9229083632",
        "category": "US Small Cap",
        "expense_ratio": 0.10,
        "description": "Petites capitalisations américaines"
    },
    {
        "name": "Fidelity Nasdaq Composite Index ETF",
        "ticker": "ONEQ",
        "isin": "US3160928030",
        "category": "US Tech",
        "expense_ratio": 0.21,
        "description": "Nasdaq Composite (technologie)"
    },
    {
        "name": "SPDR S&P MidCap 400 ETF Trust",
        "ticker": "MDY",
        "isin": "US78464A7087",
        "category": "US Mid Cap",
        "expense_ratio": 0.23,
        "description": "Moyennes capitalisations américaines"
    },
    {
        "name": "VanEck Gold Miners ETF",
        "ticker": "GDX",
        "isin": "US92189F1066",
        "category": "Gold Miners",
        "expense_ratio": 0.51,
        "description": "Sociétés minières aurifères (protection inflation)"
    },
    {
        "name": "iShares 7-10 Year Treasury Bond ETF",
        "ticker": "IEF",
        "isin": "US4642872265",
        "category": "Intermediate Bonds",
        "expense_ratio": 0.15,
        "description": "Obligations d'État américaines moyen terme"
    },
    {
        "name": "iShares Core US Aggregate Bond ETF",
        "ticker": "AGG",
        "isin": "US4642872001",
        "category": "Bond Aggregate",
        "expense_ratio": 0.03,
        "description": "Obligations américaines diversifiées"
    }
]


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def get_all_tickers():
    """Retourne liste complète des tickers (PEA + CTO)."""
    return [etf['ticker'] for etf in PEA_ETFS] + [etf['ticker'] for etf in CTO_ETFS]


def get_etf_info(ticker: str):
    """
    Récupère informations ETF par ticker.
    
    Args:
        ticker: Symbol ETF (ex: "VOO")
        
    Returns:
        Dict informations ETF ou None si non trouvé
    """
    all_etfs = PEA_ETFS + CTO_ETFS
    for etf in all_etfs:
        if etf['ticker'] == ticker:
            return etf
    return None


def get_pea_tickers():
    """Retourne liste tickers PEA uniquement."""
    return [etf['ticker'] for etf in PEA_ETFS]


def get_cto_tickers():
    """Retourne liste tickers CTO uniquement."""
    return [etf['ticker'] for etf in CTO_ETFS]


def print_portfolio_summary():
    """Affiche résumé configuration portefeuille."""
    print("=" * 80)
    print("CONFIGURATION PORTEFEUILLE DUAL MOMENTUM")
    print("=" * 80)
    
    print(f"\n📊 PEA : {len(PEA_ETFS)} ETF")
    print("-" * 80)
    for etf in PEA_ETFS:
        print(f"  {etf['ticker']:6} | {etf['name']:40} | {etf['category']}")
    
    print(f"\n📊 CTO : {len(CTO_ETFS)} ETF")
    print("-" * 80)
    for etf in CTO_ETFS:
        print(f"  {etf['ticker']:6} | {etf['name']:40} | {etf['category']}")
    
    print(f"\n📈 TOTAL : {len(PEA_ETFS) + len(CTO_ETFS)} ETF")
    print("=" * 80)


if __name__ == "__main__":
    # Test configuration
    print_portfolio_summary()
    
    print("\n🧪 Test fonctions utilitaires...")
    print(f"Tous tickers : {get_all_tickers()}")
    print(f"\nInfo VOO : {get_etf_info('VOO')}")
    print(f"\nTickers PEA : {get_pea_tickers()}")
    print(f"Tickers CTO : {get_cto_tickers()}")
