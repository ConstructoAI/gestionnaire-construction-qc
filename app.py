import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import uuid

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

# Initialisation des données de session
if 'projets' not in st.session_state:
    st.session_state.projets = []

if 'entrepreneurs' not in st.session_state:
    st.session_state.entrepreneurs = []

if 'phases' not in st.session_state:
    st.session_state.phases = []

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🏗️ Gestionnaire de Projets Construction - Québec</h1>
    <p>Gérez vos projets de construction en conformité avec les standards québécois</p>
</div>
""", unsafe_allow_html=True)

# Sidebar pour navigation
st.sidebar.title("📋 Navigation")
page = st.sidebar.selectbox(
    "Choisir une section",
    ["📊 Tableau de bord", "➕ Nouveau Projet", "🏢 Projets", "👷 Entrepreneurs", "📈 Phases & Suivi", "📋 Licences RBQ"]
)

# ========== TABLEAU DE BORD ==========
if page == "📊 Tableau de bord":
    st.header("📊 Vue d'ensemble")
    
    if len(st.session_state.projets) > 0:
        df_projets = pd.DataFrame(st.session_state.projets)
        
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
                
                st.session_state.projets.append(nouveau_projet)
                st.success(f"✅ Projet '{nom_projet}' créé avec succès!")
                st.info(f"📊 Total projets: {len(st.session_state.projets)}")
                
                # Réinitialiser les champs après création
                st.session_state.nom_projet_input = ""
                st.session_state.client_input = ""
                st.session_state.adresse_input = ""
                st.session_state.description_input = ""
                st.session_state.budget_input = 0.0
                
                st.balloons()  # Animation de succès
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la création: {str(e)}")
        else:
            st.error("❌ Le nom du projet est obligatoire.")
    
    # Affichage des projets existants en aperçu
    if len(st.session_state.projets) > 0:
        st.markdown("---")
        st.subheader("📋 Projets récents")
        for i, projet in enumerate(st.session_state.projets[-3:]):  # Afficher les 3 derniers
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
    
    if len(st.session_state.projets) > 0:
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
        df_projets = pd.DataFrame(st.session_state.projets)
        
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
                        st.session_state.projets.append(nouveau_projet)
                        st.success("Projet dupliqué!")
                        st.rerun()
                
                with col3:
                    if st.button(f"Supprimer", key=f"del_{projet['id']}", type="secondary"):
                        st.session_state.projets = [p for p in st.session_state.projets if p['id'] != projet['id']]
                        st.success("Projet supprimé!")
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
                    
                    st.session_state.entrepreneurs.append(nouvel_entrepreneur)
                    st.success(f"Entrepreneur '{nom_entreprise}' ajouté avec succès!")
                    st.rerun()
                else:
                    st.error("Le nom de l'entreprise est obligatoire.")
    
    # Liste des entrepreneurs
    if len(st.session_state.entrepreneurs) > 0:
        st.subheader("📋 Liste des Entrepreneurs")
        
        for entrepreneur in st.session_state.entrepreneurs:
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
                    st.session_state.entrepreneurs = [e for e in st.session_state.entrepreneurs if e['id'] != entrepreneur['id']]
                    st.success("Entrepreneur supprimé!")
                    st.rerun()
    else:
        st.info("Aucun entrepreneur enregistré.")

# ========== PHASES & SUIVI ==========
elif page == "📈 Phases & Suivi":
    st.header("📈 Phases & Suivi des Projets")
    
    if len(st.session_state.projets) > 0:
        # Sélection du projet
        projet_selectionne = st.selectbox(
            "Sélectionner un projet",
            options=[p['nom_projet'] for p in st.session_state.projets],
            key="select_projet_phase"
        )
        
        if projet_selectionne:
            projet = next(p for p in st.session_state.projets if p['nom_projet'] == projet_selectionne)
            
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
                            ["Non assigné"] + [e['nom_entreprise'] for e in st.session_state.entrepreneurs]
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
                        
                        st.session_state.phases.append(nouvelle_phase)
                        st.success(f"Phase '{nom_phase}' ajoutée!")
                        st.rerun()
            
            # Affichage des phases du projet
            phases_projet = [p for p in st.session_state.phases if p['projet_id'] == projet['id']]
            
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
                                # Mise à jour dans la session
                                for i, p in enumerate(st.session_state.phases):
                                    if p['id'] == phase['id']:
                                        st.session_state.phases[i]['pourcentage'] = nouveau_pourcentage
                                        break
                                st.rerun()
                        
                        if phase['notes']:
                            st.write(f"**Notes:** {phase['notes']}")
                        
                        if st.button(f"Supprimer phase", key=f"del_phase_{phase['id']}", type="secondary"):
                            st.session_state.phases = [p for p in st.session_state.phases if p['id'] != phase['id']]
                            st.success("Phase supprimée!")
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
    if len(st.session_state.entrepreneurs) > 0:
        st.subheader("🔍 Vérification des Licences")
        
        entrepreneurs_avec_licence = [e for e in st.session_state.entrepreneurs if e['licence_rbq']]
        entrepreneurs_sans_licence = [e for e in st.session_state.entrepreneurs if not e['licence_rbq']]
        
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

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    Gestionnaire de Projets Construction - Québec | Conforme aux standards québécois<br>
    Développé pour faciliter la gestion de projets de construction
</div>
""", unsafe_allow_html=True)
