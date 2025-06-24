projet_rapport = st.selectbox("Projet pour le rapport", [p['nom_projet'] for p in projets], key="rapport_auto")
            projet_id = next(p['id'] for p in projets if p['nom_projet'] == projet_rapport)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Rapport d'Avancement Automatique")
                
                if st.button("🔄 Générer Rapport d'Avancement"):
                    rapport_data = generer_rapport_automatique(projet_id)
                    projet_data = next(p for p in projets if p['id'] == projet_id)
                    
                    if rapport_data:
                        # Variables pour le modèle
                        variables = {
                            'nom_projet': projet_data['nom_projet'],
                            'client': projet_data['client'],
                            **rapport_data
                        }
                        
                        modele = get_modeles_predefined()['Rapport d\'Avancement']
                        sujet_auto = modele['sujet'].format(**variables)
                        contenu_auto = modele['contenu'].format(**variables)
                        
                        st.success("Rapport généré automatiquement!")
                        
                        # Affichage du rapport généré
                        with st.expander("📋 Aperçu du Rapport Généré"):
                            st.markdown(f"**Sujet:** {sujet_auto}")
                            st.markdown("**Contenu:**")
                            st.text_area("", value=contenu_auto, height=200, disabled=True)
                        
                        # Option pour sauvegarder
                        if st.button("💾 Sauvegarder ce Rapport"):
                            comm_data = (
                                str(uuid.uuid4()),
                                projet_id,
                                'Rapport',
                                sujet_auto,
                                contenu_auto,
                                projet_data['client'],
                                datetime.now(),
                                'Généré',
                                'Normale'
                            )
                            
                            if save_communication(comm_data):
                                st.success("Rapport sauvegardé!")
                                st.cache_data.clear()
            
            with col2:
                st.markdown("#### ⚠️ Alertes Automatiques")
                
                # Vérifier s'il y a des alertes à envoyer
                alertes_possibles = []
                projet_data = next(p for p in projets if p['id'] == projet_id)
                
                # Vérification deadline
                if projet_data['date_fin_prevue']:
                    jours_restants = (projet_data['date_fin_prevue'] - date.today()).days
                    if 0 <= jours_restants <= 7:
                        alertes_possibles.append({
                            'type': 'Deadline proche',
                            'message': f"Projet se termine dans {jours_restants} jour(s)"
                        })
                
                # Vérification budget
                depenses = get_depenses(projet_id)
                if depenses:
                    total_depenses = sum(d['montant'] for d in depenses)
                    if total_depenses > projet_data['budget'] * 0.9:
                        pourcentage = (total_depenses / projet_data['budget'] * 100)
                        alertes_possibles.append({
                            'type': 'Budget',
                            'message': f"Budget utilisé à {pourcentage:.0f}%"
                        })
                
                if alertes_possibles:
                    st.warning(f"🚨 {len(alertes_possibles)} alerte(s) détectée(s)")
                    for alerte in alertes_possibles:
                        st.write(f"• **{alerte['type']}**: {alerte['message']}")
                    
                    if st.button("📧 Générer Alertes Client"):
                        for alerte in alertes_possibles:
                            if alerte['type'] == 'Budget':
                                # Utiliser le modèle d'alerte budget
                                modele = get_modeles_predefined()['Alerte Budget']
                                variables = {
                                    'nom_projet': projet_data['nom_projet'],
                                    'client': projet_data['client'],
                                    'budget_initial': projet_data['budget'],
                                    'cout_actuel': total_depenses,
                                    'variance': total_depenses - projet_data['budget'],
                                    'raison_variance': 'Coûts supplémentaires identifiés'
                                }
                                
                                sujet_alerte = modele['sujet'].format(**variables)
                                contenu_alerte = modele['contenu'].format(**variables)
                                
                                comm_data = (
                                    str(uuid.uuid4()),
                                    projet_id,
                                    'Alerte',
                                    sujet_alerte,
                                    contenu_alerte,
                                    projet_data['client'],
                                    datetime.now(),
                                    'Alerte générée',
                                    'Élevée'
                                )
                                
                                save_communication(comm_data)
                        
                        st.success("Alertes générées et sauvegardées!")
                        st.cache_data.clear()
                else:
                    st.success("✅ Aucune alerte à envoyer pour ce projet")
        
        with tab4:
            # SUIVI CLIENT
            st.subheader("📊 Suivi de la Relation Client")
            
            # Statistiques de communication par projet
            stats_comm = {}
            for projet in projets:
                comms = get_communications(projet['id'])
                stats_comm[projet['nom_projet']] = {
                    'total': len(comms),
                    'derniere': max([c['date_envoi'] for c in comms], default='Jamais') if comms else 'Jamais',
                    'en_attente': len([c for c in comms if c['statut'] in ['Envoyé', 'Alerte générée']])
                }
            
            # Affichage des statistiques
            for projet_nom, stats in stats_comm.items():
                with st.expander(f"📊 {projet_nom} - {stats['total']} communication(s)"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Communications Total", stats['total'])
                    
                    with col2:
                        if stats['derniere'] != 'Jamais':
                            derniere_date = datetime.fromisoformat(stats['derniere'][:19])
                            jours_depuis = (datetime.now() - derniere_date).days
                            st.metric("Dernière Communication", f"Il y a {jours_depuis} jour(s)")
                        else:
                            st.metric("Dernière Communication", "Jamais")
                    
                    with col3:
                        st.metric("En Attente Réponse", stats['en_attente'])
                    
                    # Recommandations
                    if stats['derniere'] == 'Jamais':
                        st.warning("⚠️ Aucune communication enregistrée")
                    elif stats['derniere'] != 'Jamais':
                        derniere_date = datetime.fromisoformat(stats['derniere'][:19])
                        jours_depuis = (datetime.now() - derniere_date).days
                        if jours_depuis > 14:
                            st.info("💡 Suggestion: Envoyer un rapport d'avancement")
            
            # Graphique de fréquence des communications
            if any(stats['total'] > 0 for stats in stats_comm.values()):
                st.subheader("📈 Fréquence des Communications")
                
                df_stats = pd.DataFrame([
                    {'Projet': projet, 'Communications': stats['total']}
                    for projet, stats in stats_comm.items()
                ])
                
                fig_comm = px.bar(
                    df_stats,
                    x='Projet',
                    y='Communications',
                    title="Nombre de Communications par Projet"
                )
                st.plotly_chart(fig_comm, use_container_width=True)

# ========== TEMPLATES DOCUMENTS ==========
elif page == "📄 Templates Documents":
    st.header("📄 Templates de Documents")
    
    st.info("Générez rapidement des documents professionnels pour vos projets")
    
    if not projets:
        st.warning("Créez d'abord un projet.")
    else:
        # Types de documents
        types_documents = {
            'Devis': {
                'icone': '💰',
                'description': 'Devis détaillé pour le client',
                'template': """DEVIS - {nom_projet}

Client: {client}
Date: {date_actuelle}
Projet: {nom_projet}
Adresse: {adresse}

DÉTAIL DES TRAVAUX:
{detail_phases}

BUDGET TOTAL: {budget:,.2f} CAD (taxes incluses)

Conditions:
- Devis valable 30 jours
- Acompte de 30% à la signature
- Paiement final à la livraison

Cordialement,
[Votre Entreprise]"""
            },
            
            'Contrat Simple': {
                'icone': '📋',
                'description': 'Contrat de base pour les travaux',
                'template': """CONTRAT DE CONSTRUCTION

Entre:
[Votre Entreprise]
Et: {client}

Objet: {nom_projet}
Lieu des travaux: {adresse}

Budget convenu: {budget:,.2f} CAD
Délai d'exécution: Du {date_debut} au {date_fin_prevue}

Travaux à réaliser:
{detail_phases}

Conditions de paiement:
- Acompte: 30% à la signature
- Paiements d'étape selon avancement
- Solde à la réception des travaux

Date: {date_actuelle}

Signatures:
Entrepreneur: ________________
Client: ________________"""
            },
            
            'Rapport de Fin de Projet': {
                'icone': '✅',
                'description': 'Rapport final de livraison',
                'template': """RAPPORT DE FIN DE PROJET

Projet: {nom_projet}
Client: {client}
Date de livraison: {date_actuelle}

RÉSUMÉ:
- Début des travaux: {date_debut}
- Fin des travaux: {date_actuelle}
- Budget initial: {budget:,.2f} CAD
- Coût final: [À compléter]

TRAVAUX RÉALISÉS:
{phases_completees}

GARANTIES:
- Garantie légale: 1 an
- Garantie décennale: 10 ans (selon travaux)

DOCUMENTS REMIS:
□ Plans as-built
□ Certificats de conformité
□ Manuels d'entretien
□ Factures des sous-traitants

Le client déclare accepter les travaux réalisés.

Signatures:
Entrepreneur: ________________
Client: ________________"""
            }
        }
        
        # Sélection du type de document
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📋 Choisir un Document")
            
            for nom_doc, info in types_documents.items():
                if st.button(f"{info['icone']} {nom_doc}", key=f"btn_{nom_doc}"):
                    st.session_state.doc_selectionne = nom_doc
            
            if 'doc_selectionne' in st.session_state:
                st.success(f"Document sélectionné: {st.session_state.doc_selectionne}")
        
        with col2:
            if 'doc_selectionne' in st.session_state:
                doc_type = st.session_state.doc_selectionne
                doc_info = types_documents[doc_type]
                
                st.subheader(f"{doc_info['icone']} Génération - {doc_type}")
                st.write(doc_info['description'])
                
                # Sélection du projet
                projet_nom = st.selectbox("Projet concerné", [p['nom_projet'] for p in projets])
                projet = next(p for p in projets if p['nom_projet'] == projet_nom)
                
                if st.button(f"📄 Générer le {doc_type}", type="primary"):
                    # Préparer les variables
                    phases_proj = get_phases(projet['id'])
                    
                    detail_phases = "\n".join([
                        f"- {phase['nom_phase']}: {phase['cout_prevu']:,.0f} CAD"
                        for phase in phases_proj
                    ]) if phases_proj else "- Travaux selon plans et devis"
                    
                    phases_completees = "\n".join([
                        f"✓ {phase['nom_phase']} ({phase['pourcentage']}%)"
                        for phase in phases_proj
                    ]) if phases_proj else "✓ Tous travaux selon contrat"
                    
                    variables = {
                        'nom_projet': projet['nom_projet'],
                        'client': projet['client'],
                        'adresse': projet['adresse'],
                        'budget': projet['budget'],
                        'date_debut': str(projet['date_debut']),
                        'date_fin_prevue': str(projet['date_fin_prevue']),
                        'date_actuelle': date.today().strftime('%d/%m/%Y'),
                        'detail_phases': detail_phases,
                        'phases_completees': phases_completees
                    }
                    
                    try:
                        document_genere = doc_info['template'].format(**variables)
                        
                        # Affichage du document
                        st.subheader(f"📄 {doc_type} Généré")
                        st.text_area(
                            "Document généré (copiez le contenu):",
                            value=document_genere,
                            height=400
                        )
                        
                        # Option de téléchargement
                        st.download_button(
                            label=f"⬇️ Télécharger {doc_type}.txt",
                            data=document_genere,
                            file_name=f"{doc_type}_{projet['nom_projet']}.txt",
                            mime="text/plain"
                        )
                        
                    except Exception as e:
                        st.error(f"Erreur lors de la génération: {e}")

# ========== ALERTES & NOTIFICATIONS ==========
elif page == "🚨 Alertes & Notifications":
    st.header("🚨 Alertes & Notifications")
    
    # Générer les alertes automatiques
    alertes_auto = check_alertes_automatiques()
    
    # Afficher les alertes par priorité
    if alertes_auto:
        # Grouper par priorité
        alertes_elevees = [a for a in alertes_auto if a['niveau_priorite'] == 'Élevé']
        alertes_moyennes = [a for a in alertes_auto if a['niveau_priorite'] == 'Moyen']
        
        if alertes_elevees:
            st.error("🔥 Alertes Priorité ÉLEVÉE")
            for alerte in alertes_elevees:
                st.error(f"**{alerte['titre']}** - {alerte['message']}")
        
        if alertes_moyennes:
            st.warning("⚠️ Alertes Priorité MOYENNE")
            for alerte in alertes_moyennes:
                st.warning(f"**{alerte['titre']}** - {alerte['message']}")
    else:
        st.success("✅ Aucune alerte active")
    
    # Alertes météo
    st.subheader("🌤️ Alertes Météo")
    meteo_alerts = get_meteo_impact()
    
    for alert in meteo_alerts:
        if alert['date'] <= date.today() + timedelta(days=2):
            st.warning(f"**{alert['date']}** - {alert['type']}: {alert['impact']}")
        else:
            st.info(f"**{alert['date']}** - {alert['type']}: {alert['impact']}")

# ========== RAPPORTS AVANCÉS ==========
elif page == "📊 Rapports Avancés":
    st.header("📊 Rapports Avancés")
    
    if not projets:
        st.warning("Aucun projet disponible pour générer des rapports.")
    else:
        # Sélection du type de rapport
        type_rapport = st.selectbox(
            "Type de rapport",
            ["Rapport de Projet Détaillé", "Tableau de Bord Exécutif", "Analyse de Performance"]
        )
        
        if type_rapport == "Rapport de Projet Détaillé":
            projet_selectionne = st.selectbox(
                "Sélectionner un projet",
                options=[p['nom_projet'] for p in projets]
            )
            
            if st.button("📋 Générer le Rapport"):
                projet = next(p for p in projets if p['nom_projet'] == projet_selectionne)
                rapport = generer_rapport_projet(projet['id'])
                
                if rapport:
                    st.markdown("---")
                    
                    # En-tête du rapport
                    st.markdown(f"# 📋 Rapport de Projet: {rapport['projet']['nom_projet']}")
                    st.markdown(f"**Généré le:** {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
                    
                    # Informations générales
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Avancement Global", f"{rapport['statistiques']['avancement_moyen']:.1f}%")
                    with col2:
                        st.metric("Phases Terminées", f"{rapport['statistiques']['phases_terminees']}/{rapport['statistiques']['total_phases']}")
                    with col3:
                        variance = rapport['statistiques']['variance_budget']
                        st.metric("Variance Budget", f"{variance:,.0f} CAD", 
                                 delta=f"{(variance/rapport['projet']['budget']*100):+.1f}%")
                    
                    # Détails des phases
                    st.subheader("📈 Détail des Phases")
                    if rapport['phases']:
                        df_phases = pd.DataFrame(rapport['phases'])
                        
                        # Graphique d'avancement
                        fig = px.bar(
                            df_phases,
                            x='nom_phase',
                            y='pourcentage',
                            color='statut',
                            title="Avancement par Phase"
                        )
                        fig.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Tableau des phases
                        st.dataframe(
                            df_phases[['nom_phase', 'statut', 'pourcentage', 'cout_prevu', 'entrepreneur_assigne']],
                            use_container_width=True
                        )
        
        elif type_rapport == "Tableau de Bord Exécutif":
            st.subheader("📊 Vue Exécutive")
            
            if projets:
                df_projets = pd.DataFrame(projets)
                
                # KPIs principaux
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    projets_actifs = len(df_projets[df_projets['statut'] == 'Actif'])
                    st.metric("Projets Actifs", projets_actifs)
                
                with col2:
                    budget_total = df_projets['budget'].sum()
                    st.metric("Portefeuille Total", f"{budget_total:,.0f} CAD")
                
                with col3:
                    projets_retard = 0  # Calcul simplifié
                    st.metric("Projets en Retard", projets_retard)
                
                with col4:
                    rentabilite = 85  # Simulation
                    st.metric("Rentabilité Moyenne", f"{rentabilite}%")
                
                # Graphiques exécutifs
                col1, col2 = st.columns(2)
                
                with col1:
                    # Répartition par statut
                    fig_pie = px.pie(
                        df_projets,
                        names='statut',
                        title="Répartition des Projets par Statut"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    # Budget par type
                    fig_bar = px.bar(
                        df_projets.groupby('type_projet')['budget'].sum().reset_index(),
                        x='type_projet',
                        y='budget',
                        title="Budget Total par Type de Projet"
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

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
        st.write(f"**Tables:** projets, entrepreneurs, phases, photos_chantier, alertes, taches_quotidiennes, depenses_detaillees, budgets_categories, communications_client, modeles_communication")
        
        if os.path.exists(DB_FILE):
            st.write(f"**Chemin complet:** {os.path.abspath(DB_FILE)}")
            st.write(f"**Dernière modification:** {datetime.fromtimestamp(os.path.getmtime(DB_FILE))}")
        
        st.code("""
        Tables de la base de données:
        
        1. projets: Informations des projets de construction
        2. entrepreneurs: Répertoire des entrepreneurs et sous-traitants
        3. phases: Phases de chaque projet avec suivi d'avancement
        4. photos_chantier: Photos documentaires des projets
        5. alertes: Système d'alertes automatiques
        6. taches_quotidiennes: Gestion des tâches quotidiennes
        7. depenses_detaillees: Suivi détaillé des coûts
        8. budgets_categories: Budgets prévisionnels par catégorie
        9. communications_client: Historique des communications
        10. modeles_communication: Templates de communication
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    Gestionnaire de Projets Construction - Québec | Conforme aux standards québécois<br>
    Développé pour faciliter la gestion de projets de construction | 💾 Données SQLite
</div>
""", unsafe_allow_html=True)import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import uuid
import sqlite3
import json
import os
from PIL import Image
import io
import base64

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

def init_photos_table():
    """Initialise la table pour les photos de chantier"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS photos_chantier (
            id TEXT PRIMARY KEY,
            projet_id TEXT,
            phase_id TEXT,
            nom_photo TEXT,
            description TEXT,
            date_prise DATE,
            donnees_image TEXT,
            taille_fichier INTEGER,
            date_creation TIMESTAMP,
            FOREIGN KEY (projet_id) REFERENCES projets (id),
            FOREIGN KEY (phase_id) REFERENCES phases (id)
        )
    """)
    conn.commit()
    conn.close()

def init_alertes_table():
    """Initialise la table des alertes"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertes (
            id TEXT PRIMARY KEY,
            projet_id TEXT,
            type_alerte TEXT,
            titre TEXT,
            message TEXT,
            niveau_priorite TEXT,
            date_alerte DATE,
            statut TEXT,
            date_creation TIMESTAMP,
            FOREIGN KEY (projet_id) REFERENCES projets (id)
        )
    """)
    conn.commit()
    conn.close()

def init_taches_table():
    """Initialise la table des tâches"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS taches_quotidiennes (
            id TEXT PRIMARY KEY,
            projet_id TEXT,
            phase_id TEXT,
            titre TEXT,
            description TEXT,
            assigne_a TEXT,
            date_echeance DATE,
            priorite TEXT,
            statut TEXT,
            temps_estime INTEGER,
            date_creation TIMESTAMP,
            FOREIGN KEY (projet_id) REFERENCES projets (id),
            FOREIGN KEY (phase_id) REFERENCES phases (id)
        )
    """)
    conn.commit()
    conn.close()

def init_cost_tables():
    """Initialise les tables de gestion des coûts"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Table des dépenses détaillées
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS depenses_detaillees (
            id TEXT PRIMARY KEY,
            projet_id TEXT,
            phase_id TEXT,
            categorie TEXT,
            sous_categorie TEXT,
            description TEXT,
            montant REAL,
            quantite REAL,
            prix_unitaire REAL,
            fournisseur TEXT,
            date_depense DATE,
            numero_facture TEXT,
            statut_validation TEXT,
            notes TEXT,
            date_creation TIMESTAMP,
            FOREIGN KEY (projet_id) REFERENCES projets (id),
            FOREIGN KEY (phase_id) REFERENCES phases (id)
        )
    """)
    
    # Table des budgets prévisionnels par catégorie
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets_categories (
            id TEXT PRIMARY KEY,
            projet_id TEXT,
            categorie TEXT,
            budget_prevu REAL,
            budget_utilise REAL,
            pourcentage_utilise REAL,
            date_mise_a_jour TIMESTAMP,
            FOREIGN KEY (projet_id) REFERENCES projets (id)
        )
    """)
    
    conn.commit()
    conn.close()

def init_communication_tables():
    """Initialise les tables de communication client"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Table des communications
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS communications_client (
            id TEXT PRIMARY KEY,
            projet_id TEXT,
            type_communication TEXT,
            sujet TEXT,
            contenu TEXT,
            destinataire TEXT,
            date_envoi TIMESTAMP,
            statut TEXT,
            reponse_client TEXT,
            date_reponse TIMESTAMP,
            priorite TEXT,
            FOREIGN KEY (projet_id) REFERENCES projets (id)
        )
    """)
    
    # Table des modèles de communication
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modeles_communication (
            id TEXT PRIMARY KEY,
            nom_modele TEXT,
            type_document TEXT,
            contenu_modele TEXT,
            variables TEXT,
            date_creation TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def init_all_modules():
    """Initialise tous les modules de l'application"""
    init_database()
    init_photos_table()
    init_alertes_table()
    init_taches_table()
    init_cost_tables()
    init_communication_tables()

# ========== FONCTIONS DE BASE - PROJETS ==========

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

# ========== FONCTIONS DE BASE - ENTREPRENEURS ==========

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

# ========== FONCTIONS DE BASE - PHASES ==========

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

# ========== FONCTIONS PHOTOS ==========

def save_photo(photo_data):
    """Sauvegarde une photo dans la base de données"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO photos_chantier 
            (id, projet_id, phase_id, nom_photo, description, date_prise, donnees_image, taille_fichier, date_creation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, photo_data)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erreur sauvegarde photo: {e}")
        return False

def get_photos(projet_id=None):
    """Récupère les photos d'un projet"""
    try:
        conn = sqlite3.connect(DB_FILE)
        if projet_id:
            df = pd.read_sql_query("SELECT * FROM photos_chantier WHERE projet_id = ? ORDER BY date_prise DESC", conn, params=(projet_id,))
        else:
            df = pd.read_sql_query("SELECT * FROM photos_chantier ORDER BY date_prise DESC", conn)
        conn.close()
        return df.to_dict('records') if not df.empty else []
    except:
        return []

# ========== FONCTIONS ALERTES ==========

def check_alertes_automatiques():
    """Vérifie et génère des alertes automatiques"""
    alertes = []
    projets = get_projets()
    
    for projet in projets:
        # Alerte deadline proche
        if projet['date_fin_prevue']:
            jours_restants = (projet['date_fin_prevue'] - date.today()).days
            if 0 <= jours_restants <= 7 and projet['statut'] == 'Actif':
                alertes.append({
                    'id': str(uuid.uuid4()),
                    'projet_id': projet['id'],
                    'type_alerte': 'Deadline',
                    'titre': f"Deadline proche - {projet['nom_projet']}",
                    'message': f"Le projet se termine dans {jours_restants} jour(s)",
                    'niveau_priorite': 'Élevé' if jours_restants <= 3 else 'Moyen',
                    'date_alerte': date.today(),
                    'statut': 'Active',
                    'date_creation': datetime.now()
                })
        
        # Alerte budget (simulé à 90% du budget)
        phases_projet = get_phases(projet['id'])
        if phases_projet:
            cout_total = sum(p.get('cout_prevu', 0) for p in phases_projet)
            if cout_total > projet['budget'] * 0.9:
                alertes.append({
                    'id': str(uuid.uuid4()),
                    'projet_id': projet['id'],
                    'type_alerte': 'Budget',
                    'titre': f"Attention Budget - {projet['nom_projet']}",
                    'message': f"Coût prévu: {cout_total:,.0f}$ / Budget: {projet['budget']:,.0f}$",
                    'niveau_priorite': 'Élevé',
                    'date_alerte': date.today(),
                    'statut': 'Active',
                    'date_creation': datetime.now()
                })
    
    return alertes

def save_alerte(alerte):
    """Sauvegarde une alerte"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO alertes 
            (id, projet_id, type_alerte, titre, message, niveau_priorite, date_alerte, statut, date_creation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(alerte.values()))
        conn.commit()
        conn.close()
        return True
    except:
        return False

# ========== FONCTIONS TÂCHES ==========

def get_taches(projet_id=None, statut=None):
    """Récupère les tâches"""
    try:
        conn = sqlite3.connect(DB_FILE)
        query = "SELECT * FROM taches_quotidiennes WHERE 1=1"
        params = []
        
        if projet_id:
            query += " AND projet_id = ?"
            params.append(projet_id)
        
        if statut:
            query += " AND statut = ?"
            params.append(statut)
        
        query += " ORDER BY date_echeance ASC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df.to_dict('records') if not df.empty else []
    except:
        return []

def save_tache(tache):
    """Sauvegarde une tâche"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO taches_quotidiennes 
            (id, projet_id, phase_id, titre, description, assigne_a, date_echeance, priorite, statut, temps_estime, date_creation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(tache.values()))
        conn.commit()
        conn.close()
        return True
    except:
        return False

# ========== FONCTIONS COÛTS ==========

def get_categories_construction():
    """Retourne les catégories de coûts standard pour la construction"""
    return {
        'Matériaux': ['Béton', 'Acier', 'Bois', 'Isolation', 'Revêtements', 'Plomberie', 'Électricité'],
        'Main d\'œuvre': ['Maçonnerie', 'Charpente', 'Plomberie', 'Électricité', 'Finition'],
        'Équipement': ['Location machines', 'Outils', 'Échafaudages', 'Transport'],
        'Services': ['Ingénierie', 'Architecture', 'Permis', 'Inspections', 'Assurances'],
        'Autres': ['Contingences', 'Nettoyage', 'Sécurité', 'Divers']
    }

def save_depense(depense_data):
    """Sauvegarde une dépense"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO depenses_detaillees 
            (id, projet_id, phase_id, categorie, sous_categorie, description, montant, quantite, 
             prix_unitaire, fournisseur, date_depense, numero_facture, statut_validation, notes, date_creation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, depense_data)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erreur sauvegarde: {e}")
        return False

def get_depenses(projet_id=None):
    """Récupère les dépenses"""
    try:
        conn = sqlite3.connect(DB_FILE)
        if projet_id:
            df = pd.read_sql_query(
                "SELECT * FROM depenses_detaillees WHERE projet_id = ? ORDER BY date_depense DESC", 
                conn, params=(projet_id,)
            )
        else:
            df = pd.read_sql_query("SELECT * FROM depenses_detaillees ORDER BY date_depense DESC", conn)
        conn.close()
        return df.to_dict('records') if not df.empty else []
    except:
        return []

def calculer_budget_utilise(projet_id, categorie=None):
    """Calcule le budget utilisé pour un projet ou une catégorie"""
    depenses = get_depenses(projet_id)
    if categorie:
        depenses = [d for d in depenses if d['categorie'] == categorie]
    return sum(d['montant'] for d in depenses)

def detecter_depassements_budget(projet_id):
    """Détecte les dépassements de budget par catégorie"""
    projet = next((p for p in get_projets() if p['id'] == projet_id), None)
    if not projet:
        return []
    
    depassements = []
    categories = get_categories_construction()
    budget_total = projet['budget']
    budget_par_categorie = budget_total / len(categories)  # Répartition simplifiée
    
    for categorie in categories.keys():
        utilise = calculer_budget_utilise(projet_id, categorie)
        pourcentage = (utilise / budget_par_categorie * 100) if budget_par_categorie > 0 else 0
        
        if pourcentage > 90:  # Alerte à 90%
            depassements.append({
                'categorie': categorie,
                'budget_prevu': budget_par_categorie,
                'budget_utilise': utilise,
                'pourcentage': pourcentage,
                'statut': 'Dépassement' if pourcentage > 100 else 'Attention'
            })
    
    return depassements

def generer_previsions_cout(projet_id):
    """Génère des prévisions de coût basées sur l'avancement"""
    phases = get_phases(projet_id)
    if not phases:
        return None
    
    # Calcul de l'avancement global
    avancement_global = sum(p['pourcentage'] for p in phases) / len(phases)
    
    # Coût déjà engagé
    cout_engage = calculer_budget_utilise(projet_id)
    
    # Prévision basée sur l'avancement
    if avancement_global > 0:
        cout_prevu_final = (cout_engage / avancement_global) * 100
    else:
        cout_prevu_final = sum(p['cout_prevu'] for p in phases)
    
    return {
        'avancement_global': avancement_global,
        'cout_engage': cout_engage,
        'cout_prevu_final': cout_prevu_final,
        'variance_prevue': cout_prevu_final - next(p['budget'] for p in get_projets() if p['id'] == projet_id)
    }

# ========== FONCTIONS COMMUNICATION ==========

def get_modeles_predefined():
    """Retourne les modèles de communication prédéfinis"""
    return {
        'Démarrage de Projet': {
            'sujet': 'Démarrage du projet {nom_projet}',
            'contenu': """Bonjour {client},

Nous sommes ravis de vous confirmer le démarrage de votre projet "{nom_projet}".

📅 Date de début: {date_debut}
📅 Date de fin prévue: {date_fin_prevue}
💰 Budget: {budget:,.0f} CAD

Notre équipe est mobilisée et nous vous tiendrons informé(e) régulièrement de l'avancement.

N'hésitez pas à nous contacter pour toute question.

Cordialement,
L'équipe de construction"""
        },
        
        'Rapport d\'Avancement': {
            'sujet': 'Rapport d\'avancement - {nom_projet}',
            'contenu': """Bonjour {client},

Voici le rapport d'avancement de votre projet "{nom_projet}" :

📊 Avancement global: {avancement}%
🏗️ Phase actuelle: {phase_actuelle}
📅 Respect du planning: {statut_planning}

Prochaines étapes:
{prochaines_etapes}

Photos de l'avancement en pièce jointe.

Cordialement,
L'équipe de construction"""
        },
        
        'Demande de Validation': {
            'sujet': 'Validation requise - {nom_projet}',
            'contenu': """Bonjour {client},

Nous avons besoin de votre validation concernant le projet "{nom_projet}".

Élément à valider: {element_validation}
Échéance pour la validation: {date_echeance}

Impact en cas de retard: {impact_retard}

Merci de nous faire un retour dans les plus brefs délais.

Cordialement,
L'équipe de construction"""
        },
        
        'Alerte Budget': {
            'sujet': 'Information importante - Budget {nom_projet}',
            'contenu': """Bonjour {client},

Nous souhaitons vous informer d'une situation concernant le budget de votre projet "{nom_projet}".

💰 Budget initial: {budget_initial:,.0f} CAD
💰 Coût actuel estimé: {cout_actuel:,.0f} CAD
📊 Variance: {variance:+,.0f} CAD

Raison de la variance: {raison_variance}

Nous proposons de programmer une réunion pour discuter des options disponibles.

Cordialement,
L'équipe de construction"""
        }
    }

def save_communication(comm_data):
    """Sauvegarde une communication"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO communications_client 
            (id, projet_id, type_communication, sujet, contenu, destinataire, date_envoi, statut, priorite)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, comm_data)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erreur sauvegarde: {e}")
        return False

def get_communications(projet_id=None):
    """Récupère les communications"""
    try:
        conn = sqlite3.connect(DB_FILE)
        if projet_id:
            df = pd.read_sql_query(
                "SELECT * FROM communications_client WHERE projet_id = ? ORDER BY date_envoi DESC", 
                conn, params=(projet_id,)
            )
        else:
            df = pd.read_sql_query("SELECT * FROM communications_client ORDER BY date_envoi DESC", conn)
        conn.close()
        return df.to_dict('records') if not df.empty else []
    except:
        return []

def generer_rapport_automatique(projet_id):
    """Génère automatiquement un rapport d'avancement"""
    projet = next((p for p in get_projets() if p['id'] == projet_id), None)
    if not projet:
        return None
    
    phases = get_phases(projet_id)
    avancement_global = sum(p['pourcentage'] for p in phases) / len(phases) if phases else 0
    
    # Trouver la phase actuelle
    phase_actuelle = "Planification"
    for phase in phases:
        if 0 < phase['pourcentage'] < 100:
            phase_actuelle = phase['nom_phase']
            break
        elif phase['pourcentage'] == 100:
            continue
    
    # Prochaines étapes
    prochaines_phases = [p['nom_phase'] for p in phases if p['pourcentage'] == 0][:3]
    prochaines_etapes = "\n".join([f"• {phase}" for phase in prochaines_phases])
    
    # Statut du planning
    if projet['date_fin_prevue']:
        jours_restants = (projet['date_fin_prevue'] - date.today()).days
        if avancement_global >= 80:
            statut_planning = "Dans les temps"
        elif jours_restants < 30 and avancement_global < 70:
            statut_planning = "Risque de retard"
        else:
            statut_planning = "Selon planning"
    else:
        statut_planning = "À définir"
    
    return {
        'avancement': f"{avancement_global:.0f}",
        'phase_actuelle': phase_actuelle,
        'statut_planning': statut_planning,
        'prochaines_etapes': prochaines_etapes if prochaines_etapes else "Phase finale en cours"
    }

def generer_rapport_projet(projet_id):
    """Génère un rapport complet pour un projet"""
    projet = next((p for p in get_projets() if p['id'] == projet_id), None)
    if not projet:
        return None
    
    phases = get_phases(projet_id)
    photos = get_photos(projet_id)
    
    # Calculs
    phases_terminees = len([p for p in phases if p['statut'] == 'Terminé'])
    avancement_moyen = sum(p['pourcentage'] for p in phases) / len(phases) if phases else 0
    cout_total_prevu = sum(p['cout_prevu'] for p in phases)
    
    rapport = {
        'projet': projet,
        'phases': phases,
        'statistiques': {
            'total_phases': len(phases),
            'phases_terminees': phases_terminees,
            'avancement_moyen': avancement_moyen,
            'cout_total_prevu': cout_total_prevu,
            'variance_budget': cout_total_prevu - projet['budget'],
            'photos_count': len(photos)
        }
    }
    
    return rapport

def get_meteo_impact():
    """Simule l'impact météo (en réalité, vous utiliseriez une API météo)"""
    # Simulation d'alertes météo
    alerts = [
        {"date": date.today() + timedelta(days=1), "type": "Pluie", "impact": "Travaux extérieurs reportés"},
        {"date": date.today() + timedelta(days=3), "type": "Vent fort", "impact": "Prudence avec les grues"},
        {"date": date.today() + timedelta(days=5), "type": "Gel", "impact": "Pas de coulage de béton"}
    ]
    return alerts

# ========== CHARGEMENT DES DONNÉES ==========

# Charger les données depuis la base de données
@st.cache_data(ttl=1)  # Cache pendant 1 seconde pour éviter les rechargements constants
def load_data():
    return {
        'projets': get_projets(),
        'entrepreneurs': get_entrepreneurs(),
        'phases': get_phases()
    }

# Initialiser la base de données
init_all_modules()

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
    [
        "📊 Tableau de bord",
        "🧠 Dashboard Intelligent",
        "➕ Nouveau Projet",
        "🏢 Projets",
        "👷 Entrepreneurs",
        "📈 Phases & Suivi",
        "💰 Gestion des Coûts",
        "✅ Tâches Quotidiennes",
        "📸 Photos de Chantier",
        "📞 Communication Client",
        "📄 Templates Documents",
        "🚨 Alertes & Notifications",
        "📊 Rapports Avancés",
        "📋 Licences RBQ",
        "🗄️ Base de Données"
    ]
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

# ========== DASHBOARD INTELLIGENT ==========
elif page == "🧠 Dashboard Intelligent":
    st.header("🧠 Tableau de Bord Intelligent")
    
    if not projets:
        st.warning("Aucun projet disponible.")
    else:
        # Sélecteur de période
        col1, col2 = st.columns(2)
        with col1:
            date_debut_dash = st.date_input("Date de début", value=date.today() - timedelta(days=30))
        with col2:
            date_fin_dash = st.date_input("Date de fin", value=date.today())
        
        # KPIs intelligents
        st.subheader("📊 KPIs Intelligents")
        
        # Calculs intelligents
        df_projets = pd.DataFrame(projets)
        projets_actifs = len(df_projets[df_projets['statut'] == 'Actif'])
        budget_total = df_projets['budget'].sum()
        
        # Calcul de la rentabilité estimée
        rentabilite_moyenne = 0
        for projet in projets:
            phases_proj = get_phases(projet['id'])
            if phases_proj:
                cout_prevu = sum(p['cout_prevu'] for p in phases_proj)
                if cout_prevu > 0:
                    rentabilite = (projet['budget'] - cout_prevu) / projet['budget'] * 100
                    rentabilite_moyenne += rentabilite
        
        rentabilite_moyenne = rentabilite_moyenne / len(projets) if projets else 0
        
        # Affichage des métriques
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Projets Actifs", projets_actifs, delta=f"+{len(projets) - projets_actifs} terminés")
        
        with col2:
            st.metric("Chiffre d'Affaires", f"{budget_total:,.0f} CAD")
        
        with col3:
            st.metric("Rentabilité Moyenne", f"{rentabilite_moyenne:.1f}%", 
                     delta="🎯 Objectif: 20%")
        
        with col4:
            # Calcul du taux de respect des délais (simulé)
            taux_delai = 85  # Simulation
            st.metric("Respect des Délais", f"{taux_delai}%", delta="+5% vs mois dernier")
        
        # Graphiques intelligents
        col1, col2 = st.columns(2)
        
        with col1:
            # Tendance des projets dans le temps
            st.subheader("📈 Tendance Temporelle")
            df_projets['date_debut'] = pd.to_datetime(df_projets['date_debut'])
            projets_par_mois = df_projets.set_index('date_debut').resample('M').size()
            
            fig_tendance = px.line(
                x=projets_par_mois.index,
                y=projets_par_mois.values,
                title="Nombre de Projets Démarrés par Mois"
            )
            st.plotly_chart(fig_tendance, use_container_width=True)
        
        with col2:
            # Performance par type de projet
            st.subheader("🏗️ Performance par Type")
            perf_type = df_projets.groupby('type_projet').agg({
                'budget': 'mean',
                'nom_projet': 'count'
            }).round(0)
            perf_type.columns = ['Budget Moyen', 'Nombre']
            
            fig_perf = px.bar(
                perf_type,
                x=perf_type.index,
                y='Budget Moyen',
                title="Budget Moyen par Type de Projet"
            )
            st.plotly_chart(fig_perf, use_container_width=True)
        
        # Alertes intelligentes
        st.subheader("🚨 Alertes Intelligentes")
        
        alertes_auto = []
        
        # Vérifier chaque projet
        for projet in projets:
            if projet['statut'] == 'Actif':
                # Alerte deadline
                if projet['date_fin_prevue']:
                    jours_restants = (projet['date_fin_prevue'] - date.today()).days
                    if jours_restants <= 7:
                        alertes_auto.append({
                            'type': 'warning' if jours_restants > 3 else 'error',
                            'message': f"⏰ {projet['nom_projet']}: {jours_restants} jour(s) restant(s)"
                        })
                
                # Alerte budget
                depenses = get_depenses(projet['id'])
                if depenses:
                    total_depenses = sum(d['montant'] for d in depenses)
                    if total_depenses > projet['budget'] * 0.9:
                        alertes_auto.append({
                            'type': 'warning',
                            'message': f"💰 {projet['nom_projet']}: Budget à {(total_depenses/projet['budget']*100):.0f}%"
                        })
        
        # Afficher les alertes
        if alertes_auto:
            for alerte in alertes_auto:
                if alerte['type'] == 'error':
                    st.error(alerte['message'])
                else:
                    st.warning(alerte['message'])
        else:
            st.success("✅ Aucune alerte active")

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

# ========== GESTION DES COÛTS ==========
elif page == "💰 Gestion des Coûts":
    st.header("💰 Gestion des Coûts")
    
    if not projets:
        st.warning("Créez d'abord un projet pour gérer les coûts.")
    else:
        # Sélection du projet
        projet_selectionne = st.selectbox(
            "Sélectionner un projet",
            options=[p['nom_projet'] for p in projets]
        )
        
        if not projet_selectionne:
            st.stop()
        
        projet = next(p for p in projets if p['nom_projet'] == projet_selectionne)
        
        # Onglets pour organiser les fonctionnalités
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Vue d'ensemble", "➕ Nouvelle Dépense", "📈 Analyses", "⚠️ Alertes"])
        
        with tab1:
            # VUE D'ENSEMBLE DES COÛTS
            st.subheader(f"💰 Coûts - {projet_selectionne}")
            
            # Métriques principales
            col1, col2, col3, col4 = st.columns(4)
            
            budget_total = projet['budget']
            cout_engage = calculer_budget_utilise(projet['id'])
            pourcentage_utilise = (cout_engage / budget_total * 100) if budget_total > 0 else 0
            budget_restant = budget_total - cout_engage
            
            with col1:
                st.metric("Budget Total", f"{budget_total:,.0f} CAD")
            with col2:
                st.metric("Coût Engagé", f"{cout_engage:,.0f} CAD", 
                         delta=f"{pourcentage_utilise:.1f}% utilisé")
            with col3:
                st.metric("Budget Restant", f"{budget_restant:,.0f} CAD")
            with col4:
                phases_proj = get_phases(projet['id'])
                avancement = sum(p['pourcentage'] for p in phases_proj) / len(phases_proj) if phases_proj else 0
                st.metric("Avancement", f"{avancement:.1f}%")
            
            # Graphique de répartition par catégorie
            depenses = get_depenses(projet['id'])
            if depenses:
                df_depenses = pd.DataFrame(depenses)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Répartition par catégorie
                    depenses_par_cat = df_depenses.groupby('categorie')['montant'].sum().reset_index()
                    fig_pie = px.pie(
                        depenses_par_cat,
                        values='montant',
                        names='categorie',
                        title="Répartition des Coûts par Catégorie"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    # Évolution dans le temps
                    df_depenses['date_depense'] = pd.to_datetime(df_depenses['date_depense'])
                    evolution = df_depenses.groupby('date_depense')['montant'].sum().cumsum().reset_index()
                    
                    fig_line = px.line(
                        evolution,
                        x='date_depense',
                        y='montant',
                        title="Évolution Cumulative des Coûts"
                    )
                    # Ajouter ligne de budget
                    fig_line.add_hline(y=budget_total, line_dash="dash", line_color="red", 
                                      annotation_text="Budget Total")
                    st.plotly_chart(fig_line, use_container_width=True)
            
            # Tableau des dernières dépenses
            if depenses:
                st.subheader("📋 Dernières Dépenses")
                df_recent = pd.DataFrame(depenses[:10])  # 10 dernières
                st.dataframe(
                    df_recent[['date_depense', 'categorie', 'description', 'montant', 'fournisseur']],
                    use_container_width=True
                )
        
        with tab2:
            # NOUVELLE DÉPENSE
            st.subheader("➕ Ajouter une Dépense")
            
            col1, col2 = st.columns(2)
            
            with col1:
                categories = get_categories_construction()
                categorie = st.selectbox("Catégorie", list(categories.keys()))
                sous_categorie = st.selectbox("Sous-catégorie", categories[categorie])
                description = st.text_input("Description de la dépense")
                fournisseur = st.text_input("Fournisseur")
            
            with col2:
                montant = st.number_input("Montant (CAD)", min_value=0.0, step=0.01)
                quantite = st.number_input("Quantité", min_value=0.0, step=0.1, value=1.0)
                prix_unitaire = st.number_input("Prix unitaire (CAD)", min_value=0.0, step=0.01)
                date_depense = st.date_input("Date de la dépense", value=date.today())
                numero_facture = st.text_input("Numéro de facture")
            
            # Calcul automatique
            if prix_unitaire > 0 and quantite > 0:
                montant_calcule = prix_unitaire * quantite
                st.info(f"Montant calculé: {montant_calcule:,.2f} CAD")
                if st.button("Utiliser le montant calculé"):
                    montant = montant_calcule
            
            phases_proj = get_phases(projet['id'])
            phase_associee = st.selectbox(
                "Phase associée (optionnel)",
                ["Aucune"] + [p['nom_phase'] for p in phases_proj]
            )
            
            notes = st.text_area("Notes additionnelles")
            
            if st.button("💾 Enregistrer la Dépense", type="primary"):
                if description and montant > 0:
                    phase_id = None
                    if phase_associee != "Aucune":
                        phase_id = next(p['id'] for p in phases_proj if p['nom_phase'] == phase_associee)
                    
                    depense_data = (
                        str(uuid.uuid4()),
                        projet['id'],
                        phase_id,
                        categorie,
                        sous_categorie,
                        description,
                        montant,
                        quantite,
                        prix_unitaire,
                        fournisseur,
                        date_depense,
                        numero_facture,
                        'En attente',  # statut_validation
                        notes,
                        datetime.now()
                    )
                    
                    if save_depense(depense_data):
                        st.success("Dépense enregistrée avec succès!")
                        st.cache_data.clear()
                        st.rerun()
                else:
                    st.error("Veuillez remplir au minimum la description et le montant.")
        
        with tab3:
            # ANALYSES AVANCÉES
            st.subheader("📈 Analyses de Coûts")
            
            # Prévisions
            previsions = generer_previsions_cout(projet['id'])
            if previsions:
                st.markdown("### 🔮 Prévisions")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Coût Final Prévu", f"{previsions['cout_prevu_final']:,.0f} CAD")
                with col2:
                    variance = previsions['variance_prevue']
                    st.metric("Variance Prévue", f"{variance:+,.0f} CAD", 
                             delta=f"{(variance/budget_total*100):+.1f}%")
                with col3:
                    efficacite = (previsions['avancement_global'] / (cout_engage / budget_total * 100)) if cout_engage > 0 else 0
                    st.metric("Efficacité Budget", f"{efficacite:.1f}")
            
            # Analyse par phase
            if depenses and phases_proj:
                st.markdown("### 📊 Coûts par Phase")
                
                # Créer un DataFrame avec les coûts par phase
                cout_par_phase = []
                for phase in phases_proj:
                    depenses_phase = [d for d in depenses if d['phase_id'] == phase['id']]
                    cout_reel = sum(d['montant'] for d in depenses_phase)
                    
                    cout_par_phase.append({
                        'Phase': phase['nom_phase'],
                        'Budget Prévu': phase['cout_prevu'],
                        'Coût Réel': cout_reel,
                        'Variance': cout_reel - phase['cout_prevu'],
                        'Avancement': phase['pourcentage']
                    })
                
                df_phases = pd.DataFrame(cout_par_phase)
                
                # Graphique comparatif
                fig = go.Figure()
                fig.add_trace(go.Bar(name='Budget Prévu', x=df_phases['Phase'], y=df_phases['Budget Prévu']))
                fig.add_trace(go.Bar(name='Coût Réel', x=df_phases['Phase'], y=df_phases['Coût Réel']))
                fig.update_layout(title="Comparaison Budget vs Coût Réel par Phase", barmode='group')
                st.plotly_chart(fig, use_container_width=True)
                
                # Tableau détaillé
                st.dataframe(df_phases, use_container_width=True)
        
        with tab4:
            # ALERTES ET DÉPASSEMENTS
            st.subheader("⚠️ Alertes de Budget")
            
            depassements = detecter_depassements_budget(projet['id'])
            
            if depassements:
                for dep in depassements:
                    if dep['statut'] == 'Dépassement':
                        st.error(f"🔴 **{dep['categorie']}**: Dépassement de {dep['pourcentage']:.1f}% "
                                f"({dep['budget_utilise']:,.0f}$ / {dep['budget_prevu']:,.0f}$)")
                    else:
                        st.warning(f"🟡 **{dep['categorie']}**: Attention {dep['pourcentage']:.1f}% utilisé "
                                  f"({dep['budget_utilise']:,.0f}$ / {dep['budget_prevu']:,.0f}$)")
            else:
                st.success("✅ Aucun dépassement de budget détecté")
            
            # Prévisions d'alerte
            st.markdown("### 📅 Prévisions d'Alertes")
            
            if previsions and previsions['variance_prevue'] > 0:
                st.warning(f"⚠️ Risque de dépassement de {previsions['variance_prevue']:,.0f}$ "
                          f"({(previsions['variance_prevue']/budget_total*100):+.1f}%)")
            
            # Recommandations automatiques
            st.markdown("### 💡 Recommandations")
            
            if pourcentage_utilise > 80:
                st.info("📊 Considérez une révision du budget avec le client")
            
            if previsions and previsions['avancement_global'] < 50 and cout_engage > budget_total * 0.6:
                st.warning("🎯 Rythme de dépenses trop élevé par rapport à l'avancement")
            
            # Actions recommandées
            st.markdown("#### Actions Suggérées:")
            actions = []
            
            if depassements:
                actions.append("• Renégocier les prix avec les fournisseurs")
                actions.append("• Réviser la portée du projet")
            
            if pourcentage_utilise > 90:
                actions.append("• Préparer un avenant au contrat")
                actions.append("• Alerter le client immédiatement")
            
            for action in actions:
                st.write(action)

# ========== TÂCHES QUOTIDIENNES ==========
elif page == "✅ Tâches Quotidiennes":
    st.header("✅ Tâches Quotidiennes")
    
    if not projets:
        st.warning("Créez d'abord un projet pour gérer les tâches.")
    else:
        # Ajouter une tâche
        with st.expander("➕ Nouvelle Tâche"):
            col1, col2 = st.columns(2)
            
            with col1:
                projet_tache = st.selectbox("Projet", [p['nom_projet'] for p in projets])
                titre_tache = st.text_input("Titre de la tâche")
                description_tache = st.text_area("Description")
            
            with col2:
                assigne_a = st.selectbox("Assigné à", ["Non assigné"] + [e['nom_entreprise'] for e in entrepreneurs])
                date_echeance = st.date_input("Date d'échéance", value=date.today())
                priorite = st.selectbox("Priorité", ["Basse", "Normale", "Élevée", "Urgente"])
                temps_estime = st.number_input("Temps estimé (heures)", min_value=0.5, step=0.5)
            
            if st.button("💾 Créer la Tâche"):
                if titre_tache:
                    projet_id = next(p['id'] for p in projets if p['nom_projet'] == projet_tache)
                    
                    nouvelle_tache = {
                        'id': str(uuid.uuid4()),
                        'projet_id': projet_id,
                        'phase_id': None,
                        'titre': titre_tache,
                        'description': description_tache,
                        'assigne_a': assigne_a,
                        'date_echeance': date_echeance,
                        'priorite': priorite,
                        'statut': 'À faire',
                        'temps_estime': int(temps_estime * 60),  # Convertir en minutes
                        'date_creation': datetime.now()
                    }
                    
                    if save_tache(nouvelle_tache):
                        st.success("Tâche créée avec succès!")
                        st.cache_data.clear()
                        st.rerun()
        
        # Affichage des tâches
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Tâches d'Aujourd'hui")
            taches_aujourdhui = get_taches()
            taches_jour = [t for t in taches_aujourdhui if t['date_echeance'] <= date.today().strftime('%Y-%m-%d')]
            
            if taches_jour:
                for tache in taches_jour:
                    priorite_color = {
                        'Urgente': '🔴',
                        'Élevée': '🟠',
                        'Normale': '🟡',
                        'Basse': '🟢'
                    }
                    
                    with st.container():
                        st.markdown(f"""
                        **{priorite_color.get(tache['priorite'], '🟡')} {tache['titre']}**
                        - Assigné à: {tache['assigne_a']}
                        - Temps estimé: {tache['temps_estime']//60}h{tache['temps_estime']%60:02d}
                        - Description: {tache['description'][:100]}...
                        """)
                        
                        if st.button(f"✅ Marquer terminée", key=f"complete_{tache['id']}"):
                            # Mise à jour du statut (implémentation simplifiée)
                            st.success("Tâche marquée comme terminée!")
            else:
                st.info("Aucune tâche pour aujourd'hui!")
        
        with col2:
            st.subheader("📅 Tâches à Venir")
            taches_futures = [t for t in get_taches() if t['date_echeance'] > date.today().strftime('%Y-%m-%d')]
            
            if taches_futures:
                for tache in taches_futures[:5]:  # Afficher les 5 prochaines
                    st.write(f"**{tache['titre']}** - {tache['date_echeance']}")
            else:
                st.info("Aucune tâche planifiée")

# ========== PHOTOS DE CHANTIER ==========
elif page == "📸 Photos de Chantier":
    st.header("📸 Photos de Chantier")
    
    if len(projets) == 0:
        st.warning("Créez d'abord un projet pour ajouter des photos.")
    else:
        # Sélection du projet
        projet_selectionne = st.selectbox(
            "Sélectionner un projet",
            options=[p['nom_projet'] for p in projets]
        )
        
        if projet_selectionne:
            projet = next(p for p in projets if p['nom_projet'] == projet_selectionne)
            
            # Upload de photos
            with st.expander("📸 Ajouter des Photos"):
                col1, col2 = st.columns(2)
                
                with col1:
                    uploaded_files = st.file_uploader(
                        "Choisir des photos",
                        type=['png', 'jpg', 'jpeg'],
                        accept_multiple_files=True
                    )
                    
                    phases_proj = get_phases(projet['id'])
                    phase_selectionnee = st.selectbox(
                        "Phase associée",
                        options=['Général'] + [p['nom_phase'] for p in phases_proj]
                    )
                
                with col2:
                    description_photo = st.text_area("Description des photos")
                    date_prise = st.date_input("Date de prise", value=date.today())
                    
                    if st.button("💾 Sauvegarder les photos"):
                        if uploaded_files:
                            for uploaded_file in uploaded_files:
                                # Convertir l'image en base64
                                image_data = base64.b64encode(uploaded_file.read()).decode()
                                
                                phase_id = None
                                if phase_selectionnee != 'Général':
                                    phase_id = next(p['id'] for p in phases_proj if p['nom_phase'] == phase_selectionnee)
                                
                                photo_data = (
                                    str(uuid.uuid4()),
                                    projet['id'],
                                    phase_id,
                                    uploaded_file.name,
                                    description_photo,
                                    date_prise,
                                    image_data,
                                    len(uploaded_file.getvalue()),
                                    datetime.now()
                                )
                                
                                if save_photo(photo_data):
                                    st.success(f"Photo {uploaded_file.name} sauvegardée!")
                                
                            st.cache_data.clear()
                            st.rerun()
            
            # Affichage des photos
            photos = get_photos(projet['id'])
            if photos:
                st.subheader(f"📷 Photos de {projet_selectionne}")
                
                cols = st.columns(3)
                for i, photo in enumerate(photos):
                    with cols[i % 3]:
                        # Décoder l'image
                        image_data = base64.b64decode(photo['donnees_image'])
                        image = Image.open(io.BytesIO(image_data))
                        
                        st.image(image, caption=photo['nom_photo'], use_container_width=True)
                        st.write(f"📅 {photo['date_prise']}")
                        if photo['description']:
                            st.write(f"📝 {photo['description']}")

# ========== COMMUNICATION CLIENT ==========
elif page == "📞 Communication Client":
    st.header("📞 Communication Client")
    
    if not projets:
        st.warning("Créez d'abord un projet pour gérer les communications.")
    else:
        # Onglets
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Historique", "✉️ Nouvelle Communication", "🤖 Rapports Auto", "📊 Suivi Client"])
        
        with tab1:
            # HISTORIQUE DES COMMUNICATIONS
            st.subheader("📋 Historique des Communications")
            
            # Filtres
            col1, col2 = st.columns(2)
            with col1:
                projet_filtre = st.selectbox(
                    "Filtrer par projet",
                    ["Tous"] + [p['nom_projet'] for p in projets]
                )
            with col2:
                type_filtre = st.selectbox(
                    "Type de communication",
                    ["Tous", "Email", "Appel", "Réunion", "Rapport", "Alerte"]
                )
            
            # Récupérer et filtrer les communications
            if projet_filtre == "Tous":
                communications = get_communications()
            else:
                projet_id = next(p['id'] for p in projets if p['nom_projet'] == projet_filtre)
                communications = get_communications(projet_id)
            
            if type_filtre != "Tous":
                communications = [c for c in communications if c['type_communication'] == type_filtre]
            
            # Affichage des communications
            if communications:
                for comm in communications:
                    projet_nom = next((p['nom_projet'] for p in projets if p['id'] == comm['projet_id']), 'Projet inconnu')
                    
                    with st.expander(f"📧 {comm['sujet']} - {projet_nom} ({comm['date_envoi'][:10]})"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Type:** {comm['type_communication']}")
                            st.write(f"**Destinataire:** {comm['destinataire']}")
                            st.write(f"**Contenu:**")
                            st.text_area("", value=comm['contenu'], height=100, disabled=True, key=f"content_{comm['id']}")
                        
                        with col2:
                            priorite_color = {'Élevée': '🔴', 'Normale': '🟡', 'Basse': '🟢'}
                            st.write(f"**Priorité:** {priorite_color.get(comm['priorite'], '🟡')} {comm['priorite']}")
                            st.write(f"**Statut:** {comm['statut']}")
                            
                            if comm['reponse_client']:
                                st.write(f"**Réponse client:**")
                                st.text_area("", value=comm['reponse_client'], height=60, disabled=True, key=f"response_{comm['id']}")
            else:
                st.info("Aucune communication trouvée avec ces filtres.")
        
        with tab2:
            # NOUVELLE COMMUNICATION
            st.subheader("✉️ Nouvelle Communication")
            
            # Sélection du projet
            projet_comm = st.selectbox("Projet concerné", [p['nom_projet'] for p in projets])
            projet_selectionne = next(p for p in projets if p['nom_projet'] == projet_comm)
            
            col1, col2 = st.columns(2)
            
            with col1:
                type_comm = st.selectbox("Type de communication", 
                                       ["Email", "Appel", "Réunion", "Rapport", "Alerte", "SMS"])
                
                # Modèles prédéfinis
                modeles = get_modeles_predefined()
                modele_choisi = st.selectbox("Utiliser un modèle", ["Personnalisé"] + list(modeles.keys()))
                
                destinataire = st.text_input("Destinataire", value=projet_selectionne['client'])
                priorite = st.selectbox("Priorité", ["Normale", "Élevée", "Basse"])
            
            with col2:
                sujet = st.text_input("Sujet")
                
                if modele_choisi != "Personnalisé":
                    if st.button(f"📋 Charger le modèle '{modele_choisi}'"):
                        modele = modeles[modele_choisi]
                        sujet = modele['sujet']
                        st.rerun()
            
            # Contenu de la communication
            if modele_choisi != "Personnalisé" and modele_choisi in modeles:
                modele = modeles[modele_choisi]
                
                # Variables automatiques pour le modèle
                variables = {
                    'nom_projet': projet_selectionne['nom_projet'],
                    'client': projet_selectionne['client'],
                    'date_debut': str(projet_selectionne['date_debut']),
                    'date_fin_prevue': str(projet_selectionne['date_fin_prevue']),
                    'budget': projet_selectionne['budget']
                }
                
                # Variables spéciales pour certains modèles
                if modele_choisi == 'Rapport d\'Avancement':
                    rapport_data = generer_rapport_automatique(projet_selectionne['id'])
                    if rapport_data:
                        variables.update(rapport_data)
                
                try:
                    contenu_prevu = modele['contenu'].format(**variables)
                    sujet_prevu = modele['sujet'].format(**variables)
                except KeyError as e:
                    contenu_prevu = modele['contenu']
                    sujet_prevu = modele['sujet']
                    st.warning(f"Variable manquante: {e}")
                
                if not sujet:
                    sujet = sujet_prevu
                
                contenu = st.text_area("Contenu", value=contenu_prevu, height=300)
            else:
                contenu = st.text_area("Contenu", height=300)
            
            # Actions
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💾 Sauvegarder le Brouillon"):
                    if sujet and contenu:
                        comm_data = (
                            str(uuid.uuid4()),
                            projet_selectionne['id'],
                            type_comm,
                            sujet,
                            contenu,
                            destinataire,
                            datetime.now(),
                            'Brouillon',
                            priorite
                        )
                        
                        if save_communication(comm_data):
                            st.success("Brouillon sauvegardé!")
                            st.cache_data.clear()
            
            with col2:
                if st.button("📧 Marquer comme Envoyé", type="primary"):
                    if sujet and contenu:
                        comm_data = (
                            str(uuid.uuid4()),
                            projet_selectionne['id'],
                            type_comm,
                            sujet,
                            contenu,
                            destinataire,
                            datetime.now(),
                            'Envoyé',
                            priorite
                        )
                        
                        if save_communication(comm_data):
                            st.success("Communication marquée comme envoyée!")
                            st.balloons()
                            st.cache_data.clear()
                            st.rerun()
            
            with col3:
                if st.button("📋 Aperçu"):
                    if sujet and contenu:
                        st.markdown("### 📧 Aperçu de la Communication")
                        st.markdown(f"**À:** {destinataire}")
                        st.markdown(f"**Sujet:** {sujet}")
                        st.markdown("**Contenu:**")
                        st.markdown(contenu)
        
        with tab3:
            # RAPPORTS AUTOMATIQUES
            st.subheader("🤖 Génération Automatique de Rapports")
            
            projet_rapport = st.selectbox("Projet pour le rapport", [p['nom_projet'] for p in projets], key="rapport_auto")
            projet_id = next(p['id'] for p in projets if p['nom
