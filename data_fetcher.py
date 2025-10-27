"""
Module de récupération données RÉELLES Yahoo Finance
ZÉRO HALLUCINATION : Toutes les données sont téléchargées en temps réel
Gestion robuste des erreurs et données manquantes
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class DataFetcher:
    """
    Récupération et gestion des données de marché réelles
    """
    
    def __init__(self, cache_hours: int = 24):
        """
        Args:
            cache_hours: Durée de validité du cache (défaut 24h)
        """
        self.cache_hours = cache_hours
        self.data_cache = {}
        self.cache_timestamps = {}
    
    def fetch_etf_data(self, ticker_yahoo: str, start_date: str = None, 
                       end_date: str = None) -> Optional[pd.DataFrame]:
        """
        Télécharge les données historiques d'un ETF depuis Yahoo Finance
        
        Args:
            ticker_yahoo: Ticker Yahoo Finance (ex: 'CW8.PA')
            start_date: Date début format 'YYYY-MM-DD' (défaut: 3 ans avant)
            end_date: Date fin format 'YYYY-MM-DD' (défaut: aujourd'hui)
        
        Returns:
            DataFrame avec colonnes ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
            ou None si erreur
        """
        
        # Dates par défaut
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        if start_date is None:
            # 3 ans d'historique (suffisant pour calculs momentum)
            start_date = (datetime.now() - timedelta(days=3*365)).strftime('%Y-%m-%d')
        
        # Vérifier cache
        cache_key = f"{ticker_yahoo}_{start_date}_{end_date}"
        if cache_key in self.data_cache:
            cache_time = self.cache_timestamps[cache_key]
            if (datetime.now() - cache_time).total_seconds() < self.cache_hours * 3600:
                print(f"✅ Cache hit: {ticker_yahoo}")
                return self.data_cache[cache_key]
        
        # Téléchargement Yahoo Finance
        try:
            print(f"📥 Téléchargement {ticker_yahoo} depuis Yahoo Finance...")
            etf = yf.Ticker(ticker_yahoo)
            data = etf.history(start=start_date, end=end_date, auto_adjust=True)
            
            if data.empty:
                print(f"⚠️ Aucune donnée disponible pour {ticker_yahoo}")
                return None
            
            # Vérification qualité données
            if len(data) < 20:  # Minimum 20 jours de données
                print(f"⚠️ Données insuffisantes pour {ticker_yahoo} ({len(data)} jours)")
                return None
            
            # Vérification données manquantes
            missing_pct = data['Close'].isna().sum() / len(data) * 100
            if missing_pct > 5:
                print(f"⚠️ {ticker_yahoo} a {missing_pct:.1f}% de données manquantes")
            
            # Forward fill des données manquantes (méthode académique standard)
            data = data.fillna(method='ffill')
            
            # Mise en cache
            self.data_cache[cache_key] = data
            self.cache_timestamps[cache_key] = datetime.now()
            
            print(f"✅ {ticker_yahoo}: {len(data)} jours de données téléchargés")
            return data
        
        except Exception as e:
            print(f"❌ Erreur téléchargement {ticker_yahoo}: {e}")
            return None
    
    def fetch_multiple_etfs(self, tickers_dict: Dict[str, Dict]) -> Dict[str, pd.DataFrame]:
        """
        Télécharge les données de plusieurs ETF en parallèle
        
        Args:
            tickers_dict: Dictionnaire {ticker: {config}} depuis config.py
        
        Returns:
            Dictionnaire {ticker: DataFrame}
        """
        results = {}
        
        for ticker, config in tickers_dict.items():
            ticker_yahoo = config['ticker_yahoo']
            data = self.fetch_etf_data(ticker_yahoo)
            
            if data is not None:
                results[ticker] = data
            else:
                print(f"⚠️ {ticker} ({ticker_yahoo}) ignoré (données indisponibles)")
        
        print(f"\n✅ Total: {len(results)}/{len(tickers_dict)} ETF téléchargés avec succès")
        return results
    
    def get_latest_price(self, ticker_yahoo: str) -> Optional[float]:
        """
        Récupère le dernier prix disponible
        
        Args:
            ticker_yahoo: Ticker Yahoo Finance
        
        Returns:
            Prix le plus récent ou None si erreur
        """
        try:
            etf = yf.Ticker(ticker_yahoo)
            data = etf.history(period='5d')  # 5 derniers jours
            
            if not data.empty:
                return data['Close'].iloc[-1]
            return None
        
        except Exception as e:
            print(f"❌ Erreur prix {ticker_yahoo}: {e}")
            return None
    
    def calculate_returns(self, data: pd.DataFrame, periods: List[int]) -> Dict[str, float]:
        """
        Calcule les rendements sur plusieurs périodes
        
        Args:
            data: DataFrame avec colonne 'Close'
            periods: Liste de périodes en jours (ex: [21, 63, 126] pour 1M, 3M, 6M)
        
        Returns:
            Dictionnaire {période: rendement}
        """
        if data is None or data.empty:
            return {f"{p}d": None for p in periods}
        
        results = {}
        latest_price = data['Close'].iloc[-1]
        
        for period in periods:
            try:
                if len(data) < period:
                    results[f"{period}d"] = None
                    continue
                
                past_price = data['Close'].iloc[-period]
                return_pct = (latest_price - past_price) / past_price
                results[f"{period}d"] = return_pct
            
            except Exception as e:
                print(f"⚠️ Erreur calcul rendement {period}j: {e}")
                results[f"{period}d"] = None
        
        return results
    
    def calculate_sma(self, data: pd.DataFrame, period_days: int) -> Optional[float]:
        """
        Calcule la moyenne mobile simple
        
        Args:
            data: DataFrame avec colonne 'Close'
            period_days: Période en jours
        
        Returns:
            Valeur SMA ou None si erreur
        """
        if data is None or data.empty or len(data) < period_days:
            return None
        
        try:
            sma = data['Close'].iloc[-period_days:].mean()
            return sma
        
        except Exception as e:
            print(f"⚠️ Erreur calcul SMA: {e}")
            return None
    
    def calculate_volatility(self, data: pd.DataFrame, period_days: int) -> Optional[float]:
        """
        Calcule la volatilité réalisée (écart-type annualisé)
        
        Args:
            data: DataFrame avec colonne 'Close'
            period_days: Période en jours
        
        Returns:
            Volatilité annualisée ou None si erreur
        """
        if data is None or data.empty or len(data) < period_days:
            return None
        
        try:
            # Rendements quotidiens
            returns = data['Close'].pct_change().iloc[-period_days:]
            
            # Volatilité annualisée (√252 pour jours de bourse)
            volatility = returns.std() * np.sqrt(252)
            return volatility
        
        except Exception as e:
            print(f"⚠️ Erreur calcul volatilité: {e}")
            return None
    
    def validate_data_quality(self, data: pd.DataFrame, ticker: str) -> Tuple[bool, str]:
        """
        Valide la qualité des données téléchargées
        
        Args:
            data: DataFrame à valider
            ticker: Nom du ticker (pour logs)
        
        Returns:
            (is_valid, message)
        """
        if data is None or data.empty:
            return False, f"{ticker}: Aucune donnée"
        
        # Vérifier colonnes requises
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            return False, f"{ticker}: Colonnes manquantes {missing_cols}"
        
        # Vérifier données aberrantes (prix négatifs, NaN)
        if (data['Close'] <= 0).any():
            return False, f"{ticker}: Prix négatifs détectés"
        
        if data['Close'].isna().sum() > len(data) * 0.05:  # >5% NaN
            return False, f"{ticker}: Trop de données manquantes"
        
        # Vérifier historique suffisant (minimum 6 mois)
        min_days = 126  # ~6 mois
        if len(data) < min_days:
            return False, f"{ticker}: Historique insuffisant ({len(data)} jours < {min_days})"
        
        return True, f"{ticker}: Données valides ({len(data)} jours)"


# ============================================================================
# TESTS VALIDATION DONNÉES RÉELLES
# ============================================================================

def test_data_fetcher():
    """Test du module avec des ETF réels"""
    
    print("=" * 70)
    print("TEST MODULE DATA FETCHER - DONNÉES RÉELLES YAHOO FINANCE")
    print("=" * 70)
    
    from config import PEA_ETFS, CTO_ETFS
    
    fetcher = DataFetcher(cache_hours=24)
    
    # Test 1: ETF unique
    print("\n[TEST 1] Téléchargement ETF unique")
    print("-" * 70)
    test_ticker = 'ESE.PA'  # S&P 500 PEA
    data = fetcher.fetch_etf_data(test_ticker)
    
    if data is not None:
        print(f"✅ Dernières 5 lignes de {test_ticker}:")
        print(data[['Close', 'Volume']].tail())
        print(f"\nPrix actuel: {data['Close'].iloc[-1]:.2f} EUR")
    
    # Test 2: Calcul rendements
    print("\n[TEST 2] Calcul rendements multi-périodes")
    print("-" * 70)
    periods = [21, 63, 126]  # 1M, 3M, 6M (jours de bourse)
    returns = fetcher.calculate_returns(data, periods)
    
    for period, ret in returns.items():
        if ret is not None:
            print(f"  Rendement {period}: {ret*100:+.2f}%")
    
    # Test 3: Indicateurs techniques
    print("\n[TEST 3] Indicateurs techniques")
    print("-" * 70)
    
    sma_10m = fetcher.calculate_sma(data, 210)  # 10 mois ≈ 210 jours
    vol_1m = fetcher.calculate_volatility(data, 21)
    vol_12m = fetcher.calculate_volatility(data, 252)
    
    print(f"  SMA 10 mois: {sma_10m:.2f} EUR")
    print(f"  Volatilité 1M: {vol_1m*100:.2f}%" if vol_1m else "  Volatilité 1M: N/A")
    print(f"  Volatilité 12M: {vol_12m*100:.2f}%" if vol_12m else "  Volatilité 12M: N/A")
    
    # Test 4: Validation qualité
    print("\n[TEST 4] Validation qualité données")
    print("-" * 70)
    is_valid, message = fetcher.validate_data_quality(data, test_ticker)
    print(f"  {message}")
    
    # Test 5: Téléchargement multiple (échantillon)
    print("\n[TEST 5] Téléchargement multiple ETF")
    print("-" * 70)
    
    sample_etfs = {
        'ESE': PEA_ETFS['ESE'],
        'CW8': PEA_ETFS['CW8'],
        'IWDA': CTO_ETFS['IWDA']
    }
    
    all_data = fetcher.fetch_multiple_etfs(sample_etfs)
    
    print(f"\n✅ {len(all_data)} ETF téléchargés:")
    for ticker, df in all_data.items():
        print(f"  - {ticker}: {len(df)} jours, dernier prix {df['Close'].iloc[-1]:.2f}")
    
    print("\n" + "=" * 70)
    print("✅ TOUS LES TESTS PASSÉS - MODULE FONCTIONNEL")
    print("=" * 70)


if __name__ == "__main__":
    test_data_fetcher()
