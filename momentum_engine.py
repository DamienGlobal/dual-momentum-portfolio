"""
Moteur de calcul Dual Momentum académique (Antonacci GEM 2014).

Implémente :
- Formule pondérée optimale : Score = 12% × R₁ₘ + 40% × R₃ₘ + 48% × R₆ₘ
- Filtres protection : Absolu, Tendance, Volatilité
- Calculs rendements multi-périodes
- Indicateurs techniques (SMA, volatilité)

Références académiques :
- Antonacci, G. (2014). "Dual Momentum Investing"
- Faber, M. (2013). "A Quantitative Approach to Tactical Asset Allocation"
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging

# Configuration logging
logger = logging.getLogger(__name__)

# =============================================================================
# PARAMÈTRES ACADÉMIQUES DUAL MOMENTUM (Antonacci GEM 2014)
# =============================================================================

MOMENTUM_WEIGHTS = {
    '1m': 0.12,   # 12% poids rendement 1 mois
    '3m': 0.40,   # 40% poids rendement 3 mois  
    '6m': 0.48    # 48% poids rendement 6 mois
}

FILTERS = {
    'absolute': {
        'enabled': True,
        'threshold': 0.0  # Score momentum > 0
    },
    'trend': {
        'enabled': True,
        'sma_period': 10  # Prix > SMA 10 mois
    },
    'volatility': {
        'enabled': True,
        'multiplier': 1.5  # Vol 1M < 1.5× Vol 12M
    }
}


class MomentumEngine:
    """
    Moteur calculs momentum académiques.
    
    Attributes:
        weights: Dict pondérations rendements (1m, 3m, 6m)
        filters: Dict configuration filtres protection
    """
    
    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        filters: Optional[Dict] = None
    ):
        """
        Initialise moteur momentum.
        
        Args:
            weights: Pondérations personnalisées (défaut Antonacci)
            filters: Configuration filtres (défaut académique)
        """
        self.weights = weights or MOMENTUM_WEIGHTS
        self.filters = filters or FILTERS
        
        # Validation pondérations
        total_weight = sum(self.weights.values())
        if not np.isclose(total_weight, 1.0, atol=0.01):
            logger.warning(f"⚠️ Somme pondérations = {total_weight:.2%} (attendu 100%)")
    
    
    def calculate_returns(
        self,
        df: pd.DataFrame,
        periods: Optional[Dict[str, int]] = None
    ) -> Dict[str, float]:
        """
        Calcule rendements multi-périodes.
        
        Args:
            df: DataFrame prix historiques (colonnes Date, Close)
            periods: Dict {nom: jours_trading} périodes calcul
                    Défaut: {'r1m': 21, 'r3m': 63, 'r6m': 126, 'r12m': 252}
        
        Returns:
            Dict {période: rendement} (ex: {'r1m': 0.05, 'r3m': 0.12, ...})
        """
        if df.empty or 'Close' not in df.columns:
            logger.warning("⚠️ DataFrame vide ou colonne Close manquante")
            return {}
        
        periods = periods or {
            'r1m': 21,    # ~1 mois (21 jours trading)
            'r3m': 63,    # ~3 mois
            'r6m': 126,   # ~6 mois
            'r12m': 252   # ~12 mois
        }
        
        returns = {}
        current_price = df['Close'].iloc[-1]
        
        for period_name, days in periods.items():
            if len(df) < days + 1:
                logger.warning(f"⚠️ Historique insuffisant pour {period_name} "
                             f"(besoin {days+1} jours, disponible {len(df)})")
                returns[period_name] = 0.0
                continue
            
            past_price = df['Close'].iloc[-(days + 1)]
            
            if past_price <= 0:
                logger.warning(f"⚠️ Prix passé invalide pour {period_name}: {past_price}")
                returns[period_name] = 0.0
                continue
            
            returns[period_name] = (current_price / past_price) - 1.0
        
        return returns
    
    
    def calculate_weighted_momentum(self, df: pd.DataFrame) -> float:
        """
        Calcule score momentum pondéré académique.
        
        Formule Antonacci GEM :
        Score = 12% × R₁ₘ + 40% × R₃ₘ + 48% × R₆ₘ
        
        Args:
            df: DataFrame prix historiques
            
        Returns:
            Score momentum (float, ex: 0.15 = +15%)
        """
        returns = self.calculate_returns(df)
        
        if not returns:
            logger.warning("⚠️ Aucun rendement calculé, score = 0")
            return 0.0
        
        score = (
            self.weights['1m'] * returns.get('r1m', 0.0) +
            self.weights['3m'] * returns.get('r3m', 0.0) +
            self.weights['6m'] * returns.get('r6m', 0.0)
        )
        
        return score
    
    
    def calculate_sma(
        self,
        df: pd.DataFrame,
        periods: int = 10
    ) -> float:
        """
        Calcule moyenne mobile simple (SMA).
        
        Args:
            df: DataFrame prix historiques
            periods: Nombre périodes (mois, converti en jours trading)
        
        Returns:
            Valeur SMA ou prix actuel si historique insuffisant
        """
        if df.empty or 'Close' not in df.columns:
            return 0.0
        
        # Conversion mois → jours trading (~21 jours/mois)
        days = periods * 21
        
        if len(df) < days:
            logger.warning(f"⚠️ Historique insuffisant pour SMA {periods}M "
                         f"(besoin {days} jours, disponible {len(df)})")
            return df['Close'].iloc[-1]
        
        sma = df['Close'].iloc[-days:].mean()
        return sma
    
    
    def calculate_volatility(
        self,
        df: pd.DataFrame,
        months: int = 12
    ) -> float:
        """
        Calcule volatilité annualisée.
        
        Args:
            df: DataFrame prix historiques
            months: Période calcul (en mois)
        
        Returns:
            Volatilité annualisée (ex: 0.15 = 15%)
        """
        if df.empty or 'Close' not in df.columns:
            return 0.0
        
        days = months * 21  # Conversion mois → jours trading
        
        if len(df) < days + 1:
            logger.warning(f"⚠️ Historique insuffisant pour volatilité {months}M")
            return 0.0
        
        # Calcul rendements journaliers
        prices = df['Close'].iloc[-(days + 1):].values
        returns = np.diff(prices) / prices[:-1]
        
        # Volatilité annualisée (252 jours trading/an)
        volatility = np.std(returns) * np.sqrt(252)
        
        return volatility
    
    
    def apply_absolute_filter(self, score: float) -> bool:
        """
        Filtre absolu : score momentum > seuil.
        
        Protection bear market : évite investissement si momentum négatif.
        
        Args:
            score: Score momentum
            
        Returns:
            True si filtre passé, False sinon
        """
        if not self.filters['absolute']['enabled']:
            return True
        
        threshold = self.filters['absolute']['threshold']
        return score > threshold
    
    
    def apply_trend_filter(
        self,
        df: pd.DataFrame,
        sma_periods: Optional[int] = None
    ) -> bool:
        """
        Filtre tendance : prix actuel > SMA.
        
        Confirmation tendance haussière : évite faux signaux.
        
        Args:
            df: DataFrame prix historiques
            sma_periods: Nombre mois SMA (défaut 10)
            
        Returns:
            True si filtre passé, False sinon
        """
        if not self.filters['trend']['enabled']:
            return True
        
        sma_periods = sma_periods or self.filters['trend']['sma_period']
        
        current_price = df['Close'].iloc[-1]
        sma = self.calculate_sma(df, periods=sma_periods)
        
        return current_price > sma
    
    
    def apply_volatility_filter(
        self,
        df: pd.DataFrame,
        multiplier: Optional[float] = None
    ) -> bool:
        """
        Filtre volatilité : vol court terme < seuil × vol long terme.
        
        Protection turbulence : évite actifs erratiques.
        
        Args:
            df: DataFrame prix historiques
            multiplier: Multiplicateur seuil (défaut 1.5)
            
        Returns:
            True si filtre passé, False sinon
        """
        if not self.filters['volatility']['enabled']:
            return True
        
        multiplier = multiplier or self.filters['volatility']['multiplier']
        
        vol_1m = self.calculate_volatility(df, months=1)
        vol_12m = self.calculate_volatility(df, months=12)
        
        if vol_12m == 0:
            return True  # Évite division par zéro
        
        return vol_1m < (multiplier * vol_12m)
    
    
    def apply_all_filters(self, df: pd.DataFrame, score: float) -> Dict[str, bool]:
        """
        Applique tous les filtres protection.
        
        Args:
            df: DataFrame prix historiques
            score: Score momentum
            
        Returns:
            Dict {nom_filtre: passé} (ex: {'absolute': True, 'trend': False, ...})
        """
        results = {
            'absolute': self.apply_absolute_filter(score),
            'trend': self.apply_trend_filter(df),
            'volatility': self.apply_volatility_filter(df)
        }
        
        results['all_pass'] = all(results.values())
        
        return results


if __name__ == "__main__":
    # Tests unitaires
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Test MomentumEngine...")
    
    # Données test
    dates = pd.bdate_range(end=datetime.now(), periods=300, freq='D')
    prices = 100 * (1 + np.random.randn(300).cumsum() * 0.01)
    df_test = pd.DataFrame({'Date': dates, 'Close': prices})
    
    # Initialisation
    engine = MomentumEngine()
    
    # Test calculs
    print("\n📊 Rendements multi-périodes :")
    returns = engine.calculate_returns(df_test)
    for period, ret in returns.items():
        print(f"  {period}: {ret:+.2%}")
    
    print("\n📈 Score momentum pondéré :")
    score = engine.calculate_weighted_momentum(df_test)
    print(f"  Score: {score:+.2%}")
    
    print("\n🔍 Filtres protection :")
    filters = engine.apply_all_filters(df_test, score)
    for filter_name, passed in filters.items():
        status = "✅" if passed else "❌"
        print(f"  {filter_name}: {status}")
    
    print("\n✅ Tests terminés")
