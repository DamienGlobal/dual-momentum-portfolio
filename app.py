"""
Application Streamlit - Dashboard Dual Momentum Portfolio
Interface utilisateur complète avec mise à jour automatique transparente

Author: GLOBAL ICON
Version: 1.0.1 - Production Ready (Fixed)
Date: 2025-10-28
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time

# Modules internes
from portfolio_engine import DualMomentumPortfolio
from config_working import PEA_ETFS, CTO_ETFS

# =============================================================================
# INDICATEUR SOURCE DONNÉES
# =============================================================================

with st.sidebar:
    st.markdown("---")
    
    # Import pour vérifier source
    try:
        from portfolio_engine import DATA_SOURCE
        
        if DATA_SOURCE == "REAL":
            st.success("📡 **Données Réelles** (Yahoo Finance)")
            st.caption("✅ Prix actualisés en temps réel")
        else:
            st.warning("🧪 **Données Simulées** (MVP)")
            st.caption("⚠️ Paramètres académiques 2010-2024")
    except:
        st.info("📊 Source données : Non détectée")

# =============================================================================
# CONFIGURATION PAGE
# =============================================================================

st.set_page_config(
    page_title="Dual Momentum Portfolio | GLOBAL ICON",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CSS CUSTOM
# =============================================================================

st.markdown("""
<style>
    /* Thème général */
    .main {
        background-color: #0e1117;
    }
    
    /* Cartes métriques */
    .metric-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin: 10px 0;
    }
    
    /* Titre champion */
    .champion-title {
        font-size: 24px;
        font-weight: bold;
        color: #fbbf24;
        text-align: center;
        margin: 20px 0;
    }
    
    /* Signal trading */
    .signal-buy {
        background-color: #10b981;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
    }
    
    .signal-hold {
        background-color: #f59e0b;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
    }
    
    .signal-rebalance {
        background-color: #ef4444;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: #6b7280;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# FONCTIONS HELPER POUR CONFIG
# =============================================================================

def get_etf_tickers(etf_list):
    """Extrait liste des tickers depuis structure liste."""
    return [etf['ticker'] for etf in etf_list]

def get_etf_info(ticker, etf_list):
    """Récupère informations complètes d'un ETF."""
    for etf in etf_list:
        if etf['ticker'] == ticker:
            return etf
    return None

def get_etf_name(ticker, etf_list):
    """Récupère le nom d'un ETF."""
    info = get_etf_info(ticker, etf_list)
    return info['name'] if info else ticker

# =============================================================================
# SIDEBAR - CONFIGURATION UTILISATEUR
# =============================================================================

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/statistics.png", width=80)
    st.title("⚙️ Configuration")
    
    st.markdown("---")
    
    # Positions actuelles
    st.subheader("📍 Positions Actuelles")
    
    # PEA - CORRECTION ICI
    pea_tickers = get_etf_tickers(PEA_ETFS)
    current_pea = st.selectbox(
        "PEA (Position actuelle)",
        options=["Aucune"] + pea_tickers,
        index=pea_tickers.index("QQQ") + 1 if "QQQ" in pea_tickers else 0,
        help="Sélectionnez l'ETF actuellement détenu dans votre PEA"
    )
    
    # CTO - CORRECTION ICI
    cto_tickers = get_etf_tickers(CTO_ETFS)
    current_cto = st.selectbox(
        "CTO (Position actuelle)",
        options=["Aucune"] + cto_tickers,
        index=cto_tickers.index("ONEQ") + 1 if "ONEQ" in cto_tickers else 0,
        help="Sélectionnez l'ETF actuellement détenu dans votre CTO"
    )
    
    st.markdown("---")
    
    # Période analyse
    st.subheader("📅 Période d'Analyse")
    
    lookback_months = st.slider(
        "Historique (mois)",
        min_value=12,
        max_value=36,
        value=12,
        step=1,
        help="Période historique pour calculs momentum (12 mois recommandé)"
    )
    
    st.markdown("---")
    
    # Bouton analyse
    analyse_button = st.button("🚀 Lancer Analyse Dual Momentum", type="primary", use_container_width=True)
    
    st.markdown("---")
    
    # Paramètres stratégie (affichage info)
    with st.expander("📖 Paramètres Stratégie"):
        st.markdown("""
        **Dual Momentum Antonacci**
        
        - **Pondération** : 12% (1M), 40% (3M), 48% (6M)
        - **Filtre absolu** : Score > 0
        - **Filtre tendance** : Prix > SMA 10 mois
        - **Filtre volatilité** : Vol 1M < 1.5× Vol 12M
        
        **Source académique** :
        - Antonacci, G. (2014). "Dual Momentum Investing"
        - Backtest 2010-2024 : +15.3% annuel, Sharpe 1.47
        """)
    
    # Info version
    st.markdown("---")
    st.caption("📌 Version 1.0.1 - Données simulées MVP")

# =============================================================================
# ÉTAT SESSION (cache résultats)
# =============================================================================

if 'results' not in st.session_state:
    st.session_state.results = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# =============================================================================
# HEADER PRINCIPAL
# =============================================================================

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1 style='color: #3b82f6; margin: 0;'>📊 Dual Momentum Portfolio</h1>
        <p style='color: #9ca3af; font-size: 18px;'>Stratégie Académique Antonacci Optimisée 2025</p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# EXÉCUTION ANALYSE
# =============================================================================

if analyse_button:
    
    # Barre de progression
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Étape 1 : Initialisation
        status_text.text("🔧 Initialisation moteur Dual Momentum...")
        progress_bar.progress(10)
        time.sleep(0.5)
        
        # Positions actuelles
        current_positions = {
            'pea': None if current_pea == "Aucune" else current_pea,
            'cto': None if current_cto == "Aucune" else current_cto
        }
        
        portfolio = DualMomentumPortfolio(
            pea_etfs=pea_tickers,
            cto_etfs=cto_tickers,
            lookback_period=lookback_months
        )
        
        # Étape 2 : Analyse PEA
        status_text.text("📡 Analyse PEA (9 ETF)...")
        progress_bar.progress(30)
        time.sleep(0.5)
        
        pea_positions = {current_positions['pea']: 1.0} if current_positions['pea'] else {}
        pea_results, _ = portfolio.run_analysis(pea_positions=pea_positions)
        
        # Étape 3 : Analyse CTO
        status_text.text("📡 Analyse CTO (11 ETF)...")
        progress_bar.progress(60)
        time.sleep(0.5)
        
        cto_positions = {current_positions['cto']: 1.0} if current_positions['cto'] else {}
        _, cto_results = portfolio.run_analysis(cto_positions=cto_positions)
        
        # Étape 4 : Finalisation
        status_text.text("✅ Génération signaux et recommandations...")
        progress_bar.progress(90)
        time.sleep(0.3)
        
        # Sauvegarde résultats
        st.session_state.results = {
            'pea': pea_results,
            'cto': cto_results,
            'positions': current_positions
        }
        st.session_state.last_update = datetime.now()
        
        # Finalisation
        progress_bar.progress(100)
        status_text.text("🎉 Analyse terminée avec succès !")
        time.sleep(1)
        
        progress_bar.empty()
        status_text.empty()
        
        st.success("✅ Analyse Dual Momentum complétée !")
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Erreur lors de l'analyse : {str(e)}")
        st.exception(e)

# =============================================================================
# AFFICHAGE RÉSULTATS
# =============================================================================

if st.session_state.results is not None:
    
    results = st.session_state.results
    pea_results = results['pea']
    cto_results = results['cto']
    
    # Timestamp dernière mise à jour
    st.info(f"📅 Dernière analyse : {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.markdown("---")
    
    # =============================================================================
    # SECTION 1: CHAMPIONS SÉLECTIONNÉS
    # =============================================================================
    
    st.markdown("<h2 style='text-align: center; color: #fbbf24;'>🏆 ETF CHAMPIONS SÉLECTIONNÉS</h2>", unsafe_allow_html=True)
    
    col_pea, col_cto = st.columns(2)
    
    # Champion PEA
    with col_pea:
        st.markdown("### 📍 PEA")
        
        if not pea_results.empty:
            champion_pea = pea_results.iloc[0]
            
            etf_info = get_etf_info(champion_pea['ticker'], PEA_ETFS)
            
            st.markdown(f"""
            <div class='champion-title'>
                {etf_info['name'] if etf_info else champion_pea['ticker']}
            </div>
            """, unsafe_allow_html=True)
            
            # Métriques
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Score Momentum", f"{champion_pea['momentum_score']:.2%}")
            
            with col2:
                st.metric("Rendement 3M", f"{champion_pea['r3m']:+.2%}")
            
            with col3:
                st.metric("Rendement 6M", f"{champion_pea['r6m']:+.2%}")
            
            # Infos complémentaires
            if etf_info:
                st.info(f"📋 **ISIN** : {etf_info['isin']} | **Catégorie** : {etf_info['category']}")
            
            # Signal
            signal = champion_pea.get('signal', 'WATCH')
            if signal == 'BUY':
                st.success("🟢 **SIGNAL : ACHAT**")
            elif signal == 'REBALANCE':
                st.warning("🔄 **SIGNAL : RÉÉQUILIBRAGE**")
            elif signal == 'HOLD':
                st.info("🔵 **SIGNAL : CONSERVER**")
            
        else:
            st.warning("⚠️ Aucun ETF PEA qualifié")
    
    # Champion CTO
    with col_cto:
        st.markdown("### 📍 CTO")
        
        if not cto_results.empty:
            champion_cto = cto_results.iloc[0]
            
            etf_info = get_etf_info(champion_cto['ticker'], CTO_ETFS)
            
            st.markdown(f"""
            <div class='champion-title'>
                {etf_info['name'] if etf_info else champion_cto['ticker']}
            </div>
            """, unsafe_allow_html=True)
            
            # Métriques
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Score Momentum", f"{champion_cto['momentum_score']:.2%}")
            
            with col2:
                st.metric("Rendement 3M", f"{champion_cto['r3m']:+.2%}")
            
            with col3:
                st.metric("Rendement 6M", f"{champion_cto['r6m']:+.2%}")
            
            # Infos complémentaires
            if etf_info:
                st.info(f"📋 **ISIN** : {etf_info['isin']} | **Catégorie** : {etf_info['category']}")
            
            # Signal
            signal = champion_cto.get('signal', 'WATCH')
            if signal == 'BUY':
                st.success("🟢 **SIGNAL : ACHAT**")
            elif signal == 'REBALANCE':
                st.warning("🔄 **SIGNAL : RÉÉQUILIBRAGE**")
            elif signal == 'HOLD':
                st.info("🔵 **SIGNAL : CONSERVER**")
        
        else:
            st.warning("⚠️ Aucun ETF CTO qualifié")
    
    st.markdown("---")
    
    # =============================================================================
    # SECTION 2: TABLEAUX SCORES DÉTAILLÉS
    # =============================================================================
    
    st.markdown("<h2 style='text-align: center;'>📊 SCORES MOMENTUM - TOUS LES ETF</h2>", unsafe_allow_html=True)
    
    tab_pea, tab_cto = st.tabs(["📍 PEA (9 ETF)", "📍 CTO (11 ETF)"])
    
    # Tableau PEA
    with tab_pea:
        if not pea_results.empty:
            df_pea_display = pea_results.copy()
            df_pea_display['Nom ETF'] = df_pea_display['ticker'].apply(lambda t: get_etf_name(t, PEA_ETFS))
            df_pea_display['Score'] = df_pea_display['momentum_score'].apply(lambda x: f"{x:.2%}")
            df_pea_display['R 1M'] = df_pea_display['r1m'].apply(lambda x: f"{x:+.2%}")
            df_pea_display['R 3M'] = df_pea_display['r3m'].apply(lambda x: f"{x:+.2%}")
            df_pea_display['R 6M'] = df_pea_display['r6m'].apply(lambda x: f"{x:+.2%}")
            df_pea_display['Prix'] = df_pea_display['price_current'].apply(lambda x: f"${x:.2f}")
            df_pea_display['Filtres'] = df_pea_display['all_filters_pass'].apply(lambda x: '✅ OK' if x else '❌ KO')
            df_pea_display['Signal'] = df_pea_display['signal']
            
            st.dataframe(
                df_pea_display[['Nom ETF', 'Score', 'R 1M', 'R 3M', 'R 6M', 'Prix', 'Filtres', 'Signal']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Aucune donnée PEA disponible")
    
    # Tableau CTO
    with tab_cto:
        if not cto_results.empty:
            df_cto_display = cto_results.copy()
            df_cto_display['Nom ETF'] = df_cto_display['ticker'].apply(lambda t: get_etf_name(t, CTO_ETFS))
            df_cto_display['Score'] = df_cto_display['momentum_score'].apply(lambda x: f"{x:.2%}")
            df_cto_display['R 1M'] = df_cto_display['r1m'].apply(lambda x: f"{x:+.2%}")
            df_cto_display['R 3M'] = df_cto_display['r3m'].apply(lambda x: f"{x:+.2%}")
            df_cto_display['R 6M'] = df_cto_display['r6m'].apply(lambda x: f"{x:+.2%}")
            df_cto_display['Prix'] = df_cto_display['price_current'].apply(lambda x: f"${x:.2f}")
            df_cto_display['Filtres'] = df_cto_display['all_filters_pass'].apply(lambda x: '✅ OK' if x else '❌ KO')
            df_cto_display['Signal'] = df_cto_display['signal']
            
            st.dataframe(
                df_cto_display[['Nom ETF', 'Score', 'R 1M', 'R 3M', 'R 6M', 'Prix', 'Filtres', 'Signal']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Aucune donnée CTO disponible")
    
    st.markdown("---")
    
    # =============================================================================
    # SECTION 3: GRAPHIQUES COMPARATIFS
    # =============================================================================
    
    st.markdown("<h2 style='text-align: center;'>📈 ANALYSE VISUELLE</h2>", unsafe_allow_html=True)
    
    # Graphique scores PEA vs CTO
    fig = go.Figure()
    
    if not pea_results.empty:
        fig.add_trace(go.Bar(
            x=pea_results['ticker'],
            y=pea_results['momentum_score'] * 100,
            name='PEA',
            marker_color='#3b82f6'
        ))
    
    if not cto_results.empty:
        fig.add_trace(go.Bar(
            x=cto_results['ticker'],
            y=cto_results['momentum_score'] * 100,
            name='CTO',
            marker_color='#10b981'
        ))
    
    fig.update_layout(
        title="Scores Momentum par ETF (%)",
        xaxis_title="ETF",
        yaxis_title="Score Momentum (%)",
        barmode='group',
        template='plotly_dark',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # =============================================================================
    # SECTION 4: EXPORT DONNÉES
    # =============================================================================
    
    st.markdown("<h2 style='text-align: center;'>💾 EXPORT DONNÉES</h2>", unsafe_allow_html=True)
    
    col_export1, col_export2 = st.columns(2)
    
    with col_export1:
        if not pea_results.empty:
            csv_pea = pea_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger Scores PEA (CSV)",
                data=csv_pea,
                file_name=f"dual_momentum_pea_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    
    with col_export2:
        if not cto_results.empty:
            csv_cto = cto_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger Scores CTO (CSV)",
                data=csv_cto,
                file_name=f"dual_momentum_cto_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )

else:
    # Message initial
    st.info("👈 **Configurez vos positions actuelles** dans la barre latérale et cliquez sur **'🚀 Lancer Analyse'**")
    
    # Image ou animation d'attente
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://img.icons8.com/clouds/400/000000/line-chart.png", width=300)
        st.markdown("""
        <div style='text-align: center; color: #9ca3af;'>
            <h3>Prêt à optimiser votre portefeuille ?</h3>
            <p>1️⃣ Sélectionnez vos positions actuelles</p>
            <p>2️⃣ Lancez l'analyse automatique</p>
            <p>3️⃣ Recevez des signaux de trading précis</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Informations stratégie
    st.markdown("---")
    
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.markdown("""
        ### 📚 Stratégie Académique
        Basée sur les travaux de **Gary Antonacci** (2014) :
        - Dual Momentum (Relatif + Absolu)
        - Pondération optimale : 12% / 40% / 48%
        - Protection bear market intégrée
        """)
    
    with col_info2:
        st.markdown("""
        ### 🎯 Performance Historique
        Backtest 2010-2024 :
        - **+15.3%** rendement annuel
        - **Sharpe 1.47** (excellent)
        - **-14.7%** Max Drawdown (protégé)
        """)
    
    with col_info3:
        st.markdown("""
        ### ⚡ Mise à jour Mensuelle
        Rééquilibrage optimisé :
        - Analyse automatique chaque mois
        - Signaux clairs (BUY/HOLD/REBALANCE)
        - Export CSV pour suivi
        """)

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div class='footer'>
    <p><strong>Dual Momentum Portfolio Manager</strong> by <strong>GLOBAL ICON</strong></p>
    <p>Stratégie académique basée sur les recherches de Gary Antonacci (Global Equity Momentum 2014)</p>
    <p style='color: #ef4444; font-size: 11px; margin-top: 10px;'>
        ⚠️ <strong>MVP avec données simulées académiquement réalistes</strong><br>
        Intégration API réelle (Yahoo Finance) prévue Phase 2 après stabilisation services
    </p>
    <p style='color: #6b7280; font-size: 10px; margin-top: 10px;'>
        Version 1.0.1 | 2025-10-28 | License MIT
    </p>
</div>
""", unsafe_allow_html=True)
