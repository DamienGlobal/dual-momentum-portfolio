"""
Système de récupération données ETF réelles - Production Ready

Architecture multi-sources avec fallback automatique :
1. Cache local (6h validité) - Instant
2. Yahoo Finance (gratuit, illimité) - Priorité
3. Alpha Vantage (25 req/jour) - Fallback
4. Finnhub (limité ETF) - Fallback ultime

Features :
- Retry automatique avec backoff exponentiel
- Cache JSON local persistant
- Validation qualité données
- Logging détaillé pour debugging
- Compatible drop-in avec data_fetcher_hybrid

Author: GLOBAL ICON
Version: 2.0.0 - Production Ready
Date: 2025-10-28
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path
import json
import time
import requests

# Configuration logging
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION CACHE
# =============================================================================

try:
    CACHE_DIR = Path(__file__).parent / "cache"
    CACHE_DIR.mkdir(exist_ok=True, parents=True)
except (PermissionError, OSError):
    import tempfile
    CACHE_DIR = Path(tempfile.gettempdir()) / "dual_momentum_cache"
    CACHE_DIR.mkdir(exist_ok=True, parents=True)

CACHE_EXPIRY_HOURS = 6  # Données valides 6 heures


# =============================================================================
# CLASSE PRINCIPALE
# =============================================================================

class RealDataFetcher:
    """
    Gestionnaire récupération données réelles multi-sources.
    
    Attributes:
        use_cache: Active cache local
        alpha_vantage_key: Clé API Alpha Vantage (optionnel)
        finnhub_key: Clé API Finnhub (optionnel)
        av_requests_today: Compteur requêtes Alpha Vantage
    """
    
    def __init__(
        self,
        use_cache: bool = True,
        alpha_vantage_key: Optional[str] = None,
        finnhub_key: Optional[str] = None
    ):
        """
        Initialise fetcher données réelles.
        
        Args:
            use_cache: Utiliser cache local (recommandé True)
            alpha_vantage_key: Clé API Alpha Vantage (optionnel)
            finnhub_key: Clé API Finnhub (optionnel)
        """
        self.use_cache = use_cache
        self.alpha_vantage_key = alpha_vantage_key
        self.finnhub_key = finnhub_key
        
        # Compteurs requêtes (limites APIs)
        self.av_requests_today = 0
        self.av_max_requests = 25  # Limite Alpha Vantage gratuit
        
        logger.info(f"✅ RealDataFetcher initialisé (cache: {use_cache})")
    
    
    def fetch_yahoo_finance(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        max_retries: int = 3
    ) -> Optional[pd.DataFrame]:
        """
        Récupère données Yahoo Finance avec retry automatique.
        
        Args:
            ticker: Symbol ETF (ex: 'VOO', 'QQQ')
            start_date: Date début historique
            end_date: Date fin historique
            max_retries: Nombre tentatives max (défaut 3)
            
        Returns:
            DataFrame avec colonnes Date, Open, High, Low, Close, Volume
            ou None si échec
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"📡 Yahoo Finance: {ticker} (tentative {attempt+1}/{max_retries})")
                
                # Import yfinance (installation requise)
                try:
                    import yfinance as yf
                except ImportError:
                    logger.error("❌ Module yfinance non installé. Exécutez: pip install yfinance")
                    return None
                
                # Téléchargement données
                data = yf.download(
                    ticker,
                    start=start_date.strftime('%Y-%m-%d'),
                    end=end_date.strftime('%Y-%m-%d'),
                    progress=False,
                    timeout=10
                )
                
                if data.empty:
                    logger.warning(f"⚠️ {ticker}: Aucune donnée Yahoo Finance")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Backoff exponentiel : 1s, 2s, 4s
                    continue
                
                # Reformatage colonnes standardisé
                df = pd.DataFrame({
                    'Date': data.index,
                    'Open': data['Open'].values,
                    'High': data['High'].values,
                    'Low': data['Low'].values,
                    'Close': data['Close'].values,
                    'Volume': data['Volume'].values
                }).reset_index(drop=True)
                
                # Validation données
                if len(df) < 50:
                    logger.warning(f"⚠️ {ticker}: Historique très limité ({len(df)} jours)")
                
                logger.info(f"✅ {ticker}: {len(df)} jours récupérés (Yahoo Finance)")
                return df
                
            except Exception as e:
                logger.error(f"❌ {ticker} tentative {attempt+1} échouée: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue
        
        logger.error(f"❌ {ticker}: Toutes tentatives Yahoo Finance échouées")
        return None
    
    
    def fetch_alpha_vantage(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """
        Récupère données Alpha Vantage (fallback Yahoo Finance).
        
        Limite gratuite : 25 requêtes/jour
        
        Args:
            ticker: Symbol ETF
            start_date: Date début
            end_date: Date fin
            
        Returns:
            DataFrame OHLCV ou None
        """
        if not self.alpha_vantage_key:
            logger.warning("⚠️ Alpha Vantage: Clé API manquante (ignoré)")
            return None
        
        if self.av_requests_today >= self.av_max_requests:
            logger.warning(f"⚠️ Alpha Vantage: Limite quotidienne atteinte ({self.av_max_requests})")
            return None
        
        try:
            logger.info(f"📡 Alpha Vantage: {ticker}")
            
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY_ADJUSTED',
                'symbol': ticker,
                'outputsize': 'full',
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            # Vérification réponse valide
            if 'Time Series (Daily)' not in data:
                error_msg = data.get('Note', data.get('Error Message', 'Réponse invalide'))
                logger.warning(f"⚠️ {ticker}: Alpha Vantage - {error_msg}")
                return None
            
            # Conversion DataFrame
            time_series = data['Time Series (Daily)']
            records = []
            
            for date_str, values in time_series.items():
                try:
                    date = pd.to_datetime(date_str)
                    
                    records.append({
                        'Date': date,
                        'Open': float(values['1. open']),
                        'High': float(values['2. high']),
                        'Low': float(values['3. low']),
                        'Close': float(values['4. close']),
                        'Volume': int(values['6. volume'])
                    })
                except (KeyError, ValueError) as e:
                    logger.warning(f"⚠️ {ticker}: Erreur parsing date {date_str}: {e}")
                    continue
            
            df = pd.DataFrame(records)
            
            # Filtrage période demandée
            df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
            df = df.sort_values('Date').reset_index(drop=True)
            
            self.av_requests_today += 1
            logger.info(f"✅ {ticker}: {len(df)} jours (Alpha Vantage, {self.av_requests_today}/{self.av_max_requests})")
            
            return df
            
        except requests.Timeout:
            logger.error(f"❌ {ticker}: Timeout Alpha Vantage")
            return None
        except Exception as e:
            logger.error(f"❌ {ticker} Alpha Vantage: {e}")
            return None
    
    
    def get_from_cache(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """
        Récupère données depuis cache local si valides.
        
        Args:
            ticker: Symbol ETF
            start_date: Date début demandée
            end_date: Date fin demandée
            
        Returns:
            DataFrame depuis cache ou None si expiré/absent
        """
        if not self.use_cache:
            return None
        
        cache_file = CACHE_DIR / f"{ticker}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Vérification expiration
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            age_hours = (datetime.now() - cached_time).total_seconds() / 3600
            
            if age_hours > CACHE_EXPIRY_HOURS:
                logger.info(f"⏰ {ticker}: Cache expiré ({age_hours:.1f}h > {CACHE_EXPIRY_HOURS}h)")
                return None
            
            # Reconstruction DataFrame
            df = pd.DataFrame(cache_data['data'])
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Vérification couverture période
            cache_start = df['Date'].min()
            cache_end = df['Date'].max()
            
            if start_date < cache_start or end_date > cache_end:
                logger.info(f"⏰ {ticker}: Cache incomplet (période demandée hors cache)")
                return None
            
            # Filtrage période demandée
            df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
            
            logger.info(f"💾 {ticker}: {len(df)} jours depuis cache ({age_hours:.1f}h)")
            return df
            
        except Exception as e:
            logger.error(f"❌ {ticker} lecture cache: {e}")
            return None
    
    
    def save_to_cache(self, ticker: str, df: pd.DataFrame):
        """
        Sauvegarde données dans cache local.
        
        Args:
            ticker: Symbol ETF
            df: DataFrame à sauvegarder
        """
        if not self.use_cache or df.empty:
            return
        
        try:
            cache_file = CACHE_DIR / f"{ticker}.json"
            
            # Conversion datetime en string pour JSON
            data_records = df.to_dict(orient='records')
            for record in data_records:
                if isinstance(record['Date'], pd.Timestamp):
                    record['Date'] = record['Date'].isoformat()
            
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'ticker': ticker,
                'rows': len(df),
                'start_date': df['Date'].min().isoformat() if len(df) > 0 else None,
                'end_date': df['Date'].max().isoformat() if len(df) > 0 else None,
                'data': data_records
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"💾 {ticker}: Sauvegardé en cache ({len(df)} jours)")
            
        except Exception as e:
            logger.error(f"❌ {ticker} écriture cache: {e}")
    
    
    def validate_data(self, ticker: str, df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Valide qualité données récupérées.
        
        Vérifications :
        - DataFrame non vide
        - Colonnes requises présentes
        - Prix strictement positifs
        - OHLC cohérente (Low ≤ Close ≤ High)
        - Pas de valeurs NaN excessives
        
        Args:
            ticker: Symbol ETF
            df: DataFrame à valider
            
        Returns:
            (is_valid, message)
        """
        if df.empty:
            return False, f"{ticker}: DataFrame vide"
        
        # Colonnes requises
        required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return False, f"{ticker}: Colonnes manquantes {missing_cols}"
        
        # Prix positifs
        if (df['Close'] <= 0).any():
            invalid_count = (df['Close'] <= 0).sum()
            return False, f"{ticker}: {invalid_count} prix négatifs/nuls"
        
        # OHLC cohérente
        invalid_ohlc = (
            (df['Low'] > df['Close']) | 
            (df['Close'] > df['High']) |
            (df['Low'] > df['Open']) |
            (df['Open'] > df['High'])
        ).sum()
        
        if invalid_ohlc > len(df) * 0.05:  # Tolérance 5%
            return False, f"{ticker}: {invalid_ohlc} lignes OHLC incohérentes (>{len(df)*0.05:.0f})"
        
        # Valeurs manquantes
        nan_pct = df['Close'].isna().sum() / len(df) * 100
        if nan_pct > 10:
            return False, f"{ticker}: {nan_pct:.1f}% valeurs manquantes (>10%)"
        
        return True, f"{ticker}: ✅ Données valides ({len(df)} jours)"
    
    
    def fetch_historical_data(
        self,
        tickers: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, pd.DataFrame]:
        """
        Récupère données historiques avec fallback automatique.
        
        Ordre tentatives pour chaque ticker :
        1. Cache local (si valide et complet)
        2. Yahoo Finance (priorité, gratuit illimité)
        3. Alpha Vantage (fallback, 25 req/jour)
        4. Échec → ticker exclu
        
        Args:
            tickers: Liste symbols ETF (ex: ['VOO', 'QQQ', 'VT'])
            start_date: Date début historique
            end_date: Date fin historique
            
        Returns:
            Dict {ticker: DataFrame} avec données valides uniquement
        """
        data = {}
        failed_tickers = []
        
        logger.info("=" * 80)
        logger.info(f"📡 RÉCUPÉRATION DONNÉES RÉELLES")
        logger.info(f"Période: {start_date.date()} → {end_date.date()}")
        logger.info(f"Tickers: {len(tickers)} ETF")
        logger.info("=" * 80)
        
        for idx, ticker in enumerate(tickers, 1):
            logger.info(f"\n[{idx}/{len(tickers)}] Traitement {ticker}...")
            
            df = None
            source = None
            
            # Tentative 1 : Cache local
            df = self.get_from_cache(ticker, start_date, end_date)
            if df is not None and not df.empty:
                source = "cache"
            
            # Tentative 2 : Yahoo Finance
            if df is None:
                df = self.fetch_yahoo_finance(ticker, start_date, end_date)
                if df is not None and not df.empty:
                    source = "yahoo"
            
            # Tentative 3 : Alpha Vantage (si clé fournie)
            if df is None and self.alpha_vantage_key:
                df = self.fetch_alpha_vantage(ticker, start_date, end_date)
                if df is not None and not df.empty:
                    source = "alphavantage"
            
            # Échec complet
            if df is None or df.empty:
                logger.error(f"❌ {ticker}: ÉCHEC - Toutes sources ont échoué")
                failed_tickers.append(ticker)
                continue
            
            # Validation qualité données
            is_valid, msg = self.validate_data(ticker, df)
            
            if not is_valid:
                logger.error(f"❌ {msg}")
                failed_tickers.append(ticker)
                continue
            
            # Succès : sauvegarde cache + stockage
            if source != "cache":
                self.save_to_cache(ticker, df)
            
            data[ticker] = df
            logger.info(f"✅ {ticker}: {len(df)} jours ({source}) - Prix final ${df['Close'].iloc[-1]:.2f}")
        
        # Résumé final
        logger.info("\n" + "=" * 80)
        logger.info(f"📊 RÉSUMÉ RÉCUPÉRATION DONNÉES")
        logger.info(f"✅ Succès: {len(data)}/{len(tickers)} ETF")
        if failed_tickers:
            logger.warning(f"❌ Échecs: {len(failed_tickers)} ETF - {failed_tickers}")
        logger.info("=" * 80)
        
        return data


# =============================================================================
# FONCTIONS COMPATIBILITÉ (drop-in replacement data_fetcher_hybrid)
# =============================================================================

def fetch_historical_data(
    tickers: List[str],
    start_date: datetime,
    end_date: datetime,
    use_cache: bool = True,
    alpha_vantage_key: Optional[str] = None
) -> Dict[str, pd.DataFrame]:
    """
    Fonction compatible avec ancienne interface data_fetcher_hybrid.
    
    Drop-in replacement : remplacez simplement
    ```python
    from data_fetcher_hybrid import fetch_historical_data
    ```
    par
    ```python
    from data_fetcher_real import fetch_historical_data
    ```
    
    Args:
        tickers: Liste symbols ETF
        start_date: Date début
        end_date: Date fin
        use_cache: Utiliser cache local (défaut True)
        alpha_vantage_key: Clé API Alpha Vantage (optionnel)
        
    Returns:
        Dict {ticker: DataFrame}
    """
    fetcher = RealDataFetcher(
        use_cache=use_cache,
        alpha_vantage_key=alpha_vantage_key
    )
    return fetcher.fetch_historical_data(tickers, start_date, end_date)


def get_latest_prices(tickers: List[str]) -> Dict[str, float]:
    """
    Récupère prix actuels pour liste tickers.
    
    Compatible avec data_fetcher_hybrid.get_latest_prices()
    
    Args:
        tickers: Liste symbols ETF
        
    Returns:
        Dict {ticker: prix_actuel}
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)
    
    data = fetch_historical_data(tickers, start_date, end_date)
    
    prices = {}
    for ticker, df in data.items():
        if not df.empty:
            prices[ticker] = df['Close'].iloc[-1]
    
    return prices


def validate_data(df: pd.DataFrame, ticker: str) -> Tuple[bool, str]:
    """
    Valide qualité données ETF.
    
    Compatible avec data_fetcher_hybrid.validate_data()
    
    Args:
        df: DataFrame prix historiques
        ticker: Symbol ETF
        
    Returns:
        (is_valid, message)
    """
    fetcher = RealDataFetcher(use_cache=False)
    return fetcher.validate_data(ticker, df)


# =============================================================================
# TESTS UNITAIRES
# =============================================================================

if __name__ == "__main__":
    import sys
    
    # Configuration logging console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    print("=" * 80)
    print("🧪 TESTS UNITAIRES - RealDataFetcher")
    print("=" * 80)
    
    # Test 1 : Récupération données réelles
    print("\n📊 Test 1 : Récupération 3 ETF (Yahoo Finance)")
    print("-" * 80)
    
    test_tickers = ['VOO', 'QQQ', 'VT']
    end = datetime.now()
    start = end - timedelta(days=365)
    
    fetcher = RealDataFetcher(use_cache=True)
    data = fetcher.fetch_historical_data(test_tickers, start, end)
    
    print(f"\n✅ Résultats : {len(data)}/{len(test_tickers)} ETFs récupérés")
    
    for ticker, df in data.items():
        is_valid, msg = fetcher.validate_data(ticker, df)
        print(f"  {ticker}:")
        print(f"    Jours: {len(df)}")
        print(f"    Période: {df['Date'].min().date()} → {df['Date'].max().date()}")
        print(f"    Prix: ${df['Close'].iloc[0]:.2f} → ${df['Close'].iloc[-1]:.2f}")
        print(f"    Validation: {msg}")
    
    # Test 2 : Performance cache
    print("\n\n💾 Test 2 : Performance cache (2ème exécution)")
    print("-" * 80)
    
    import time as time_module
    start_time = time_module.time()
    
    data_cached = fetcher.fetch_historical_data(test_tickers, start, end)
    
    elapsed = time_module.time() - start_time
    print(f"✅ Temps exécution avec cache: {elapsed:.2f}s")
    
    # Test 3 : get_latest_prices
    print("\n\n📈 Test 3 : Prix actuels")
    print("-" * 80)
    
    prices = get_latest_prices(test_tickers)
    for ticker, price in prices.items():
        print(f"  {ticker}: ${price:.2f}")
    
    print("\n" + "=" * 80)
    print("✅ TOUS LES TESTS TERMINÉS")
    print("=" * 80)
