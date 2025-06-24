import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import uuid

# Configuration de la page
st.set_page_config(
    page_title="Gestionnaire de Projets Construction QC",
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
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2a5298;
    }
    .status-actif { color: #28a745; font-weight: bold; }
    .status-pause { color: #ffc107; font-weight: bold; }
    .status-termine { color: #6c757d; font-weight: bold; }
    .status-retard { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialisation des données de session
def init_session_state():
    if 'projets' not in st.session_state:
        st.session_state.projets = []
    if 'taches' not in st.session_state:
        st.session_state.taches = []
    if 'entrepreneurs' not in st.session_state:
        st.session_state.entrepreneurs = []

# Types de projets de construction au Québec
TYPES_PROJETS = [
    "Résidentiel unifamilial",
    "Résidentiel multifamilial", 
    "Commercial",
    "Industriel",
    "Infrastructure",
    "Rénovation",
    "Agrandissement"
]

# Phases de construction typiques
PHASES_CONSTRUCTION = [
    "Planification",
    "Permis et autorisations",
    "Excavation et fondations",
    "Structure",
    "Toiture",
    "Plomberie et électricité",
    "Isolation et cloisons",
    "Finition intérieure",
    "Finition extérieure",
    "Inspection finale"
]

STATUTS = ["Actif", "En pause", "Terminé", "En retard"]

def ajouter_projet():
    st.subheader("➕ Nouveau Projet")
    
    with st.form("nouveau_projet"):
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("Nom du projet*")
            type_projet = st.selectbox("Type de projet", TYPES_PROJETS)
            client = st.text_input("Client")
            adresse = st.text_area("Adresse du chantier")
            
        with col2:
            budget = st.number_input("Budget ($CAD)", min_value=0.0, step=1000.0)
            date_debut = st.date_input("Date de début")
            date_fin = st.date_input("Date de fin prévue")
            statut = st.selectbox("Statut", STATUTS)
            
        description = st.text_area("Description du projet")
        
        submitted = st.form_submit_button("Créer le projet")
        
        if submitted and nom:
            nouveau_projet = {
                'id': str(uuid.uuid4()),
                'nom': nom,
                'type': type_projet,
                'client': client,
                'adresse': adresse,
                'budget': budget,
                'date_debut': date_debut.strftime('%Y-%m-%d'),
                'date_fin': date_fin.strftime('%Y-%m-%d'),
                'statut': statut,
                'description': description,
                'date_creation': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            st.session_state.projets.append(nouveau_projet)
            st.success(f"Projet '{nom}' créé avec succès!")
            st.experimental_rerun()

def afficher_projets():
    st.subheader("📋 Liste des Projets")
    
    if not st.session_state.projets:
        st.info("Aucun projet créé. Utilisez l'onglet 'Nouveau Projet' pour commencer.")
        return
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    with col1:
        filtre_statut = st.selectbox("Filtrer par statut", ["Tous"] + STATUTS)
    with col2:
        filtre_type = st.selectbox("Filtrer par type", ["Tous"] + TYPES_PROJETS)
    with col3:
        recherche = st.text_input("Rechercher par nom")
    
    # Application des filtres
    projets_filtres = st.session_state.projets
    if filtre_statut != "Tous":
        projets_filtres = [p for p in projets_filtres if p['statut'] == filtre_statut]
    if filtre_type != "Tous":
        projets_filtres = [p for p in projets_filtres if p['type'] == filtre_type]
    if recherche:
        projets_filtres = [p for p in projets_filtres if recherche.lower() in p['nom'].lower()]
    
    # Affichage des projets
    for i, projet in enumerate(projets_filtres):
        with st.expander(f"🏗️ {projet['nom']} - {projet['statut']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Client:** {projet['client']}")
                st.write(f"**Type:** {projet['type']}")
                st.write(f"**Adresse:** {projet['adresse']}")
                
            with col2:
                st.write(f"**Budget:** {projet['budget']:,.0f} $CAD")
                st.write(f"**Début:** {projet['date_debut']}")
                st.write(f"**Fin prévue:** {projet['date_fin']}")
                
            with col3:
                statut_class = f"status-{projet['statut'].lower().replace(' ', '-').replace('é', 'e')}"
                st.markdown(f"**Statut:** <span class='{statut_class}'>{projet['statut']}</span>", 
                          unsafe_allow_html=True)
                
                # Calcul du pourcentage d'avancement
                date_debut = datetime.strptime(projet['date_debut'], '%Y-%m-%d')
                date_fin = datetime.strptime(projet['date_fin'], '%Y-%m-%d')
                date_actuelle = datetime.now()
                
                if date_actuelle < date_debut:
                    progression = 0
                elif date_actuelle > date_fin:
                    progression = 100
                else:
                    duree_totale = (date_fin - date_debut).days
                    duree_ecoulee = (date_actuelle - date_debut).days
                    progression = min(100, max(0, (duree_ecoulee / duree_totale) * 100))
                
                st.progress(progression / 100)
                st.write(f"**Progression:** {progression:.1f}%")
            
            if st.button(f"Supprimer {projet['nom']}", key=f"del_{projet['id']}"):
                st.session_state.projets = [p for p in st.session_state.projets if p['id'] != projet['id']]
                st.experimental_rerun()

def gestion_taches():
    st.subheader("✅ Gestion des Tâches")
    
    if not st.session_state.projets:
        st.warning("Créez d'abord un projet pour ajouter des tâches.")
        return
    
    # Sélection du projet
    noms_projets = [p['nom'] for p in st.session_state.projets]
    projet_selectionne = st.selectbox("Sélectionner un projet", noms_projets)
    
    if projet_selectionne:
        projet_id = next(p['id'] for p in st.session_state.projets if p['nom'] == projet_selectionne)
        
        # Ajout de nouvelle tâche
        with st.expander("➕ Ajouter une tâche"):
            with st.form("nouvelle_tache"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nom_tache = st.text_input("Nom de la tâche*")
                    phase = st.selectbox("Phase de construction", PHASES_CONSTRUCTION)
                    priorite = st.selectbox("Priorité", ["Faible", "Moyenne", "Élevée", "Critique"])
                    
                with col2:
                    date_debut_tache = st.date_input("Date de début", key="tache_debut")
                    date_fin_tache = st.date_input("Date de fin", key="tache_fin")
                    statut_tache = st.selectbox("Statut", ["À faire", "En cours", "Terminée", "Bloquée"])
                
                description_tache = st.text_area("Description")
                
                if st.form_submit_button("Ajouter la tâche") and nom_tache:
                    nouvelle_tache = {
                        'id': str(uuid.uuid4()),
                        'projet_id': projet_id,
                        'nom': nom_tache,
                        'phase': phase,
                        'priorite': priorite,
                        'date_debut': date_debut_tache.strftime('%Y-%m-%d'),
                        'date_fin': date_fin_tache.strftime('%Y-%m-%d'),
                        'statut': statut_tache,
                        'description': description_tache
                    }
                    st.session_state.taches.append(nouvelle_tache)
                    st.success("Tâche ajoutée avec succès!")
                    st.experimental_rerun()
        
        # Affichage des tâches du projet
        taches_projet = [t for t in st.session_state.taches if t['projet_id'] == projet_id]
        
        if taches_projet:
            st.write(f"**Tâches pour le projet: {projet_selectionne}**")
            
            for tache in taches_projet:
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{tache['nom']}** - {tache['phase']}")
                    
                with col2:
                    couleur_priorite = {
                        "Faible": "🟢", "Moyenne": "🟡", 
                        "Élevée": "🟠", "Critique": "🔴"
                    }
                    st.write(f"{couleur_priorite[tache['priorite']]} {tache['priorite']}")
                    
                with col3:
                    st.write(f"{tache['date_debut']} → {tache['date_fin']}")
                    
                with col4:
                    if st.button("🗑️", key=f"del_tache_{tache['id']}"):
                        st.session_state.taches = [t for t in st.session_state.taches if t['id'] != tache['id']]
                        st.experimental_rerun()
        else:
            st.info("Aucune tâche pour ce projet.")

def tableau_bord():
    st.subheader("📊 Tableau de Bord")
    
    if not st.session_state.projets:
        st.info("Aucune donnée à afficher. Créez des projets pour voir les statistiques.")
        return
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Projets totaux", len(st.session_state.projets))
        
    with col2:
        projets_actifs = len([p for p in st.session_state.projets if p['statut'] == 'Actif'])
        st.metric("Projets actifs", projets_actifs)
        
    with col3:
        budget_total = sum(p['budget'] for p in st.session_state.projets)
        st.metric("Budget total", f"{budget_total:,.0f} $CAD")
        
    with col4:
        taches_total = len(st.session_state.taches)
        st.metric("Tâches totales", taches_total)
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        # Répartition par statut
        df_statuts = pd.DataFrame(st.session_state.projets)
        if not df_statuts.empty:
            statut_counts = df_statuts['statut'].value_counts()
            fig_statuts = px.pie(
                values=statut_counts.values,
                names=statut_counts.index,
                title="Répartition des projets par statut"
            )
            st.plotly_chart(fig_statuts, use_container_width=True)
    
    with col2:
        # Répartition par type
        if not df_statuts.empty:
            type_counts = df_statuts['type'].value_counts()
            fig_types = px.bar(
                x=type_counts.index,
                y=type_counts.values,
                title="Projets par type de construction",
                labels={'x': 'Type de projet', 'y': 'Nombre de projets'}
            )
            fig_types.update_xaxis(tickangle=45)
            st.plotly_chart(fig_types, use_container_width=True)
    
    # Timeline des projets
    if st.session_state.projets:
        st.subheader("📅 Timeline des Projets")
        
        timeline_data = []
        for projet in st.session_state.projets:
            timeline_data.append({
                'Projet': projet['nom'],
                'Début': projet['date_debut'],
                'Fin': projet['date_fin'],
                'Statut': projet['statut']
            })
        
        df_timeline = pd.DataFrame(timeline_data)
        df_timeline['Début'] = pd.to_datetime(df_timeline['Début'])
        df_timeline['Fin'] = pd.to_datetime(df_timeline['Fin'])
        
        fig_timeline = px.timeline(
            df_timeline,
            x_start="Début",
            x_end="Fin",
            y="Projet",
            color="Statut",
            title="Calendrier des Projets"
        )
        fig_timeline.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_timeline, use_container_width=True)

def gestion_entrepreneurs():
    st.subheader("👷 Gestion des Entrepreneurs")
    
    # Ajout d'entrepreneur
    with st.expander("➕ Ajouter un entrepreneur"):
        with st.form("nouvel_entrepreneur"):
            col1, col2 = st.columns(2)
            
            with col1:
                nom_entreprise = st.text_input("Nom de l'entreprise*")
                contact = st.text_input("Personne contact")
                telephone = st.text_input("Téléphone")
                
            with col2:
                email = st.text_input("Email")
                specialite = st.selectbox("Spécialité", [
                    "Excavation", "Fondation", "Charpente", "Toiture",
                    "Plomberie", "Électricité", "Isolation", "Cloisons sèches",
                    "Peinture", "Carrelage", "Menuiserie", "Autre"
                ])
                licence_rbq = st.text_input("Licence RBQ")
            
            adresse = st.text_area("Adresse")
            notes = st.text_area("Notes")
            
            if st.form_submit_button("Ajouter l'entrepreneur") and nom_entreprise:
                nouvel_entrepreneur = {
                    'id': str(uuid.uuid4()),
                    'nom_entreprise': nom_entreprise,
                    'contact': contact,
                    'telephone': telephone,
                    'email': email,
                    'specialite': specialite,
                    'licence_rbq': licence_rbq,
                    'adresse': adresse,
                    'notes': notes
                }
                st.session_state.entrepreneurs.append(nouvel_entrepreneur)
                st.success("Entrepreneur ajouté avec succès!")
                st.experimental_rerun()
    
    # Liste des entrepreneurs
    if st.session_state.entrepreneurs:
        st.write("**Liste des Entrepreneurs**")
        
        for entrepreneur in st.session_state.entrepreneurs:
            with st.expander(f"🏢 {entrepreneur['nom_entreprise']} - {entrepreneur['specialite']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Contact:** {entrepreneur['contact']}")
                    st.write(f"**Téléphone:** {entrepreneur['telephone']}")
                    st.write(f"**Email:** {entrepreneur['email']}")
                    
                with col2:
                    st.write(f"**Spécialité:** {entrepreneur['specialite']}")
                    st.write(f"**Licence RBQ:** {entrepreneur['licence_rbq']}")
                    st.write(f"**Adresse:** {entrepreneur['adresse']}")
                
                if entrepreneur['notes']:
                    st.write(f"**Notes:** {entrepreneur['notes']}")
                
                if st.button(f"Supprimer {entrepreneur['nom_entreprise']}", key=f"del_entr_{entrepreneur['id']}"):
                    st.session_state.entrepreneurs = [e for e in st.session_state.entrepreneurs if e['id'] != entrepreneur['id']]
                    st.experimental_rerun()
    else:
        st.info("Aucun entrepreneur enregistré.")

# Interface principale
def main():
    init_session_state()
    
    # En-tête
    st.markdown("""
    <div class="main-header">
        <h1>🏗️ Gestionnaire de Projets Construction - Québec</h1>
        <p>Gérez vos projets de construction en conformité avec les standards québécois</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Barre latérale
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choisir une section",
        ["Tableau de Bord", "Projets", "Nouveau Projet", "Tâches", "Entrepreneurs"]
    )
    
    # Informations système
    st.sidebar.markdown("---")
    st.sidebar.info(f"""
    **Projets:** {len(st.session_state.projets)}
    **Tâches:** {len(st.session_state.taches)}
    **Entrepreneurs:** {len(st.session_state.entrepreneurs)}
    """)
    
    # Affichage des pages
    if page == "Tableau de Bord":
        tableau_bord()
    elif page == "Projets":
        afficher_projets()
    elif page == "Nouveau Projet":
        ajouter_projet()
    elif page == "Tâches":
        gestion_taches()
    elif page == "Entrepreneurs":
        gestion_entrepreneurs()

if __name__ == "__main__":
    main()
