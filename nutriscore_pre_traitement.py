import nutriscore_pre_traitement as va_pre
import va_geo_nutriscore
import pandas as pd
from time import time
from datetime import datetime
import numpy as np


# ---------------------------------------------------------------------------------------------
#                               VARIABLES GLOBALES
# ---------------------------------------------------------------------------------------------
# Variables Globales

# Colonne à exclure du chargement
df_col_to_exclude = {'url', 'created_t','last_modified_t',
                     'image_url', 'image_small_url','image_nutrition_url', 'image_nutrition_small_url',
                     'image_ingredients_url', 'image_ingredients_small_url', 'energy_100g',
                     'countries', 'states', 'states_tags', 'states_en', 'categories', 'categories_tags','main_category'}

df_columns_names_keeped_origin = {'code', 'created_datetime', 'last_modified_datetime', 'product_name', 'generic_name', 'nova_group',
                                'quantity', 'packaging_tags', "brands_tags", "categories_tags","main_category_en", "origins_tags",
                                "manufacturing_places_tags", "labels_tags", "emb_codes_tags", "cities_tags",
                                "purchase_places", "stores", "countries_tags", "traces_tags", "additives_n",
                                "additives_tags", "main_category", "pnns_groups_1", "pnns_groups_2", "energy-kcal_100g",
                                "energy_100g", "fat_100g", "saturated-fat_100g", "carbohydrates_100g", "sugars_100g",
                                "proteins_100g", "salt_100g", "sodium_100g", "nutrition-score-fr_100g", "nutrition-score",
                                "ingredients_text", "allergens", "ingredients_from_palm_oil_n", "nutriscore_grade"}


NB_NUTRI_MIN = 8

# ---------------------------------------------------------------------------------------------
#                              FONCTIONS UTILES
# ---------------------------------------------------------------------------------------------
def get_energy_columns_names(df, verbose=False):
    """Construit et retourne la liste des noms de colonnes des energy
    Args:
        df (DataFrame): Données
        verbose (bool, optional): Mode debug. Defaults to False.

    Returns:
        List(String): liste des noms de colonne
    """
    lst_nut = get_nutriments_columns_names(df, verbose)
    lst_nrj = lst_nut[lst_nut.str.contains("energy")] 
    return lst_nrj


def get_nutriments_columns_names(df, verbose=False):
    """Construit et retourne la liste des noms de colonnes des nutriments (toutes les colonnes finissant par _100g + "additives_n")
    Args:
        df (DataFrame): Données
        verbose (bool, optional): Mode debug. Defaults to False.

    Returns:
        List(String): liste des noms de colonne
    """
    lst_nut = df.columns[df.columns.str.contains("_100g")]
    lst_nut = lst_nut.drop('fruits-vegetables-nuts-estimate-from-ingredients_100g')
    lst_nut=list(lst_nut)
    lst_nut.append("additives_n")
    return lst_nut


def get_numeric_columns_names(df, verbose=False):
    """Construit et retourne la liste des noms de colonnes des nutriments (toutes les colonnes finissant par _100g + "additives_n")
    Args:
        df (DataFrame): Données
        verbose (bool, optional): Mode debug. Defaults to False.

    Returns:
        List(String): liste des noms de colonne
    """
    lst_nut = df.columns[df.columns.str.contains("_100g") | df.columns.str.contains("_n")]
    lst_nut=list(lst_nut)
    return lst_nut


def get_outliers_columns_names(df, verbose=False):
    """Retourne la liste des colonnes où traiter les outliers

    Args:
        df (DataFrame): 
        verbose (bool, optional): Mode debug. Defaults to False.

    Returns:
        [type]: [description]
    """
    # Colonnes numériques
    nutri = get_numeric_columns_names(df, verbose)
    # Retrait des colonnes que nous ne souhaitons pas modéliser
    nutri.remove("nutrition-score-fr_100g")
    nutri.remove("additives_n")
    nutri.remove("ingredients_from_palm_oil_n")
    nutri.remove("ingredients_that_may_be_from_palm_oil_n")
    return nutri


# ---------------------------------------------------------------------------------------------
#                          NETTOYAGE et COMPLEMENT DES DONNEES
# ---------------------------------------------------------------------------------------------
"""
Colonnes à supprimer
74 % NaN => 1 ['quantity']
75 % NaN => 3 ['serving_size', 'serving_quantity', 'fiber_100g']
78 % NaN => 3 ['labels', 'labels_tags', 'labels_en']
79 % NaN => 2 ['additives_tags', 'additives_en']
84 % NaN => 2 ['packaging', 'packaging_tags']
85 % NaN => 1 ['brand_owner']
86 % NaN => 5 ['stores', 'trans-fat_100g', 'cholesterol_100g', 'calcium_100g', 'iron_100g']
89 % NaN => 2 ['vitamin-a_100g', 'vitamin-c_100g']
90 % NaN => 1 ['allergens']
92 % NaN => 2 ['purchase_places', 'energy-kj_100g']
93 % NaN => 6 ['manufacturing_places', 'manufacturing_places_tags', 'emb_codes', 'emb_codes_tags', 'traces_tags', 'traces_en']
94 % NaN => 2 ['generic_name', 'traces']
95 % NaN => 4 ['origins', 'origins_tags', 'origins_en', 'potassium_100g']
96 % NaN => 2 ['first_packaging_code_geo', 'cities_tags']
97 % NaN => 3 ['ingredients_that_may_be_from_palm_oil_tags', 'monounsaturated-fat_100g', 'polyunsaturated-fat_100g']
98 % NaN => 4 ['alcohol_100g', 'vitamin-b1_100g', 'vitamin-b2_100g', 'vitamin-pp_100g']
99 % NaN => 58 ['abbreviated_product_name', 'packaging_text', 'ingredients_from_palm_oil_tags', 'ecoscore_score_fr', 'ecoscore_grade_fr', 'energy-from-fat_100g', 'omega-3-fat_100g', 'omega-6-fat_100g', 'omega-9-fat_100g', 'starch_100g', 'polyols_100g', 'soluble-fiber_100g', 'insoluble-fiber_100g', 'casein_100g', 'serum-proteins_100g', 'nucleotides_100g', 'beta-carotene_100g', 'vitamin-d_100g', 'vitamin-e_100g', 'vitamin-k_100g', 'vitamin-b6_100g', 'vitamin-b9_100g', 'folates_100g', 'vitamin-b12_100g', 'biotin_100g', 'pantothenic-acid_100g', 'silica_100g', 'bicarbonate_100g', 'chloride_100g', 'phosphorus_100g', 'magnesium_100g', 'zinc_100g', 'copper_100g', 'manganese_100g', 'fluoride_100g', 'selenium_100g', 'chromium_100g', 'molybdenum_100g', 'iodine_100g', 'caffeine_100g', 'taurine_100g', 'ph_100g', 'fruits-vegetables-nuts_100g', 'fruits-vegetables-nuts-dried_100g', 'fruits-vegetables-nuts-estimate_100g', 'collagen-meat-protein-ratio_100g', 'cocoa_100g', 'chlorophyl_100g', 'carbon-footprint_100g', 'carbon-footprint-from-meat-or-fish_100g', 'nutrition-score-uk_100g', 'glycemic-index_100g', 'water-hardness_100g', 'choline_100g', 'phylloquinone_100g', 'beta-glucan_100g', 'inositol_100g', 'carnitine_100g']
100 % NaN => 39 ['cities', 'allergens_en', 'no_nutriments', 'additives', 'ingredients_from_palm_oil', 'ingredients_that_may_be_from_palm_oil', '-butyric-acid_100g', '-caproic-acid_100g', '-caprylic-acid_100g', '-capric-acid_100g', '-lauric-acid_100g', '-myristic-acid_100g', '-palmitic-acid_100g', '-stearic-acid_100g', '-arachidic-acid_100g', '-behenic-acid_100g', '-lignoceric-acid_100g', '-cerotic-acid_100g', '-montanic-acid_100g', '-melissic-acid_100g', '-alpha-linolenic-acid_100g', '-eicosapentaenoic-acid_100g', '-docosahexaenoic-acid_100g', '-linoleic-acid_100g', '-arachidonic-acid_100g', '-gamma-linolenic-acid_100g', '-dihomo-gamma-linolenic-acid_100g', '-oleic-acid_100g', '-elaidic-acid_100g', '-gondoic-acid_100g', '-mead-acid_100g', '-erucic-acid_100g', '-nervonic-acid_100g', '-sucrose_100g', '-glucose_100g', '-fructose_100g', '-lactose_100g', '-maltose_100g', '-maltodextrins_100g']
"""
def remove_na_columns(df, max_na=73, verbose=True, inplace=True):
    """Supprime les colonnes qui ont un pourcentage de NA supérieur au max_na

    Args:
        df (DataFrame): Données à nettoyer
        max_na (int) : pourcentage de NA maximum accepté (qui sera conserver)
        verbose (bool, optional): Mode debug. Defaults to False.
        inplace (bool, optional): Pour mettre à jour la dataframe reçue directement. Defaults to True.

    Returns:
        [DataFrame]: DataFrame avec les données mises à jour
    """
    t0 = time()
    if not inplace:
        df = df.copy()
        
    to_remove = set()
    dict_col = {}

    # Constitution de la list des colonnes à supprimer
    for col in df.columns:
        pourcent = int((df[col].isna().sum()*100)/df.shape[0])
        list = dict_col.get(pourcent, [])
        list.append(col)
        dict_col[pourcent] = list
        if (pourcent > max_na and 'energy-kj_100g' not in col) or col in df_col_to_exclude:
            to_remove.add(col)
    
    if verbose:
        for k in range(101):
            if len(dict_col.get(k, [])) > 0:
                print(k, "=>", len(dict_col.get(k, [])), dict_col.get(k, []))
    
    shape_start = df.shape
    # Suppression des colonnes
    df.drop(to_remove, axis=1, inplace=True)
    shape_end = df.shape
    
    t1 = (time() - t0) / 60
    print("remove_na_columns, shape start: ",shape_start,"=>",shape_end," in {0:.3f} minutes............................................... END".format(t1))        
    return df  


def complete_kcal_from_kj_values(df, verbose=True, inplace=True):
    """Calcule le nombre de calories à partir des kj et remplace les NaN par le résultat. 1 Kj = 239,006 kcal

    Args:
        df (DataFrame): Données à nettoyer
        verbose (bool, optional): Mode debug. Defaults to False.
        inplace (bool, optional): Pour mettre à jour la dataframe reçue directement. Defaults to True.

    Returns:
        [DataFrame]: DataFrame avec les données mises à jour
    """
    t0 = time()
    if not inplace:
        df = df.copy()
    stard_na = df["energy-kcal_100g"].isna().sum()
    if stard_na > 0:
        df.loc[df["energy-kcal_100g"].isna(), "energy-kcal_100g"] = df["energy-kj_100g"] * 239.006
    nb_na = df["energy-kcal_100g"].isna().sum()
    
    t1 = (time() - t0) / 60
    print("complete_kcal_from_kj_values NA {:_}".format(stard_na), "> {:_}".format(nb_na), "({:_})".format(stard_na - nb_na) ,"in {0:.2f} minutes...................................... END".format(t1))    
    return df  


def complete_kj_from_kcal_values(df, verbose=True, inplace=True):
    """Calcule le nombre de calories à partir des kj et remplace les NaN par le résultat. 1 Kj = 239,006 kcal

    Args:
        df (DataFrame): Données à nettoyer
        verbose (bool, optional): Mode debug. Defaults to False.
        inplace (bool, optional): Pour mettre à jour la dataframe reçue directement. Defaults to True.

    Returns:
        [DataFrame]: DataFrame avec les données mises à jour
    """
    t0 = time()
    if not inplace:
        df = df.copy()
    stard_na = df["energy-kj_100g"].isna().sum()
    if stard_na > 0:
        df.loc[df["energy-kj_100g"].isna(), "energy-kj_100g"] = df["energy-kcal_100g"] / 239.006
    nb_na = df["energy-kj_100g"].isna().sum()
    
    t1 = (time() - t0) / 60
    print("complete_kj_from_kcal_values NA {:_}".format(stard_na), "> {:_}".format(nb_na), "({:_})".format(stard_na - nb_na) ,"in {0:.2f} minutes...................................... END".format(t1))     
    return df  


def replace_unknown_and_absurded_values(df, verbose=False, inplace=True):
    """
    Replace all unknown and absurded values by nan value, to facilitate cleaning
    :param df: DataFrame
    :param verbose: <boolean>: True pour mode debug
    :param inplace:<boolean> : False to make a Dataframe copy en return it, True to update the param Dataframe
    :return: DataFrame
    """
    t0 = time()
    if not inplace:
        df = df.copy()
    nb_columns_updated = 0
    nb_na_before = df.isna().sum().sum()

    nb_start = df.shape[0]
    # La somme des nutriments ne doit pas dépasser 100g
    df = df[~((df['fat_100g'] + df['carbohydrates_100g'] + df['salt_100g'] + df['proteins_100g'])>100)]
    print("Suppression des produits dont la somme des nutriments est > 100g =>",nb_start - df.shape[0],"produits supprimés------------------------- DONE")

    # Traitement des colonnes corrélées
    nb = df[(df["fat_100g"]<df["saturated-fat_100g"])].shape[0]
    df.loc[(df["fat_100g"]<df["saturated-fat_100g"]), "saturated-fat_100g"] = np.nan
    print("Produits où les satured fat sont > aux fat =>",nb,"produits impactés------------------------- DONE")
    
    nb = df[(df["carbohydrates_100g"]<df["sugars_100g"])].shape[0]
    df.loc[(df["carbohydrates_100g"]<df["sugars_100g"]), "sugars_100g"] = np.nan
    print("Produits où les sucres sont > aux glucides =>",nb,"produits impactés------------------------- DONE")

    # L'énergie ne peut pas être supérieure à 900 Kcal
    nb = df[(df["energy-kcal_100g"]>900)].shape[0]
    df.loc[df["energy-kcal_100g"]>900, "energy-kcal_100g"] = np.nan
    print("Produits où l'énergie Kcal est >  900 =>",nb,"produits impactés------------------------- DONE")

    # L'énergie ne peut pas être supérieure à 3 700 KJ
    nb = df[(df["energy-kj_100g"]>3700)].shape[0]
    df.loc[df["energy-kj_100g"]>3700, "energy-kj_100g"] = np.nan
    print("Produits où l'énergie Kj est > 3 700 =>",nb,"produits impactés------------------------- DONE")

    for column in df.columns:
        # Remplacement des unknown
        nb_na_before_col = df[column].isna().sum()
        df.loc[df[column] == 'unknown', column] = np.nan

        # Traitement de nutriscore qui doivent avoir des données entre –15 et +40
        if "nutrition-score" in column:
            if "-fr_100g" in column:
                df.loc[df[column] > 40, column] = np.nan
                df.loc[df[column] < -15, column] = np.nan
            else:
                # nutrition-score-uk
                pass
        # Traitement des colonnes qui devraient avoir des valeurs entre 0 et 100g
        # fields that end with _100g correspond to the amount of a nutriment (in g, or kJ for energy) 
        # for 100 g or 100 ml of product
        elif "100g" in column:
            # or kJ for energy
            # Le nombre peut donc être au dessus de 100
            if "energy" not in column:
                df.loc[df[column] > 100, column] = np.nan
            df.loc[df[column] < 0, column] = np.nan
        # Comptabilisation des modifications
        nb_na_after_col3 = df[column].isna().sum()
        if nb_na_after_col3 > nb_na_before_col:
            nb_columns_updated += 1
        
    nb_na_after = df.isna().sum().sum()
    t1 = (time() - t0) / 60
    print("replace_unknown_and_absurded_values",nb_columns_updated, "col updated and NA {:_}".format(nb_na_before), "> {:_}".format(nb_na_after), "({:_})".format(nb_na_after - nb_na_before) ,"in {0:.2f} minutes...................................... END".format(t1))
    return df


def clean_pms_group_na_level1(df, verbose=True, inplace=True):
    """Créé une nouvelle colonne "pnns_groups" avec en premier le pnns_groups_2, si NA, le pnns_groups_1, si NA main_category 
    Args:
        df (DataFrame): Données à nettoyer
        verbose (bool, optional): Mode debug. Defaults to False.
        inplace (bool, optional): Pour mettre à jour la dataframe reçue directement. Defaults to True.

    Returns:
        [DataFrame]: Nouveau DataFrame avec la nouvelle colonne
    """
    t0= time()
    if not inplace:
        df = df.copy()

    # Affectation d'un groupe lorsque c'est possible
    df["pnns_groups"] = df["pnns_groups_2"]
    df["pnns_groups"] = df["pnns_groups"].astype('object')
    
    nb_na = df["pnns_groups"].isna().sum()
    stard_na = nb_na
    
    # /!\ Attention, l'ordre des colonnes a de l'importance
    col_to_process = ["pnns_groups_1", 'main_category_en']

    for col in col_to_process:
        if nb_na > 0:
            if verbose:
                print(nb_na, ">", end="")
            if col in df.columns:
                df.loc[df["pnns_groups"].isna(), "pnns_groups"] = df[col]
                nb_na = df["pnns_groups"].isna().sum()                   
        else:
            break
    if verbose:
        print(nb_na)
    
    t1 = (time() - t0) / 60
    print("clean_pms_group_na NA {:_}".format(stard_na), "> {:_}".format(nb_na), "({:_})".format(stard_na - nb_na) ,"in {0:.2f} minutes...................................... END".format(t1))
    return df


def replace_na_nutri_by_mean_by_pnns(df, column_names, verbose=True, inplace=True):
    """Remplace les NA des nutriments (column_names) par la valeur moyenne de la catégorie de ce produit ("pnns_groups")

    Args:
        df (DataFrame): Données à corriger
        column_names (List(String)): liste des noms de colonne
        verbose (bool, optional): Mode debug. Defaults to False.
        inplace (bool, optional): Pour mettre à jour la dataframe reçue directement. Defaults to True.

    Returns:
        df (DataFrame): Données corrigée
    """
    t0 = time()
    if not inplace:
        df = df.copy()
    nb_na_before = df.isna().sum().sum()

    # On ne prend que les pnns_group qui ont plus de 100 produits
    df_sup=df.groupby('pnns_groups').sum()
    df_sup["count"] = df_sup.sum(axis=1)
    df_sup["count"].dropna(inplace=True)
    df_sup_filtred=df_sup[df_sup["count"]>100]
    df_sup_filtred.shape
    # Liste des pnns_groups avec plus de 100 produits
    group_keep_ind=df_sup_filtred.index
    if verbose:
        print(group_keep_ind)

    # Récupération des moyennes pour les catégories représentatives pour chaque nutriment
    nut_mean3=df[df['pnns_groups'].isin(group_keep_ind)].groupby("pnns_groups").mean()[column_names]
    if verbose:
        print('groupby("pnns_groups")',nut_mean3.head(10))
        print('groupby("pnns_groups")',nut_mean3.index)
        print('groupby("pnns_groups")',nut_mean3.shape)

    for nut in column_names:
        nb_na_col_before = df[nut].isna().sum()

        # Il faut supprimer les valeurs NA
        nut_mean = nut_mean3[nut].dropna()
        if verbose:
            print('df_mean[nut].dropna()',nut_mean.shape, "vs",nut_mean3[nut].shape, "before drop na")
            print('df_mut_mean',nut_mean.head(10))
            print('df_mut_mean',nut_mean.index)

        # On récupère la liste des pnns_goups concerncés pour ce nutriment en na du df
        df_nut_from_df_na_nut =df[(df[nut].isna() & df['pnns_groups'].notna())][['pnns_groups', nut]]
        # On reset l'index pour avoir la colonne "pnns_groups" comme dans le df (pour le merge)
        nut_mean_reindex = nut_mean.reset_index()
        # Pour conserver l'index, on commence par faire un reset, puis on merge, puis on réaffecte l'index
        # On fusionne les deux DF sur la colonne pnns_groups
        nut_mean_sized = df_nut_from_df_na_nut.reset_index().merge(nut_mean_reindex,on="pnns_groups").set_index('index')
        # On affecte les valeurs au DF initiale, comme l'index est le même, 
        # on affecte les valeurs uniquements aux lignes de l'index de nut_mean_sized, donc des NA avec pnns_groups
        # La colonne fusionnée voit son nom complete d'un _y
        df.loc[nut_mean_sized.index, nut]=nut_mean_sized[nut+"_y"]
        
        nb_na_col_after = df[nut].isna().sum()
        if verbose:
            print(nut,":", nb_na_col_before, "=>", nb_na_col_after, "(", nb_na_col_after - nb_na_col_before,")")

    nb_na_after = df.isna().sum().sum()
    t1 = (time() - t0) / 60
    print("replace_na_nutri_by_mean_by_pnns NA {:_}".format(nb_na_before), "> {:_}".format(nb_na_after), "({:_})".format(nb_na_after - nb_na_before) ,"in {0:.2f} minutes...................................... END".format(t1))
    return df


def clean_df_na(df, verbose=False, inplace=True, remove_added_col=False):
    t0 = time()
    if not inplace:
        df = df.copy()

    nb_na_before = df.isna().sum().sum()
    # on compte le nombre de valeurs manquantes pour les ligne et on stocke dans une nouvelle colonne
    print("Add NB_NAN_0 Column", end="")
    df['NB_NAN_0'] = df.isna().sum(axis=1)
    # trie des lignes en fonction du nombre de valeurs manquantes
    df = df.sort_values('NB_NAN_0')
    print(df.shape, "---------- DONE")

    # Suppression des données qui ont le même code
    print("Remove duplicated 'code'", end="")
    df = df.drop_duplicates('code', keep='first')
    nb_na_after = df.isna().sum().sum()
    print(":",df.shape,"NA {:_}".format(nb_na_before), "> {:_}".format(nb_na_after), "({:_})".format(nb_na_after - nb_na_before) ,"---------- DONE")

    # Suppression des lignes qui n'ont aucun nutriment ni de note nutriscore
    print("Remove lines nutrigrade == NAN and NUTRI <",NB_NUTRI_MIN,"/", end="")
    col_nutri = get_nutriments_columns_names(df, verbose)
    df['NB_NAN_NUTRI'] = df[col_nutri].isna().sum(axis=1)
    # trie des lignes en fonction du nombre de valeurs manquantes
    df = df.sort_values('NB_NAN_NUTRI', ascending=False)
    df.drop(df[((df['NB_NAN_NUTRI']>NB_NUTRI_MIN) & (df['nutriscore_grade'].isna()))].index, axis=0, inplace=True)
    nb_na_after = df.isna().sum().sum()
    print(len(col_nutri), col_nutri,"NA {:_}".format(nb_na_before), "> {:_}".format(nb_na_after), "({:_})".format(nb_na_after - nb_na_before) ,"---------- DONE")
    
    # Suppression des doublons sur les autres colonnes :
    print("duplicated on other columns ",
              df.duplicated(subset=['brands_tags', 'product_name', 'countries_tags', 'categories_en', 'ingredients_text', 'pnns_groups_1', 'pnns_groups_2', 'main_category_en']).value_counts(), end="")
    df = df.drop_duplicates(subset=['brands_tags', 'product_name', 'countries_tags', 'categories_en', 'ingredients_text', 'pnns_groups_1', 'pnns_groups_2', 'main_category_en'], keep='first')
    nb_na_after = df.isna().sum().sum()
    print(":",df.shape,"NA {:_}".format(nb_na_before), "> {:_}".format(nb_na_after), "({:_})".format(nb_na_after - nb_na_before) ,"---------- DONE")

    # Pas d'intérêt au dédoublonnage du duo 'brands_tags', 'product_name'
    # par contre suppression des lignes qui n'ont pas de nom de produit
    print("Remove na 'product_name'", end="")
    df = df.dropna(subset=['product_name'])
    nb_na_after = df.isna().sum().sum()
    print(":",df.shape,"NA {:_}".format(nb_na_before), "> {:_}".format(nb_na_after), "({:_})".format(nb_na_after - nb_na_before) ,"---------- DONE")
    # Partie ajoutée après les premières analyses
    print("Clean pmms group")
    df = clean_pms_group_na_level1(df, verbose, inplace)
    if verbose:
        print(df.head())
        print(df["pnns_groups"])
    print("Clean pmms group",df.shape, "---------- DONE")
    
    print("Complete energy datas", end="")
    df = complete_kcal_from_kj_values(df, verbose, inplace)
    df = complete_kj_from_kcal_values(df, verbose, inplace)
    if verbose:
        print(df.head())
        print(df[["energy-kcal_100g", 'energy-kj_100g']])
    nb_na_after = df.isna().sum().sum()
    print(":",df.shape,"NA {:_}".format(nb_na_before), "> {:_}".format(nb_na_after), "({:_})".format(nb_na_after - nb_na_before) ,"---------- DONE")

    if remove_added_col:
        # on supprime la colonne qui n'est plus utile
        df = df.drop('NB_NAN_0', axis=1)
        df = df.drop('NB_NAN_NUTRI', axis=1)
    else:
        df['NB_NAN_LAST'] = df.isna().sum(axis=1)
    nb_na_after = df.isna().sum().sum()
    t1 = (time() - t0) / 60
    print("clean_df_na: {:_}".format(nb_na_before), "=> {:_}".format(nb_na_after), "({:_})".format(nb_na_after - nb_na_before),
          "in {0:.3f} minutes................................................... END".format(t1))
    return df


def typing_data(df, verbose=False, inplace=True):
    """Applique le typage des données de la DataFrame

    Args:
        df (DataFrame): Données à nettoyer
        verbose (bool, optional): Mode debug. Defaults to False.
        inplace (bool, optional): Pour mettre à jour la dataframe reçue directement. Defaults to True.

    Returns:
        [DataFrame]: Les données typées
    """
    t0 = time()
    # ----- Traitement des types de données -----#
    if not inplace:
        df = df.copy()
    nb_update = 0
    # convertir les données dans les types adaptés
    for column in df.columns:
        if 'nova_group' in column or 'nutri_group' in column:
            df[column].fillna(value=0, inplace=True)
            df[column] = df[column].astype(int)
            nb_update += 1 
        elif "_grade" in column or 'pnns_groups' in column :
            try:
                if "nutriscore_grade" in column:
                    df[column] = df[column].str.upper()
                    if verbose:
                        print(df[column].head(10))
                df[column] = df[column].astype('category')
                nb_update += 1 
                if verbose:
                    print("SUCCESS =>", column, "as category")
                
            except:
                print("typing_data FAIL =>", column, "as category")
        elif "_datetime" in column:
            try:
                df[column] = pd.to_datetime(df[column])
                nb_update += 1
                if verbose:
                    print("SUCCESS =>", column, "as datetime") 
            except:
                print("typing_data FAIL =>", column, "as datetime")
        elif "_name" in column or '_tags' in column or "categor" in column or "_text" in column or "countries" in column or "creator" in column or "brands" in column or "code" in column:
            if verbose:
                print("typing_data PASS =>", column)
        else:
            try:
                # il faut convertir la colonne en numérique
                df[column] = pd.to_numeric(df[column])  
                nb_update += 1    
                if verbose:
                    print("SUCCESS =>", column, "as numeric")      
            except:
                print("typing_data FAIL =>", column, "as numeric")
    if verbose:
        df.info()
    t1 = time() - t0
    print(
        "typing_data",nb_update,"upated {0:.3f} secondes................................................... END".format(
            t1))
    return df


def category_nutriscore(score):
    """Retourne le code nutriscore en fonction du score

    Args:
        score (int): nutriscore

    Returns:
        [String]: Le code nutriscore
    """
    if -15 <= score < -1:
        return "A"
    elif -1 <= score < 4:
        return 'B'
    elif 4 <= score < 12:
        return 'C'
    elif 12 <= score < 17:
        return 'D'
    elif 17 <= score <= 40:
        return 'E'
    else:
        return np.nan


def group_nutriscore(score):
    """Retourne le groupe nutriscore en fonction du score

    Args:
        score (String): Le code nutriscore

    Returns:
        [Int]: Le groupe nutriscore
    """
    if isinstance(score, str) and score.lower() in 'abcde':
        score = score.lower()
        if score == "a":
            return 1
        elif score == "b":
            return 2
        elif score == "c":
            return 3
        elif score == "d":
            return 4
        elif score == "e":
            return 5    
    return 0


def prepare_nutri_data(df, verbose=False, inplace=True):
    """Affectation des catéogies de score suivant la note nutriscode

    Args:
        df (DataFrame): [description]
        verbose (bool, optional): Mode debug. Defaults to False.
        inplace (bool, optional): Pour mettre à jour la dataframe reçue directement. Defaults to True.

    Returns:
        DataFrame: DataFrame mis à jour
    """
    t0 = time()
    if not inplace:
        df = df.copy()
    nb_na_before = df['nutriscore_grade'].isna().sum()
    # Ajout de la catégorie de score
    df.loc[df['nutriscore_grade'].isna(),'nutriscore_grade'] = df["nutrition-score-fr_100g"].map(category_nutriscore)
    # Passage en majuscule des notations
    df['nutriscore_grade'] = df['nutriscore_grade'].str.upper()
    # On affecte un entier correspondant à un lettre du code nutriscore
    df['nutri_group'] = df['nutriscore_grade'].map(group_nutriscore)

    if verbose:
        print(df.head(10))
    nb_na_after = df['nutriscore_grade'].isna().sum()
    t1 = time() - t0
    print("prepare_nutri_data : NA {:_}".format(nb_na_before), "> {:_}".format(nb_na_after), "({:_})".format(nb_na_after - nb_na_before) ,"in {0:.2f} secondes...................................... END".format(t1))
    return df


def get_outliers_datas(df, colname):
    """[summary]

    Args:
        df ([type]): [description]
        colname ([type]): [description]

    Returns:
        (float, float, float, float): q_low, q_hi,iqr, q_min, q_max
    """
    # .quantile(0.25) pour Q1
    q_low = df[colname].quantile(0.25)
    #  .quantité(0.75) pour Q3
    q_hi  = df[colname].quantile(0.75)
    # IQR = Q3 - Q1
    iqr = q_hi - q_low
    # Max = Q3 + (1.5 * IQR)
    q_max = q_hi + (1.5 * iqr)
    # Min = Q1 - (1.5 * IQR)
    q_min = q_low - (1.5 * iqr)
    return q_low, q_hi,iqr, q_min, q_max


def remove_outliers(df, columns=None, remove=False, verbose=False):
    """Cette fonction permet de traiter les outliers pour les toutes la liste colonnes reçue ou pour toutes les colonnes

    Args:
        df (DataFrame): Données à nettoyer
        columns ([String], optional): Liste des colonnes à traiter, si valeur par défaut, toutes les colonnes seront traitées. Defaults to None.
        verbose (bool, optional): Mode debug. Defaults to False.

    Returns:
        [DataFrame]: nouveau dataframe mis à jour
    """
    df = df.copy()
    # Si aucune colonne n'est précisée, on traite toute les colonnes du DF
    if columns is None:
        columns = df.column

    for column in columns:
        q_low, q_hi, iqr, q_min, q_max = get_outliers_datas(df, column)
        df = remove_column_outliers(df, column, q_low, q_hi, iqr, q_min, q_max, remove, verbose)
    return df


def remove_column_outliers(df, column_name, q_low, q_hi,iqr, q_min, q_max, remove=False, verbose=False):
    """Cette fonction permet de traiter les outliers pour les toutes la liste colonnes reçue ou pour toutes les colonnes

    Args:
        df (DataFrame): Données à nettoyer
        columns ([String], optional): Liste des colonnes à traiter, si valeur par défaut, toutes les colonnes seront traitées. Defaults to None.
        verbose (bool, optional): Mode debug. Defaults to False.

    Returns:
        [DataFrame]: nouveau dataframe mis à jour
    """
    df = df.copy()
    # Si aucune colonne n'est précisée, on traite toute les colonnes du DF
    if column_name is not None:
        try:
            if df[column_name].dtypes == 'float64' or df[column_name].dtypes == 'int' or isinstance(df[column_name].dtypes, int):
                
                #median = df[column].median()
                # On remplace par NaN, car NaN seront ensuite traité
                if remove:
                    df = df[(df[column_name] <= q_max) & (df[column_name] >= q_min)]
                    if verbose:
                        print("remove_outliers:", column_name, "<",q_min,"and >", q_max, " to DEL---------------> END")
                else:
                    df.loc[~(df[column_name] <= q_max) & (df[column_name] >= q_min), column_name] = np.nan
                    if verbose :
                        print("remove_outliers:", column_name, "<",q_min,"and >", q_max, " to NAN---------------> END")
        except:
            print("Exception remove_outliers:", column_name)
    return df


def create_column_unique_file(df, file_path):
    """Fonction pour écrire dans un fichier chaque colonne avec ses valeurs uniques et le nombre de chacune
    L'objectif est de pouvoir analyser le type de données contenu dans les colonnes.
    Les fichiers sont écrits au même emplacement que le fichier de données source.
    Il s'agit principalement de debuggage, non nécessaire au reste du traitement.

    Args:
        df (DataFrame): Données à représenter
    """
    
    for column in df.columns:
        if 'nutriscore_grade' not in column and 'code' not in column and '_datetime' not in column and 'countries_tags' not in column and 'nova_group' not in column:
            df[column].unique()
            df_category = df[column].value_counts()
            now = datetime.now() # current date and time
            date_time = now.strftime("%Y-%m-%d-%H_%M_%S")
            df_cat = pd.DataFrame(df_category)
            df_cat.to_csv(file_path+'nutriscore_'+column + date_time + '.csv', sep='\t', index=True)


# ---------------------------------------------------------------------------------------------
#                               MAIN
# ---------------------------------------------------------------------------------------------
def main():
    verbose = False
    verboseMain = False
    t0 = time()
    skiprows = 0
    nrows = 500000 + skiprows
    nrows = 0

    # ---------------------------------------------------------------------------------------------
    # Chargement des données
    # ---------------------------------------------------------------------------------------------
    print("Chargement des données", end="")

    df = None
    file_path = 'C:\\Users\\User\\WORK\\workspace-simplon-ia\\projets\\equipe_nutriscore\\'
    if nrows > 0:
        print("(", skiprows, "to", nrows,"rows)")
        df = pd.read_csv(file_path+'data_nutriscore.csv', skiprows=skiprows, nrows=nrows, sep="\t", encoding="utf-8",
                        low_memory=False)
    else:
        print("")
        df = pd.read_csv(file_path+'data_nutriscore.csv', sep="\t", encoding="utf-8", low_memory=False)

    t1 = (time() - t0)/60
    print("Chargement des données ", df.shape,
    ".... in {0:.2f} minutes................................................... END".format(t1))

    # Suppression des colonnes qui ont plus de 73% de valeurs NAN
    df = va_pre.remove_na_columns(df, 73, verbose)
    if verboseMain:
        df.shape
        df.columns

    # Remplacement des valeurs inconnues et absurdes
    df = va_pre.replace_unknown_and_absurded_values(df, verbose=verboseMain)
    if verboseMain:
        # Vérifier les colonnes qui manquent plus ou moins de données
        print(df.isna().mean().sort_values(ascending=False))

    # ---------------------------------------------------------------------------------------------
    # NETTOYAGE DES DONNEES
    df = va_pre.clean_df_na(df, verbose)

    # ---------------------------------------------------------------------------------------------
    # COMPLEMENT DES DONNEES
    df = va_pre.typing_data(df, verbose)

    df = remove_outliers(df, verbose=verbose)

    # ----- Traitement des pays -----#
    df_country = va_geo_nutriscore.split_country_columns(df, 'countries_tags', verbose)
    if verboseMain:
        print(df_country.shape)
        print(df_country.head(10))
        print(df_country.tail(10))

    countries_names = df_country["country"]
    countries_names_origin_to_new = va_geo_nutriscore.get_official_country_name(countries_names, verbose=True)
    if verboseMain:
        print(countries_names_origin_to_new)

    final_df_countries = va_geo_nutriscore.create_df_by_country_with_location(countries_names_origin_to_new, df, verbose=verbose)
    if verboseMain:
        print(final_df_countries.head(10))

    now = datetime.now() # current date and time
    date_time = now.strftime("%Y-%m-%d-%H_%M_%S")
    # Création d'un fichier CVS plus léger pour faciliter la phase de d'analyse des données
    final_df_countries.to_csv(file_path+'nutriscore_filtered_countries_' + date_time + '.csv', sep='\t', index=False)
    
    # on supprime la colonne qui n'est plus utile
    df = df.drop('NB_NAN_0', axis=1)
    df = df.drop('NB_NAN_LAST', axis=1)
    df.to_csv(file_path+'nutriscore_cleans_datas_' + date_time + '.csv', sep='\t', index=False)

    # L'appel à cette fonction est mis en commentaire car non nécessaire à chaque exécution
    # create_column_unique_file(df, file_path)
    # --------------------- Fin du main



def test():
    # RUN MAIN
    firstTime = time()
    main()
    t1 = (time() - firstTime) / 60
    print("TOTAL TIME {0:.3f} minutes.................................... END".format(t1))
