#!/usr/bin/env python3
"""
Data Fetcher Real - Version 2.2.0
Récupération données réelles ETF via APIs externes
CORRECTIONS : Endpoint gratuit + Rate limiting + Retry intelligent

Changelog v2.2.0 (2025-10-28) :
- FIX CRITIQUE : TIME_SERIES_DAILY au lieu de DAILY_ADJUSTED (gratuit vs premium)
- AJOUT : Rate limiting intelligent (4 req/min avec safety margin)
- AJOUT : Retry exponentiel avec backoff automatique
- AJOUT : Logging détaillé pour debugging
- AMÉLIORATION : Cache local 24h (au lieu de 6h)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import requests
import json
import os
from pathlib import Path
import time
from typing import Optional, Dict, List, Tuple

# Configuration logging professionnel
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('data_fetcher_real')

# ============================================================================
# CONFIGURATION GLOBALE
# ============================================================================

CACHE_DIR = Path(__file__).parent / "cache_data_real"
CACHE_DURATION_HOURS = 24  # Cache valide 24h (au lieu de 6h)

# Rate limiting Alpha Vantage (plan gratuit : 5 req/min max)
RATE_LIMIT_CALLS = 4  # Safety margin : 4 au lieu de 5
RATE_LIMIT_PERIOD = 60  # Secondes

# Retry configuration
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2  # Délai base en secondes (2, 4, 8...)


class RateLimiter:
    """Gestionnaire rate limiting pour API externe"""
    
    def __init__(self, max_calls: int, period_seconds: int):
        self.max_calls = max_calls
        self.period = period_seconds
        self.calls = []
    
    def wait_if_needed(self):
        """Attendre si limite atteinte"""
        now = time.time()
        
        # Nettoyer vieux appels
        self.calls = [t for t in self.calls if now - t < self.period]
        
        # Vérifier limite
        if len(self.calls) >= self.max_calls:
            oldest_call = self.calls[0]
            wait_time = self.period - (now - oldest_call) + 1  # +1s safety
            if wait_time > 0:
                logger.info(f"⏸️  Rate limiting: attente {wait_time:.1f}s...")
                time.sleep(wait_time)
                self.calls = []  # Reset après attente
        
        self.calls.append(time.time())


class DataFetcherReal:
    """
    Récupération données réelles multi-sources avec fallback automatique
    
    Sources (ordre de priorité) :
    1. Yahoo Finance (yfinance) - Primaire
    2. Alpha Vantage API - Fallback
    3. Cache local - Ultime fallback
    
    Features :
    - Rate limiting intelligent
    - Retry automatique avec backoff exponentiel
    - Cache local JSON
    - Logging détaillé
    """
    
    def __init__(self, alpha_vantage_key: Optional[str] = None):
        """
        Initialisation du fetcher
        
        Args:
            alpha_vantage_key: Clé API Alpha Vantage (optionnel)
        """
        self.alpha_vantage_key = alpha_vantage_key
        self.rate_limiter = RateLimiter(RATE_LIMIT_CALLS, RATE_LIMIT_PERIOD)
        
        # Créer dossier cache
        CACHE_DIR.mkdir(exist_ok=True)
        
        logger.info("=" * 70)
        logger.info("🚀 DataFetcherReal v2.2.0 - Données Réelles ETF")
        logger.info("=" * 70)
        logger.info(f"📁 Cache directory: {CACHE_DIR}")
        logger.info(f"⏱️  Cache duration: {CACHE_DURATION_HOURS}h")
        
        if self.alpha_vantage_key:
            logger.info("✅ Alpha Vantage: Activé")
            logger.info(f"🔒 Rate limiting: {RATE_LIMIT_CALLS} req/{RATE_LIMIT_PERIOD}s")
        else:
            logger.info("⚠️  Alpha Vantage: Désactivé (pas de clé API)")
        
        logger.info("=" * 70)
    
    def get_cache_path(self, ticker: str) -> Path:
        """Chemin fichier cache pour un ticker"""
        return CACHE_DIR / f"{ticker}_cache.json"
    
    def is_cache_valid(self, ticker: str) -> bool:
        """Vérifier si cache existe et est valide"""
        cache_file = self.get_cache_path(ticker)
        
        if not cache_file.exists():
            return False
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            age_hours = (datetime.now() - cache_time).total_seconds() / 3600
            
            is_valid = age_hours < CACHE_DURATION_HOURS
            
            if is_valid:
                logger.debug(f"💾 {ticker}: Cache valide (âge: {age_hours:.1f}h)")
            else:
                logger.debug(f"⌛ {ticker}: Cache expiré (âge: {age_hours:.1f}h)")
            
            return is_valid
            
        except Exception as e:
            logger.warning(f"⚠️  {ticker}: Cache corrompu ({e})")
            return False
    
    def load_from_cache(self, ticker: str) -> Optional[pd.DataFrame]:
        """Charger données depuis cache local"""
        try:
            cache_file = self.get_cache_path(ticker)
            
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            df = pd.DataFrame(cache_data['data'])
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            
            logger.info(f"💾 {ticker}: Chargé depuis cache ({len(df)} jours)")
            return df
            
        except Exception as e:
            logger.error(f"❌ {ticker}: Erreur lecture cache ({e})")
            return None
    
    def save_to_cache(self, ticker: str, df: pd.DataFrame):
        """Sauvegarder données dans cache local"""
        try:
            cache_file = self.get_cache_path(ticker)
            
            # Préparer données pour JSON
            df_copy = df.reset_index()
            df_copy['Date'] = df_copy['Date'].astype(str)
            
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'ticker': ticker,
                'data': df_copy.to_dict('records')
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.debug(f"💾 {ticker}: Sauvegardé en cache ({len(df)} jours)")
            
        except Exception as e:
            logger.warning(f"⚠️  {ticker}: Erreur écriture cache ({e})")
    
    def fetch_yahoo_finance(self, ticker: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Récupération via Yahoo Finance (yfinance)
        
        Args:
            ticker: Symbole ETF (ex: "VOO")
            start_date: Date début (format: "YYYY-MM-DD")
            end_date: Date fin (format: "YYYY-MM-DD")
        
        Returns:
            DataFrame avec colonnes : Open, High, Low, Close, Volume
            None si échec
        """
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(f"📡 Yahoo Finance: {ticker} (tentative {attempt}/{MAX_RETRIES})")
                
                # Télécharger données
                data = yf.download(
                    ticker,
                    start=start_date,
                    end=end_date,
                    progress=False,
                    auto_adjust=False  # Garder prix non ajustés
                )
                
                # Vérifier succès
                if data.empty:
                    logger.warning(f"⚠️  {ticker}: Aucune donnée retournée")
                    if attempt < MAX_RETRIES:
                        wait_time = RETRY_BACKOFF_BASE ** attempt
                        logger.info(f"⏳ Retry dans {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    return None
                
                # Gérer MultiIndex si présent (yfinance >= 0.2.50)
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(0)
                
                # Normaliser noms colonnes
                data.columns = [col.title() for col in data.columns]
                
                # Vérifier colonnes requises
                required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                if not all(col in data.columns for col in required_cols):
                    logger.error(f"❌ {ticker}: Colonnes manquantes (trouvées: {list(data.columns)})")
                    return None
                
                # Sélectionner colonnes pertinentes
                df = data[required_cols].copy()
                
                # Nettoyer données
                df = df.dropna()
                
                if df.empty:
                    logger.warning(f"⚠️  {ticker}: Toutes les données sont NaN")
                    return None
                
                logger.info(f"✅ {ticker}: Yahoo Finance OK ({len(df)} jours)")
                return df
                
            except Exception as e:
                logger.warning(f"⚠️  {ticker}: Yahoo Finance échoué (tentative {attempt}): {type(e).__name__}: {str(e)}")
                
                if attempt < MAX_RETRIES:
                    wait_time = RETRY_BACKOFF_BASE ** attempt
                    logger.info(f"⏳ Retry dans {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ {ticker}: Yahoo Finance échec définitif après {MAX_RETRIES} tentatives")
                    return None
        
        return None
    
    def fetch_alpha_vantage(self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Récupération via Alpha Vantage API (fallback)
        
        ⚠️ CORRECTION v2.2.0 : Utilise TIME_SERIES_DAILY (gratuit)
        au lieu de TIME_SERIES_DAILY_ADJUSTED (premium)
        
        Args:
            ticker: Symbole ETF (ex: "VOO")
        
        Returns:
            DataFrame avec colonnes : Open, High, Low, Close, Volume
            None si échec
        """
        if not self.alpha_vantage_key:
            logger.debug(f"⏭️  {ticker}: Alpha Vantage ignoré (pas de clé)")
            return None
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # Rate limiting
                self.rate_limiter.wait_if_needed()
                
                logger.info(f"📡 Alpha Vantage: {ticker} (tentative {attempt}/{MAX_RETRIES})")
                
                url = "https://www.alphavantage.co/query"
                params = {
                    'function': 'TIME_SERIES_DAILY',  # ✅ CORRIGÉ : endpoint gratuit
                    'symbol': ticker,
                    'outputsize': 'full',  # Récupérer maximum de données
                    'apikey': self.alpha_vantage_key
                }
                
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                
                data_json = response.json()
                
                # Vérifier erreurs API
                if 'Error Message' in data_json:
                    logger.error(f"❌ {ticker}: {data_json['Error Message']}")
                    return None
                
                if 'Note' in data_json:
                    logger.warning(f"⚠️  {ticker}: Rate limit API atteint - {data_json['Note']}")
                    if attempt < MAX_RETRIES:
                        wait_time = 60  # Attendre 1 minute si rate limit
                        logger.info(f"⏳ Retry dans {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    return None
                
                if 'Information' in data_json:
                    logger.warning(f"ℹ️  {ticker}: {data_json['Information']}")
                    return None
                
                # Parser données
                time_series = data_json.get('Time Series (Daily)', {})
                
                if not time_series:
                    logger.error(f"❌ {ticker}: Pas de données dans la réponse")
                    logger.debug(f"🔍 Clés JSON reçues: {list(data_json.keys())}")
                    
                    if attempt < MAX_RETRIES:
                        wait_time = RETRY_BACKOFF_BASE ** attempt
                        logger.info(f"⏳ Retry dans {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    return None
                
                # Convertir en DataFrame
                df_list = []
                for date_str, values in time_series.items():
                    df_list.append({
                        'Date': pd.to_datetime(date_str),
                        'Open': float(values['1. open']),
                        'High': float(values['2. high']),
                        'Low': float(values['3. low']),
                        'Close': float(values['4. close']),
                        'Volume': int(values['5. volume'])
                    })
                
                df = pd.DataFrame(df_list)
                df.set_index('Date', inplace=True)
                df.sort_index(inplace=True)
                
                logger.info(f"✅ {ticker}: Alpha Vantage OK ({len(df)} jours)")
                return df
                
            except requests.exceptions.Timeout:
                logger.warning(f"⏱️  {ticker}: Alpha Vantage timeout (tentative {attempt})")
                if attempt < MAX_RETRIES:
                    wait_time = RETRY_BACKOFF_BASE ** attempt
                    time.sleep(wait_time)
                else:
                    return None
                    
            except Exception as e:
                logger.error(f"❌ {ticker}: Alpha Vantage erreur (tentative {attempt}): {type(e).__name__}: {str(e)}")
                
                if attempt < MAX_RETRIES:
                    wait_time = RETRY_BACKOFF_BASE ** attempt
                    time.sleep(wait_time)
                else:
                    return None
        
        return None
    
    def fetch_etf_data(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Récupération données ETF avec stratégie multi-sources
        
        Stratégie :
        1. Vérifier cache local (si valide)
        2. Essayer Yahoo Finance
        3. Fallback Alpha Vantage
        4. Fallback cache local (même expiré)
        
        Args:
            ticker: Symbole ETF (ex: "VOO")
            start_date: Date début (défaut: 5 ans en arrière)
            end_date: Date fin (défaut: aujourd'hui)
        
        Returns:
            DataFrame avec données OHLCV, None si échec total
        """
        # Dates par défaut
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=5*365)).strftime('%Y-%m-%d')
        
        logger.info(f"\n{'─'*70}")
        logger.info(f"📊 Récupération: {ticker} ({start_date} → {end_date})")
        logger.info(f"{'─'*70}")
        
        # Étape 1 : Cache valide
        if self.is_cache_valid(ticker):
            df = self.load_from_cache(ticker)
            if df is not None:
                return df
        
        # Étape 2 : Yahoo Finance
        df = self.fetch_yahoo_finance(ticker, start_date, end_date)
        if df is not None:
            self.save_to_cache(ticker, df)
            return df
        
        logger.warning(f"⚠️  {ticker}: Yahoo Finance échoué, tentative Alpha Vantage...")
        
        # Étape 3 : Alpha Vantage
        df = self.fetch_alpha_vantage(ticker)
        if df is not None:
            # Filtrer dates demandées
            df = df[(df.index >= start_date) & (df.index <= end_date)]
            self.save_to_cache(ticker, df)
            return df
        
        logger.warning(f"⚠️  {ticker}: Alpha Vantage échoué, tentative cache expiré...")
        
        # Étape 4 : Cache expiré (ultime fallback)
        cache_file = self.get_cache_path(ticker)
        if cache_file.exists():
            df = self.load_from_cache(ticker)
            if df is not None:
                logger.warning(f"⚠️  {ticker}: Utilisation cache EXPIRÉ (mieux que rien)")
                return df
        
        logger.error(f"❌ {ticker}: ÉCHEC - Toutes sources ont échoué")
        return None
    
    def fetch_portfolio_data(
        self,
        tickers: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Récupération données pour plusieurs ETF
        
        Args:
            tickers: Liste symboles ETF (ex: ["VOO", "VT", "VWO"])
            start_date: Date début (défaut: 5 ans)
            end_date: Date fin (défaut: aujourd'hui)
        
        Returns:
            Dictionnaire {ticker: DataFrame} avec résultats
            (uniquement tickers ayant réussi)
        """
        logger.info("\n" + "=" * 70)
        logger.info(f"📦 RÉCUPÉRATION PORTFOLIO : {len(tickers)} ETF")
        logger.info("=" * 70)
        
        results = {}
        success_count = 0
        
        for i, ticker in enumerate(tickers, 1):
            logger.info(f"\n[{i}/{len(tickers)}] Traitement: {ticker}")
            
            df = self.fetch_etf_data(ticker, start_date, end_date)
            
            if df is not None:
                results[ticker] = df
                success_count += 1
                logger.info(f"✅ {ticker}: Succès ({len(df)} jours de données)")
            else:
                logger.error(f"❌ {ticker}: Échec total")
        
        logger.info("\n" + "=" * 70)
        logger.info(f"📊 RÉSULTAT FINAL")
        logger.info("=" * 70)
        logger.info(f"✅ Succès: {success_count}/{len(tickers)} ETF ({success_count/len(tickers)*100:.1f}%)")
        logger.info(f"❌ Échecs: {len(tickers)-success_count}/{len(tickers)} ETF")
        logger.info("=" * 70)
        
        return results


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_fetcher(alpha_vantage_key: Optional[str] = None) -> DataFetcherReal:
    """
    Factory function pour créer instance DataFetcherReal
    
    Gère automatiquement la détection de la clé API depuis Streamlit secrets
    
    Args:
        alpha_vantage_key: Clé API (optionnel, auto-détectée si None)
    
    Returns:
        Instance DataFetcherReal configurée
    """
    # Auto-détection depuis Streamlit secrets
    if alpha_vantage_key is None:
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'alpha_vantage' in st.secrets:
                alpha_vantage_key = st.secrets['alpha_vantage']['api_key']
                logger.info("✅ Clé Alpha Vantage détectée depuis Streamlit secrets")
        except Exception as e:
            logger.debug(f"ℹ️  Streamlit secrets non disponibles: {e}")
    
    return DataFetcherReal(alpha_vantage_key=alpha_vantage_key)


# ============================================================================
# EXEMPLE D'UTILISATION
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║          DATA FETCHER REAL v2.2.0 - TEST MODULE             ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Configuration test
    TEST_TICKERS = ["VOO", "VT", "VWO"]
    ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")  # Variable environnement
    
    # Créer fetcher
    fetcher = get_fetcher(alpha_vantage_key=ALPHA_VANTAGE_KEY)
    
    # Test récupération
    print(f"\n🧪 Test récupération {len(TEST_TICKERS)} ETF...")
    results = fetcher.fetch_portfolio_data(
        tickers=TEST_TICKERS,
        start_date="2020-01-01"
    )
    
    # Afficher résultats
    print(f"\n📊 Résultats :")
    for ticker, df in results.items():
        print(f"  ✅ {ticker}: {len(df)} jours ({df.index.min().date()} → {df.index.max().date()})")
        print(f"     Dernier cours: ${df['Close'].iloc[-1]:.2f}")
    
    print("\n✅ Test terminé")
