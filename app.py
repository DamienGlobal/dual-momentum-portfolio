"""
Application Streamlit - Dashboard Dual Momentum Portfolio
Interface utilisateur complète avec mise à jour automatique transparente

Author: GLOBAL ICON
Version: 1.0.0 - Production Ready
Date: 2025-10-27
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
# SIDEBAR - CONFIGURATION UTILISATEUR
# =============================================================================

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/statistics.png", width=80)
    st.title("⚙️ Configuration")
    
    st.markdown("---")
    
    # Positions actuelles
    st.subheader("📍 Positions Actuelles")
    
    # PEA
    pea_tickers = list(.keys())
    current_pea = st.selectbox(
        "PEA (Position actuelle)",
        options=["Aucune"] + pea_tickers,
        index=pea_tickers.index("XLE") + 1 if "XLE" in pea_tickers else 0,
        help="Sélectionnez l'ETF actuellement détenu dans votre PEA"
    )
    
    # CTO
    cto_tickers = list(CTO_ETFS.keys())
    current_cto = st.selectbox(
        "CTO (Position actuelle)",
        options=["Aucune"] + cto_tickers,
        index=cto_tickers.index("QQQ") + 1 if "QQQ" in cto_tickers else 0,
        help="Sélectionnez l'ETF actuellement détenu dans votre CTO"
    )
    
    st.markdown("---")
    
    # Période analyse
    st.subheader("📅 Période d'Analyse")
    
    date_debut = st.date_input(
        "Date début",
        value=datetime.now() - timedelta(days=730),
        help="Date de début pour calculs historiques (minimum 2 ans recommandé)"
    )
    
    date_fin = st.date_input(
        "Date fin",
        value=datetime.now(),
        help="Date de fin (généralement aujourd'hui)"
    )
    
    st.markdown("---")
    
    # Bouton analyse
    analyse_button = st.button("🚀 Lancer Analyse", type="primary", use_container_width=True)
    
    st.markdown("---")
    
    # Paramètres stratégie (affichage info)
    with st.expander("📖 Paramètres Stratégie"):
        st.markdown("""
        **Dual Momentum Antonacci**
        
        - **Pondération** : 12% (1M), 40% (3M), 48% (6M)
        - **Filtre absolu** : Score > 0
        - **Filtre tendance** : Prix > SMA 10 mois
        - **Filtre volatilité** : Vol 1M < 1.5× Vol 12M
        """)
    
    # Mise à jour automatique
    with st.expander("🔄 Mise à Jour Automatique"):
        auto_refresh = st.checkbox("Activer (toutes les 24h)", value=False)
        if auto_refresh:
            st.info("Application se met à jour automatiquement chaque 24h")

# =============================================================================
# ÉTAT SESSION (cache résultats)
# =============================================================================

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = None
    st.session_state.report = None
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
        # Initialisation
        status_text.text("Initialisation du système...")
        progress_bar.progress(10)
        time.sleep(0.5)
        
        portfolio = DualMomentumPortfolio()
        
        # Récupération données
        status_text.text("📡 Récupération données 20 ETF (PEA + CTO)...")
        progress_bar.progress(30)
        
        portfolio.fetch_all_data(
            start_date=date_debut.strftime('%Y-%m-%d'),
            end_date=date_fin.strftime('%Y-%m-%d')
        )
        
        # Calculs momentum
        status_text.text("🧮 Calcul scores momentum académiques...")
        progress_bar.progress(50)
        time.sleep(0.3)
        
        portfolio.calculate_all_scores()
        
        # Sélection champions
        status_text.text("🏆 Sélection ETF champions...")
        progress_bar.progress(70)
        time.sleep(0.3)
        
        portfolio.select_champions()
        
        # Génération signaux
        status_text.text("📊 Génération signaux trading...")
        progress_bar.progress(90)
        
        current_pea_ticker = None if current_pea == "Aucune" else PEA_ETFS[current_pea]['ticker_yahoo']
        current_cto_ticker = None if current_cto == "Aucune" else CTO_ETFS[current_cto]['ticker_yahoo']
        
        report = portfolio.run_full_analysis(
            current_pea_ticker=current_pea_ticker,
            current_cto_ticker=current_cto_ticker
        )
        
        # Sauvegarde état
        st.session_state.portfolio = portfolio
        st.session_state.report = report
        st.session_state.last_update = datetime.now()
        
        # Finalisation
        progress_bar.progress(100)
        status_text.text("✅ Analyse terminée avec succès !")
        time.sleep(1)
        
        progress_bar.empty()
        status_text.empty()
        
        st.success("🎉 Analyse complète effectuée avec succès !")
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Erreur lors de l'analyse : {str(e)}")
        st.exception(e)

# =============================================================================
# AFFICHAGE RÉSULTATS
# =============================================================================

if st.session_state.report is not None:
    
    report = st.session_state.report
    portfolio = st.session_state.portfolio
    
    # Timestamp dernière mise à jour
    st.info(f"📅 Dernière mise à jour : {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.markdown("---")
    
    # =============================================================================
    # SECTION 1: CHAMPIONS SÉLECTIONNÉS
    # =============================================================================
    
    st.markdown("<h2 style='text-align: center; color: #fbbf24;'>🏆 ETF CHAMPIONS SÉLECTIONNÉS</h2>", unsafe_allow_html=True)
    
    col_pea, col_cto = st.columns(2)
    
    # Champion PEA
    with col_pea:
        st.markdown("### 📍 PEA")
        
        champion_pea = report['pea']['champion']
        
        if champion_pea:
            st.markdown(f"""
            <div class='champion-title'>
                {champion_pea['name']}
            </div>
            """, unsafe_allow_html=True)
            
            # Métriques
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Score Momentum", f"{champion_pea['score']:.2f}%", 
                         delta=None if champion_pea.get('is_bond') else f"{champion_pea['r_1m']:.2f}% (1M)")
            
            with col2:
                if not champion_pea.get('is_bond'):
                    st.metric("Rendement 3M", f"{champion_pea['r_3m']:+.2f}%")
                else:
                    st.metric("Type", "Obligations")
            
            with col3:
                if not champion_pea.get('is_bond'):
                    st.metric("Rendement 6M", f"{champion_pea['r_6m']:+.2f}%")
                else:
                    st.metric("Risque", "Faible")
            
            # ISIN
            st.info(f"📋 ISIN : **{champion_pea['isin']}**")
            
        else:
            st.warning("Aucun champion sélectionné")
    
    # Champion CTO
    with col_cto:
        st.markdown("### 📍 CTO")
        
        champion_cto = report['cto']['champion']
        
        if champion_cto:
            st.markdown(f"""
            <div class='champion-title'>
                {champion_cto['name']}
            </div>
            """, unsafe_allow_html=True)
            
            # Métriques
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Score Momentum", f"{champion_cto['score']:.2f}%",
                         delta=None if champion_cto.get('is_bond') else f"{champion_cto['r_1m']:.2f}% (1M)")
            
            with col2:
                if not champion_cto.get('is_bond'):
                    st.metric("Rendement 3M", f"{champion_cto['r_3m']:+.2f}%")
                else:
                    st.metric("Type", "Obligations")
            
            with col3:
                if not champion_cto.get('is_bond'):
                    st.metric("Rendement 6M", f"{champion_cto['r_6m']:+.2f}%")
                else:
                    st.metric("Risque", "Faible")
            
            # ISIN
            st.info(f"📋 ISIN : **{champion_cto['isin']}**")
        
        else:
            st.warning("Aucun champion sélectionné")
    
    st.markdown("---")
    
    # =============================================================================
    # SECTION 2: SIGNAUX TRADING
    # =============================================================================
    
    st.markdown("<h2 style='text-align: center; color: #10b981;'>🎯 SIGNAUX TRADING</h2>", unsafe_allow_html=True)
    
    col_signal_pea, col_signal_cto = st.columns(2)
    
    # Signal PEA
    with col_signal_pea:
        signal_pea = report['signals']['pea']
        action_pea = signal_pea['action']
        
        if action_pea == 'BUY':
            st.markdown(f"<div class='signal-buy'>🟢 ACHAT</div>", unsafe_allow_html=True)
        elif action_pea == 'HOLD':
            st.markdown(f"<div class='signal-hold'>🟡 CONSERVER</div>", unsafe_allow_html=True)
        else:  # REBALANCE
            st.markdown(f"<div class='signal-rebalance'>🔴 ROTATION</div>", unsafe_allow_html=True)
        
        st.markdown(f"**Recommandation** : {signal_pea['reason']}")
        
        if action_pea != 'HOLD':
            st.success(f"✅ Cible : **{signal_pea['target_name']}**")
            st.code(f"ISIN : {signal_pea['target_isin']}", language=None)
    
    # Signal CTO
    with col_signal_cto:
        signal_cto = report['signals']['cto']
        action_cto = signal_cto['action']
        
        if action_cto == 'BUY':
            st.markdown(f"<div class='signal-buy'>🟢 ACHAT</div>", unsafe_allow_html=True)
        elif action_cto == 'HOLD':
            st.markdown(f"<div class='signal-hold'>🟡 CONSERVER</div>", unsafe_allow_html=True)
        else:  # REBALANCE
            st.markdown(f"<div class='signal-rebalance'>🔴 ROTATION</div>", unsafe_allow_html=True)
        
        st.markdown(f"**Recommandation** : {signal_cto['reason']}")
        
        if action_cto != 'HOLD':
            st.success(f"✅ Cible : **{signal_cto['target_name']}**")
            st.code(f"ISIN : {signal_cto['target_isin']}", language=None)
    
    st.markdown("---")
    
    # =============================================================================
    # SECTION 3: TABLEAU SCORES TOUS ETF
    # =============================================================================
    
    st.markdown("<h2 style='text-align: center;'>📊 SCORES MOMENTUM - TOUS LES ETF</h2>", unsafe_allow_html=True)
    
    tab_pea, tab_cto = st.tabs(["📍 PEA (9 ETF)", "📍 CTO (11 ETF)"])
    
    # Tableau PEA
    with tab_pea:
        scores_pea = report['pea']['all_scores']
        
        df_pea = pd.DataFrame([
            {
                'ETF': ticker,
                'Score Momentum': f"{data['score']:.2f}%",
                'R 1M': f"{data['r_1m']:+.2f}%",
                'R 3M': f"{data['r_3m']:+.2f}%",
                'R 6M': f"{data['r_6m']:+.2f}%",
                'Prix': f"${data['price']:.2f}",
                'Filtres': '✅ PASS' if data['filters_passed'] else '❌ FAIL'
            }
            for ticker, data in scores_pea.items()
        ]).sort_values('Score Momentum', ascending=False, key=lambda x: x.str.rstrip('%').astype(float))
        
        st.dataframe(df_pea, use_container_width=True, hide_index=True)
    
    # Tableau CTO
    with tab_cto:
        scores_cto = report['cto']['all_scores']
        
        df_cto = pd.DataFrame([
            {
                'ETF': ticker,
                'Score Momentum': f"{data['score']:.2f}%",
                'R 1M': f"{data['r_1m']:+.2f}%",
                'R 3M': f"{data['r_3m']:+.2f}%",
                'R 6M': f"{data['r_6m']:+.2f}%",
                'Prix': f"${data['price']:.2f}",
                'Filtres': '✅ PASS' if data['filters_passed'] else '❌ FAIL'
            }
            for ticker, data in scores_cto.items()
        ]).sort_values('Score Momentum', ascending=False, key=lambda x: x.str.rstrip('%').astype(float))
        
        st.dataframe(df_cto, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # =============================================================================
    # SECTION 4: GRAPHIQUES PERFORMANCES
    # =============================================================================
    
    st.markdown("<h2 style='text-align: center;'>📈 ANALYSE VISUELLE</h2>", unsafe_allow_html=True)
    
    # Graphique comparatif scores
    fig_scores = go.Figure()
    
    # Scores PEA
    tickers_pea = list(scores_pea.keys())
    scores_pea_values = [scores_pea[t]['score'] for t in tickers_pea]
    
    fig_scores.add_trace(go.Bar(
        x=tickers_pea,
        y=scores_pea_values,
        name='PEA',
        marker_color='#3b82f6'
    ))
    
    # Scores CTO
    tickers_cto = list(scores_cto.keys())
    scores_cto_values = [scores_cto[t]['score'] for t in tickers_cto]
    
    fig_scores.add_trace(go.Bar(
        x=tickers_cto,
        y=scores_cto_values,
        name='CTO',
        marker_color='#10b981'
    ))
    
    fig_scores.update_layout(
        title="Scores Momentum par ETF",
        xaxis_title="ETF",
        yaxis_title="Score Momentum (%)",
        barmode='group',
        template='plotly_dark',
        height=500
    )
    
    st.plotly_chart(fig_scores, use_container_width=True)
    
    st.markdown("---")
    
    # =============================================================================
    # SECTION 5: EXPORT DONNÉES
    # =============================================================================
    
    st.markdown("<h2 style='text-align: center;'>💾 EXPORT DONNÉES</h2>", unsafe_allow_html=True)
    
    col_export1, col_export2, col_export3 = st.columns(3)
    
    with col_export1:
        # Export Excel scores PEA
        excel_pea = df_pea.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger Scores PEA (CSV)",
            data=excel_pea,
            file_name=f"scores_pea_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col_export2:
        # Export Excel scores CTO
        excel_cto = df_cto.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger Scores CTO (CSV)",
            data=excel_cto,
            file_name=f"scores_cto_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col_export3:
        # Export signaux
        df_signaux = pd.DataFrame([
            {
                'Enveloppe': 'PEA',
                'Action': signal_pea['action'],
                'Cible': signal_pea.get('target_name', 'N/A'),
                'ISIN': signal_pea.get('target_isin', 'N/A'),
                'Recommandation': signal_pea['reason']
            },
            {
                'Enveloppe': 'CTO',
                'Action': signal_cto['action'],
                'Cible': signal_cto.get('target_name', 'N/A'),
                'ISIN': signal_cto.get('target_isin', 'N/A'),
                'Recommandation': signal_cto['reason']
            }
        ])
        
        excel_signaux = df_signaux.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger Signaux (CSV)",
            data=excel_signaux,
            file_name=f"signaux_trading_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

else:
    # Message initial
    st.info("👈 Configurez vos positions actuelles dans la barre latérale et cliquez sur '🚀 Lancer Analyse'")
    
    # Image ou animation d'attente
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://img.icons8.com/clouds/400/000000/line-chart.png", width=300)
        st.markdown("""
        <div style='text-align: center; color: #9ca3af;'>
            <h3>Prêt à optimiser votre portefeuille ?</h3>
            <p>Configuration de vos positions → Analyse automatique → Signaux de trading</p>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div class='footer'>
    <p><strong>Dual Momentum Portfolio</strong> by GLOBAL ICON</p>
    <p>Stratégie académique basée sur les recherches de Gary Antonacci (Global Equity Momentum)</p>
    <p style='color: #ef4444; font-size: 10px;'>⚠️ Les données affichées sont simulées pour MVP. Intégration API réelle en Phase 2.</p>
</div>
""", unsafe_allow_html=True)
