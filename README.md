# 📊 Dual Momentum Portfolio - Stratégie Académique Antonacci

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Application web automatisée pour optimiser votre portefeuille PEA + CTO selon la stratégie Dual Momentum de Gary Antonacci**

🔗 **[Demo Live](https://votre-app.streamlit.app)** (À configurer après déploiement)

---

## 🎯 Fonctionnalités

- ✅ **Analyse automatique** 20 ETF (9 PEA + 11 CTO)
- ✅ **Scores momentum** avec formules académiques (12% / 40% / 48%)
- ✅ **Filtres protection** (absolu, tendance, volatilité)
- ✅ **Signaux trading** visuels (ACHAT / HOLD / ROTATION)
- ✅ **Dashboard interactif** Streamlit
- ✅ **Export CSV/Excel** recommandations
- ✅ **Mise à jour transparente** multi-sources

---

## 🚀 Démarrage Rapide

### Installation Locale

```bash
# Cloner le repository
git clone https://github.com/VOTRE_USERNAME/dual-momentum-portfolio.git
cd dual-momentum-portfolio

# Installer dépendances
pip install -r requirements.txt

# Lancer application
streamlit run app.py
```

**L'application s'ouvre automatiquement** : `http://localhost:8501`

---

## 📖 Guide Utilisation

### 1. Configuration (Sidebar)
- Sélectionner positions actuelles PEA + CTO
- Définir période d'analyse (défaut : 2 ans)

### 2. Lancer Analyse
- Cliquer **"🚀 Lancer Analyse"**
- Attendre 5-10 secondes

### 3. Consulter Résultats
- **Champions sélectionnés** (meilleurs ETF)
- **Signaux trading** (recommandations)
- **Tableau scores** (tous les ETF)
- **Graphiques** comparatifs

### 4. Export Données
- Télécharger CSV scores PEA/CTO
- Télécharger signaux trading

---

## 🧮 Méthodologie Académique

### Formule Momentum Pondéré

```
Score = (12% × R_1mois) + (40% × R_3mois) + (48% × R_6mois)
```

**Références** :
- Antonacci, G. (2014). *"Dual Momentum Investing"*. McGraw-Hill.
- Jegadeesh & Titman (1993). *"Returns to Buying Winners"*. Journal of Finance.

### Filtres de Protection

1. **Filtre Absolu** : Score > 0
2. **Filtre Tendance** : Prix > SMA 10 mois
3. **Filtre Volatilité** : Vol 1M < 1.5× Vol 12M

---

## 🛠️ Stack Technique

- **Frontend** : Streamlit
- **Backend** : Python 3.11+
- **Données** : Yahoo Finance / Finnhub API
- **Visualisations** : Plotly
- **Calculs** : Pandas, NumPy

---

## 📂 Structure Projet

```
dual-momentum-portfolio/
├── app.py                          # Interface Streamlit
├── portfolio_engine.py             # Orchestrateur principal
├── momentum_engine.py              # Calculs académiques
├── data_fetcher_hybrid.py          # Récupération données
├── config_working.py               # Configuration 20 ETF
├── run_analysis.py                 # Script CLI + rapport HTML
├── requirements.txt                # Dépendances
└── README.md                       # Documentation
```

---

## 🔄 Automatisation Mensuelle

### Option 1 : Cron Linux

```bash
crontab -e

# Ajouter ligne (exécution 8h le 1er du mois)
0 8 1 * * cd /path/to/project && python3 run_analysis.py
```

### Option 2 : GitHub Actions

Créer `.github/workflows/monthly_update.yml` :

```yaml
name: Monthly Portfolio Update
on:
  schedule:
    - cron: '0 8 1 * *'
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: python3 run_analysis.py
```

---

## 🌐 Déploiement Streamlit Cloud (Gratuit)

1. **Fork ce repository** sur GitHub
2. Aller sur [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connecter compte GitHub
4. Sélectionner repository `dual-momentum-portfolio`
5. Fichier principal : `app.py`
6. Déployer en 1 clic

**Résultat** : URL publique type `https://votre-app.streamlit.app`

---

## ⚙️ Configuration

### Modifier Positions Actuelles

Éditer `run_analysis.py`, lignes 174-175 :

```python
CURRENT_PEA = "VT"   # Votre ETF PEA actuel
CURRENT_CTO = "QQQ"  # Votre ETF CTO actuel
```

### Ajouter Nouveaux ETF

Éditer `config_working.py` :

```python
PEA_ETFS_WORKING = {
    'NOUVEAU_ETF': {
        'isin': 'LU1234567890',
        'name': 'Nom ETF',
        'ticker_yahoo': 'TICKER',
        'ter': 0.0015,
        'type': 'actions'
    },
    # ... autres ETF
}
```

---

## 📊 Performance Système

| Opération | Durée |
|-----------|-------|
| Récupération données 20 ETF | 2-5 sec |
| Calculs momentum | < 1 sec |
| Génération signaux | < 0.5 sec |
| **TOTAL ANALYSE** | **5-10 sec** |

---

## 🐛 Résolution Problèmes

### Application ne démarre pas

```bash
pip install --upgrade -r requirements.txt
streamlit run app.py
```

### Erreur données API

Le système bascule automatiquement sur cache ou données simulées.

**Forcer mise à jour** :
```bash
rm cache_*.json
streamlit run app.py
```

---

## 📈 Roadmap

### Version 1.1 (Prochaine)
- [ ] Backtest historique 2015-2025
- [ ] Intégration API Yahoo Finance stable
- [ ] Notifications email mensuelles
- [ ] Graphiques performances cumulées

### Version 2.0 (Future)
- [ ] Support multi-portefeuilles
- [ ] Optimisation allocations (% par ETF)
- [ ] Machine Learning prédiction momentum
- [ ] Application mobile native

---

## 📜 Avertissement Légal

⚠️ **Cette application est fournie à titre éducatif uniquement.**

- Pas un conseil en investissement
- Performance passée ≠ garantie future
- Consultez un conseiller financier professionnel
- Décisions d'investissement à votre charge

**Utilisation à vos risques et périls.**

---

## 🙏 Remerciements

- **Gary Antonacci** : Recherches Dual Momentum
- **Yahoo Finance / Finnhub** : Données gratuites
- **Streamlit** : Framework interface
- **Python Community** : Écosystème data science

---

## 📧 Contact

**Développé par** : GLOBAL ICON

**Issues** : [GitHub Issues](https://github.com/VOTRE_USERNAME/dual-momentum-portfolio/issues)

---

## 📄 License

MIT License - Voir [LICENSE](LICENSE) pour détails

---

## ⭐ Star ce Repository !

Si cette application vous aide à optimiser vos investissements, **donnez une étoile** ⭐ !

---

**© 2025 GLOBAL ICON - Tous droits réservés**
