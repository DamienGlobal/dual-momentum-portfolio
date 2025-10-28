"""
Moteur orchestrateur du portefeuille Dual Momentum.

Pipeline :
1. Récupération données historiques multi-sources
2. Nettoyage et validation données
3. Calcul scores momentum pondérés
4. Application filtres protection (absolu, tendance, volatilité)
5. Génération signaux investissement

Formule académique (Antonacci GEM 2014) :
Score = 12% × R₁ₘ + 40% × R₃ₘ + 48% × R₆ₘ

Filtres :
- Absolu : Score > 0 (protection bear market)
- Tendance : Prix > SMA 10 mois (confirmation tendance)
- Volatilité : Vol 1M < 1.5× Vol 12M (éviter actifs erratiques)

Version: 2.0.0 - Production Ready (Phase 2 - Real Data)
Author: GLOBAL ICON
Date: 2025-10-28
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

# =============================================================================
# IMPORTS MODULES INTERNES - DONNÉES AVEC FALLBACK AUTOMATIQUE
# =============================================================================

# Import données avec fallback automatique MVP → Production
try:
    from data_fetcher_real import fetch_historical_data, get_latest_prices, validate_data
    DATA_SOURCE = "REAL"
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("✅ MODE PRODUCTION : Données réelles activées")
    logger.info("   Source : Yahoo Finance (gratuit, illimité)")
    logger.info("   Fallback : Alpha Vantage (optionnel, 25 req/jour)")
    logger.info("   Cache : Local JSON (6h validité)")
    logger.info("=" * 80)
except ImportError as e:
    from data_fetcher_hybrid import fetch_historical_data, get_latest_prices, validate_data
    DATA_SOURCE = "SIMULATED"
    logger = logging.getLogger(__name__)
    logger.warning("=" * 80)
    logger.warning("⚠️  MODE MVP : Données simulées académiques")
    logger.warning(f"   Raison : data_fetcher_real non disponible ({e})")
    logger.warning("   Impact : Paramètres statistiques réalistes mais prix simulés")
    logger.warning("   Usage : Formation, démonstration, validation stratégie")
    logger.warning("=" * 80)

# Imports autres modules internes
from momentum_engine import MomentumEngine
from config_working import PEA_ETFS, CTO_ETFS

# Configuration logging (si pas déjà configuré)
if not logger.hasHandlers():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


# =============================================================================
# FONCTION UTILITAIRE - DÉTECTION MODE DONNÉES
# =============================================================================

def get_data_source_info() -> Dict[str, str]:
    """
    Retourne informations source données actuelle.
    
    Utilisé par app.py pour afficher indicateur sidebar.
    
    Returns:
        Dict avec clés : source, description, status, icon, color
    """
    if DATA_SOURCE == "REAL":
        return {
            'source': 'REAL',
            'description': 'Données réelles Yahoo Finance',
            'status': 'production',
            'icon': '📡',
            'color': 'success'
        }
    else:
        return {
            'source': 'SIMULATED',
            'description': 'Données simulées académiques',
            'status': 'mvp',
            'icon': '🧪',
            'color': 'warning'
        }


# =============================================================================
# CLASSE PRINCIPALE - DUAL MOMENTUM PORTFOLIO
# =============================================================================

class DualMomentumPortfolio:
    """
    Gestionnaire de portefeuille Dual Momentum académique.
    
    Attributes:
        pea_etfs: Liste tickers ETF éligibles PEA
        cto_etfs: Liste tickers ETF compte-titres ordinaire
        lookback_period: Période analyse momentum (défaut 12 mois)
        momentum_engine: Instance moteur calculs momentum
        data_source: Source données actuelle ('REAL' ou 'SIMULATED')
    """
    
    def __init__(
        self,
        pea_etfs: Optional[List[str]] = None,
        cto_etfs: Optional[List[str]] = None,
        lookback_period: int = 12
    ):
        """
        Initialise gestionnaire portefeuille.
        
        Args:
            pea_etfs: Tickers ETF PEA (défaut config_working.PEA_ETFS)
            cto_etfs: Tickers ETF CTO (défaut config_working.CTO_ETFS)
            lookback_period: Mois historique analyse (défaut 12)
        """
        self.pea_etfs = pea_etfs or [etf['ticker'] for etf in PEA_ETFS]
        self.cto_etfs = cto_etfs or [etf['ticker'] for etf in CTO_ETFS]
        self.lookback_period = lookback_period
        self.momentum_engine = MomentumEngine()
        self.data_source = DATA_SOURCE  # Exposition info source données
        
        logger.info("=" * 80)
        logger.info("🚀 INITIALISATION DUAL MOMENTUM PORTFOLIO")
        logger.info("=" * 80)
        logger.info(f"Portfolio PEA : {len(self.pea_etfs)} ETF")
        logger.info(f"Portfolio CTO : {len(self.cto_etfs)} ETF")
        logger.info(f"Total univers : {len(self.pea_etfs) + len(self.cto_etfs)} ETF")
        logger.info(f"Lookback      : {lookback_period} mois")
        logger.info(f"Source données: {self.data_source}")
        logger.info("=" * 80)
    
    
    def fetch_data(self, tickers: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Récupère données historiques pour liste tickers.
        
        Args:
            tickers: Liste symbols ETF
            
        Returns:
            Dict {ticker: DataFrame} avec colonnes Date, Open, High, Low, Close, Volume
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.lookback_period * 30 + 60)  # +2 mois buffer
        
        logger.info(f"📥 Récupération données {len(tickers)} ETFs "
                   f"({start_date.date()} → {end_date.date()})")
        
        from data_fetcher_real import fetch_historical_data

        data = fetch_historical_data(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            use_cache=True
        )
        
        # Validation données
        valid_data = {}
        for ticker, df in data.items():
            is_valid, msg = validate_data(df, ticker)
            if is_valid:
                valid_data[ticker] = df
                logger.info(f"  ✅ {msg}")
            else:
                logger.warning(f"  ❌ {msg} - Exclu de l'analyse")
        
        logger.info(f"📊 Données valides : {len(valid_data)}/{len(tickers)} ETFs")
        return valid_data
    
    
    def calculate_momentum_scores(
        self,
        data: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """
        Calcule scores momentum pondérés pour tous ETFs.
        
        Formule : Score = 12% × R₁ₘ + 40% × R₃ₘ + 48% × R₆ₘ
        
        Args:
            data: Dict {ticker: DataFrame prix historiques}
            
        Returns:
            DataFrame avec colonnes :
            - ticker, momentum_score, r1m, r3m, r6m, r12m
            - price_current, price_10m_sma
            - volatility_1m, volatility_12m
        """
        results = []
        
        for ticker, df in data.items():
            try:
                # Calcul score momentum
                score = self.momentum_engine.calculate_weighted_momentum(df)
                
                # Calcul rendements individuels
                returns = self.momentum_engine.calculate_returns(df)
                
                # Calcul indicateurs protection
                current_price = df['Close'].iloc[-1]
                sma_10m = self.momentum_engine.calculate_sma(df, periods=10)
                vol_1m = self.momentum_engine.calculate_volatility(df, months=1)
                vol_12m = self.momentum_engine.calculate_volatility(df, months=12)
                
                results.append({
                    'ticker': ticker,
                    'momentum_score': score,
                    'r1m': returns.get('r1m', 0),
                    'r3m': returns.get('r3m', 0),
                    'r6m': returns.get('r6m', 0),
                    'r12m': returns.get('r12m', 0),
                    'price_current': current_price,
                    'price_10m_sma': sma_10m,
                    'volatility_1m': vol_1m,
                    'volatility_12m': vol_12m
                })
                
                logger.info(f"✅ {ticker}: Score {score:.2%}, "
                          f"R1M {returns.get('r1m', 0):.2%}, "
                          f"R6M {returns.get('r6m', 0):.2%}")
                
            except Exception as e:
                logger.error(f"❌ Erreur calcul {ticker}: {e}")
                continue
        
        df_results = pd.DataFrame(results)
        
        if not df_results.empty:
            df_results = df_results.sort_values('momentum_score', ascending=False)
        
        logger.info(f"📊 Scores calculés : {len(df_results)} ETFs")
        return df_results
    
    
    def apply_filters(self, df_scores: pd.DataFrame) -> pd.DataFrame:
        """
        Applique filtres protection académiques.
        
        Filtres (Antonacci) :
        1. Absolu : momentum_score > 0 (évite bear markets)
        2. Tendance : price_current > price_10m_sma (confirmation tendance)
        3. Volatilité : volatility_1m < 1.5 × volatility_12m (évite panic selling)
        
        Args:
            df_scores: DataFrame scores momentum
            
        Returns:
            DataFrame avec colonnes additionnelles :
            - filter_absolute, filter_trend, filter_volatility (bool)
            - all_filters_pass (bool)
        """
        if df_scores.empty:
            logger.warning("⚠️ DataFrame scores vide, aucun filtre appliqué")
            return df_scores
        
        # Filtre 1 : Absolu (score > 0)
        df_scores['filter_absolute'] = df_scores['momentum_score'] > 0
        
        # Filtre 2 : Tendance (prix > SMA 10 mois)
        df_scores['filter_trend'] = df_scores['price_current'] > df_scores['price_10m_sma']
        
        # Filtre 3 : Volatilité (vol 1M < 1.5× vol 12M)
        df_scores['filter_volatility'] = (
            df_scores['volatility_1m'] < (1.5 * df_scores['volatility_12m'])
        )
        
        # Filtre combiné
        df_scores['all_filters_pass'] = (
            df_scores['filter_absolute'] &
            df_scores['filter_trend'] &
            df_scores['filter_volatility']
        )
        
        # Statistiques filtres
        n_total = len(df_scores)
        n_absolute = df_scores['filter_absolute'].sum()
        n_trend = df_scores['filter_trend'].sum()
        n_volatility = df_scores['filter_volatility'].sum()
        n_all = df_scores['all_filters_pass'].sum()
        
        logger.info(f"🔍 Filtres appliqués :")
        logger.info(f"  Absolu (score > 0) : {n_absolute}/{n_total} ✅")
        logger.info(f"  Tendance (prix > SMA) : {n_trend}/{n_total} ✅")
        logger.info(f"  Volatilité (1M < 1.5×12M) : {n_volatility}/{n_total} ✅")
        logger.info(f"  TOUS FILTRES : {n_all}/{n_total} ETFs qualifiés 🎯")
        
        return df_scores
    
    
    def generate_signals(
        self,
        df_scores: pd.DataFrame,
        current_positions: Optional[Dict[str, float]] = None
    ) -> pd.DataFrame:
        """
        Génère signaux investissement basés scores et filtres.
        
        Logique :
        - REBALANCE : ETF champion actuel, ajuster poids
        - BUY : ETF champion, pas en position
        - HOLD : ETF en position, tous filtres OK
        - SELL : ETF en position, filtres échoués
        - WATCH : ETF non champion, filtres OK (opportunité future)
        
        Args:
            df_scores: DataFrame scores + filtres
            current_positions: Dict {ticker: poids_portfolio} positions actuelles
            
        Returns:
            DataFrame avec colonne additionnelle 'signal'
        """
        if df_scores.empty:
            logger.warning("⚠️ DataFrame scores vide, aucun signal généré")
            return df_scores
        
        current_positions = current_positions or {}
        
        # Identifier champion (score max, tous filtres OK)
        df_qualified = df_scores[df_scores['all_filters_pass']].copy()
        
        if df_qualified.empty:
            logger.warning("⚠️ Aucun ETF qualifié, position cash recommandée")
            df_scores['signal'] = 'CASH'
            return df_scores
        
        champion = df_qualified.iloc[0]['ticker']
        
        # Génération signaux
        signals = []
        for _, row in df_scores.iterrows():
            ticker = row['ticker']
            is_champion = (ticker == champion)
            is_qualified = row['all_filters_pass']
            is_held = ticker in current_positions
            
            if is_champion and is_held:
                signal = 'REBALANCE'
            elif is_champion and not is_held:
                signal = 'BUY'
            elif is_held and is_qualified:
                signal = 'HOLD'
            elif is_held and not is_qualified:
                signal = 'SELL'
            elif is_qualified:
                signal = 'WATCH'
            else:
                signal = 'IGNORE'
            
            signals.append(signal)
        
        df_scores['signal'] = signals
        
        # Statistiques signaux
        signal_counts = df_scores['signal'].value_counts()
        logger.info(f"📊 Signaux générés :")
        for signal, count in signal_counts.items():
            logger.info(f"  {signal}: {count} ETFs")
        logger.info(f"🏆 Champion : {champion}")
        
        return df_scores
    
    
    def run_analysis(
        self,
        pea_positions: Optional[Dict[str, float]] = None,
        cto_positions: Optional[Dict[str, float]] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Exécute analyse complète PEA + CTO.
        
        Pipeline :
        1. Fetch données historiques
        2. Calcul scores momentum
        3. Application filtres protection
        4. Génération signaux investissement
        
        Args:
            pea_positions: Dict {ticker: poids} positions PEA actuelles
            cto_positions: Dict {ticker: poids} positions CTO actuelles
            
        Returns:
            (df_pea_results, df_cto_results) : Tuple DataFrames résultats
        """
        logger.info("=" * 80)
        logger.info("🚀 DÉMARRAGE ANALYSE DUAL MOMENTUM")
        logger.info("=" * 80)
        
        # Analyse PEA
        logger.info("\n📊 ANALYSE PEA")
        logger.info("-" * 80)
        pea_data = self.fetch_data(self.pea_etfs)
        pea_scores = self.calculate_momentum_scores(pea_data)
        pea_scores = self.apply_filters(pea_scores)
        pea_results = self.generate_signals(pea_scores, pea_positions)
        
        # Analyse CTO
        logger.info("\n📊 ANALYSE CTO")
        logger.info("-" * 80)
        cto_data = self.fetch_data(self.cto_etfs)
        cto_scores = self.calculate_momentum_scores(cto_data)
        cto_scores = self.apply_filters(cto_scores)
        cto_results = self.generate_signals(cto_scores, cto_positions)
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ ANALYSE TERMINÉE")
        logger.info("=" * 80)
        
        return pea_results, cto_results


# =============================================================================
# TESTS UNITAIRES
# =============================================================================

if __name__ == "__main__":
    # Test unitaire
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🧪 Test DualMomentumPortfolio...\n")
    
    # Initialisation
    portfolio = DualMomentumPortfolio()
    
    # Positions test
    test_pea_positions = {'VOO': 0.50, 'QQQ': 0.50}
    test_cto_positions = {'ACWI': 1.0}
    
    # Exécution analyse
    pea_results, cto_results = portfolio.run_analysis(
        pea_positions=test_pea_positions,
        cto_positions=test_cto_positions
    )
    
    # Affichage résultats
    print("\n" + "=" * 80)
    print("📊 RÉSULTATS PEA")
    print("=" * 80)
    print(pea_results[['ticker', 'momentum_score', 'signal', 'all_filters_pass']].head(10))
    
    print("\n" + "=" * 80)
    print("📊 RÉSULTATS CTO")
    print("=" * 80)
    print(cto_results[['ticker', 'momentum_score', 'signal', 'all_filters_pass']].head(10))
    
    print("\n✅ Tests terminés")
