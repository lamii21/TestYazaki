"""
Tableau de bord analytique pour le système BOM
Visualisations et métriques avancées
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Any

class BOMAnalyticsDashboard:
    """
    Tableau de bord analytique pour le système BOM
    """
    
    def __init__(self, repository=None):
        """
        Initialise le dashboard
        
        Args:
            repository: Repository pour accéder aux données
        """
        self.repository = repository
        self.setup_page_config()
    
    def setup_page_config(self):
        """Configure la page Streamlit"""
        st.set_page_config(
            page_title="📊 BOM Analytics Dashboard",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def render_dashboard(self):
        """Affiche le tableau de bord complet"""
        st.title("📊 Tableau de Bord BOM Analytics")
        st.markdown("---")
        
        # Sidebar pour les filtres
        self.render_sidebar()
        
        # Métriques principales
        self.render_key_metrics()
        
        # Graphiques principaux
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_status_distribution()
            self.render_project_analysis()
        
        with col2:
            self.render_trend_analysis()
            self.render_supplier_analysis()
        
        # Analyses détaillées
        st.markdown("---")
        self.render_detailed_analysis()
        
        # Alertes et recommandations
        self.render_alerts_recommendations()
    
    def render_sidebar(self):
        """Affiche la barre latérale avec les filtres"""
        st.sidebar.header("🔍 Filtres")
        
        # Filtre par période
        st.sidebar.subheader("📅 Période")
        date_range = st.sidebar.date_input(
            "Sélectionner la période",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now()
        )
        
        # Filtre par projet
        st.sidebar.subheader("📋 Projets")
        projects = self.get_available_projects()
        selected_projects = st.sidebar.multiselect(
            "Sélectionner les projets",
            options=projects,
            default=projects[:5] if len(projects) > 5 else projects
        )
        
        # Filtre par statut
        st.sidebar.subheader("🏷️ Statuts")
        statuses = ['D', 'X', '0', 'NaN']
        selected_statuses = st.sidebar.multiselect(
            "Sélectionner les statuts",
            options=statuses,
            default=statuses
        )
        
        # Bouton de rafraîchissement
        if st.sidebar.button("🔄 Actualiser les données"):
            st.experimental_rerun()
        
        return {
            'date_range': date_range,
            'projects': selected_projects,
            'statuses': selected_statuses
        }
    
    def render_key_metrics(self):
        """Affiche les métriques clés"""
        st.subheader("📈 Métriques Clés")
        
        # Récupérer les données
        stats = self.get_key_statistics()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="📦 Total Pièces",
                value=stats.get('total_parts', 0),
                delta=stats.get('parts_delta', 0)
            )
        
        with col2:
            st.metric(
                label="✅ Actives (D)",
                value=stats.get('active_parts', 0),
                delta=stats.get('active_delta', 0)
            )
        
        with col3:
            st.metric(
                label="🔄 À Remplacer (X)",
                value=stats.get('replace_parts', 0),
                delta=stats.get('replace_delta', 0)
            )
        
        with col4:
            st.metric(
                label="⚠️ Doublons (0)",
                value=stats.get('duplicate_parts', 0),
                delta=stats.get('duplicate_delta', 0)
            )
        
        with col5:
            st.metric(
                label="❓ Inconnus (NaN)",
                value=stats.get('unknown_parts', 0),
                delta=stats.get('unknown_delta', 0)
            )
    
    def render_status_distribution(self):
        """Graphique de distribution des statuts"""
        st.subheader("🏷️ Distribution des Statuts")
        
        # Données d'exemple (à remplacer par vraies données)
        status_data = {
            'Statut': ['D (Actif)', 'X (À remplacer)', '0 (Doublon)', 'NaN (Inconnu)'],
            'Nombre': [1250, 85, 23, 42],
            'Couleur': ['#2E8B57', '#FFD700', '#FF6347', '#FFA500']
        }
        
        df_status = pd.DataFrame(status_data)
        
        # Graphique en camembert
        fig = px.pie(
            df_status, 
            values='Nombre', 
            names='Statut',
            color_discrete_sequence=df_status['Couleur'],
            title="Répartition par Statut"
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_trend_analysis(self):
        """Analyse des tendances temporelles"""
        st.subheader("📈 Évolution Temporelle")
        
        # Données d'exemple pour les 30 derniers jours
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        
        trend_data = pd.DataFrame({
            'Date': dates,
            'Nouvelles_Pieces': np.random.poisson(5, len(dates)),
            'Modifications': np.random.poisson(3, len(dates)),
            'Suppressions': np.random.poisson(1, len(dates))
        })
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=trend_data['Date'],
            y=trend_data['Nouvelles_Pieces'],
            mode='lines+markers',
            name='Nouvelles Pièces',
            line=dict(color='#2E8B57')
        ))
        
        fig.add_trace(go.Scatter(
            x=trend_data['Date'],
            y=trend_data['Modifications'],
            mode='lines+markers',
            name='Modifications',
            line=dict(color='#FFD700')
        ))
        
        fig.add_trace(go.Scatter(
            x=trend_data['Date'],
            y=trend_data['Suppressions'],
            mode='lines+markers',
            name='Suppressions',
            line=dict(color='#FF6347')
        ))
        
        fig.update_layout(
            title="Évolution des Activités BOM",
            xaxis_title="Date",
            yaxis_title="Nombre d'Opérations",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_project_analysis(self):
        """Analyse par projet"""
        st.subheader("📋 Analyse par Projet")
        
        # Données d'exemple
        project_data = pd.DataFrame({
            'Projet': ['PROJ_A', 'PROJ_B', 'PROJ_C', 'PROJ_D', 'PROJ_E'],
            'Total_Pieces': [450, 320, 280, 150, 100],
            'Actives': [420, 300, 260, 140, 95],
            'A_Remplacer': [25, 15, 15, 8, 4],
            'Problemes': [5, 5, 5, 2, 1]
        })
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Actives',
            x=project_data['Projet'],
            y=project_data['Actives'],
            marker_color='#2E8B57'
        ))
        
        fig.add_trace(go.Bar(
            name='À Remplacer',
            x=project_data['Projet'],
            y=project_data['A_Remplacer'],
            marker_color='#FFD700'
        ))
        
        fig.add_trace(go.Bar(
            name='Problèmes',
            x=project_data['Projet'],
            y=project_data['Problemes'],
            marker_color='#FF6347'
        ))
        
        fig.update_layout(
            title="Répartition par Projet",
            xaxis_title="Projet",
            yaxis_title="Nombre de Pièces",
            barmode='stack',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_supplier_analysis(self):
        """Analyse des fournisseurs"""
        st.subheader("🏭 Analyse Fournisseurs")
        
        # Données d'exemple
        supplier_data = pd.DataFrame({
            'Fournisseur': ['Fournisseur A', 'Fournisseur B', 'Fournisseur C', 'Fournisseur D', 'Autres'],
            'Nombre_Pieces': [380, 250, 180, 120, 70],
            'Valeur_Totale': [15000, 12000, 8500, 6000, 3500]
        })
        
        # Graphique en barres horizontales
        fig = px.bar(
            supplier_data,
            x='Nombre_Pieces',
            y='Fournisseur',
            orientation='h',
            title="Top Fournisseurs par Nombre de Pièces",
            color='Valeur_Totale',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    def render_detailed_analysis(self):
        """Analyses détaillées"""
        st.subheader("🔍 Analyses Détaillées")
        
        tab1, tab2, tab3 = st.tabs(["📊 Données Brutes", "🔄 Historique", "💰 Analyse Coûts"])
        
        with tab1:
            self.render_raw_data_table()
        
        with tab2:
            self.render_history_analysis()
        
        with tab3:
            self.render_cost_analysis()
    
    def render_raw_data_table(self):
        """Table des données brutes avec filtres"""
        st.write("### 📋 Données Master BOM")
        
        # Données d'exemple
        sample_data = pd.DataFrame({
            'Part Number': [f'PN{i:03d}' for i in range(1, 101)],
            'Projet': np.random.choice(['PROJ_A', 'PROJ_B', 'PROJ_C'], 100),
            'Statut': np.random.choice(['D', 'X', '0', 'NaN'], 100, p=[0.7, 0.15, 0.1, 0.05]),
            'Description': [f'Composant {i}' for i in range(1, 101)],
            'Fournisseur': np.random.choice(['Fournisseur A', 'Fournisseur B', 'Fournisseur C'], 100),
            'Prix': np.random.uniform(0.1, 50.0, 100).round(2)
        })
        
        # Filtres interactifs
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox("Filtrer par Statut", ['Tous'] + list(sample_data['Statut'].unique()))
        
        with col2:
            project_filter = st.selectbox("Filtrer par Projet", ['Tous'] + list(sample_data['Projet'].unique()))
        
        with col3:
            search_term = st.text_input("Rechercher Part Number")
        
        # Appliquer les filtres
        filtered_data = sample_data.copy()
        
        if status_filter != 'Tous':
            filtered_data = filtered_data[filtered_data['Statut'] == status_filter]
        
        if project_filter != 'Tous':
            filtered_data = filtered_data[filtered_data['Projet'] == project_filter]
        
        if search_term:
            filtered_data = filtered_data[filtered_data['Part Number'].str.contains(search_term, case=False)]
        
        st.dataframe(filtered_data, use_container_width=True, height=400)
        
        # Bouton d'export
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="📥 Exporter en CSV",
            data=csv,
            file_name=f"bom_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    def render_history_analysis(self):
        """Analyse de l'historique des modifications"""
        st.write("### 🔄 Historique des Modifications")
        
        # Données d'exemple d'historique
        history_data = pd.DataFrame({
            'Date': pd.date_range(start=datetime.now() - timedelta(days=30), periods=50, freq='D'),
            'Part Number': [f'PN{np.random.randint(1, 100):03d}' for _ in range(50)],
            'Action': np.random.choice(['Création', 'Modification', 'Suppression'], 50),
            'Ancien Statut': np.random.choice(['D', 'X', '0', 'NaN'], 50),
            'Nouveau Statut': np.random.choice(['D', 'X', '0', 'NaN'], 50),
            'Utilisateur': np.random.choice(['User1', 'User2', 'System'], 50)
        })
        
        # Graphique des activités par jour
        daily_activity = history_data.groupby('Date').size().reset_index(name='Nombre_Modifications')
        
        fig = px.line(
            daily_activity,
            x='Date',
            y='Nombre_Modifications',
            title="Activité Quotidienne",
            markers=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Table de l'historique
        st.dataframe(history_data.sort_values('Date', ascending=False), use_container_width=True)
    
    def render_cost_analysis(self):
        """Analyse des coûts"""
        st.write("### 💰 Analyse des Coûts")
        
        # Métriques de coût
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Coût Total", "€125,450", "↑ 5.2%")
        
        with col2:
            st.metric("📊 Coût Moyen/Pièce", "€12.35", "↓ 2.1%")
        
        with col3:
            st.metric("🏭 Top Fournisseur", "Fournisseur A", "45% du total")
        
        with col4:
            st.metric("📈 Évolution Mensuelle", "+€3,200", "↑ 2.6%")
        
        # Graphique de répartition des coûts
        cost_data = pd.DataFrame({
            'Catégorie': ['Électronique', 'Mécanique', 'Logiciel', 'Services', 'Autres'],
            'Coût': [45000, 35000, 25000, 15000, 5450],
            'Pourcentage': [35.9, 27.9, 19.9, 12.0, 4.3]
        })
        
        fig = px.treemap(
            cost_data,
            path=['Catégorie'],
            values='Coût',
            title="Répartition des Coûts par Catégorie"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_alerts_recommendations(self):
        """Alertes et recommandations"""
        st.subheader("🚨 Alertes et Recommandations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("#### 🚨 Alertes")
            
            alerts = [
                {"type": "error", "message": "15 pièces avec statut X depuis plus de 30 jours"},
                {"type": "warning", "message": "23 doublons détectés nécessitent une vérification"},
                {"type": "info", "message": "Nouveau fournisseur ajouté: Fournisseur E"}
            ]
            
            for alert in alerts:
                if alert["type"] == "error":
                    st.error(alert["message"])
                elif alert["type"] == "warning":
                    st.warning(alert["message"])
                else:
                    st.info(alert["message"])
        
        with col2:
            st.write("#### 💡 Recommandations")
            
            recommendations = [
                "Réviser les pièces avec statut X pour optimisation",
                "Consolider les fournisseurs pour réduire les coûts",
                "Mettre à jour les descriptions manquantes",
                "Planifier audit des doublons identifiés"
            ]
            
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
    
    def get_available_projects(self) -> List[str]:
        """Récupère la liste des projets disponibles"""
        # À remplacer par vraie requête DB
        return ['PROJ_A', 'PROJ_B', 'PROJ_C', 'PROJ_D', 'PROJ_E']
    
    def get_key_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques clés"""
        # À remplacer par vraies données
        return {
            'total_parts': 1400,
            'parts_delta': 25,
            'active_parts': 1250,
            'active_delta': 15,
            'replace_parts': 85,
            'replace_delta': 5,
            'duplicate_parts': 23,
            'duplicate_delta': 2,
            'unknown_parts': 42,
            'unknown_delta': 3
        }

def main():
    """Fonction principale pour lancer le dashboard"""
    dashboard = BOMAnalyticsDashboard()
    dashboard.render_dashboard()

if __name__ == "__main__":
    main()
