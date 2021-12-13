import nutriscore_pre_traitement as va_pre
import pandas as pd
import numpy as np
from time import time
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import matplotlib as mp
from matplotlib.collections import LineCollection
from scipy.cluster.hierarchy import dendrogram

# ---------------------------------------------------------------------------------------------
# CONSTANTES GLOBALES
# ---------------------------------------------------------------------------------------------
colorsPaletteSeaborn = ["deep", "muted", "bright", "pastel", "dark", "colorblind"]
colors = ["b", "g", "r", "c", "m", "y", "k"]
colorsSeaborn = {"b": "blue", "g": "green", "r": "red", "c": "cyan", "m": "magenta", "y": "yellow", "k": "black", "w": "white"}
nutriscore_colors = {"A":"green", "B":"#AACE73","C":"yellow","D":"orange","E":"red", 
                     "1":"green", "2":"#AACE73","3":"yellow","4":"orange","5":"red",
                     1:"green", 2:"#AACE73",3:"yellow",4:"orange",5:"red",
                     "1.0":"green", "2.0":"yellow","3.0":"orange","4.0":"red", 
                     1.0:"green", 2.0:"yellow",3.0:"orange",4.0:"red", np.nan:"blue"}
nutriscore_colors_list = ["green", "#AACE73","yellow","orange","red"]
PLOT_FIGURE_BAGROUNG_COLOR = 'tan'
PLOT_BAGROUNG_COLOR = PLOT_FIGURE_BAGROUNG_COLOR

# ---------------------------------------------------------------------------------------------
# FUNCTIONS GRAPHIQUES
# ---------------------------------------------------------------------------------------------
def draw_pie(df, column_name, axe, verbose=False):
    """Fonction pour dessiner un graphe pie pour la colonne reçue
    Args:
        df (DataFrame): Données à représenter
        column_name (String): colonne à représenter
        country_name_list (list[String], optional): Liste des pays à traiter. Defaults to [].
        verbose (bool, optional): Mode debug. Defaults to False.
    """
    df_nova = df[~df[column_name].isna()][column_name].value_counts().reset_index()
    df_nova = df_nova.sort_values("index")
    # Affichage des graphiques
    axe.pie(df_nova[column_name], labels=df_nova["index"], colors=nutriscore_colors_list, autopct='%.0f%%')
    axe.legend(df_nova["index"], loc="upper left")
    axe.set_title(column_name)
    axe.set_facecolor(PLOT_BAGROUNG_COLOR)


def draw_pie_multiple(df, column_names, verbose=False):
    """Fonction pour dessiner un graphe pie pour la colonne reçue

    Args:
        df (DataFrame): Données à représenter
        column_name (String): colonne à représenter
        country_name_list (list[String], optional): Liste des pays à traiter. Defaults to [].
        verbose (bool, optional): Mode debug. Defaults to False.
    """
    figure, axes = plt.subplots(1,len(column_names))
    i = 0
    for column_name in column_names:
        if len(column_names) > 1:
            draw_pie(df, column_name, axes[i], verbose)
        else:
            draw_pie(df, column_name, axes, verbose)
        i += 1
    figure.set_size_inches(15, 5, forward=True)
    figure.set_dpi(100)
    figure.patch.set_facecolor(PLOT_FIGURE_BAGROUNG_COLOR)
    figure.suptitle("NUTRISCORE - "+column_name+" REPARTITION", fontsize=16)
    plt.show()
    print("draw_pie", column_name," ................................................. END")


def draw_pie_multiple_by_value(df, column_name, values, compare_column_names, verbose=False):
    """ Fonction pour dessiner un graphe pie pour la colonne reçue

    Args:
        df (DataFrame): Données à représenter
        column_name (String): colonne à représenter
        country_name_list (list[String], optional): Liste des pays à traiter. Defaults to [].
        verbose (bool, optional): Mode debug. Defaults to False.
    """
    figure, axes = plt.subplots(1,len(values))
    i = 0
    for val in values:
        draw_pie(df[df[column_name]==val], compare_column_names, axes[i], verbose)
        axes[i].set_title(column_name+"="+str(val))
        axes[i].set_facecolor(PLOT_BAGROUNG_COLOR)   
        i += 1
    figure.set_size_inches(15, 5, forward=True)
    figure.set_dpi(100)
    figure.patch.set_facecolor(PLOT_FIGURE_BAGROUNG_COLOR)
    figure.suptitle("NUTRISCORE - "+compare_column_names +" REPARTITION switch "+column_name, fontsize=16)
    plt.show()
    print("draw_pie", column_name," ................................................. END")


def create_and_draw_nutriscore_group(df, columns_name=['countries_en', 'brands'], group_name='nutriscore_grade', title=""):
    ####################### CREATION DF PAR NUTRI-SCORE #######################
    data_nutri_brand = df.groupby(columns_name)[group_name].value_counts().unstack(fill_value=0)
    data_nutri_brand["sum"] = data_nutri_brand.sum(axis=1)
    data_nutri_brand=data_nutri_brand.sort_values(by="sum", ascending=False)
    print(data_nutri_brand.shape)
    data_nutri_brand = data_nutri_brand.drop("sum", axis=1)

    figure, axes = plt.subplots(1, 1)
    data_nova2 = data_nutri_brand.transpose().reset_index()
    sns.set()
    data_nova2.set_index(group_name).T.plot(kind='barh',
                                                    stacked=True, ax=axes, color=nutriscore_colors)
    axes.set_facecolor(PLOT_BAGROUNG_COLOR)
    figure.set_size_inches(15, data_nutri_brand.shape[0]//2, forward=True)
    figure.set_dpi(100)
    figure.patch.set_facecolor(PLOT_FIGURE_BAGROUNG_COLOR)
    figure.suptitle(title, fontsize=14)
    plt.show


def draw_correlation_graphe(df, verbose):
    """Dessine le graphe de corrélation des données

    Args:
        df (DataFrame): Données à représenter
        verbose (bool, optional): Mode debug. Defaults to False.
    """
    corr_df = df.corr()
    if verbose:
        print("CORR ------------------")
        print(corr_df, "\n")
    figure, ax = plt.subplots(1,1)
    figure.set_size_inches(18.5, 10.5, forward=True)
    figure.set_dpi(100)
    figure.suptitle("NUTRISCORE - Corrélation entre les données", fontsize=16)
    figure.patch.set_facecolor(PLOT_FIGURE_BAGROUNG_COLOR)
    ax.set_facecolor(PLOT_BAGROUNG_COLOR)
    sns.heatmap(corr_df, annot=True)
    plt.show()


def graphe_outliers(df_out, column, q_min, q_max):
    figure, axes = plt.subplots(1,2)
    # Avant traitement des outliers
    # Boite à moustaches
    df_out.boxplot(column=[column], grid=True, ax=axes[0])
    # scatter
    df_only_ok = df_out[(df_out[column]>=q_min) & (df_out[column]<=q_max)]
    df_only_ouliers = df_out[(df_out[column]<q_min) | (df_out[column]>q_max)]
    plt.scatter(df_only_ok[column].index, df_only_ok[column].values, c='blue')
    plt.scatter(df_only_ouliers[column].index, df_only_ouliers[column].values, c='red')
    # Dimensionnement du graphe
    figure.set_size_inches(18, 7, forward=True)
    figure.patch.set_facecolor(PLOT_FIGURE_BAGROUNG_COLOR)
    figure.set_dpi(100)
    figure.suptitle("NUTRISCORE - "+column, fontsize=16)
    plt.show()


def create_boxplot_by_data_before_and_after_outliers(df, remove=True, verbose=False):
    """Représente les boites à moustache par groupe : première ligne avant nettoyage des outliers, seconde ligne après nettoyage.
    Toutes les colonnes de types numériques sont représentées et regroupées avec les colonnes data_names

    Args:
        df (DataFrame): Données à traiter
        data_names ([String]): liste des colonnes avec lesquelles faire le regroupement
        verbose (bool, optional): Mode debug. Defaults to False.

    Returns:
        [DataFrame]: copie du dataframe de départ, nettoyé de ses outliers
    """
    df = df.copy()
    # Colonnes numériques
    nutri = va_pre.get_outliers_columns_names(df, verbose)
    
    for column in nutri:
        try:
            if df[column].dtypes == 'float64' or df[column].dtypes == 'int' or isinstance(df[column].dtypes, int):
                # Dessin du graphe
                q_low, q_hi,iqr, q_min, q_max = va_pre.get_outliers_datas(df, column)
                graphe_outliers(df, column, q_min, q_max)

                # Boite à moustaches
                df = va_pre.remove_outliers(df, [column], remove=remove, verbose=verbose)
                graphe_outliers(df, column, q_min, q_max)
            if verbose :
                print("create_boxplot_by_data_before_and_after_outliers:", column, "--------------- > END")
        except:
            print("Exception create_boxplot_by_data_before_and_after_outliers:", column)
    return df


# Calcul des outliers pour toutes les colonnes
def create_boxplot_by_data_with_outliers_then_without_outliers(df, dic_outliers=None, remove=True, verbose=False):
    """Représente les boites à moustache par groupe : première ligne avant nettoyage des outliers, seconde ligne après nettoyage.
    Toutes les colonnes de types numériques sont représentées et regroupées avec les colonnes data_names

    Args:
        df (DataFrame): Données à traiter
        data_names ([String]): liste des colonnes avec lesquelles faire le regroupement
        verbose (bool, optional): Mode debug. Defaults to False.

    Returns:
        [DataFrame]: copie du dataframe de départ, nettoyé de ses outliers
    """
    df = df.copy()
    # Colonnes numériques
    nutri = va_pre.get_outliers_columns_names(df, verbose)
    # Calcul des outliers initiaux
    dic_outliers = {}

    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("~                                       Données AVANT traitement des outliers                                           ~")
    print("~",nutri, "~")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    for column in nutri:
        try:
            if df[column].dtypes == 'float64' or df[column].dtypes == 'int' or isinstance(df[column].dtypes, int):
                # q_low, q_hi,iqr, q_min, q_max
                dic_outliers[column] = va_pre.get_outliers_datas(df, column)
                # Dessin du graphe
                graphe_outliers(df, column, dic_outliers[column][3], dic_outliers[column][4])
            if verbose :
                print("create_boxplot_by_data_before_and_after_outliers:", column, "--------------- > END")
        except:
            print("Exception create_boxplot_by_data_before_and_after_outliers:", column)

    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("~                                      Données APRES suppression des outliers                                           ~")
    print("~",nutri, "~")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    # Génération des graphes après suppression des outliers
    for column in nutri:
        try:
            if df[column].dtypes == 'float64' or df[column].dtypes == 'int' or isinstance(df[column].dtypes, int):
                # q_low, q_hi,iqr, q_min, q_max
                q_low, q_hi,iqr, q_min, q_max = dic_outliers[column]
                # Suppression des outliers
                df = va_pre.remove_column_outliers(df, column, q_low, q_hi,iqr, q_min, q_max, remove=remove, verbose=verbose)
                # Boite à moustaches
                # Dessin du graphe
                graphe_outliers(df, column, dic_outliers[column][3], dic_outliers[column][4])
            if verbose :
                print("create_boxplot_by_data_before_and_after_outliers:", column, "--------------- > END")
        except:
            print("Exception create_boxplot_by_data_before_and_after_outliers:", column)
    return df


def createNutriGraph(data, column_name='nutriscore_grade', size=5):
    figure, axes = plt.subplots(1, 1)
    data_plot = data.transpose().reset_index()
    data_plot = data_plot.drop(size, axis=0)
    sns.set()
    colors = ["green", "#AACE73", "yellow", "orange", "red"]
    data_plot.set_index(column_name).T.plot(kind='barh',
                                                    stacked=True, ax=axes, color=colors)
    axes.set_facecolor(PLOT_BAGROUNG_COLOR)
    figure.set_size_inches(7, 8, forward=True)
    figure.set_dpi(100)
    figure.patch.set_facecolor(PLOT_FIGURE_BAGROUNG_COLOR)
    plt.title(column_name, fontsize=14)
    plt.show()


def draw_scatter(df, colname, q_min, q_max):
    df_only_ok = df[(df[colname]>=q_min) & (df[colname]<=q_max)]
    df_only_ouliers = df[(df[colname]<q_min) | (df[colname]>q_max)]

    plt.scatter(df_only_ok[colname].index, df_only_ok[colname].values, c='blue')
    plt.scatter(df_only_ouliers[colname].index, df_only_ouliers[colname].values, c='red')
    plt.show()


def draw_boxplot_v(df, colname):
    plt.figure(figsize=(5,10), facecolor=PLOT_FIGURE_BAGROUNG_COLOR)
    df.boxplot(column=[colname], grid=True)


def draw_boxplot_h(df, colname):
    plt.figure(figsize=(15,5), facecolor=PLOT_FIGURE_BAGROUNG_COLOR)
    sns.boxplot(data=df[colname],x=df[colname])


def display_circles(pcs, n_comp, pca, axis_ranks, labels=None, label_rotation=0, lims=None):
    for d1, d2 in axis_ranks: # On affiche les 3 premiers plans factoriels, donc les 6 premières composantes
        if d2 < n_comp:

            # initialisation de la figure
            fig, ax = plt.subplots(figsize=(7,6))

            # détermination des limites du graphique
            if lims is not None :
                xmin, xmax, ymin, ymax = lims
            elif pcs.shape[1] < 30 :
                xmin, xmax, ymin, ymax = -1, 1, -1, 1
            else :
                xmin, xmax, ymin, ymax = min(pcs[d1,:]), max(pcs[d1,:]), min(pcs[d2,:]), max(pcs[d2,:])

            # affichage des flèches
            # s'il y a plus de 30 flèches, on n'affiche pas le triangle à leur extrémité
            if pcs.shape[1] < 30 :
                plt.quiver(np.zeros(pcs.shape[1]), np.zeros(pcs.shape[1]),
                   pcs[d1,:], pcs[d2,:], 
                   angles='xy', scale_units='xy', scale=1, color="grey")
                # (voir la doc : https://matplotlib.org/api/_as_gen/matplotlib.pyplot.quiver.html)
            else:
                lines = [[[0,0],[x,y]] for x,y in pcs[[d1,d2]].T]
                ax.add_collection(LineCollection(lines, axes=ax, alpha=.1, color='black'))
                ax.set_facecolor(PLOT_BAGROUNG_COLOR)
            
            # affichage des noms des variables  
            if labels is not None:  
                for i,(x, y) in enumerate(pcs[[d1,d2]].T):
                    if x >= xmin and x <= xmax and y >= ymin and y <= ymax :
                        plt.text(x, y, labels[i], fontsize='14', ha='center', va='center', rotation=label_rotation, color="blue", alpha=0.5)
            
            # affichage du cercle
            circle = plt.Circle((0,0), 1, facecolor='none', edgecolor='b')
            plt.gca().add_artist(circle)

            # définition des limites du graphique
            plt.xlim(xmin, xmax)
            plt.ylim(ymin, ymax)
            # affichage des lignes horizontales et verticales
            plt.plot([-1, 1], [0, 0], color='grey', ls='--')
            plt.plot([0, 0], [-1, 1], color='grey', ls='--')

            # nom des axes, avec le pourcentage d'inertie expliqué
            plt.xlabel('F{} ({}%)'.format(d1+1, round(100*pca.explained_variance_ratio_[d1],1)))
            plt.ylabel('F{} ({}%)'.format(d2+1, round(100*pca.explained_variance_ratio_[d2],1)))

            fig.patch.set_facecolor(PLOT_FIGURE_BAGROUNG_COLOR)
            plt.title("Cercle des corrélations (F{} et F{})".format(d1+1, d2+1))
            plt.show(block=False)
        

def display_factorial_planes_by_theme(X_projected,pca, n_comp, axis_ranks, alpha=0.5, illustrative_var=None, by_theme=False):
    for d1,d2 in axis_ranks:
        if d2 < n_comp:
            # affichage des points
            illustrative_var = np.array(illustrative_var)
            valil = np.unique(illustrative_var)

            figure, axes = plt.subplots(2,len(valil)//2)

            # détermination des limites du graphique
            boundary = np.max(np.abs(X_projected[:, [d1,d2]])) * 1.1
            
            # On commence par traiter le NAN pour plus de lisibilité dans le graphe
            value = str(np.nan)
            i = 0
            j = 0
            if value in valil :
                _display_one_scatter(X_projected, pca, axes[i][j], value, d1, d2, alpha,boundary, illustrative_var)
                valil = valil[valil != value]
                j += 1
            
            for value in valil:
                _display_one_scatter(X_projected, pca, axes[i][j], value, d1, d2, alpha,boundary, illustrative_var)
                
                j += 1
                if j > (len(valil)//2):
                    i += 1
                    j = 0
            
            figure.set_size_inches(18.5, 7, forward=True)
            figure.set_dpi(100)
            figure.patch.set_facecolor(PLOT_FIGURE_BAGROUNG_COLOR)
            figure.suptitle("Projection des individus (sur F{} et F{})".format(d1+1, d2+1))
            plt.show(block=False)


def display_factorial_planes(X_projected, n_comp, pca, axis_ranks, labels=None, alpha=0.5, illustrative_var=None):
    for d1,d2 in axis_ranks:
        if d2 < n_comp:
 
            # initialisation de la figure       
            plt.figure(figsize=(7,6), facecolor=PLOT_FIGURE_BAGROUNG_COLOR)
        
            # affichage des points
            if illustrative_var is None:
                plt.scatter(X_projected[:, d1], X_projected[:, d2], alpha=alpha)
            else:
                illustrative_var = np.array(illustrative_var)
                valil = np.unique(illustrative_var)
                # On commence par traiter le NAN pour plus de lisibilité dans le graphe
                value = str(np.nan)
                if value in valil :
                    selected = np.where(illustrative_var == value)
                    plt.scatter(X_projected[selected, d1], X_projected[selected, d2], alpha=alpha, label=value, c=nutriscore_colors.get(value, "blue"), s=100)
                    valil = valil[valil != value]
                for value in valil:
                    selected = np.where(illustrative_var == value)
                    plt.scatter(X_projected[selected, d1], X_projected[selected, d2], alpha=alpha, label=value, c=nutriscore_colors.get(value, "blue"), s=100)
                plt.legend()

            # affichage des labels des points
            if labels is not None:
                for i,(x,y) in enumerate(X_projected[:,[d1,d2]]):
                    plt.text(x, y, labels[i],
                              fontsize='14', ha='center',va='center') 
                
            # détermination des limites du graphique
            boundary = np.max(np.abs(X_projected[:, [d1,d2]])) * 1.1
            plt.xlim([-boundary,boundary])
            plt.ylim([-boundary,boundary])
        
            # affichage des lignes horizontales et verticales
            plt.plot([-100, 100], [0, 0], color='grey', ls='--')
            plt.plot([0, 0], [-100, 100], color='grey', ls='--')

            # nom des axes, avec le pourcentage d'inertie expliqué
            plt.xlabel('F{} ({}%)'.format(d1+1, round(100*pca.explained_variance_ratio_[d1],1)))
            plt.ylabel('F{} ({}%)'.format(d2+1, round(100*pca.explained_variance_ratio_[d2],1)))
            plt.title("Projection des individus (sur F{} et F{})".format(d1+1, d2+1))
            plt.show(block=False)

def display_scree_plot(pca):
    scree = pca.explained_variance_ratio_*100
    plt.figure(figsize=(18,7), facecolor=PLOT_FIGURE_BAGROUNG_COLOR)
    plt.bar(np.arange(len(scree))+1, scree)
    plt.plot(np.arange(len(scree))+1, scree.cumsum(),c="red",marker='o')
    plt.xlabel("rang de l'axe d'inertie")
    plt.ylabel("pourcentage d'inertie")
    plt.title("Eboulis des valeurs propres")
    plt.show(block=False)

def plot_dendrogram(Z, names):
    plt.figure(figsize=(18,7), facecolor=PLOT_FIGURE_BAGROUNG_COLOR)
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('distance')
    dendrogram(
        Z,
        labels = names,
        orientation = "left",
    )
    plt.show()

 
def _display_one_scatter(X_projected, pca, axe,value, d1, d2, alpha, boundary, illustrative_var):
    selected = np.where(illustrative_var == value)
    c=nutriscore_colors.get(value, "blue")
    axe.scatter(X_projected[selected, d1], X_projected[selected, d2], alpha=alpha, label=value, c=c, s=100)
    axe.legend()
    # nom des axes, avec le pourcentage d'inertie expliqué
    axe.set_xlabel('F{} ({}%)'.format(d1+1, round(100*pca.explained_variance_ratio_[d1],1)))
    axe.set_ylabel('F{} ({}%)'.format(d2+1, round(100*pca.explained_variance_ratio_[d2],1)))

    axe.set_xlim([-boundary,boundary])
    axe.set_ylim([-boundary,boundary])
    # affichage des lignes horizontales et verticales
    axe.plot([-100, 100], [0, 0], color='grey', ls='--')
    axe.plot([0, 0], [-100, 100], color='grey', ls='--')
    axe.set_facecolor(PLOT_BAGROUNG_COLOR)
    
