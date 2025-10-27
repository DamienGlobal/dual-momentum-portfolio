"""
Script d'analyse rapide - Alternative interface Streamlit
Génère rapport complet en ligne de commande + fichier HTML

Usage: python3 run_analysis.py
"""

from portfolio_engine import DualMomentumPortfolio
from config_working import PEA_ETFS_WORKING, CTO_ETFS_WORKING
import pandas as pd
from datetime import datetime

def generate_html_report(report, output_file="rapport_momentum.html"):
    """Génère rapport HTML professionnel"""
    
    champion_pea = report['pea']['champion']
    champion_cto = report['cto']['champion']
    
    signal_pea = report['signals']['pea']
    signal_cto = report['signals']['cto']
    
    scores_pea = report['pea']['all_scores']
    scores_cto = report['cto']['all_scores']
    
    # HTML Template
    html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dual Momentum Portfolio - Rapport {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }}
        h1 {{
            color: #667eea;
            text-align: center;
            font-size: 36px;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            font-size: 16px;
            margin-bottom: 30px;
        }}
        .date {{
            text-align: center;
            color: #999;
            font-size: 14px;
            margin-bottom: 40px;
        }}
        .section {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        .section h2 {{
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .champions {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        .champion-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .champion-card h3 {{
            color: #667eea;
            margin-top: 0;
        }}
        .champion-name {{
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin: 15px 0;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin: 15px 0;
        }}
        .metric {{
            background: #f0f4ff;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }}
        .metric-label {{
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 18px;
            font-weight: bold;
            color: #667eea;
        }}
        .signal {{
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            font-weight: bold;
            text-align: center;
        }}
        .signal-buy {{
            background: #10b981;
            color: white;
        }}
        .signal-hold {{
            background: #f59e0b;
            color: white;
        }}
        .signal-rebalance {{
            background: #ef4444;
            color: white;
        }}
        .isin {{
            background: #e0e7ff;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            margin: 10px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .pass {{
            color: #10b981;
            font-weight: bold;
        }}
        .fail {{
            color: #ef4444;
            font-weight: bold;
        }}
        .footer {{
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Dual Momentum Portfolio</h1>
        <div class="subtitle">Stratégie Académique Antonacci Optimisée 2025</div>
        <div class="date">Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</div>
        
        <!-- CHAMPIONS -->
        <div class="section">
            <h2>🏆 ETF Champions Sélectionnés</h2>
            <div class="champions">
                <!-- PEA -->
                <div class="champion-card">
                    <h3>📍 PEA</h3>
                    <div class="champion-name">{champion_pea['name']}</div>
                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-label">Score Momentum</div>
                            <div class="metric-value">{champion_pea['score']:.2f}%</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Rendement 3M</div>
                            <div class="metric-value">{champion_pea['r_3m']:+.2f}%</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Rendement 6M</div>
                            <div class="metric-value">{champion_pea['r_6m']:+.2f}%</div>
                        </div>
                    </div>
                    <div class="isin">ISIN : {champion_pea['isin']}</div>
                    <div class="signal signal-{signal_pea['action'].lower()}">
                        {signal_pea['action']}
                    </div>
                    <p style="text-align: center; color: #666;">
                        {signal_pea['reason']}
                    </p>
                </div>
                
                <!-- CTO -->
                <div class="champion-card">
                    <h3>📍 CTO</h3>
                    <div class="champion-name">{champion_cto['name']}</div>
                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-label">Score Momentum</div>
                            <div class="metric-value">{champion_cto['score']:.2f}%</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Rendement 3M</div>
                            <div class="metric-value">{champion_cto['r_3m']:+.2f}%</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Rendement 6M</div>
                            <div class="metric-value">{champion_cto['r_6m']:+.2f}%</div>
                        </div>
                    </div>
                    <div class="isin">ISIN : {champion_cto['isin']}</div>
                    <div class="signal signal-{signal_cto['action'].lower()}">
                        {signal_cto['action']}
                    </div>
                    <p style="text-align: center; color: #666;">
                        {signal_cto['reason']}
                    </p>
                </div>
            </div>
        </div>
        
        <!-- SCORES PEA -->
        <div class="section">
            <h2>📊 Scores Momentum - PEA (9 ETF)</h2>
            <table>
                <thead>
                    <tr>
                        <th>ETF</th>
                        <th>Score</th>
                        <th>R 1M</th>
                        <th>R 3M</th>
                        <th>R 6M</th>
                        <th>Prix</th>
                        <th>Filtres</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Scores PEA triés
    sorted_pea = sorted(scores_pea.items(), key=lambda x: x[1]['score'], reverse=True)
    for ticker, data in sorted_pea:
        filter_class = "pass" if data['filters_passed'] else "fail"
        filter_text = "✅ PASS" if data['filters_passed'] else "❌ FAIL"
        html += f"""
                    <tr>
                        <td><strong>{ticker}</strong></td>
                        <td>{data['score']:.2f}%</td>
                        <td>{data['r_1m']:+.2f}%</td>
                        <td>{data['r_3m']:+.2f}%</td>
                        <td>{data['r_6m']:+.2f}%</td>
                        <td>${data['price']:.2f}</td>
                        <td class="{filter_class}">{filter_text}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
        
        <!-- SCORES CTO -->
        <div class="section">
            <h2>📊 Scores Momentum - CTO (11 ETF)</h2>
            <table>
                <thead>
                    <tr>
                        <th>ETF</th>
                        <th>Score</th>
                        <th>R 1M</th>
                        <th>R 3M</th>
                        <th>R 6M</th>
                        <th>Prix</th>
                        <th>Filtres</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Scores CTO triés
    sorted_cto = sorted(scores_cto.items(), key=lambda x: x[1]['score'], reverse=True)
    for ticker, data in sorted_cto:
        filter_class = "pass" if data['filters_passed'] else "fail"
        filter_text = "✅ PASS" if data['filters_passed'] else "❌ FAIL"
        html += f"""
                    <tr>
                        <td><strong>{ticker}</strong></td>
                        <td>{data['score']:.2f}%</td>
                        <td>{data['r_1m']:+.2f}%</td>
                        <td>{data['r_3m']:+.2f}%</td>
                        <td>{data['r_6m']:+.2f}%</td>
                        <td>${data['price']:.2f}</td>
                        <td class="{filter_class}">{filter_text}</td>
                    </tr>
        """
    
    html += f"""
                </tbody>
            </table>
        </div>
        
        <!-- FOOTER -->
        <div class="footer">
            <p><strong>Dual Momentum Portfolio</strong> by GLOBAL ICON</p>
            <p>Stratégie académique basée sur les recherches de Gary Antonacci</p>
            <p style="color: #ef4444;">⚠️ Les données affichées sont simulées pour MVP. Intégration API réelle en Phase 2.</p>
        </div>
    </div>
</body>
</html>
    """
    
    # Sauvegarder fichier
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ Rapport HTML généré : {output_file}")
    return output_file

def main():
    print("\n" + "=" * 80)
    print("DUAL MOMENTUM PORTFOLIO - ANALYSE COMPLÈTE")
    print("=" * 80)
    
    # Positions actuelles (modifiables)
    CURRENT_PEA = "XLE"   # ← MODIFIER ICI votre position PEA actuelle
    CURRENT_CTO = "QQQ"   # ← MODIFIER ICI votre position CTO actuelle
    
    print(f"\n📍 Positions actuelles configurées :")
    print(f"   PEA : {CURRENT_PEA}")
    print(f"   CTO : {CURRENT_CTO}")
    
    # Initialiser portfolio
    portfolio = DualMomentumPortfolio()
    
    # Exécuter analyse
    report = portfolio.run_full_analysis(
        current_pea_ticker=CURRENT_PEA,
        current_cto_ticker=CURRENT_CTO
    )
    
    # Extraire résultats
    champion_pea = report['pea']['champion']
    champion_cto = report['cto']['champion']
    
    signal_pea = report['signals']['pea']
    signal_cto = report['signals']['cto']
    
    # Afficher résumé
    print("\n" + "=" * 80)
    print("RÉSUMÉ SIGNAUX TRADING")
    print("=" * 80)
    
    print(f"\n🏆 PEA CHAMPION : {champion_pea['name']}")
    print(f"   Score : {champion_pea['score']:.2f}%")
    print(f"   ISIN : {champion_pea['isin']}")
    print(f"   Signal : {signal_pea['action']}")
    print(f"   → {signal_pea['reason']}")
    
    print(f"\n🏆 CTO CHAMPION : {champion_cto['name']}")
    print(f"   Score : {champion_cto['score']:.2f}%")
    print(f"   ISIN : {champion_cto['isin']}")
    print(f"   Signal : {signal_cto['action']}")
    print(f"   → {signal_cto['reason']}")
    
    # Générer rapport HTML
    print("\n" + "=" * 80)
    print("GÉNÉRATION RAPPORT HTML")
    print("=" * 80)
    
    html_file = generate_html_report(report)
    
    print("\n" + "=" * 80)
    print("✅✅✅ ANALYSE TERMINÉE AVEC SUCCÈS ✅✅✅")
    print("=" * 80)
    
    print(f"\n📄 Rapport disponible : [computer://{html_file}]({html_file})")
    print("\n💡 Pour modifier positions actuelles, éditer lignes 174-175 de ce fichier")

if __name__ == "__main__":
    main()
