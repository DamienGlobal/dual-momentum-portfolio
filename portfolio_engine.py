"""
Moteur de gestion complète du portefeuille Dual Momentum
Orchestration: Données + Calculs + Sélection + Signaux

Author: GLOBAL ICON - Dual Momentum System
Version: 1.0.0 - Full Integration
Date: 2025-10-27
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Modules internes
from config_working import PEA_ETFS_WORKING, CTO_ETFS_WORKING
from data_fetcher_hybrid import fetch_multiple_etfs, get_etf_complete_data
from momentum_engine import MomentumEngine

# =============================================================================
# CLASSE PRINCIPALE: GESTIONNAIRE DE PORTEFEUILLE
# =============================================================================

class DualMomentumPortfolio:
    """
    Gestionnaire complet de portefeuille Dual Momentum
    
    Responsabilités:
    - Récupération données tous ETF (PEA + CTO)
    - Calcul scores momentum pondérés
    - Application filtres protection
    - Sélection champion par enveloppe
    - Génération signaux trading
    """
    
    def __init__(self):
        """Initialise le gestionnaire avec configuration"""
        
        # Configuration ETF par enveloppe
        self.pea_etfs = PEA_ETFS_WORKING
        self.cto_etfs = CTO_ETFS_WORKING
        
        # Moteur momentum
        self.momentum = MomentumEngine()
        
        # Stockage données
        self.pea_data: Dict[str, pd.DataFrame] = {}
        self.cto_data: Dict[str, pd.DataFrame] = {}
        
        # Résultats calculs
        self.pea_scores: Dict[str, Dict] = {}
        self.cto_scores: Dict[str, Dict] = {}
        
        # Champions sélectionnés
        self.pea_champion: Optional[Dict] = None
        self.cto_champion: Optional[Dict] = None
        
        # Timestamp dernière mise à jour
        self.last_update: Optional[datetime] = None
    
    # =========================================================================
    # ÉTAPE 1: RÉCUPÉRATION DONNÉES
    # =========================================================================
    
    def fetch_all_data(self, start_date: str = None, end_date: str = None):
        """
        Récupère données historiques pour tous les ETF (PEA + CTO)
        
        Parameters:
        -----------
        start_date, end_date : str, optional
            Période d'analyse (YYYY-MM-DD)
        """
        
        print("\n" + "=" * 80)
        print("ÉTAPE 1/5: RÉCUPÉRATION DONNÉES HISTORIQUES")
        print("=" * 80)
        
        # ETF PEA
        print("\n[PEA] Récupération données...")
        pea_tickers = [etf['ticker_yahoo'] for etf in self.pea_etfs.values()]
        self.pea_data = fetch_multiple_etfs(pea_tickers, start_date, end_date)
        
        # ETF CTO
        print("\n[CTO] Récupération données...")
        cto_tickers = [etf['ticker_yahoo'] for etf in self.cto_etfs.values()]
        self.cto_data = fetch_multiple_etfs(cto_tickers, start_date, end_date)
        
        print(f"\n✅ RÉCUPÉRATION TERMINÉE")
        print(f"   PEA: {len(self.pea_data)}/{len(pea_tickers)} ETF")
        print(f"   CTO: {len(self.cto_data)}/{len(cto_tickers)} ETF")
        
        self.last_update = datetime.now()
    
    # =========================================================================
    # ÉTAPE 2: CALCUL SCORES MOMENTUM
    # =========================================================================
    
    def calculate_all_scores(self):
        """
        Calcule scores momentum pour tous les ETF avec filtres
        """
        
        print("\n" + "=" * 80)
        print("ÉTAPE 2/5: CALCUL SCORES MOMENTUM")
        print("=" * 80)
        
        # Scores PEA
        print("\n[PEA] Calcul scores...")
        self.pea_scores = self._calculate_scores_for_data(self.pea_data, self.pea_etfs)
        
        # Scores CTO
        print("\n[CTO] Calcul scores...")
        self.cto_scores = self._calculate_scores_for_data(self.cto_data, self.cto_etfs)
        
        print(f"\n✅ CALCUL TERMINÉ")
        print(f"   PEA: {len(self.pea_scores)} ETF analysés")
        print(f"   CTO: {len(self.cto_scores)} ETF analysés")
    
    def _calculate_scores_for_data(
        self,
        data_dict: Dict[str, pd.DataFrame],
        etf_config: Dict
    ) -> Dict[str, Dict]:
        """
        Calcule scores pour un dictionnaire de données
        """
        
        scores = {}
        
        for ticker, data in data_dict.items():
            # Dernière ligne = données les plus récentes
            latest = data.iloc[-1]
            
            # Score momentum pondéré (convertir % en décimal)
            score = self.momentum.calculate_weighted_momentum_score(
                returns_1m=latest['R_21'] / 100,
                returns_3m=latest['R_63'] / 100,
                returns_6m=latest['R_126'] / 100
            )
            
            # Filtres de protection
            filter_absolute = self.momentum.check_absolute_momentum(score)
            filter_trend = self.momentum.check_trend_filter(latest['Close'], latest['SMA_200'])
            filter_vol = self.momentum.check_volatility_filter(
                vol_1m=latest['Vol_21'] / 100,
                vol_12m=data['Vol_21'].tail(252).mean() / 100
            )
            
            filters_passed = filter_absolute and filter_trend and filter_vol
            
            # Stocker résultats (score en %)
            scores[ticker] = {
                'score': score * 100 if score is not None else 0,
                'r_1m': latest['R_21'],
                'r_3m': latest['R_63'],
                'r_6m': latest['R_126'],
                'price': latest['Close'],
                'sma_200': latest['SMA_200'],
                'vol_1m': latest['Vol_21'],
                'filters_passed': filters_passed,
                'date': data.index[-1]
            }
            
            print(f"   {ticker}: Score={score*100:+.2f}% | Filtres={'✅ PASS' if filters_passed else '❌ FAIL'}")
        
        return scores
    
    # =========================================================================
    # ÉTAPE 3: SÉLECTION CHAMPIONS
    # =========================================================================
    
    def select_champions(self):
        """
        Sélectionne ETF champion pour chaque enveloppe (PEA + CTO)
        """
        
        print("\n" + "=" * 80)
        print("ÉTAPE 3/5: SÉLECTION ETF CHAMPIONS")
        print("=" * 80)
        
        # Champion PEA
        print("\n[PEA] Sélection champion...")
        self.pea_champion = self._select_champion_from_scores(
            self.pea_scores,
            self.pea_etfs,
            envelope="PEA"
        )
        
        # Champion CTO
        print("\n[CTO] Sélection champion...")
        self.cto_champion = self._select_champion_from_scores(
            self.cto_scores,
            self.cto_etfs,
            envelope="CTO"
        )
        
        print(f"\n✅ SÉLECTION TERMINÉE")
    
    def _select_champion_from_scores(
        self,
        scores: Dict[str, Dict],
        etf_config: Dict,
        envelope: str
    ) -> Optional[Dict]:
        """
        Sélectionne champion depuis scores calculés
        """
        
        # Filtrer ETF valides (filtres passés)
        valid_etfs = {
            ticker: data for ticker, data in scores.items()
            if data['filters_passed']
        }
        
        if not valid_etfs:
            print(f"   ⚠️ AUCUN ETF ne passe les filtres → Position obligations")
            
            # Trouver ETF obligations dans config
            bond_etf = None
            for ticker, etf_info in etf_config.items():
                if etf_info.get('type') == 'obligations':
                    bond_etf = {
                        'ticker': ticker,
                        'ticker_yahoo': etf_info['ticker_yahoo'],
                        'name': etf_info['name'],
                        'score': 0.0,
                        'is_bond': True,
                        'reason': 'Aucun ETF actions ne passe les filtres'
                    }
                    break
            
            print(f"   → {bond_etf['name'] if bond_etf else 'N/A'}")
            return bond_etf
        
        # Trouver ETF avec score maximum
        champion_ticker = max(valid_etfs, key=lambda t: valid_etfs[t]['score'])
        champion_data = valid_etfs[champion_ticker]
        
        # Récupérer infos depuis config
        champion_info = None
        for ticker, etf_info in etf_config.items():
            if etf_info['ticker_yahoo'] == champion_ticker:
                champion_info = etf_info
                break
        
        result = {
            'ticker': champion_ticker,
            'name': champion_info['name'] if champion_info else champion_ticker,
            'isin': champion_info['isin'] if champion_info else 'N/A',
            'score': champion_data['score'],
            'r_1m': champion_data['r_1m'],
            'r_3m': champion_data['r_3m'],
            'r_6m': champion_data['r_6m'],
            'price': champion_data['price'],
            'is_bond': False,
            'date': champion_data['date']
        }
        
        print(f"   🏆 CHAMPION: {result['name']}")
        print(f"      Score: {result['score']:+.2f}%")
        print(f"      Rendements: 1M={result['r_1m']:+.2f}%, 3M={result['r_3m']:+.2f}%, 6M={result['r_6m']:+.2f}%")
        
        return result
    
    # =========================================================================
    # ÉTAPE 4: GÉNÉRATION SIGNAUX TRADING
    # =========================================================================
    
    def generate_signals(
        self,
        current_pea_ticker: str = None,
        current_cto_ticker: str = None
    ) -> Dict:
        """
        Génère signaux de trading (BUY/HOLD/SELL)
        
        Parameters:
        -----------
        current_pea_ticker, current_cto_ticker : str, optional
            Tickers actuellement détenus dans chaque enveloppe
        
        Returns:
        --------
        dict
            Signaux pour PEA et CTO avec recommandations
        """
        
        print("\n" + "=" * 80)
        print("ÉTAPE 4/5: GÉNÉRATION SIGNAUX TRADING")
        print("=" * 80)
        
        signals = {
            'pea': self._generate_signal_for_envelope(
                champion=self.pea_champion,
                current_ticker=current_pea_ticker,
                envelope='PEA'
            ),
            'cto': self._generate_signal_for_envelope(
                champion=self.cto_champion,
                current_ticker=current_cto_ticker,
                envelope='CTO'
            ),
            'date': datetime.now()
        }
        
        print(f"\n✅ SIGNAUX GÉNÉRÉS")
        return signals
    
    def _generate_signal_for_envelope(
        self,
        champion: Optional[Dict],
        current_ticker: str,
        envelope: str
    ) -> Dict:
        """
        Génère signal pour une enveloppe
        """
        
        if champion is None:
            return {
                'action': 'HOLD',
                'reason': 'Aucun champion sélectionné',
                'target_ticker': None
            }
        
        champion_ticker = champion['ticker']
        
        # Comparer avec position actuelle
        if current_ticker is None:
            action = 'BUY'
            reason = f"Position initiale: Acheter {champion['name']}"
        elif current_ticker == champion_ticker:
            action = 'HOLD'
            reason = f"Maintenir position actuelle: {champion['name']}"
        else:
            action = 'REBALANCE'
            reason = f"Rotation: Vendre {current_ticker} → Acheter {champion['name']}"
        
        signal = {
            'action': action,
            'reason': reason,
            'target_ticker': champion_ticker,
            'target_name': champion['name'],
            'target_isin': champion['isin'],
            'score': champion['score'],
            'is_bond': champion.get('is_bond', False)
        }
        
        print(f"\n[{envelope}] {action}: {reason}")
        print(f"      Cible: {signal['target_name']} (ISIN: {signal['target_isin']})")
        
        return signal
    
    # =========================================================================
    # ÉTAPE 5: RAPPORT COMPLET
    # =========================================================================
    
    def get_portfolio_report(self) -> Dict:
        """
        Génère rapport complet du portefeuille
        
        Returns:
        --------
        dict
            Rapport structuré avec tous les détails
        """
        
        return {
            'timestamp': self.last_update,
            'pea': {
                'champion': self.pea_champion,
                'all_scores': self.pea_scores,
                'nb_etfs_analyzed': len(self.pea_data)
            },
            'cto': {
                'champion': self.cto_champion,
                'all_scores': self.cto_scores,
                'nb_etfs_analyzed': len(self.cto_data)
            }
        }
    
    # =========================================================================
    # WORKFLOW COMPLET
    # =========================================================================
    
    def run_full_analysis(
        self,
        current_pea_ticker: str = None,
        current_cto_ticker: str = None,
        start_date: str = None,
        end_date: str = None
    ) -> Dict:
        """
        Exécute analyse complète de bout en bout
        
        Parameters:
        -----------
        current_pea_ticker, current_cto_ticker : str, optional
            Positions actuellement détenues
        start_date, end_date : str, optional
            Période d'analyse
        
        Returns:
        --------
        dict
            Signaux de trading + rapport complet
        """
        
        print("\n" + "🚀" * 40)
        print("ANALYSE COMPLÈTE PORTEFEUILLE DUAL MOMENTUM")
        print("🚀" * 40)
        
        # Pipeline complet
        self.fetch_all_data(start_date, end_date)
        self.calculate_all_scores()
        self.select_champions()
        signals = self.generate_signals(current_pea_ticker, current_cto_ticker)
        
        print("\n" + "=" * 80)
        print("ÉTAPE 5/5: RAPPORT FINAL")
        print("=" * 80)
        
        report = self.get_portfolio_report()
        report['signals'] = signals
        
        print(f"\n✅✅✅ ANALYSE COMPLÈTE TERMINÉE ✅✅✅")
        
        return report

# =============================================================================
# TESTS UNITAIRES
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TEST PORTFOLIO ENGINE - WORKFLOW COMPLET")
    print("=" * 80)
    
    # Initialiser gestionnaire
    portfolio = DualMomentumPortfolio()
    
    # Positions actuelles utilisateur (depuis contexte)
    CURRENT_PEA = "XLE"  # LU1834983550 (Amundi STOXX 600 Basic Resources) → XLE équivalent
    CURRENT_CTO = "QQQ"  # LU1829221024 (Amundi Core Nasdaq-100) → QQQ équivalent
    
    # Exécuter analyse complète
    report = portfolio.run_full_analysis(
        current_pea_ticker=CURRENT_PEA,
        current_cto_ticker=CURRENT_CTO
    )
    
    # Afficher résumé
    print("\n" + "=" * 80)
    print("RÉSUMÉ SIGNAUX")
    print("=" * 80)
    
    print(f"\n[PEA] {report['signals']['pea']['action']}")
    print(f"   {report['signals']['pea']['reason']}")
    
    print(f"\n[CTO] {report['signals']['cto']['action']}")
    print(f"   {report['signals']['cto']['reason']}")
    
    print("\n" + "=" * 80)
