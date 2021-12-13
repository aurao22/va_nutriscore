import numpy as np
import re

# ---------------------------------------------------------------------------------------------
#                               TRAITEMENT DES PAYS
# ---------------------------------------------------------------------------------------------
_correspondance_with_official_name = {'0': np.nan, '1-53': np.nan, '3-4': np.nan,
                                     'Albanie':'Albania',
                                     'Bosnia I Hercegovina Bosnian': 'Bosnia And Herzegovina',
                                     'Estados Unidos': 'United States', "Etats-unis": 'United States',
                                     "etats-unis": 'United States',
                                     'vereinigte-staaten-von-amerika': 'United States', 'La Reunion': 'Reunion',
                                     'la-reunion': 'Reunion',
                                     "Palestinian territories": 'State of Palestine',
                                     'Palestinian Territories': 'State of Palestine', 'algerie': 'Algeria',
                                     'all-over-the-world': np.nan,
                                     'allemagne': 'Germany', 'argentina,es': 'Argentina', 'autriche': 'Austria',
                                     'Austria France Germany': 'Austria',
                                     'be-en-france': 'France', 'belgica': 'Belgium', 'belgie': 'Belgium',
                                     'belgien': 'Belgium',
                                     'belgio': 'Belgium', 'belgique': 'Belgium', 'belgique-france': 'Belgium',
                                     'belgium,fr': 'Belgium', 'bulagria':'Bulgaria','bulgarien':'Bulgaria',
                                     'bulagria':'Bulgaria','blugaria':'Bulgaria',
                                     'birleşik-krallık-en-turkey': 'turkey',
                                     'bosnia-i-hercegovina-bosnian': 'Bosnia And Herzegovina',
                                     'brazil,pt': 'Brazil', 'cameroon,fr': 'Cameroon', 'chile,fr': 'Chile',
                                     'chile9': 'Chile', 'cameroun':'Cameroon', 'κύπρο':'Cyprus',
                                     'cote-d-ivoire': 'Ivory Coast', 'croatia,fr': 'Croatia', 'croacia': 'Croatia', 'česko':'Czech Republic',
                                     'czech-republic':'Czech Republic', 'czech-repblik':'Czech Republic', 'czechy':'Czech Republic','czech-republi':'Czech Republic',
                                     'democratic-democratic-republic-of-the-congo': 'Democratic Republic Of The Congo',
                                     'democratic-republic-of-the-congo': 'Democratic Republic Of The Congo',
                                     'danemark':'Denmark', 'dinamarca':'Denmark',
                                     'deutschland': 'Germany', 'east-germany': 'Germany', 'en-chile': 'Chile',
                                     'en-en-united-kingdom': 'United Kingdom', 'espa�a': 'Spain',
                                     'estados unidos': 'United States', 'estados-unidos': 'United States',
                                     'etats-unis': 'United States','Vereinigte Staaten Von Amerika': 'United States',
                                     'Europa': 'European Union',
                                     'europe': 'European Union', 'france,de': 'France', 'france,es': 'France',
                                     'france,fr': 'France', 'france-en-australia': 'France', 'france-en-be': 'France',
                                     'france-australia': 'France', 'france-germany': 'France',
                                     'france-en-germany': 'France', 'france-en-nl': 'France', 'france-espana': 'France',
                                     'france-spain': 'France', 'france-suisse': 'France', 'dom-tom': 'France',
                                     'france-switzerland-germany': 'France','franca':'France',
                                     'france-united-kingdom': 'France', 'france-united-states': 'France',
                                     'francia': 'France', 'francia-espana': 'France', 'francia-spain': 'France',
                                     'francja': 'France', 'frankreich': 'France',
                                     'frankreich-deutschland': 'France', 'guatemaltecos': 'Guatemala',
                                     'frankrijk': 'France', 'franța': 'France', 'germany,de': 'Germany',
                                     'germany,fr': 'Germany', 'alemania': 'Germany', 'germania':'Germany', 'Niemcy': 'Germany', 'guadalupe':'Guadeloupe',
                                     'germany,it': 'Germany', 'niemcy': 'Germany', 'guinee':'Guinea', 
                                     'hungria': 'Hungary', 'hungaria': 'Hungary',
                                     'kosovo':'Kosovo', 'korea':"Democratic People's Republic of Korea",
                                     'inda': 'India', 'indian-subcontinent': 'India',
                                     'irland-en-de': 'Ireland','irlanda': 'Ireland', "irland": 'Ireland', 'ישראל':'Israel',
                                     'italia': 'Italy', 'italien': 'Italy', 'italy,fr': 'Italy', 'italy,it': 'Italy', 'andria': 'Italy',
                                     'latinoamerica':'Latin America', 'korea-한국어':'Korea',
                                     'luxemburgo':'Luxembourg', 'iraqi-kurdistan':'Kurdistan irakien',
                                     'maroc': 'Morocco', 'marruecos': 'Morocco','marokko': 'Morocco',
                                     'maroc-espania': 'Morocco', 'المغرب': 'Morocco', 'mexico,es': 'Mexico', 'mexique': 'Mexico', 'mexixco': 'Mexico', 'tijuana-baja-california': 'Mexico',
                                     'morocco,fr': 'Morocco', 'marruecos': 'Morocco', 'malay':'Malaysia',
                                     'martinica':'Martinique', 'mongolia':'Mongolia',
                                     'nan': np.nan, 'netherlands,nl': 'Netherlands', 'niederlande': 'Netherlands','Paises Bajos': 'Netherlands',
                                     'nederland': 'Netherlands',
                                     'nouvelle-caledonie': 'New Caledonia', 'new-zealand-english':'New Zealand',
                                     'oslo':'Norway',
                                     'null-australia': 'Australia', 'palestinian-territories': 'State of Palestine','فلسطين':"State of Palestine",
                                     'paris-france': 'France', 'ranska': 'France', 'francia-italia-spagna-en-spain': 'France', 
                                     'worldwide':"Wordl", 
                                     'pays-bas': 'Netherlands', 'poland,fr': 'Poland', 'polonia': 'Poland', 'pologne': 'Poland',
                                     'polska': 'Poland', 'polen': 'Poland','poland-polski': 'Poland', 'poland-romania': 'Poland', 'portugal,de': 'Portugal',
                                     'portugal,es': 'Portugal', 'portugal,fr': 'Portugal', 
                                     'product-of-india': 'India', 'polinesia-francesa':'French Polynesia', 'polynesie-francaise':'French Polynesia',
                                     'republic-of-macedonia': 'North Macedonia', 'republic-of-the-congo': 'Congo',
                                     'republica-dominicana-espanol':'Dominican Republic', 'soviet-union':'Russian Federation','russia-русский':'Russian Federation', 'rusia':'Russian Federation',
                                     'royaume-uni': 'United Kingdom', "Royaume-uni": 'United Kingdom', "En-en-united-kingdom": 'United Kingdom',
                                     'reino-unido': 'United Kingdom', 'england': 'United Kingdom', 
                                     'inglaterra': 'United Kingdom', 'England': 'United Kingdom',
                                     'romanina':'Romania', 'romaniaă':'Romania', 
                                     'wales': 'United Kingdom', 'serbie':'Serbia',
                                     'slowakai':'Slovakia', 'eslovenia':'Slovenia', 'espagne': 'Spain',
                                     'spagna en spain': 'Spain','spagna': 'Spain', 'spain,ca': 'Spain', 'spain,es': 'Spain', 'españa': 'Spain',
                                     'spain,fr': 'Spain', 'espanha': 'Spain', 'spanien': 'Spain', 'Singapour':'Singapore', 'Svizzera': 'Switzerland',
                                     'suisse': 'Switzerland', 'szwajcaria': 'Switzerland', 'svizzera': 'Switzerland',
                                     'schweiz': 'Switzerland', 'suiza': 'Switzerland', 'svizzera': 'Switzerland',  'suomi': 'Finland',
                                     'sverige': 'Sweden', 'schweden': 'Sweden', 'suecia': 'Sweden', 'swaziland': 'Sweden','swiss': 'Switzerland',
                                     'slowenien':'Slovenia', 'slowakai':'Slovakia',
                                     'the-bahamas': 'Bahamas', 'thailande':'Thailand',
                                     'trinidad-tobagot-english': 'Trinidad And Tobago',
                                     'tunisia,fr': 'Tunisia', 'tunisie': 'Tunisia', 'تونس': 'Tunisia', 'turkiye': 'Turkey',
                                     'union-europeenne-france': 'France', 'europa': 'France',
                                     'yugoslavia':'Yugoslavia', 'vatican-city':'Holy See',
                                     'u-s-minor-outlying-islands':'US Minor Outlying Islands',
                                     'unknown': np.nan, 'desconocido': np.nan, 'Desconocido': np.nan, 'mundo': np.nan, 'world': np.nan, 'worldwide': np.nan, 'world-s-coconut-trading-s-l': np.nan, 'الأردن': 'Jordan',
                                     'لأردن': 'Jordan', '10-07-21': np.nan, 'كل-الدول': np.nan}


str_to_remove_from_name = {'-bahasa-indonesia', '-bahasa-melayu', '-dansk', '-deutsch', '-eesti', '-english',
                           '-espanol', '-francais', '-france', '-netherlands', '-spain','-espana', 
                           '-hrvatski', '-islenska', '-italiano', '-latviešu', '-lietuvių', '-magyar', '-nederlands',
                           '-norsk', '-suisse', '-en-germany', '-united-kingdom', '-united-states'
                           '-polski', '-portugues', '-pyсский', '-roman', '-romană', '-slovene', '-slovenčina',
                           '-srpski', '-suomi','-deutschland',
                           '-svenska', '-tiếng-việt', '-turkce', '-yкраї́Нська', '-Čeština', '-eλληνικά', '-Български',
                           '-mакедонски-jазик', '-mонгол Хэл', '-pусский', '-עברית', '-ไทย', '-ქართული', '-ភាសាខ្មែរ',
                           '-中文', '-日本語', '-粵語', '-한국어', '-\u200f', "\u200f",
                           ' Bahasa Indonesia', ' Bahasa Melayu', ' Dansk', ' Deutsch', ' Eesti', ' English',
                           ' Espanol', ' Francais', 
                           ' Hrvatski', ' Islenska', ' Italiano', ' Latviešu', ' Lietuvių', ' Magyar', ' Nederlands',
                           ' Norsk',
                           ' Polski', ' Portugues', ' Pyсский', ' Roman', ' Romană', ' Slovene', ' Slovenčina',
                           ' Srpski', ' Suomi',
                           ' Svenska', ' Tiếng Việt', ' Turkce', ' Yкраї́Нська', ' Čeština', ' Ελληνικά', ' Български',
                           ' Македонски Јазик', ' Монгол Хэл', ' Русский', ' עברית', ' ไทย', ' ქართული', ' ភាសាខ្មែរ',
                           ' 中文', ' 日本語', ' 粵語', ' 한국어', '-\u200f', "\u200f"}


str_to_remove_second_step_from_name = {'en:', 'fr:', 'es:', 'de:', 'nl:', 'ar:', 'pt:', 'ru:', 'ro:', 'it:', 'sk:',"-en", "en-", "-be", "-nl"}


def data_country_names_their_official_name():
    """[summary]

    Returns:
        [dict(String, String)]: [description]
    """
    result = {}

    for k,v in _correspondance_with_official_name.items():
        k_clean = k.lower().strip()
        result[k_clean] = v
        k3 = clean_name(k_clean, False, False)
        result[k3] = v
        k2 = k3.strip().replace("-", " ")
        result[k2.strip()] = v
    return result


def official_country_name_their_data_variations(verbose=False):
    """[summary]

    Args:
        verbose (bool, optional): [description]. Defaults to False.

    Returns:
        [type]: [description]
    """
    origin_to_official_name = data_country_names_their_official_name()
    official_name_to_origine = {}
    for origin, officiel in origin_to_official_name.items():
        if officiel is not None and officiel is not np.nan and isinstance(officiel, str):
            if officiel not in official_name_to_origine:
                official_name_to_origine[officiel] = set()
            official_name_to_origine[officiel].add(origin)
    return official_name_to_origine


def clean_name(name_to_clean, replace_tiret=True, format=True):
    name = name_to_clean
    if isinstance(name, str):
        if format:
            name = name.lower()
        # Suppression des parties non souhaitées
        for to_remove in str_to_remove_from_name:
            name = name.replace(to_remove, "")
        for to_remove in str_to_remove_second_step_from_name:
            name = name.replace(to_remove, "")
        name = re.sub('^[a-z]{2}(:|-)',  '', name)
        name = re.sub('(-|,)[a-z]{2}$',  '', name)
        if format:
            name = name.title()
            name = name.replace(" Of ", " of ")
            name = name.replace(" The ", " the ")
            name = name.replace(" And ", " and ")
        
        if replace_tiret:
            name = name.replace("-", " ")
        name = name.strip()
    return name


def revert_dic(countries_names_origin_to_new):
    revert_dic = {}
    for k, v in countries_names_origin_to_new.items():
        if v is not np.nan :
            list = revert_dic.get(v, [])
            if list is None:
                list = []
            list.append(k)
            revert_dic[v] = list
    keys = sorted(revert_dic.keys())
    for k in keys:
        print("'"+k+"':"+str(revert_dic[k])+",", end="")
    return revert_dic


test_list2 = ['0', '1-53', '3-4', 'afghanistan', 'afrique', 'aland-islands', 'albania', 'aldi',
                  'alemania', 'algeria',
                  'algeria-austria-belgium-canada-france-germany-italy-luxembourg-mexico-morocco-netherlands-portugal-senegal-spain-switzerland-tunisia-united-kingdom-united-states',
                  'algerie', 'all-over-the-world', 'allemagne', 'amapa-pracuuba', 'american-samoa', 'andorra', 'andria',
                  'angola', 'anguilla', 'antigua-and-barbuda', 'argentina', 'argentina,es', 'armenia', 'aruba',
                  'australia',
                  'austria', 'austria-france-germany', 'azerbaijan', 'bahrain', 'bangladesh', 'barbados',
                  'be-en-france', 'belarus',
                  'belgica', 'belgie', 'belgien', 'belgio', 'belgique', 'belgique-france', 'belgium', 'belgium,fr',
                  'belize',
                  'benin', 'bermuda', 'bhutan', 'birleşik-krallık-en-turkey', 'bolivia', 'bosnia-and-herzegovina',
                  'botswana',
                  'brazil', 'brazil,pt', 'british-indian-ocean-territory', 'british-virgin-islands', 'brunei',
                  'bulgaria',
                  'burkina-faso', 'burundi', 'cambodia', 'cameroon', 'cameroon,fr', 'canada', 'cape-verde',
                  'caribbean-netherlands',
                  'cayman-islands', 'cemac', 'central-african-republic', 'chad', 'chile', 'chile,fr', 'chile9', 'china',
                  'christmas-island',
                  'cocos-keeling-islands', 'colombia', 'comoros', 'cook-islands', 'costa-rica', 'cote-d-ivoire',
                  'cramopolis-de-minas', 'croatia', 'croatia,fr', 'cuba', 'curacao', 'cyprus', 'czech-republic',
                  'czechy',
                  'democratic-republic-of-the-congo', 'denmark', 'desconocido', 'deutschland', 'djibouti', 'dom-tom',
                  'dominica', 'dominican-republic', 'east-germany', 'ecuador', 'egypt', 'el-salvador',
                  'em-todos-os-paises',
                  'en', 'en-chile', 'en-en-united-kingdom', 'england', 'equatorial-guinea', 'eritrea', 'espa�a',
                  'estonia',
                  'ethiopia', 'europa', 'european-union', 'faroe-islands', 'fes', 'fiji', 'finland', 'france',
                  'france,de',
                  'france,es', 'france,fr', 'france-en-australia', 'france-en-be', 'france-en-germany', 'france-en-nl',
                  'france-espana',
                  'france-spain', 'france-suisse', 'france-switzerland-germany', 'france-united-kingdom',
                  'france-united-states', 'francia',
                  'francia-espana', 'francia-spain', 'francja', 'frankreich', 'frankreich-deutschland', 'frankrijk',
                  'franța', 'french-guiana', 'french-polynesia', 'gabon', 'gambia', 'georgia', 'germany', 'germany,de',
                  'germany,fr', 'germany,it', 'ghana', 'gibraltar', 'greece', 'greenland', 'grenada', 'guadeloupe',
                  'guam', 'guatemala',
                  'guatemaltecos', 'guernsey', 'guinea', 'guyana', 'haiti', 'honduras', 'hong-kong', 'hungary',
                  'iacobeni',
                  'iceland', 'ikram', 'inda', 'india', 'indian-subcontinent', 'indonesia', 'iran', 'iraq', 'ireland',
                  'irland-en-de',
                  'isle-of-man', 'israel', 'italia', 'italien', 'italy', 'italy,fr', 'italy,it', 'jamaica', 'japan',
                  'jersey',
                  'jordan', 'kazakhstan', 'keine-ahnung', 'kenya', 'knm', 'kolkata', 'korea', 'kosovo', 'kuwait',
                  'kyrgyzstan', 'la-reunion', 'laos', 'latinoamerica', 'latvia', 'lebanon', 'lesotho', 'liberia',
                  'libya',
                  'liechtenstein', 'lithuania', 'luxembourg', 'macau', 'madagascar', 'malawi', 'malay', 'malaysia',
                  'maldives',
                  'mali', 'malta', 'maroc', 'maroc-espania', 'martinique', 'mauritania', 'mauritius', 'mayotte',
                  'mazedonien',
                  'mexico', 'mexico,es', 'mexixco', 'moldova', 'monaco', 'mongolia', 'montenegro', 'montserrat',
                  'morocco',
                  'morocco,fr', 'mozambique', 'mundo', 'myanmar', 'namibia', 'nan', 'nederland', 'nepal', 'netherlands',
                  'netherlands,nl', 'new-caledonia', 'new-zealand', 'nicaragua', 'niger', 'nigeria', 'north-korea',
                  'north-macedonia',
                  'northern-mariana-islands', 'norway', 'nouvelle-caledonie', 'null-australia', 'oman', 'paises-bajos',
                  'pakistan', 'palau', 'palestinian-territories', 'panama', 'papua-new-guinea', 'paraguay',
                  'paris-france',
                  'pays-bas', 'peru', 'philippines', 'poland', 'poland,fr', 'pologne', 'polska', 'portugal',
                  'portugal,de',
                  'portugal,es', 'portugal,fr', 'product-of-india', 'puerto-rico', 'qatar', 'rango',
                  'republic-of-macedonia',
                  'republic-of-the-congo', 'reunion', 'rggr', 'rob', 'romania', 'royaume-uni', 'russia', 'rwanda',
                  'saint-kitts-and-nevis',
                  'saint-lucia', 'saint-martin', 'saint-pierre-and-miquelon', 'saint-vincent-and-the-grenadines',
                  'san-marino',
                  'sao-tome-and-principe', 'saudi-arabia', 'senegal', 'serbia', 'serravalle-scrivia', 'seychelles',
                  'sierra-leone', 'singapore', 'sint-maarten', 'slovakia', 'slovenia', 'somalia', 'south-africa',
                  'south-asia',
                  'south-korea', 'south-sudan', 'spagna en spain', 'spain', 'spain,ca', 'spain,es', 'spain,fr',
                  'spanien', 'sri-lanka', 'state-of-palestine', 'sudan', 'suisse', 'suiza', 'suomi', 'suriname',
                  'sverige',
                  'swaziland', 'sweden', 'switzerland', 'syria', 'taiwan', 'tajikistan', 'tanzania', 'thailand',
                  'the-bahamas',
                  'tijuana-baja-california', 'togo', 'tonga', 'trinidad-and-tobago', 'tunisia', 'tunisia,fr', 'tunisie',
                  'turkey',
                  'turkiye', 'u-s-minor-outlying-islands', 'ue', 'uganda', 'ukraine', 'union-europeenne-france',
                  'united-arab-emirates',
                  'united-kingdom', 'united-states', 'unknown', 'uruguay', 'uzbekistan', 'vanuatu', 'vatican-city',
                  'venezuela',
                  'vietnam', 'virgin-islands-of-the-united-states', 'wallis-and-futuna', 'world',
                  'world-s-coconut-trading-s-l,pt',
                  'worldwide', 'xk', 'yemen', 'yugoslavia', 'zagreb-hrvatska', 'zambia', 'zimbabwe', 'česko', 'ελλάδα',
                  'снг', 'الأردن', 'المغرب', 'ایران', 'فلسطين-\u200f', 'كل-الدول']


def _test():
    for origin in test_list2:
        print(origin, "=>", clean_name(origin, False, False), "=>", clean_name(origin, True, True))




