"""
Module de récupération de données réelles depuis Yahoo Finance et Alpha Vantage
Version: 2.1.0 - Compatible yfinance 0.2.48
"""

import logging
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import yfinance as yf
import requests

# Configuration logging
logger = logging.getLogger(__name__)

# Configuration cache
CACHE_DIR = "/tmp/etf_cache"
CACHE_DURATION_HOURS = 6


class RealDataFetcher:
    """
    Classe pour récupérer des données réelles depuis Yahoo Finance et Alpha Vantage
    avec système de cache et retry automatique
    """
    
    def __init__(self, alpha_vantage_key: Optional[str] = None, use_cache: bool = True):
        """
        Initialise le fetcher avec clé API optionnelle et cache
        
        Args:
            alpha_vantage_key: Clé API Alpha Vantage (fallback)
            use_cache: Activer le cache local (défaut: True)
        """
        self.alpha_vantage_key = alpha_vantage_key
        self.use_cache = use_cache
        
        # Créer répertoire cache si nécessaire
        if self.use_cache:
            os.makedirs(CACHE_DIR, exist_ok=True)
        
        logger.info(f"✅ RealDataFetcher initialisé (cache: {self.use_cache})")
    
    def get_cache_path(self, ticker: str, start_date: datetime, end_date: datetime) -> str:
        """Génère le chemin du fichier cache pour un ticker et une période"""
        cache_key = f"{ticker}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"
        return os.path.join(CACHE_DIR, cache_key)
    
    def load_from_cache(self, ticker: str, start_date: datetime, end_date: datetime) -> Optional[pd.DataFrame]:
        """
        Charge les données depuis le cache si disponibles et valides
        
        Returns:
            DataFrame ou None si cache inexistant/expiré
        """
        if not self.use_cache:
            return None
        
        cache_path = self.get_cache_path(ticker, start_date, end_date)
        
        try:
            if not os.path.exists(cache_path):
                return None
            
            # Vérifier âge du cache
            cache_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_path))
            if cache_age > timedelta(hours=CACHE_DURATION_HOURS):
                logger.debug(f"💾 {ticker}: Cache expiré ({cache_age.total_seconds()/3600:.1f}h)")
                os.remove(cache_path)
                return None
            
            # Charger données
            with open(cache_path, 'r') as f:
                data_dict = json.load(f)
            
            df = pd.DataFrame(data_dict['data'])
            df.index = pd.to_datetime(df.index)
            
            logger.info(f"💾 {ticker}: {len(df)} jours chargés depuis cache")
            return df
            
        except Exception as e:
            logger.warning(f"⚠️ {ticker}: Erreur lecture cache: {str(e)}")
            return None
    
    def save_to_cache(self, ticker: str, start_date: datetime, end_date: datetime, data: pd.DataFrame):
        """Sauvegarde les données dans le cache"""
        if not self.use_cache or data is None or data.empty:
            return
        
        cache_path = self.get_cache_path(ticker, start_date, end_date)
        
        try:
            data_dict = {
                'ticker': ticker,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'data': data.reset_index().to_dict(orient='list')
            }
            
            with open(cache_path, 'w') as f:
                json.dump(data_dict, f)
            
            logger.debug(f"💾 {ticker}: Données sauvegardées en cache")
            
        except Exception as e:
            logger.warning(f"⚠️ {ticker}: Erreur sauvegarde cache: {str(e)}")
    
    def fetch_yahoo_finance(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        max_retries: int = 3
    ) -> Optional[pd.DataFrame]:
        """
        Récupère les données depuis Yahoo Finance avec retry et validation structure
        
        Args:
            ticker: Symbole ETF (ex: 'VT')
            start_date: Date début
            end_date: Date fin
            max_retries: Nombre de tentatives (défaut: 3)
        
        Returns:
            DataFrame avec colonnes ['close', 'volume', ...] ou None
        """
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"📡 Yahoo Finance: {ticker} (tentative {attempt}/{max_retries})")
                
                # Téléchargement données (compatible yfinance 0.2.48)
                data = yf.download(
                    ticker,
                    start=start_date.strftime('%Y-%m-%d'),
                    end=end_date.strftime('%Y-%m-%d'),
                    progress=False,
                    auto_adjust=True,
                    timeout=10
                )
                
                # Cas 1 : Données vides
                if data is None or data.empty:
                    logger.warning(f"⚠️ {ticker}: Aucune donnée retournée (tentative {attempt})")
                    if attempt < max_retries:
                        time.sleep(2 ** attempt)
                        continue
                    return None
                
                # Cas 2 : MultiIndex DataFrame (yfinance >=0.2.50 - sécurité)
                if isinstance(data.columns, pd.MultiIndex):
                    logger.debug(f"📋 {ticker}: Conversion MultiIndex → Simple DataFrame")
                    data.columns = data.columns.droplevel(0)
                
                # Cas 3 : Normalisation noms colonnes
                data.columns = [str(col).lower().replace(' ', '_') for col in data.columns]
                
                # Validation colonne 'close' obligatoire
                if 'close' not in data.columns and 'adj_close' not in data.columns:
                    raise ValueError(
                        f"Colonne 'close' manquante. Colonnes: {list(data.columns)}"
                    )
                
                # Renommer 'adj_close' → 'close' si nécessaire
                if 'adj_close' in data.columns and 'close' not in data.columns:
                    data = data.rename(columns={'adj_close': 'close'})
                
                # Nettoyage NaN
                data = data.dropna(subset=['close'])
                
                if data.empty:
                    logger.warning(f"⚠️ {ticker}: Données vides après nettoyage")
                    return None
                
                # Succès
                nb_days = len(data)
                logger.info(f"✅ {ticker}: {nb_days} jours récupérés (Yahoo Finance)")
                return data
                
            except Exception as e:
                logger.error(f"❌ {ticker} tentative {attempt} échouée: {str(e)}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"❌ {ticker}: Toutes tentatives Yahoo Finance échouées")
                    return None
        
        return None
    
    def fetch_alpha_vantage(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """
        Récupère les données depuis Alpha Vantage (fallback)
        
        Args:
            ticker: Symbole ETF
            start_date: Date début
            end_date: Date fin
        
        Returns:
            DataFrame ou None si échec
        """
        if not self.alpha_vantage_key:
            logger.debug(f"⚠️ {ticker}: Alpha Vantage désactivé (pas de clé API)")
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
            response.raise_for_status()
            
            data_json = response.json()
            
            # Vérifier erreurs API
            if 'Error Message' in data_json:
                logger.error(f"❌ {ticker}: {data_json['Error Message']}")
                return None
            
            if 'Note' in data_json:
                logger.warning(f"⚠️ {ticker}: Limite API atteinte")
                return None
            
            # Parser données
            time_series = data_json.get('Time Series (Daily)', {})
            if not time_series:
                logger.error(f"❌ {ticker}: Pas de données dans la réponse")
                return None
            
            # Convertir en DataFrame
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Renommer colonnes
            df.columns = [col.split('. ')[1].lower().replace(' ', '_') for col in df.columns]
            df = df.rename(columns={'adjusted_close': 'close'})
            
            # Convertir en float
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Filtrer période
            df = df[(df.index >= start_date) & (df.index <= end_date)]
            
            if df.empty:
                logger.warning(f"⚠️ {ticker}: Aucune donnée dans la période")
                return None
            
            logger.info(f"✅ {ticker}: {len(df)} jours récupérés (Alpha Vantage)")
            return df
            
        except Exception as e:
            logger.error(f"❌ {ticker}: Erreur Alpha Vantage: {str(e)}")
            return None
    
    def fetch_single_ticker(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """
        Récupère les données pour un ticker avec fallback automatique
        
        Ordre des sources :
        1. Cache local (si activé)
        2. Yahoo Finance (source principale)
        3. Alpha Vantage (fallback si clé API fournie)
        
        Args:
            ticker: Symbole ETF
            start_date: Date début
            end_date: Date fin
        
        Returns:
            DataFrame ou None si toutes sources échouent
        """
        # Tentative 1 : Cache
        cached_data = self.load_from_cache(ticker, start_date, end_date)
        if cached_data is not None:
            return cached_data
        
        # Tentative 2 : Yahoo Finance
        data = self.fetch_yahoo_finance(ticker, start_date, end_date)
        if data is not None:
            self.save_to_cache(ticker, start_date, end_date, data)
            return data
        
        # Tentative 3 : Alpha Vantage
        logger.warning(f"⚠️ {ticker}: Yahoo Finance échoué, tentative Alpha Vantage...")
        data = self.fetch_alpha_vantage(ticker, start_date, end_date)
        if data is not None:
            self.save_to_cache(ticker, start_date, end_date, data)
            return data
        
        logger.error(f"❌ {ticker}: ÉCHEC - Toutes sources ont échoué")
        return None
    
    def fetch_multiple_tickers(
        self,
        tickers: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, pd.DataFrame]:
        """
        Récupère les données pour plusieurs tickers
        
        Args:
            tickers: Liste symboles ETF
            start_date: Date début
            end_date: Date fin
        
        Returns:
            Dictionnaire {ticker: DataFrame} (tickers échoués exclus)
        """
        logger.info("="*80)
        logger.info("📡 RÉCUPÉRATION DONNÉES RÉELLES")
        logger.info(f"Période: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
        logger.info(f"Tickers: {len(tickers)} ETF")
        logger.info("="*80)
        
        results = {}
        failed_tickers = []
        
        for i, ticker in enumerate(tickers, 1):
            logger.info(f"\n[{i}/{len(tickers)}] Traitement {ticker}...")
            
            data = self.fetch_single_ticker(ticker, start_date, end_date)
            
            if data is not None:
                results[ticker] = data
            else:
                failed_tickers.append(ticker)
            
            # Rate limiting (éviter ban Yahoo Finance)
            if i < len(tickers):
                time.sleep(0.5)
        
        # Résumé
        logger.info("\n" + "="*80)
        logger.info("📊 RÉSUMÉ RÉCUPÉRATION DONNÉES")
        logger.info(f"✅ Succès: {len(results)}/{len(tickers)} ETF")
        if failed_tickers:
            logger.warning(f"❌ Échecs: {len(failed_tickers)} ETF - {failed_tickers}")
        logger.info("="*80)
        
        return results


# ============================================================================
# FONCTIONS PUBLIQUES (Interface avec portfolio_engine.py)
# ============================================================================

def fetch_historical_data(
    tickers: List[str],
    start_date: datetime,
    end_date: datetime,
    alpha_vantage_key: Optional[str] = None,
    use_cache: bool = True
) -> Dict[str, pd.DataFrame]:
    """
    Point d'entrée principal pour récupérer des données historiques réelles
    
    Args:
        tickers: Liste symboles ETF (ex: ['VT', 'VOO', 'VWO'])
        start_date: Date début période
        end_date: Date fin période
        alpha_vantage_key: Clé API Alpha Vantage (optionnel, fallback)
        use_cache: Utiliser cache local (défaut: True)
    
    Returns:
        Dictionnaire {ticker: DataFrame} avec colonnes ['close', 'volume', ...]
    
    Exemple:
        >>> data = fetch_historical_data(
        ...     tickers=['VT', 'VOO'],
        ...     start_date=datetime(2024, 1, 1),
        ...     end_date=datetime(2024, 12, 31)
        ... )
        >>> print(data['VT'].head())
    """
    fetcher = RealDataFetcher(
        alpha_vantage_key=alpha_vantage_key,
        use_cache=use_cache
    )
    
    return fetcher.fetch_multiple_tickers(tickers, start_date, end_date)


def get_latest_price(ticker: str) -> Optional[float]:
    """
    Récupère le dernier prix disponible pour un ticker
    
    Args:
        ticker: Symbole ETF
    
    Returns:
        Prix de clôture le plus récent ou None
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        fetcher = RealDataFetcher(use_cache=False)
        data = fetcher.fetch_single_ticker(ticker, start_date, end_date)
        
        if data is not None and not data.empty:
            return float(data['close'].iloc[-1])
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération prix {ticker}: {str(e)}")
        return None


def validate_ticker(ticker: str) -> bool:
    """
    Vérifie qu'un ticker existe et retourne des données
    
    Args:
        ticker: Symbole ETF à valider
    
    Returns:
        True si ticker valide, False sinon
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        fetcher = RealDataFetcher(use_cache=False)
        data = fetcher.fetch_single_ticker(ticker, start_date, end_date)
        
        return data is not None and not data.empty
        
    except Exception:
        return False


# ============================================================================
# TESTS UNITAIRES
# ============================================================================

if __name__ == "__main__":
    # Configuration logging pour tests
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    print("🧪 Tests data_fetcher_real.py\n")
    
    # Test 1 : Ticker unique
    print("Test 1: Récupération ticker unique (VOO)...")
    end = datetime.now()
    start = end - timedelta(days=365)
    
    data = fetch_historical_data(['VOO'], start, end)
    
    if 'VOO' in data:
        print(f"✅ VOO: {len(data['VOO'])} jours récupérés")
        print(f"   Colonnes: {list(data['VOO'].columns)}")
        print(f"   Prix actuel: ${data['VOO']['close'].iloc[-1]:.2f}")
    else:
        print("❌ Échec récupération VOO")
    
    # Test 2 : Prix en temps réel
    print("\nTest 2: Prix en temps réel (VT)...")
    price = get_latest_price('VT')
    if price:
        print(f"✅ VT: ${price:.2f}")
    else:
        print("❌ Échec récupération prix VT")
    
    # Test 3 : Validation ticker
    print("\nTest 3: Validation tickers...")
    valid = validate_ticker('VOO')
    invalid = validate_ticker('INVALID_TICKER_123')
    print(f"✅ VOO valide: {valid}")
    print(f"✅ INVALID_TICKER_123 invalide: {not invalid}")
    
    print("\n🎉 Tests terminés!")
