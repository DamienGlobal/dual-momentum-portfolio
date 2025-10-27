#!/bin/bash

################################################################################
# Script de Déploiement Automatique - Dual Momentum Portfolio
# Usage: bash deploy.sh
################################################################################

echo "========================================================================"
echo "🚀 DÉPLOIEMENT DUAL MOMENTUM PORTFOLIO"
echo "========================================================================"
echo ""

# Vérifier Python
echo "1️⃣ Vérification Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 non trouvé. Veuillez installer Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ Python détecté: $PYTHON_VERSION"
echo ""

# Vérifier pip
echo "2️⃣ Vérification pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip non trouvé. Installation..."
    python3 -m ensurepip --upgrade
fi
echo "✅ pip opérationnel"
echo ""

# Installer dépendances
echo "3️⃣ Installation dépendances..."
pip3 install --quiet --no-input -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Toutes les dépendances installées"
else
    echo "❌ Erreur installation dépendances"
    exit 1
fi
echo ""

# Tuer Streamlit existant
echo "4️⃣ Nettoyage processus existants..."
pkill -f "streamlit run app.py" 2>/dev/null
sleep 2
echo "✅ Processus nettoyés"
echo ""

# Lancer Streamlit
echo "5️⃣ Démarrage application Streamlit..."
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &
STREAMLIT_PID=$!

echo "✅ Streamlit lancé (PID: $STREAMLIT_PID)"
echo ""

# Attendre démarrage
echo "6️⃣ Vérification démarrage..."
sleep 5

if ps -p $STREAMLIT_PID > /dev/null; then
    echo "✅ Application opérationnelle"
    echo ""
    echo "========================================================================"
    echo "🎉 DÉPLOIEMENT RÉUSSI"
    echo "========================================================================"
    echo ""
    echo "📍 Application accessible sur:"
    echo "   → Local:    http://localhost:8501"
    echo "   → Réseau:   http://$(hostname -I | awk '{print $1}'):8501"
    echo ""
    echo "📝 Logs disponibles: streamlit.log"
    echo "🛑 Arrêter: pkill -f streamlit"
    echo ""
    echo "========================================================================"
else
    echo "❌ Erreur démarrage application"
    echo "Voir logs: cat streamlit.log"
    exit 1
fi
