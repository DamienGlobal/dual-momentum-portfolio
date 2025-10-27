"""
Module de récupération de données via Finnhub API
API professionnelle gratuite (60 req/min) avec support ETF mondial

Author: GLOBAL ICON - Dual Momentum System
Version: 1.0.0 - Finnhub Integration
Date: 2025-10-27
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
import json

# =============================================================================
# CONFIGURATION API FINNHUB
# =============================================================================

FINNHUB_API_KEY = "d3vrmn9r01qn5gnjbcagd3vrmn9r01qn5gnjbcb0"  # ✅ Clé API configurée
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

# Cache local pour éviter requêtes répétées
CACHE_FILE = "/home/user/dual_momentum_app/cache_finnhub.json"
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
# RÉCUPÉRATION DONNÉES FINNHUB
# =============================================================================

def fetch_etf_data_finnhub(
    ticker: str,
    start_date: str = None,
    end_date: str = None
) -> Optional[pd.DataFrame]:
    """
    Récupère données historiques ETF via Finnhub API
    
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
    
    # 2. DATES PAR DÉFAUT
    if end_date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    if start_date is None:
        start_date = end_date - timedelta(days=730)  # 2 ans
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    
    # Conversion en timestamps Unix
    from_ts = int(start_date.timestamp())
    to_ts = int(end_date.timestamp())
    
    # 3. PARAMÈTRES REQUÊTE API
    url = f"{FINNHUB_BASE_URL}/stock/candle"
    params = {
        'symbol': ticker,
        'resolution': 'D',  # Daily
        'from': from_ts,
        'to': to_ts,
        'token': FINNHUB_API_KEY
    }
    
    try:
        # 4. REQUÊTE HTTP
        print(f"🔄 {ticker}: Récupération depuis Finnhub...")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data_json = response.json()
        
        # 5. VÉRIFIER ERREURS API
        if 'error' in data_json:
            print(f"❌ {ticker}: Erreur API - {data_json['error']}")
            return None
        
        if data_json.get('s') == 'no_data':
            print(f"❌ {ticker}: Aucune donnée disponible pour cette période")
            return None
        
        if 'c' not in data_json or 'v' not in data_json or 't' not in data_json:
            print(f"❌ {ticker}: Données incomplètes dans réponse API")
            return None
        
        # 6. PARSER DONNÉES
        # Format Finnhub: {c: [close], h: [high], l: [low], o: [open], t: [timestamp], v: [volume]}
        df = pd.DataFrame({
            'Date': pd.to_datetime(data_json['t'], unit='s'),
            'Close': data_json['c'],
            'Volume': data_json['v']
        })
        
        df.set_index('Date', inplace=True)
        df = df.sort_index()
        
        # 7. VÉRIFIER QUALITÉ DONNÉES
        if len(df) < 20:
            print(f"❌ {ticker}: Données insuffisantes ({len(df)} jours)")
            return None
        
        # 8. SAUVEGARDER CACHE
        save_to_cache(ticker, df)
        
        print(f"✅ {ticker}: {len(df)} jours récupérés (de {df.index.min().date()} à {df.index.max().date()})")
        
        # 9. RESPECTER LIMITE API (60 requêtes/minute)
        time.sleep(1.1)  # 1.1s entre requêtes = max 54 req/min (sécurité)
        
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
    prices = fetch_etf_data_finnhub(ticker, start_date, end_date)
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
    print(f"RÉCUPÉRATION DONNÉES POUR {len(tickers)} ETFs via Finnhub")
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
    Configure la clé API Finnhub
    
    ⚠️ OBTENIR CLÉ GRATUITE: https://finnhub.io/register
    
    Parameters:
    -----------
    api_key : str
        Clé API gratuite (60 requêtes/minute)
    """
    global FINNHUB_API_KEY
    FINNHUB_API_KEY = api_key
    print(f"✅ Clé API Finnhub configurée: {api_key[:8]}...{api_key[-4:]}")

# =============================================================================
# TESTS UNITAIRES
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TEST MODULE DATA_FETCHER_FINNHUB")
    print("=" * 80)
    
    # Vérifier clé API configurée
    if FINNHUB_API_KEY == "YOUR_KEY_HERE":
        print("\n❌ ERREUR: Clé API non configurée")
        print("\n📝 INSTRUCTIONS:")
        print("1. Aller sur: https://finnhub.io/register")
        print("2. Créer compte gratuit (email requis)")
        print("3. Copier clé API depuis Dashboard")
        print("4. Modifier FINNHUB_API_KEY dans ce fichier")
        print("\nOu utiliser: set_api_key('votre_cle_ici')")
    else:
        # Test 1: Récupération ETF unique (avec cache)
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
