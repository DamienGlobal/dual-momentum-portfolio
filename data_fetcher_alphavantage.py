"""
Module de récupération de données via Alpha Vantage API
Alternative professionnelle à Yahoo Finance pour fiabilité maximale

Author: GLOBAL ICON - Dual Momentum System
Version: 1.0.0 - Alpha Vantage Integration
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import json

# =============================================================================
# CONFIGURATION API ALPHA VANTAGE
# =============================================================================

ALPHA_VANTAGE_API_KEY = "DEMO"  # ⚠️ REMPLACER PAR VOTRE CLÉ GRATUITE
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# Cache local pour éviter requêtes répétées
CACHE_FILE = "/home/user/dual_momentum_app/cache_alphavantage.json"
CACHE_DURATION_HOURS = 24

# =============================================================================
# GESTION CACHE LOCAL
# =============================================================================

def load_cache() -> Dict:
    """Charge le cache local depuis le fichier JSON"""
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
            # Nettoyer entrées expirées
            now = datetime.now().timestamp()
            cache = {
                k: v for k, v in cache.items()
                if now - v['timestamp'] < CACHE_DURATION_HOURS * 3600
            }
            return cache
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_cache(cache: Dict):
    """Sauvegarde le cache dans le fichier JSON"""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def get_from_cache(ticker: str) -> Optional[pd.DataFrame]:
    """Récupère données depuis le cache si valides"""
    cache = load_cache()
    if ticker in cache:
        data = pd.DataFrame(cache[ticker]['data'])
        data['Date'] = pd.to_datetime(data['Date'])
        data.set_index('Date', inplace=True)
        return data
    return None

def save_to_cache(ticker: str, data: pd.DataFrame):
    """Sauvegarde données dans le cache"""
    cache = load_cache()
    cache[ticker] = {
        'timestamp': datetime.now().timestamp(),
        'data': data.reset_index().to_dict(orient='records')
    }
    save_cache(cache)

# =============================================================================
# RÉCUPÉRATION DONNÉES ALPHA VANTAGE
# =============================================================================

def fetch_etf_data_alphavantage(
    ticker: str,
    start_date: str = None,
    end_date: str = None
) -> Optional[pd.DataFrame]:
    """
    Récupère données historiques ETF via Alpha Vantage API
    
    Parameters:
    -----------
    ticker : str
        Symbole boursier (ex: "VOO", "QQQ", "VT")
    start_date : str, optional
        Date début format YYYY-MM-DD (défaut: 2 ans avant)
    end_date : str, optional
        Date fin format YYYY-MM-DD (défaut: aujourd'hui)
    
    Returns:
    --------
    pd.DataFrame
        Colonnes: Date (index), Close, Volume
        Ou None si échec
    """
    
    # 1. VÉRIFIER CACHE
    cached_data = get_from_cache(ticker)
    if cached_data is not None:
        print(f"✅ {ticker}: Données depuis cache (valide {CACHE_DURATION_HOURS}h)")
        return cached_data
    
    # 2. PARAMÈTRES REQUÊTE API
    params = {
        'function': 'TIME_SERIES_DAILY_ADJUSTED',
        'symbol': ticker,
        'outputsize': 'full',  # Historique complet (20+ ans)
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    
    try:
        # 3. REQUÊTE HTTP
        print(f"🔄 {ticker}: Récupération depuis Alpha Vantage...")
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        
        data_json = response.json()
        
        # 4. VÉRIFIER ERREURS API
        if 'Error Message' in data_json:
            print(f"❌ {ticker}: Erreur API - {data_json['Error Message']}")
            return None
        
        if 'Note' in data_json:
            print(f"⚠️ {ticker}: Limite API atteinte - {data_json['Note']}")
            return None
        
        if 'Time Series (Daily)' not in data_json:
            print(f"❌ {ticker}: Données introuvables dans réponse API")
            return None
        
        # 5. PARSER DONNÉES
        time_series = data_json['Time Series (Daily)']
        
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Colonnes: '1. open', '2. high', '3. low', '4. close', '5. adjusted close', '6. volume'
        df['Close'] = df['5. adjusted close'].astype(float)
        df['Volume'] = df['6. volume'].astype(float)
        
        df = df[['Close', 'Volume']]
        
        # 6. FILTRER DATES
        if start_date:
            df = df[df.index >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df.index <= pd.to_datetime(end_date)]
        
        # 7. VÉRIFIER QUALITÉ DONNÉES
        if len(df) < 20:
            print(f"❌ {ticker}: Données insuffisantes ({len(df)} jours)")
            return None
        
        # 8. SAUVEGARDER CACHE
        save_to_cache(ticker, df)
        
        print(f"✅ {ticker}: {len(df)} jours récupérés (de {df.index.min().date()} à {df.index.max().date()})")
        
        # 9. RESPECTER LIMITE API (5 requêtes/minute)
        time.sleep(12)  # 12s entre chaque requête = 5 req/min max
        
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"❌ {ticker}: Erreur réseau - {str(e)}")
        return None
    except Exception as e:
        print(f"❌ {ticker}: Erreur inattendue - {str(e)}")
        return None

# =============================================================================
# CALCULS TECHNIQUES (IDENTIQUE À data_fetcher.py)
# =============================================================================

def calculate_returns(
    prices: pd.DataFrame,
    periods: List[int] = [21, 63, 126]
) -> pd.DataFrame:
    """
    Calcule rendements sur différentes périodes
    
    Parameters:
    -----------
    prices : pd.DataFrame
        Prix de clôture ajustés (colonne 'Close')
    periods : list
        Périodes en jours ouvrés (défaut: [21, 63, 126] = 1M, 3M, 6M)
    
    Returns:
    --------
    pd.DataFrame
        Colonnes: R_21, R_63, R_126 (rendements en %)
    """
    returns_df = pd.DataFrame(index=prices.index)
    
    for period in periods:
        col_name = f'R_{period}'
        # Rendement = (Prix_t / Prix_t-period) - 1
        returns_df[col_name] = (prices['Close'] / prices['Close'].shift(period) - 1) * 100
    
    return returns_df

def calculate_sma(prices: pd.DataFrame, window: int = 200) -> pd.Series:
    """
    Calcule moyenne mobile simple
    
    Parameters:
    -----------
    prices : pd.DataFrame
        Prix de clôture (colonne 'Close')
    window : int
        Période de calcul en jours (défaut: 200 jours ≈ 10 mois)
    
    Returns:
    --------
    pd.Series
        SMA sur période spécifiée
    """
    return prices['Close'].rolling(window=window, min_periods=window).mean()

def calculate_volatility(
    prices: pd.DataFrame,
    window: int = 21
) -> pd.Series:
    """
    Calcule volatilité annualisée glissante
    
    Parameters:
    -----------
    prices : pd.DataFrame
        Prix de clôture (colonne 'Close')
    window : int
        Fenêtre de calcul en jours (défaut: 21 jours = 1 mois)
    
    Returns:
    --------
    pd.Series
        Volatilité annualisée (en %)
    """
    # Rendements quotidiens
    daily_returns = prices['Close'].pct_change()
    
    # Écart-type glissant
    rolling_std = daily_returns.rolling(window=window, min_periods=window).std()
    
    # Annualisation (√252 jours de trading)
    volatility_annualized = rolling_std * np.sqrt(252) * 100
    
    return volatility_annualized

# =============================================================================
# PIPELINE COMPLET PAR ETF
# =============================================================================

def get_etf_complete_data(
    ticker: str,
    start_date: str = None,
    end_date: str = None
) -> Optional[pd.DataFrame]:
    """
    Pipeline complet: récupération + calculs techniques
    
    Parameters:
    -----------
    ticker : str
        Symbole ETF
    start_date, end_date : str, optional
        Période d'analyse (YYYY-MM-DD)
    
    Returns:
    --------
    pd.DataFrame
        Colonnes: Close, Volume, R_21, R_63, R_126, SMA_200, Vol_21
        Ou None si échec
    """
    
    # 1. RÉCUPÉRER PRIX
    prices = fetch_etf_data_alphavantage(ticker, start_date, end_date)
    if prices is None:
        return None
    
    # 2. CALCULS TECHNIQUES
    result = prices.copy()
    
    # Rendements 1M, 3M, 6M
    returns = calculate_returns(prices, periods=[21, 63, 126])
    result = result.join(returns)
    
    # Moyenne mobile 200 jours (≈ 10 mois)
    result['SMA_200'] = calculate_sma(prices, window=200)
    
    # Volatilité 21 jours (≈ 1 mois)
    result['Vol_21'] = calculate_volatility(prices, window=21)
    
    # 3. NETTOYER VALEURS MANQUANTES
    result = result.dropna()
    
    return result

# =============================================================================
# TRAITEMENT BATCH MULTI-ETFS
# =============================================================================

def fetch_multiple_etfs(
    tickers: List[str],
    start_date: str = None,
    end_date: str = None
) -> Dict[str, pd.DataFrame]:
    """
    Récupère données pour liste d'ETFs avec gestion cache et erreurs
    
    Parameters:
    -----------
    tickers : list
        Liste de symboles boursiers
    start_date, end_date : str, optional
        Période d'analyse
    
    Returns:
    --------
    dict
        {ticker: DataFrame} pour ETFs récupérés avec succès
    """
    
    results = {}
    
    print("=" * 80)
    print(f"RÉCUPÉRATION DONNÉES POUR {len(tickers)} ETFs via Alpha Vantage")
    print("=" * 80)
    
    for ticker in tickers:
        data = get_etf_complete_data(ticker, start_date, end_date)
        if data is not None:
            results[ticker] = data
    
    print("=" * 80)
    print(f"RÉSULTATS: {len(results)}/{len(tickers)} ETFs récupérés avec succès")
    print("=" * 80)
    
    return results

# =============================================================================
# CONFIGURATION CLÉ API
# =============================================================================

def set_api_key(api_key: str):
    """
    Configure la clé API Alpha Vantage
    
    ⚠️ OBTENIR CLÉ GRATUITE: https://www.alphavantage.co/support/#api-key
    
    Parameters:
    -----------
    api_key : str
        Clé API gratuite (25 requêtes/jour)
    """
    global ALPHA_VANTAGE_API_KEY
    ALPHA_VANTAGE_API_KEY = api_key
    print(f"✅ Clé API configurée: {api_key[:8]}...{api_key[-4:]}")

# =============================================================================
# TESTS UNITAIRES
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TEST MODULE DATA_FETCHER_ALPHAVANTAGE")
    print("=" * 80)
    
    # Test 1: Récupération ETF unique (cache)
    print("\n[TEST 1] Récupération VOO (Vanguard S&P 500)...")
    data_voo = get_etf_complete_data("VOO")
    if data_voo is not None:
        print(f"✅ VOO: {len(data_voo)} jours récupérés")
        print(f"   Dernière date: {data_voo.index.max().date()}")
        print(f"   Prix actuel: ${data_voo['Close'].iloc[-1]:.2f}")
        print(f"   Rendement 1M: {data_voo['R_21'].iloc[-1]:.2f}%")
    
    # Test 2: ETF inexistant
    print("\n[TEST 2] Ticker invalide...")
    data_invalid = get_etf_complete_data("INVALIDTICKER123")
    if data_invalid is None:
        print("✅ Gestion erreur correcte pour ticker invalide")
    
    print("\n" + "=" * 80)
