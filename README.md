# Gestionnaire de Projets Construction - Québec

Une application web de gestion de projets de construction développée spécifiquement pour le marché québécois, utilisant Streamlit et déployée sur Render.

## 🎯 Fonctionnalités

- **Gestion des projets** : Création, suivi et gestion complète des projets de construction
- **Tableau de bord** : Vue d'ensemble avec métriques et graphiques
- **Gestion des tâches** : Organisation par phases de construction typiques du Québec
- **Gestion des entrepreneurs** : Répertoire avec licences RBQ
- **Rapports visuels** : Graphiques et timeline des projets

## 🏗️ Types de projets supportés

- Résidentiel unifamilial
- Résidentiel multifamilial
- Commercial
- Industriel
- Infrastructure
- Rénovation
- Agrandissement

## 📋 Phases de construction

- Planification
- Permis et autorisations
- Excavation et fondations
- Structure
- Toiture
- Plomberie et électricité
- Isolation et cloisons
- Finition intérieure
- Finition extérieure
- Inspection finale

## 🚀 Installation locale

1. Clonez le repository :
```bash
git clone https://github.com/votre-nom/gestionnaire-construction-qc.git
cd gestionnaire-construction-qc
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancez l'application :
```bash
streamlit run app.py
```

## 🌐 Déploiement sur Render

1. Créez un compte sur [Render.com](https://render.com)
2. Connectez votre repository GitHub
3. Créez un nouveau "Web Service"
4. Configurez :
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
   - **Environment** : Python 3

## 📱 Interface utilisateur

L'application comprend :
- **Tableau de bord** : Métriques et graphiques de suivi
- **Gestion des projets** : CRUD complet avec filtres
- **Gestion des tâches** : Organisation par phases
- **Répertoire entrepreneurs** : Avec licences RBQ
- **Rapports visuels** : Timeline et statistiques

## 🔧 Technologies utilisées

- **Streamlit** : Framework web Python
- **Pandas** : Manipulation de données
- **Plotly** : Visualisations interactives
- **Python** : Langage de programmation

## 📊 Fonctionnalités spécifiques au Québec

- Types de projets adaptés au marché québécois
- Phases de construction selon les standards locaux
- Gestion des licences RBQ
- Interface en français
- Budget en dollars canadiens

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Ajouter des fonctionnalités

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 📞 Support

Pour toute question ou support, créez une issue sur GitHub.

---

Développé avec ❤️ pour l'industrie de la construction au Québec
