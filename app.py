import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import uuid
import sqlite3
import json
import os

# Configuration de la page
st.set_page_config(
    page_title="Gestionnaire de Projets Construction - Québec",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .project-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2a5298;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .status-actif { color: #28a745; font-weight: bold; }
    .status-pause { color: #ffc107; font-weight: bold; }
    .status-termine { color: #6c757d; font-weight: bold; }
    .status-annule { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ========== CONFIGURATION BASE DE DONNÉES ==========
DB_FILE = "construction_projects.db"

def init_database():
    """Initialise la base de données SQLite avec les tables nécessaires"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Table des projets
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projets (
            id TEXT PRIMARY KEY,
            nom_projet TEXT NOT NULL,
            type_projet TEXT,
            client TEXT,
            adresse TEXT,
            budget REAL,
            date_debut DATE,
            date_fin_prevue DATE,
            statut TEXT,
            description TEXT,
            date_creation TIMESTAMP
        )
    """)
    
    # Table des entrepreneurs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entrepreneurs (
            id TEXT PRIMARY KEY,
            nom_entreprise TEXT NOT NULL,
            contact_principal TEXT,
            telephone TEXT,
            email TEXT,
            licence_rbq TEXT,
            specialites TEXT,
            statut TEXT,
            notes TEXT,
            date_ajout TIMESTAMP
        )
    """)
    
    # Table des phases
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS phases (
            id TEXT PRIMARY KEY,
            projet_id TEXT,
            nom_phase TEXT,
            date_debut DATE,
            date_fin_prevue DATE,
            entrepreneur_assigne TEXT,
            statut TEXT,
            pourcentage INTEGER,
            cout_prevu REAL,
            notes TEXT,
            date_creation TIMESTAMP,
            FOREIGN KEY (projet_id) REFERENCES projets (id)
        )
    """)
    
    conn.commit()
    conn.close()

def get_projets():
    """Récupère tous les projets de la base de données"""
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT * FROM projets ORDER BY date_creation DESC", conn)
        conn.close()
        
        # Convertir les dates
        if not df.empty:
            df['date_debut'] = pd.to_datetime(df['date_debut']).dt.date
            df['date_fin_prevue'] = pd.to_datetime(df['date_fin_prevue']).dt.date
            df['date_creation'] = pd.to_datetime(df['date_creation'])
        
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Erreur lors du chargement des projets: {e}")
        return []

def save_projet(projet):
    """Sauvegarde un projet dans la base de données"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO projets 
            (id, nom_projet, type_projet, client, adresse, budget, date_debut, date_fin_prevue, statut, description, date_creation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            projet['id'], projet['nom_projet'], projet['type_projet'], projet['client'],
            projet['adresse'], projet['budget'], projet['date_debut'], projet['date_fin_prevue'],
            projet['statut'], projet['description'], projet['date_creation']
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde: {e}")
        return False

def delete_projet(projet_id):
    """Supprime un projet de la base de données"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Supprimer les phases associées
        cursor.execute("DELETE FROM phases WHERE projet_id = ?", (projet_id,))
        # Supprimer le projet
        cursor.execute("DELETE FROM projets WHERE id = ?", (projet_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la suppression: {e}")
        return False

def get_entrepreneurs():
    """Récupère tous les entrepreneurs de la base de données"""
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT * FROM entrepreneurs ORDER BY date_ajout DESC", conn)
        conn.close()
        
        # Convertir specialites de JSON vers liste
        if not df.empty:
            df['specialites'] = df['specialites'].apply(lambda x: json.loads(x) if x else [])
            df['date_ajout'] = pd.to_datetime(df['date_ajout'])
        
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Erreur lors du chargement des entrepreneurs: {e}")
        return []

def save_entrepreneur(entrepreneur):
    """Sauvegarde un entrepreneur dans la base de données"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Convertir la liste de spécialités en JSON
        specialites_json = json.dumps(entrepreneur['specialites'])
        
        cursor.execute("""
            INSERT OR REPLACE INTO entrepreneurs 
            (id, nom_entreprise, contact_principal, telephone, email, licence_rbq, specialites, statut, notes, date_ajout)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entrepreneur['id'], entrepreneur['nom_entreprise'], entrepreneur['contact_principal'],
            entrepreneur['telephone'], entrepreneur['email'], entrepreneur['licence_rbq'],
            specialites_json, entrepreneur['statut'], entrepreneur['notes'], entrepreneur['date_ajout']
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde de l'entrepreneur: {e}")
        return False

def delete_entrepreneur(entrepreneur_id):
    """Supprime un entrepreneur de la base de données"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entrepreneurs WHERE id = ?", (entrepreneur_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la suppression de l'entrepreneur: {e}")
        return False

def get_phases(projet_id=None):
    """Récupère les phases de la base de données"""
    try:
        conn = sqlite3.connect(DB_FILE)
        if projet_id:
            df = pd.read_sql_query("SELECT * FROM phases WHERE projet_id = ? ORDER BY date_creation", conn, params=(projet_id,))
        else:
            df = pd.read_sql_query("SELECT * FROM phases ORDER BY date_creation", conn)
        conn.close()
        
        # Convertir les dates
        if not df.empty:
            df['date_debut'] = pd.to_datetime(df['date_debut']).dt.date
            df['date_fin_prevue'] = pd.to_datetime(df['date_fin_prevue']).dt.date
            df['date_creation'] = pd.to_datetime(df['date_creation'])
        
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Erreur lors du chargement des phases: {e}")
        return []

def save_phase(phase):
    """Sauvegarde une phase dans la base de données"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO phases 
            (id, projet_id, nom_phase, date_debut, date_fin_prevue, entrepreneur_assigne, statut, pourcentage, cout_prevu, notes, date_creation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            phase['id'], phase['projet_id'], phase['nom_phase'], phase['date_debut'],
            phase['date_fin_prevue'], phase['entrepreneur_assigne'], phase['statut'],
            phase['pourcentage'], phase['cout_prevu'], phase['notes'], phase['date_creation']
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde de la phase: {e}")
        return False

def delete_phase(phase_id):
    """Supprime une phase de la base de données"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM phases WHERE id = ?", (phase_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la suppression de la phase: {e}")
        return False

def update_phase_progress(phase_id, pourcentage):
    """Met à jour le pourcentage d'avancement d'une phase"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE phases SET pourcentage = ? WHERE id = ?", (pourcentage, phase_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la mise à jour: {e}")
        return False

# Initialiser la base de données
init_database()

# Charger les données depuis la base de données
@st.cache_data(ttl=1)  # Cache pendant 1 seconde pour éviter les rechargements constants
def load_data():
    return {
        'projets': get_projets(),
        'entrepreneurs': get_entrepreneurs(),
        'phases': get_phases()
    }

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🏗️ Gestionnaire de Projets Construction - Québec</h1>
    <p>Gérez vos projets de construction en conformité avec les standards québécois</p>
    <small>💾 Données sauvegardées automatiquement dans SQLite</small>
</div>
""", unsafe_allow_html=True)

# Sidebar pour navigation
st.sidebar.title("📋 Navigation")
page = st.sidebar.selectbox(
    "Choisir une section",
    ["📊 Tableau de bord", "➕ Nouveau Projet", "🏢 Projets", "👷 Entrepreneurs", "📈 Phases & Suivi", "📋 Licences RBQ", "🗄️ Base de Données"]
)

# Sidebar info base de données
st.sidebar.markdown("---")
st.sidebar.markdown("### 🗄️ Base de Données")
if os.path.exists(DB_FILE):
    file_size = os.path.getsize(DB_FILE)
    st.sidebar.success(f"✅ Connectée ({file_size} bytes)")
else:
    st.sidebar.warning("⚠️ DB non trouvée")

# Charger les données
data = load_data()
projets = data['projets']
entrepreneurs = data['entrepreneurs']
phases = data['phases']

# ========== TABLEAU DE BORD ==========
if page == "📊 Tableau de bord":
    st.header("📊 Vue d'ensemble")
    
    if len(projets) > 0:
        df_projets = pd.DataFrame(projets)
        
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Projets", len(df_projets))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            projets_actifs = len(df_projets[df_projets['statut'] == 'Actif'])
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Projets Actifs", projets_actifs)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            budget_total = df_projets['budget'].sum()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Budget Total", f"{budget_total:,.0f} CAD")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            budget_moyen = df_projets['budget'].mean()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Budget Moyen", f"{budget_moyen:,.0f} CAD")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Répartition par Statut")
            status_counts = df_projets['statut'].value_counts()
            fig_pie = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Distribution des Statuts"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("📈 Budgets par Type")
            fig_bar = px.bar(
                df_projets,
                x='type_projet',
                y='budget',
                title="Budget par Type de Projet",
                color='statut'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Timeline des projets
        st.subheader("📅 Timeline des Projets")
        fig_timeline = px.timeline(
            df_projets,
            x_start='date_debut',
            x_end='date_fin_prevue',
            y='nom_projet',
            color='statut',
            title="Calendrier des Projets"
        )
        fig_timeline.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_timeline, use_container_width=True)
        
    else:
        st.info("🏗️ Aucun projet créé. Commencez par ajouter votre premier projet!")

# ========== NOUVEAU PROJET ==========
elif page == "➕ Nouveau Projet":
    st.header("➕ Nouveau Projet")
    
    # Version alternative sans st.form
    col1, col2 = st.columns(2)
    
    with col1:
        nom_projet = st.text_input("Nom du projet*", key="nom_projet_input")
        type_projet = st.selectbox(
            "Type de projet",
            ["Résidentiel unifamilial", "Résidentiel multifamilial", "Commercial", "Industriel", "Institutionnel", "Infrastructure"],
            key="type_projet_input"
        )
        client = st.text_input("Client", key="client_input")
        adresse = st.text_area("Adresse du chantier", key="adresse_input")
    
    with col2:
        budget = st.number_input("Budget (CAD)", min_value=0.0, step=1000.0, key="budget_input")
        date_debut = st.date_input("Date de début", value=datetime.now().date(), key="date_debut_input")
        date_fin_prevue = st.date_input("Date de fin prévue", value=datetime.now().date(), key="date_fin_input")
        statut = st.selectbox("Statut", ["Actif", "En pause", "Terminé", "Annulé"], key="statut_input")
    
    description = st.text_area("Description du projet", key="description_input")
    
    # Bouton de création
    if st.button("🚀 Créer le projet", type="primary", key="create_project_btn"):
        if nom_projet and nom_projet.strip():
            try:
                nouveau_projet = {
                    'id': str(uuid.uuid4()),
                    'nom_projet': nom_projet.strip(),
                    'type_projet': type_projet,
                    'client': client.strip() if client else "",
                    'adresse': adresse.strip() if adresse else "",
                    'budget': float(budget) if budget else 0.0,
                    'date_debut': date_debut,
                    'date_fin_prevue': date_fin_prevue,
                    'statut': statut,
                    'description': description.strip() if description else "",
                    'date_creation': datetime.now()
                }
                
                if save_projet(nouveau_projet):
                    st.success(f"✅ Projet '{nom_projet}' créé avec succès!")
                    st.info(f"💾 Sauvegardé dans la base de données")
                    st.balloons()  # Animation de succès
                    st.cache_data.clear()  # Effacer le cache pour recharger les données
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de la sauvegarde")
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la création: {str(e)}")
        else:
            st.error("❌ Le nom du projet est obligatoire.")
    
    # Affichage des projets existants en aperçu
    if len(projets) > 0:
        st.markdown("---")
        st.subheader("📋 Projets récents")
        for i, projet in enumerate(projets[:3]):  # Afficher les 3 derniers
            with st.expander(f"🏗️ {projet['nom_projet']} - {projet['statut']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Type:** {projet['type_projet']}")
                    st.write(f"**Client:** {projet['client']}")
                with col2:
                    st.write(f"**Budget:** {projet['budget']:,.0f} CAD")
                    st.write(f"**Statut:** {projet['statut']}")

# ========== GESTION DES PROJETS ==========
elif page == "🏢 Projets":
    st.header("🏢 Gestion des Projets")
    
    if len(projets) > 0:
        # Filtres
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filtre_statut = st.multiselect(
                "Filtrer par statut",
                ["Actif", "En pause", "Terminé", "Annulé"],
                default=["Actif", "En pause"]
            )
        
        with col2:
            filtre_type = st.multiselect(
                "Filtrer par type",
                ["Résidentiel unifamilial", "Résidentiel multifamilial", "Commercial", "Industriel", "Institutionnel", "Infrastructure"]
            )
        
        with col3:
            recherche = st.text_input("🔍 Rechercher un projet")
        
        # Application des filtres
        df_projets = pd.DataFrame(projets)
        
        if filtre_statut:
            df_projets = df_projets[df_projets['statut'].isin(filtre_statut)]
        
        if filtre_type:
            df_projets = df_projets[df_projets['type_projet'].isin(filtre_type)]
        
        if recherche:
            df_projets = df_projets[
                df_projets['nom_projet'].str.contains(recherche, case=False, na=False) |
                df_projets['client'].str.contains(recherche, case=False, na=False)
            ]
        
        # Affichage des projets
        for idx, projet in df_projets.iterrows():
            with st.expander(f"🏗️ {projet['nom_projet']} - {projet['statut']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Type:** {projet['type_projet']}")
                    st.write(f"**Client:** {projet['client']}")
                    st.write(f"**Budget:** {projet['budget']:,.0f} CAD")
                    st.write(f"**Statut:** {projet['statut']}")
                
                with col2:
                    st.write(f"**Date début:** {projet['date_debut']}")
                    st.write(f"**Date fin prévue:** {projet['date_fin_prevue']}")
                    st.write(f"**Adresse:** {projet['adresse']}")
                
                if projet['description']:
                    st.write(f"**Description:** {projet['description']}")
                
                # Actions
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"Modifier", key=f"edit_{projet['id']}"):
                        st.info("Fonctionnalité de modification à implémenter")
                
                with col2:
                    if st.button(f"Dupliquer", key=f"dup_{projet['id']}"):
                        nouveau_projet = projet.copy()
                        nouveau_projet['id'] = str(uuid.uuid4())
                        nouveau_projet['nom_projet'] = f"{projet['nom_projet']} - Copie"
                        nouveau_projet['date_creation'] = datetime.now()
                        if save_projet(nouveau_projet):
                            st.success("Projet dupliqué!")
                            st.cache_data.clear()
                            st.rerun()
                
                with col3:
                    if st.button(f"Supprimer", key=f"del_{projet['id']}", type="secondary"):
                        if delete_projet(projet['id']):
                            st.success("Projet supprimé!")
                            st.cache_data.clear()
                            st.rerun()
    
    else:
        st.info("Aucun projet trouvé. Créez votre premier projet!")

# ========== ENTREPRENEURS ==========
elif page == "👷 Entrepreneurs":
    st.header("👷 Gestion des Entrepreneurs")
    
    # Formulaire pour ajouter un entrepreneur
    with st.expander("➕ Ajouter un Entrepreneur"):
        with st.form("nouvel_entrepreneur"):
            col1, col2 = st.columns(2)
            
            with col1:
                nom_entreprise = st.text_input("Nom de l'entreprise*")
                contact_principal = st.text_input("Contact principal")
                telephone = st.text_input("Téléphone")
                email = st.text_input("Email")
            
            with col2:
                licence_rbq = st.text_input("Numéro de licence RBQ")
                specialites = st.multiselect(
                    "Spécialités",
                    ["Général", "Électricité", "Plomberie", "HVAC", "Charpente", "Maçonnerie", "Toiture", "Isolation", "Peinture", "Carrelage"]
                )
                statut_entrepreneur = st.selectbox("Statut", ["Actif", "Inactif", "En évaluation"])
            
            notes = st.text_area("Notes")
            
            submit_entrepreneur = st.form_submit_button("Ajouter l'entrepreneur")
            
            if submit_entrepreneur:
                if nom_entreprise:
                    nouvel_entrepreneur = {
                        'id': str(uuid.uuid4()),
                        'nom_entreprise': nom_entreprise,
                        'contact_principal': contact_principal,
                        'telephone': telephone,
                        'email': email,
                        'licence_rbq': licence_rbq,
                        'specialites': specialites,
                        'statut': statut_entrepreneur,
                        'notes': notes,
                        'date_ajout': datetime.now()
                    }
                    
                    if save_entrepreneur(nouvel_entrepreneur):
                        st.success(f"Entrepreneur '{nom_entreprise}' ajouté avec succès!")
                        st.cache_data.clear()
                        st.rerun()
                else:
                    st.error("Le nom de l'entreprise est obligatoire.")
    
    # Liste des entrepreneurs
    if len(entrepreneurs) > 0:
        st.subheader("📋 Liste des Entrepreneurs")
        
        for entrepreneur in entrepreneurs:
            with st.expander(f"🏢 {entrepreneur['nom_entreprise']} - {entrepreneur['statut']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Contact:** {entrepreneur['contact_principal']}")
                    st.write(f"**Téléphone:** {entrepreneur['telephone']}")
                    st.write(f"**Email:** {entrepreneur['email']}")
                    st.write(f"**Licence RBQ:** {entrepreneur['licence_rbq']}")
                
                with col2:
                    st.write(f"**Spécialités:** {', '.join(entrepreneur['specialites'])}")
                    st.write(f"**Statut:** {entrepreneur['statut']}")
                    if entrepreneur['notes']:
                        st.write(f"**Notes:** {entrepreneur['notes']}")
                
                if st.button(f"Supprimer", key=f"del_ent_{entrepreneur['id']}", type="secondary"):
                    if delete_entrepreneur(entrepreneur['id']):
                        st.success("Entrepreneur supprimé!")
                        st.cache_data.clear()
                        st.rerun()
    else:
        st.info("Aucun entrepreneur enregistré.")

# ========== PHASES & SUIVI ==========
elif page == "📈 Phases & Suivi":
    st.header("📈 Phases & Suivi des Projets")
    
    if len(projets) > 0:
        # Sélection du projet
        projet_selectionne = st.selectbox(
            "Sélectionner un projet",
            options=[p['nom_projet'] for p in projets],
            key="select_projet_phase"
        )
        
        if projet_selectionne:
            projet = next(p for p in projets if p['nom_projet'] == projet_selectionne)
            
            # Phases prédéfinies pour le Québec
            phases_standard = [
                "Permis et autorisations",
                "Préparation du terrain",
                "Fondations",
                "Charpente",
                "Toiture",
                "Plomberie",
                "Électricité",
                "Isolation",
                "Cloisons sèches",
                "Revêtements de sol",
                "Peinture",
                "Finitions",
                "Inspection finale"
            ]
            
            # Ajouter une phase
            with st.expander("➕ Ajouter une Phase"):
                with st.form("nouvelle_phase"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nom_phase = st.selectbox("Phase", phases_standard)
                        date_debut_phase = st.date_input("Date de début")
                        date_fin_prevue_phase = st.date_input("Date de fin prévue")
                    
                    with col2:
                        entrepreneur_assigne = st.selectbox(
                            "Entrepreneur assigné",
                            ["Non assigné"] + [e['nom_entreprise'] for e in entrepreneurs]
                        )
                        statut_phase = st.selectbox("Statut", ["À venir", "En cours", "Terminé", "En retard"])
                        pourcentage = st.slider("Pourcentage d'avancement", 0, 100, 0)
                    
                    cout_prevu = st.number_input("Coût prévu (CAD)", min_value=0.0)
                    notes_phase = st.text_area("Notes")
                    
                    submit_phase = st.form_submit_button("Ajouter la phase")
                    
                    if submit_phase:
                        nouvelle_phase = {
                            'id': str(uuid.uuid4()),
                            'projet_id': projet['id'],
                            'nom_phase': nom_phase,
                            'date_debut': date_debut_phase,
                            'date_fin_prevue': date_fin_prevue_phase,
                            'entrepreneur_assigne': entrepreneur_assigne,
                            'statut': statut_phase,
                            'pourcentage': pourcentage,
                            'cout_prevu': cout_prevu,
                            'notes': notes_phase,
                            'date_creation': datetime.now()
                        }
                        
                        if save_phase(nouvelle_phase):
                            st.success(f"Phase '{nom_phase}' ajoutée!")
                            st.cache_data.clear()
                            st.rerun()
            
            # Affichage des phases du projet
            phases_projet = get_phases(projet['id'])
            
            if phases_projet:
                st.subheader(f"📋 Phases de {projet_selectionne}")
                
                # Graphique d'avancement
                df_phases = pd.DataFrame(phases_projet)
                fig_gantt = px.timeline(
                    df_phases,
                    x_start='date_debut',
                    x_end='date_fin_prevue',
                    y='nom_phase',
                    color='statut',
                    title="Diagramme de Gantt"
                )
                fig_gantt.update_yaxes(autorange="reversed")
                st.plotly_chart(fig_gantt, use_container_width=True)
                
                # Liste détaillée des phases
                for phase in phases_projet:
                    with st.expander(f"📅 {phase['nom_phase']} - {phase['statut']} ({phase['pourcentage']}%)"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**Début:** {phase['date_debut']}")
                            st.write(f"**Fin prévue:** {phase['date_fin_prevue']}")
                            st.write(f"**Entrepreneur:** {phase['entrepreneur_assigne']}")
                        
                        with col2:
                            st.write(f"**Statut:** {phase['statut']}")
                            st.write(f"**Avancement:** {phase['pourcentage']}%")
                            st.write(f"**Coût prévu:** {phase['cout_prevu']:,.0f} CAD")
                        
                        with col3:
                            # Mise à jour du pourcentage
                            nouveau_pourcentage = st.slider(
                                "Mettre à jour l'avancement",
                                0, 100,
                                phase['pourcentage'],
                                key=f"progress_{phase['id']}"
                            )
                            
                            if nouveau_pourcentage != phase['pourcentage']:
                                if update_phase_progress(phase['id'], nouveau_pourcentage):
                                    st.success("Avancement mis à jour!")
                                    st.cache_data.clear()
                                    st.rerun()
                        
                        if phase['notes']:
                            st.write(f"**Notes:** {phase['notes']}")
                        
                        if st.button(f"Supprimer phase", key=f"del_phase_{phase['id']}", type="secondary"):
                            if delete_phase(phase['id']):
                                st.success("Phase supprimée!")
                                st.cache_data.clear()
                                st.rerun()
            else:
                st.info("Aucune phase définie pour ce projet.")
    else:
        st.info("Créez d'abord un projet pour gérer les phases.")

# ========== LICENCES RBQ ==========
elif page == "📋 Licences RBQ":
    st.header("📋 Licences RBQ - Régie du bâtiment du Québec")
    
    st.info("""
    **Information importante:** Cette section vous aide à suivre les licences RBQ de vos entrepreneurs. 
    Vérifiez toujours la validité des licences sur le site officiel de la RBQ.
    """)
    
    # Vérification des licences des entrepreneurs
    if len(entrepreneurs) > 0:
        st.subheader("🔍 Vérification des Licences")
        
        entrepreneurs_avec_licence = [e for e in entrepreneurs if e['licence_rbq']]
        entrepreneurs_sans_licence = [e for e in entrepreneurs if not e['licence_rbq']]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Entrepreneurs avec licence", len(entrepreneurs_avec_licence))
        
        with col2:
            st.metric("Entrepreneurs sans licence", len(entrepreneurs_sans_licence))
        
        if entrepreneurs_avec_licence:
            st.subheader("✅ Entrepreneurs avec licence RBQ")
            for entrepreneur in entrepreneurs_avec_licence:
                with st.expander(f"🏢 {entrepreneur['nom_entreprise']} - {entrepreneur['licence_rbq']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Licence RBQ:** {entrepreneur['licence_rbq']}")
                        st.write(f"**Spécialités:** {', '.join(entrepreneur['specialites'])}")
                        st.write(f"**Contact:** {entrepreneur['contact_principal']}")
                    
                    with col2:
                        st.write(f"**Téléphone:** {entrepreneur['telephone']}")
                        st.write(f"**Email:** {entrepreneur['email']}")
                        st.write(f"**Statut:** {entrepreneur['statut']}")
                    
                    st.info("🔗 Vérifiez cette licence sur: https://www.rbq.gouv.qc.ca/")
        
        if entrepreneurs_sans_licence:
            st.subheader("⚠️ Entrepreneurs sans licence RBQ")
            for entrepreneur in entrepreneurs_sans_licence:
                st.warning(f"🏢 {entrepreneur['nom_entreprise']} - Aucune licence RBQ enregistrée")
    
    # Informations sur les types de licence RBQ
    st.subheader("📚 Types de Licences RBQ")
    
    types_licence = {
        "Entrepreneur général": "Construction, rénovation et réparation de bâtiments",
        "Entrepreneur spécialisé - Électricité": "Installation électrique",
        "Entrepreneur spécialisé - Plomberie": "Installation de plomberie et chauffage",
        "Entrepreneur spécialisé - Ventilation": "Système de ventilation et climatisation",
        "Entrepreneur spécialisé - Réfrigération": "Installation de réfrigération",
        "Entrepreneur spécialisé - Ascenseurs": "Installation et entretien d'ascenseurs"
    }
    
    for type_licence, description in types_licence.items():
        st.write(f"**{type_licence}:** {description}")
    
    st.markdown("---")
    st.info("Pour plus d'informations sur les licences RBQ, visitez: https://www.rbq.gouv.qc.ca/")

# ========== BASE DE DONNÉES ==========
elif page == "🗄️ Base de Données":
    st.header("🗄️ Gestion de la Base de Données")
    
    # Informations sur la base de données
    if os.path.exists(DB_FILE):
        file_size = os.path.getsize(DB_FILE)
        st.success(f"✅ Base de données connectée: {DB_FILE}")
        st.info(f"📊 Taille du fichier: {file_size:,} bytes")
    else:
        st.error("❌ Base de données non trouvée")
    
    # Statistiques
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🏗️ Projets", len(projets))
    
    with col2:
        st.metric("👷 Entrepreneurs", len(entrepreneurs))
    
    with col3:
        st.metric("📈 Phases", len(phases))
    
    st.markdown("---")
    
    # Actions sur la base de données
    st.subheader("🔧 Actions de Maintenance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Actualiser les données", type="primary"):
            st.cache_data.clear()
            st.success("Données actualisées!")
            st.rerun()
    
    with col2:
        if st.button("📊 Statistiques détaillées"):
            try:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                
                # Statistiques des tables
                cursor.execute("SELECT COUNT(*) FROM projets")
                nb_projets = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM entrepreneurs")
                nb_entrepreneurs = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM phases")
                nb_phases = cursor.fetchone()[0]
                
                cursor.execute("SELECT SUM(budget) FROM projets")
                budget_total = cursor.fetchone()[0] or 0
                
                conn.close()
                
                st.info(f"""
                **Statistiques de la base de données:**
                - Projets: {nb_projets}
                - Entrepreneurs: {nb_entrepreneurs}
                - Phases: {nb_phases}
                - Budget total: {budget_total:,.0f} CAD
                """)
                
            except Exception as e:
                st.error(f"Erreur lors de la récupération des statistiques: {e}")
    
    with col3:
        if st.button("🗑️ Nettoyer le cache"):
            st.cache_data.clear()
            st.success("Cache nettoyé!")
    
    # Sauvegarde et export
    st.subheader("💾 Sauvegarde et Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Exporter les projets (CSV)"):
            if len(projets) > 0:
                df_projets = pd.DataFrame(projets)
                csv = df_projets.to_csv(index=False)
                st.download_button(
                    label="⬇️ Télécharger projets.csv",
                    data=csv,
                    file_name="projets_construction.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Aucun projet à exporter")
    
    with col2:
        if st.button("📤 Exporter les entrepreneurs (CSV)"):
            if len(entrepreneurs) > 0:
                df_entrepreneurs = pd.DataFrame(entrepreneurs)
                # Convertir les spécialités en texte
                df_entrepreneurs['specialites'] = df_entrepreneurs['specialites'].apply(lambda x: ', '.join(x))
                csv = df_entrepreneurs.to_csv(index=False)
                st.download_button(
                    label="⬇️ Télécharger entrepreneurs.csv",
                    data=csv,
                    file_name="entrepreneurs_construction.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Aucun entrepreneur à exporter")
    
    # Informations techniques
    st.markdown("---")
    st.subheader("🔧 Informations Techniques")
    
    with st.expander("Voir les détails techniques"):
        st.write(f"**Fichier de base de données:** {DB_FILE}")
        st.write(f"**Type:** SQLite")
        st.write(f"**Tables:** projets, entrepreneurs, phases")
        
        if os.path.exists(DB_FILE):
            st.write(f"**Chemin complet:** {os.path.abspath(DB_FILE)}")
            st.write(f"**Dernière modification:** {datetime.fromtimestamp(os.path.getmtime(DB_FILE))}")
        
        st.code("""
        Tables de la base de données:
        
        1. projets:
           - id (TEXT PRIMARY KEY)
           - nom_projet, type_projet, client, adresse
           - budget (REAL), statut, description
           - date_debut, date_fin_prevue, date_creation
        
        2. entrepreneurs:
           - id (TEXT PRIMARY KEY)
           - nom_entreprise, contact_principal
           - telephone, email, licence_rbq
           - specialites (JSON), statut, notes
           - date_ajout
        
        3. phases:
           - id (TEXT PRIMARY KEY)
           - projet_id (FOREIGN KEY)
           - nom_phase, entrepreneur_assigne
           - date_debut, date_fin_prevue
           - statut, pourcentage, cout_prevu
           - notes, date_creation
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    Gestionnaire de Projets Construction - Québec | Conforme aux standards québécois<br>
    Développé pour faciliter la gestion de projets de construction | 💾 Données SQLite
</div>
""", unsafe_allow_html=True)
