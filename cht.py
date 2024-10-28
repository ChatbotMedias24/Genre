import streamlit as st
import openai
import streamlit as st
from dotenv import load_dotenv
import pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
import os
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
from streamlit_chat import message  # Importez la fonction message
import toml
import docx2txt
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
import docx2txt
from dotenv import load_dotenv
if 'previous_question' not in st.session_state:
    st.session_state.previous_question = []

# Chargement de l'API Key depuis les variables d'environnement
load_dotenv(st.secrets["OPENAI_API_KEY"])

# Configuration de l'historique de la conversation
if 'previous_questions' not in st.session_state:
    st.session_state.previous_questions = []

st.markdown(
    """
    <style>

        .user-message {
            text-align: left;
            background-color: #E8F0FF;
            padding: 8px;
            border-radius: 15px 15px 15px 0;
            margin: 4px 0;
            margin-left: 10px;
            margin-right: -40px;
            color:black;
        }

        .assistant-message {
            text-align: left;
            background-color: #F0F0F0;
            padding: 8px;
            border-radius: 15px 15px 15px 0;
            margin: 4px 0;
            margin-left: -10px;
            margin-right: 10px;
            color:black;
        }

        .message-container {
            display: flex;
            align-items: center;
        }

        .message-avatar {
            font-size: 25px;
            margin-right: 20px;
            flex-shrink: 0; /* Empêcher l'avatar de rétrécir */
            display: inline-block;
            vertical-align: middle;
        }

        .message-content {
            flex-grow: 1; /* Permettre au message de prendre tout l'espace disponible */
            display: inline-block; /* Ajout de cette propriété */
}
        .message-container.user {
            justify-content: flex-end; /* Aligner à gauche pour l'utilisateur */
        }

        .message-container.assistant {
            justify-content: flex-start; /* Aligner à droite pour l'assistant */
        }
        input[type="text"] {
            background-color: #E0E0E0;
        }

        /* Style for placeholder text with bold font */
        input::placeholder {
            color: #555555; /* Gris foncé */
            font-weight: bold; /* Mettre en gras */
        }

        /* Ajouter de l'espace en blanc sous le champ de saisie */
        .input-space {
            height: 20px;
            background-color: white;
        }
    
    </style>
    """,
    unsafe_allow_html=True
)
# Sidebar contents
textcontainer = st.container()
with textcontainer:
    logo_path = "medi.png"
    logoo_path = "NOTEPRESENTATION.png"
    st.sidebar.image(logo_path,width=150)
   
    
st.sidebar.subheader("Suggestions:")
questions = [
    "Donnez-moi un résumé du rapport ",
    "Quelles sont les principales réformes mentionnées dans le discours concernant la condition de la femme au Maroc ?",        
    "Comment le discours aborde-t-il la question de l'égalité homme-femme ?",        
    "Quels sont les objectifs que l'État marocain doit chercher à atteindre selon le discours ?",
    "Quelles sont les initiatives spécifiques mises en place pour améliorer l'accès des femmes à la justice au Maroc ?"
]
# Initialisation de l'historique de la conversation dans `st.session_state`
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = StreamlitChatMessageHistory()
def main():
    text=r"""
    
INTRODUCTION GENERALE
L'édition 2025 du Rapport sur le Budget axé sur les Résultats tenant compte de l'aspect
Genre (RBG 2025) s'inscrit dans un contexte où le Maroc consolide son engagement à la
faveur de la réduction des inégalités entre les femmes et les hommes et la promotion de
l’autonomisation des femmes, conformément aux Orientations Royales et aux
recommandations du Rapport sur le Nouveau Modèle de Développement.
Les initiatives entreprises par notre pays pour une application réussie de la Budgétisation
Sensible au Genre (BSG), alliant programmation stratégique et budgétaire au service de
l’égalité de genre, témoigne de la détermination du Maroc à rendre effectif le principe de
l’égalité entre les femmes et les hommes et asseoir, de fait, les jalons d’un développement
inclusif profitable à toutes et à tous.
Le parcours accompli par le Maroc en matière d’opérationnalisation de la BSG lui a valu
une reconnaissance à l’international, comme en témoigne les évaluations entreprises par
des institutions internationales de référence. A cet égard, la récente évaluation de la
performance du système de gestion des finances publiques sensible au genre (PEFA
Genre) acte les progrès significatifs du Maroc. Ces progrès se manifestent dans
l’intégration de la dimension genre dans la gestion des finances publiques sur les plans
juridique, programmatique ainsi que dans les mécanismes de suivi et de reporting,
illustrés notamment par l’élaboration à fréquence annuelle du Rapport sur le Budget axé
sur les Résultats tenant compte de l’aspect Genre et des documents de suivi de la
performance des départements ministériels (Projets de Performance ministériels,
Rapports de Performance, Rapports Annuels de Performance)….
Dans la continuité de ce processus, l’année 2024 marque un tournant significatif dans le
perfectionnement des outils développés pour un ancrage systématique de la dimension
genre dans les pratiques de programmation et de budgétisation de l’action publique.
Fruit d’un processus de près de 2 ans de réflexion, de concertation et d’expérimentation
impliquant le Centre d’Excellence pour la BSG (CE-BSG), l’ONU Femmes et plusieurs
départements ministériels, l’année 2024 acte la conception d’une méthodologie de
marquage des allocations budgétaires dédiées à l’égalité entre les femmes et les
hommes, alignée sur les spécificités de la gestion budgétaire nationale. Cette
méthodologie constitue, en effet, un outil rigoureux visant à renforcer la cohérence entre
les engagements pris en matière de réduction des inégalités entre les femmes et hommes
et les ressources mobilisées pour y parvenir. En favorisant la transparence et la
redevabilité dans la gestion des finances publiques, un tel dispositif constitue une
avancée majeure, positionnant le Maroc à l'avant-garde des pratiques internationales en
matière d’opérationnalisation et d’appropriation de la BSG.
Dans le sillage de cette dynamique, la première partie de l’édition du RGB 2025 décline
la méthodologie du marquage des budgets alloués à la promotion de l’égalité de genre.
En mettant en exergue le cadre référentiel et en s’inspirant des principales expériences
internationales en la matière, cette section présente les lignes directrices de


                                                                                         1
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


l’implémentation du marquage genre des dépenses allouées à l’égalité entre les femmes
et les hommes au Maroc. En outre, le Rapport analyse, dans ses deuxième, troisième et
quatrième parties les efforts consentis par les départements ministériels en faveur d’une
programmation et d’une budgétisation intégrant la dimension genre.




     2
             RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


    I.        MARQUAGE GENRE DES BUDGETS : UN NOUVEAU
              PALIER   D’ACTION   AU    SERVICE   DE   LA
              CONSOLIDATION    DE  L’APPLICATION   DE  LA
              BUDGETISATION SENSIBLE AU GENRE AU MAROC
Dans le but de garantir une application efficace et une appropriation réussie de la
Budgétisation Sensible au Genre (BSG) par les départements ministériels et de contribuer
ainsi à l’effectivité de l’égalité de genre, le Ministère de l’Economie et des Finances (MEF), à
travers le Centre d’Excellence pour la BSG (CE-BSG), en partenariat avec ONU Femmes, s’est
lancé, depuis 2022, dans un projet ambitieux visant à mettre en place un système de
marquage genre des budgets. Ce projet constitue une étape clés dans le processus
d’opérationnalisation de la BSG entamé depuis 2002.
L’initiation de ce projet est une réponse aux engagements pris par notre pays dans le cadre
de l’Agenda 2030 pour le Développement Durable, particulièrement en faveur de la
concrétisation de l’Objectif pour le Développement Durable (ODD5) « parvenir à l’égalité des
sexes et autonomiser toutes les femmes et les filles » et sa cible 5.c.1 qui suit « la proportion
des pays dotés de systèmes permettant un suivi transparent des ressources allouées à
l’égalité entre les sexes et à l’autonomisation des femmes ». En effet, cette cible vise à établir
le lien entre les engagements pris en matière de réduction des inégalités de genre et les
allocations budgétaires qui leur sont dédiées, ce qui est désormais considéré à l’échelle
internationale comme étant un domaine clé pour améliorer significativement la mise en
   uvre de la BSG1.
Dans le même sillage, la conception d’un système de marquage des dépenses allouées à la
réduction des inégalités de genre au Maroc s’aligne parfaitement sur l’initiative prise par
notre pays d’intégrer dans le troisième exercice du programme d’évaluation de performance
des systèmes de gestion des finances publiques « PEFA2 » pour l’année 20233, le cadre
supplémentaire « PEFA Genre ». Ce dernier est fondé sur une évaluation du degré de prise
en compte de l’égalité de genre dans la gestion des finances publiques, moyennant 9
indicateurs dont l’indicateur 6 et sa composante 6.1 relative au suivi des dépenses
budgétaires en faveur de l’égalité femmes-hommes.
Tenant compte de ces engagements et au regard du niveau de maturité de l’expérience
marocaine en matière d’application de la BSG, une démarche analytique visant la conception
d’un système marquage sous le prisme genre des budgets fondé sur une notation des
programmes et des projets des départements ministériels a été développée. Cette approche
qui repose sur une démarche progressive et participative impliquant le MEF et plusieurs
départements ministériels, s’inspire du système de marquage genre du Cadre de l’Aide au
Développement (CAD) conçu par l’OCDE et de plusieurs expériences internationales réussies
en les adaptant aux spécificités de la gestion budgétaire nationale. Il est à noter à cet égard
que deux départements pilotes ont été désignés pour tester cette approche. Il s’agit des
départements de la Jeunesse et de l’Education Nationale et du Préscolaire qui ont bénéficié,
durant la période 2022-2024, de formations et d’ateliers d’accompagnement permettant de
tester l’ensemble des étapes de la méthodologie de marquage retenue et d’identifier, par la
suite, les ajustements à y apporter, dans la perspective d’élargir son application au niveau
d’autres départements ministériels.

1
  « Impliquer les parlements dans la budgétisation sensible au genre », ONU Femmes, 2022.
2
  Le cadre PEFA est une méthodologie d'évaluation de la performance de la gestion des finances publiques à l'aide d'indicateurs
quantitatifs de mesure des performances. Il est important de noter que ce cadre d’évaluation est le résultat d’un programme
de partenariat géré par huit partenaires internationaux de développement
3
   Cet exercice d’évaluation a été mené par le MEF en partenariat avec la Banque mondiale, la Banque Africaine de
Développement (BAD), l’Union Européenne (UE) et l’Agence Française de Développement (AFD) et concerne l’ensemble des
départements ministériels, des institutions aux niveaux central et régional, ainsi que les établissements et les entreprises publics.


                                                                                                                                  3
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


Partant de ces éléments, la présente partie de l’édition 2025 du Rapport sur le Budget axé
sur les Résultats tenant compte de l’aspect Genre décline le cadre référentiel plaidant pour
la mise en place d’un dispositif de marquage genre des budgets. Elle présente un tour
d’horizon des expériences internationales les plus abouties en termes d’opérationnalisation
d’un marquage genre des dépenses allouées à la réduction des inégalités entre les femmes
et les hommes ainsi qu’une présentation des grandes lignes de la méthodologie conçue par
le MEF pour le développement du système de marquage genre des budgets adapté aux
mécanismes de gestion budgétaire tels qu’ils sont pratiqués à l’échelle nationale.

   1. CADRE REFERENTIEL ET PORTEES DU MARQUAGE
      GENRE DES BUDGETS
Au regard des engagements pris dans le cadre de divers instruments internationaux, dont
particulièrement l’Agenda 2030 pour le Développement Durable, en matière de
consolidation de l’effectivité de l’égalité entre les femmes et les hommes, les Etats ont de
plus en plus recours à la conception des systèmes de suivi des allocations budgétaires pour
s’assurer de l’adéquation entre les objectifs escomptés et les moyens qui leur sont dédiés.
  Encadré 1 : Programme d’Action de Beijing : Une étape jalon dans le processus de la genèse
    de la BSG et des systèmes de traçabilité des financements alloués à l’égalité de genre à
                                      l’échelle mondiale
 La conférence mondiale sur les femmes, tenue à Beijing en 1995, a joué un rôle clé dans la reconnaissance
 de la pertinence et de l’utilité de la BSG. En effet, l’une des recommandations déclinées dans la déclaration
 finale de cette conférence stipule qu’il est essentiel d’élaborer, de mettre en uvre et de surveiller, à tous
 les niveaux et avec la pleine participation des femmes, des politiques et des programmes, y compris de
 développement, qui devraient être égalitaires, efficaces, efficients et complémentaires et qui sont amenés
 à favoriser le renforcement du pouvoir d’action des femmes et leur promotion. Une autre
 recommandation issue de cette déclaration indique que les Etats qui ont adopté le Programme d’action
 de Beijing s’engagent à le traduire dans les faits, en veillant à ce que le souci d’équité entre les sexes
 imprègne toutes leurs politiques et leurs programmes.
 En termes des dispositions financières préconisées pour la concrétisation des engagements pris dans le
 cadre de ce plan d’action, une des dispositions proposées attribue aux Etats la responsabilité première
 de la réalisation des objectifs stratégiques dudit plan, tout en leur apportant les leviers d’actions pour y
 parvenir. Dès lors, ces Etats sont appelés à :
  Procéder à des examens systématiques de la façon dont les femmes bénéficient des dépenses
   publiques ;
  Ajuster les budgets pour assurer l’égalité d’accès aux dépenses publiques, tant pour améliorer la
   capacité de production que pour répondre aux besoins sociaux, et concrétiser les engagements pris
   en matière d’égalité entre les sexes à d’autres sommets et conférences des Nations Unies ;
  Affecter des ressources suffisantes pour l’opérationnalisation de la prise en compte de l’égalité de
   genre dans la programmation budgétaire …
En outre, la mobilisation, la gestion et la traçabilité des ressources allouées à la concrétisation
des objectifs fixés en termes de réduction des inégalités font, désormais, l’objet d’analyses
fines, dans le cadre du module complémentaire « PEFA Genre » qui relève du programme
d’évaluation de performance des systèmes de gestion des finances publiques « PEFA ».
1.1. L’ODD 5 et le PEFA Genre : Un cadre normatif interpellant les Etats
pour la mise en place de mécanismes aptes à assurer le suivi des
allocations budgétaires dédiées à l’égalité de genre
Cible 5.c.1 de l’ODD 5 : Cadre de suivi de la mise en place d’un système
 de marquage genre des budgets
La cible 5.c relevant de l’ODD5 incite les Etats engagés dans l’Agenda 2030 pour le
Développement Durable, dont le Maroc, à adopter des politiques bien conçues et des
dispositions législatives applicables en faveur de la promotion de l’égalité des sexes et de


     4
              RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


l’autonomisation de toutes les femmes et de toutes les filles à tous les niveaux et renforcer
celles qui existent. Le suivi du degré d’atteinte de cette cible est assuré par la cible 5.c.1 qui
mesure la proportion des pays dotés de systèmes permettant un suivi transparent des
ressources allouées à l’égalité entre les sexes et à l’autonomisation des femmes. Cet
indicateur a pour objectif de consolider l’implication des Etats pour honorer leurs
engagements en matière de réduction des inégalités entre les femmes et les hommes, par le
biais d’une programmation et d’une budgétisation qui prennent en compte la dimension
genre.
De fait, la cible 5.c.1 vise à appuyer les efforts déployés par les Etats pour le développement
des systèmes de suivi budgétaire appropriés en mesure d’assurer la traçabilité des allocations
dédiées à la promotion de l’égalité de genre4. Il est important de signaler, à cet égard, que le
système des Nations Unies a développé une grille dédiée au suivi de ladite cible 5.c.1 (voir
l’encadré ci-dessous).
     Encadré 2 : Grille développée par le Système des Nations Unies pour le suivi de la cible 5.c.1
    La grille développée par le Système des Nations Unies pour assurer le suivi de la cible 5.c.1 est articulée
    autour de trois critères qui portent sur le niveau d’application d’une programmation et d’une
    budgétisation sensibles au genre, l’adoption d’un système de gestion des finances publiques intégrant la
    dimension genre et la diffusion des informations relatives aux allocations dédiées à la promotion de
    l’égalité liée de genre. Il est important de noter que chaque critère est renseigné en fonction des réponses
    apportées aux questions adressées aux Etats. Cette grille est déclinée comme suit :
    Critère 1 : Niveau d’application d’une programmation et d’une budgétisation sensibles au genre
    Question 1.1 : Existe-t-il des politiques et/ou des programmes gouvernementaux conçus pour répondre
                 à des objectifs bien identifiés en matière d’égalité liée au genre, y compris ceux pour lesquels
                 l’égalité liée au genre n’est pas l’objectif principal mais qui intègrent des actions visant à
                 combler les écarts entre les sexes ?
    Question 1.2 : Ces politiques et/ou programmes disposent-ils de ressources adéquates allouées dans le
                 cadre du budget, suffisantes pour atteindre à la fois leurs objectifs généraux et leurs objectifs
                 en matière d’égalité liée au genre ?
    Question 1.3 : Des procédures sont-elles en place pour garantir que ces ressources soient exécutées
                 conformément au budget ?
    Critère 2 : Adoption d’un système de gestion des finances publiques intégrant la dimension genre
    Question 2.1 : Le Ministère des Finances publie-t-il des circulaires d’appel, ou d’autres directives de ce
                  type, qui fournissent des orientations spécifiques sur les allocations budgétaires sensibles au
                  genre ?
    Question 2.2 : Les politiques et programmes clés, proposés pour être intégrés dans le budget, sont-ils
                  soumis à une évaluation ex ante de l’impact sur le genre ?
    Question 2.3 : Des statistiques et des données ventilées par genre sont-elles utilisées dans les politiques
                  et programmes clés de manière à pouvoir informer les décisions politiques liées au budget ?
    Question 2.4 :      Le gouvernement fournit-il, dans le contexte du budget, une déclaration claire des
                  objectifs liés au genre (c’est-à-dire une déclaration budgétaire sur le genre ou une législation
                  budgétaire sensible au genre) ?
    Question 2.5 : Les allocations budgétaires sont-elles soumises à un « étiquetage », y compris par des
                  classificateurs fonctionnels, afin d’identifier leur lien avec les objectifs d’égalité liée au genre
                  ?
    Question 2.6 : Les politiques et programmes clés sont-ils soumis à une évaluation ex post de l’impact
    sur l’égalité de genre ?
    Question 2.7 : Le budget dans son ensemble est-il soumis à un audit indépendant pour évaluer dans
                  quelle mesure il promeut des politiques sensibles au genre ?
    Critère 3 : Diffusion des informations relatives aux allocations dédiées à la promotion de l’égalité liée de
    genre
    Question 3.1 :    Les données sur les allocations pour l’égalité de genre sont-elles publiées ?


4
    « Impliquer les parlements dans la budgétisation sensible au genre », ONU Femmes, 2022.


                                                                                                                    5
    PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


    Question 3.2 : Si ces données sont publiées, sont-elles accessibles sur le site Internet du Ministère des
                Finances (ou du bureau responsable du budget) ?
    Question 3.3 : Si oui, les données sur les allocations dédiées à l’égalité de genre sont-elles publiées en
                temps opportun ?
    Source : « Impliquer les parlements dans la budgétisation sensible au genre », ONU Femmes, 2022.

En rapport avec l’état d’avancement de la réalisation de la cible 5.c.1, il ressort de l’édition
2024 du « Point sur les Objectifs du Développement Durable5 » dont l’analyse a couvert les
données communiquées par 105 pays et régions au titre de la période 2018-2021, que
seulement 26% des pays analysés disposent d’un système perfectionné de suivi des
allocations publiques destinées à la promotion de l’égalité de genres. Près de 59% de ces
pays ont mis en place juste certaines composantes de ce système et 15% n’ont pas encore
conçu de systèmes de suivi des budgets alloués à la réduction des inégalités entre les femmes
et les hommes.
PEFA Genre : la mise en place d’un système de suivi des allocations
 budgétaires allouées à l’égalité de genre comme étant une pratique
 reflétant une bonne gestion des finances publiques sensibles au genre
Le cadre complémentaire du programme d’évaluation de performance des systèmes de
gestion des finances publiques (PEFA) visant l’évaluation de la prise en compte de l’égalité
hommes-femmes dans la gestion des finances publiques (PEFA Genre ou bien le cadre PEFA
sur la Gestion des Finances Publiques Sensible au Genre -GFPSG-6) est une réponse du
Secrétariat du PEFA aux demandes collectives et individuelles d’intervenants impliqués dans
la gestion des finances publiques et dans les réformes de budgétisation sensible au genre 7.
En effet, plusieurs acteurs et actrices de la gestion des finances publiques estiment que ce
programme constitue le cadre idoine pour rassembler les informations relatives aux
pratiques nationales en matière de GFPSG permettant aux pays concernés de mieux cerner
le rôle actuel et en perspective de la gestion des finances publiques au service de la
promotion de l’égalité de genre. Ces informations sont considérées, dès lors, comme étant
un prérequis en mesure d’enrichir les concertation en lien avec les besoins en financement
ad-hoc pour réduire sinon mettre fin aux inégalités de genre, comme acté dans la Déclaration
et le Programme d’action de Beijing, le Programme d’action d’Addis Abeba et l’Agenda 2030
pour le Développement Durable8.
Il est à signaler à cet égard que seules les autorités nationales décident de l’opportunité d’une
évaluation complémentaire de la GFPSG (PEFA Genre). Cette évaluation peut être menée de
façon indépendante, mais il est recommandé de la joindre à l’évaluation PEFA ordinaire pour
tirer parti des données déjà recueillies durant la mise en uvre de ce programme9. A l’échelle
nationale, il a été décidé de manière volontaire et pour la première fois d’intégrer dans le
troisième exercice PEFA, qui concerne l’année 2023, le cadre complémentaire « PEFA
Genre ».
Pour ce qui est de la méthodologie appliquée dans le cadre de l’évaluation complémentaire
de la GFPSG (PEFA Genre), elle est fondée sur 9 indicateurs (selon le cycle budgétaire) dont
l’indicateur 6 relatif au suivi des dépenses en faveur de l’égalité femmes-hommes (voir
schéma ci-dessous). Ainsi, selon le guide conçu par le Secrétariat PEFA pour l’application du
cadre complémentaire pour l’évaluation de la gestion des finances publiques sensible au

5
  « Point sur les objectifs de développement durable, Rapport du Secrétaire général », Conseil Economique et Social des Nations
Unies, mai 2024.
6
  La Gestion des Finances Publiques Sensible au Genre (GFPSG) qui signifie la prise en compte des préoccupations liées à la
réduction des inégalités de genre dans les politiques et pratiques budgétaires correspond à l’application d’une Budgétisation
Sensible au Genre.
7
  Ces demandes ont été manifestées lors de la consultation publique organisée en 2016 pour évaluer le nouveau cadre PEFA.
8
  Cadre complémentaire pour l’évaluation de la gestion des finances publiques sensible au genre », Secrétariat PEFA.
Washington, DC, Janvier 2020.
9
  Ibid



        6
             RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


genre, cet indicateur mesure la capacité des pouvoirs publics à suivre les dépenses
consacrées à l’égalité des sexes, de la préparation du budget à son exécution et jusqu’à
même l’élaboration des rapports d’exécution. Cela contribue à renforcer la traçabilité de ces
dépenses ainsi que la redevabilité par rapport à l’atteinte des objectifs escomptés en matière
de réduction des inégalités entre les femmes et les hommes.




 Schéma 1 : Déclinaison de la grille des indicateurs analysés dans le cadre PEFA
                   Genre structurés selon le cycle budgétaire
Source : Cadre complémentaire pour l’évaluation de la gestion des finances publiques sensible au genre », Secrétariat PEFA,
Washington, DC, Janvier 2020.
D’après le guide pour l’application du cadre complémentaire pour l’évaluation de la gestion
des finances publiques sensible au genre, le suivi des dépenses budgétaires devrait couvrir
l’ensemble du budget pour y cerner celui qui cible directement l’égalité de genre et le budget
qui a une vocation générale mais ciblant un genre spécifique. De fait, la méthodologie
conçue par le Secrétariat PEFA pour le suivi de l’indicateur 6 repose sur une catégorisation
des dépenses budgétaires qui est déclinée comme suit :
     Des programmes spécifiques visant la promotion de l’égalité de genre (exemple : les
       dépenses consacrées à la lutte contre les violences fondées sur le genre) ;
     Des Services publics généraux axés particulièrement sur un genre ou utilisés en grande
       partie par celui-ci (exemple : un projet axé sur la décentralisation et la gouvernance
       locale dont un de ces objectifs porte sur le renforcement de la participation des
       femmes à la prise de de décision à l’échelon local) ;
     Des Services publics généraux fonctionnant sans tenir particulièrement compte des
       préoccupations liées à l’égalité de genre.
Il est important de préciser que dans le cas où l’intégration de cette classification ou bien
catégorisation est prise en compte au niveau du poste budgétaire ou du code du programme,
ces derniers pourraient être « marqués » pour permettre de cerner globalement les dépenses
visant l’égalité des sexes. Ceci confère aux Etats, appliquant cette méthode, la possibilité
d’intégrer ce suivi dans le processus budgétaire et, ainsi, le systématiser pour éviter qu’il ne
soit considéré comme étant un mécanisme distinct10.




10
     Ibid.


                                                                                                                          7
     PROJET DE LOI DE FINANCES POUR L’ANNEE 2025



       2. TOUR D’HORIZON DES P RINCIPALES EXPERIENC ES
          INTERNATIONALES EN M ATIERE DE MARQUAGE
          GENRE DES BUDGETS
Comme précédemment traité, le renforcement de la traçabilité des budgets alloués à la
promotion de l’égalité de genre et de l’autonomisation des femmes, en le liant aux
engagements pris et à l’évolution des mécanismes de gestion des finances publiques, est
désormais considéré à l’échelle mondiale comme un domaine clé en mesure de consolider
l’application et l’appropriation de la BSG. De même, plusieurs grandes organisations
internationales à l’instar de l'OCDE, la Banque Mondiale et d’autres ont initié et développé
des systèmes de marquage de leurs financements pour s’assurer de la pertinence et de la
fiabilité de leurs stratégies en matière de réduction des inégalités entre les femmes et les
hommes.
Tenant compte de ces éléments, la partie qui suit met en relief les expériences les plus
marquantes émanant de plusieurs pays en termes de mise en place et d’opérationnalisation
des systèmes de marquage des allocations budgétaires consacrées à l’égalité de genre. En
outre, cette partie intègre une présentation de la méthodologie développée par l’OCDE pour
suivre les financements alloués à la promotion de l’égalité entre les femmes et les hommes
inscrits dans le Cadre de l’Aide au Développement (CAD) et qui est, d’ailleurs, considérée
comme une référence en la matière.
       2.1.   Marqueur CAD/OCDE pour la notation du degré d’intégration de
              la dimension dans la coopération au développement : Une
              référence pour plusieurs pays
Le système de marquage genre des politiques CAD/OCDE est un outil statistique
qualitatif destiné au suivi des activités visant la promotion de l’égalité de genre11qui est un
des objectifs de la politique d’aide au développement. Ce système qui repose sur l’attribution
d’une notation à trois valeurs (0, 1 et 2), permet d’identifier si un programme ou un projet
contribue directement « objectif principal » ou de manière significative « objectif significatif
» à la promotion de l’égalité entre les femmes et les hommes12. Les détails relatifs à ce
système de notation ou de catégorisation des programmes/projets sont déclinés dans le
tableau qui suit :




11
   L’OCDE a également développé des marqueurs aptes à assurer le suivi d’autres thématiques transversales en plus de l’égalité
de genre, à l’instar de la préservation de l’environnement et la lutte contre le changement climatique, en tant qu’objectifs de la
politique d’aide au développement.
12
    « Guide sur le marquage CAD/ OCDE : outil pour l’intégration systématique du nexus genre et environnement/climat »,
Direction de la Coopération au Développement et de l’action humanitaire, Ministère des Affaires étrangères et Européennes du
Luxembourg.



         8
            RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


     Valeur du              Catégorisation du
                                                                   Caractérisation du programme/projet
 Marqueur/Notation          programme/projet
                                                     Le projet/programme a été examiné au regard du
                            Non orienté vers la      marqueur mais ne vise pas la promotion de l’égalité de genre.
         CAD 0                 promotion de          Toutefois, une analyse genre dudit programme/projet a été
                            l’égalité de genre       conduite afin de s’assurer que le programme/projet n’accentuera
                                                     pas les inégalités de genre
                                                     La promotion de l’égalité de genre est un objectif important du
                              La promotion de
                                                     programme/projet mais ne constitue pas le principal motif de sa
                           l’égalité de genre est
         CAD 1                                       réalisation. Il est à noter que la promotion de l’égalité de genre
                                 un objectif
                                                     est qualifiée d’objectif « significatif » d’un programme/ projet si
                                 significatif
                                                     ce dernier vise à produire un impact positif sur l’égalité de genre.
                                                     L’égalité       de      genre       est       l’objectif    principal
                              La promotion de        du programme/projet. L’atteinte de cet objectif conditionne le
         CAD 2             l’égalité de genre est    contenu et fonctionnement du programme/projet, signifiant que
                            un objectif principal    la réduction des inégalités de genre est la raison d’être du
                                                     programme/projet
Source : « Guide sur le marquage CAD/ OCDE : outil pour l’intégration systématique du nexus genre et environnement/climat »,
Direction de la Coopération au Développement et de l’action humanitaire, Ministère des Affaires étrangères et Européennes du
Luxembourg.

                 Tableau 1 : Marqueur genre du CAD/OCDE à trois valeurs
Partant de cette déclinaison, l’attribution d’un marqueur/notation (0, 1 ou 2) est basée sur
une grille d’évaluation composée d’un ensemble de critères qui devraient être vérifiés par les
programmes/projets soumis au marquage. Le tableau ci-dessous met en relief les critères
minimums à satisfaire par marqueur/notation :

 Critères minimums                                                                        CAD 0       CAD 1      CAD 2
 - Une analyse genre du programme/projet a été réalisée
                                                                                             X           X          X
 - Les conclusions de l’analyse genre ont été prise en compte lors de la
   conception du programme/projet                                                            X           X          X

 - Les données et les indicateurs utilisées sont désagrégées par sexe                                    X          X
 - Engagement à procéder à du monitoring des résultats produits par le
   programme/projet en tenant compte de la dimension genre et d’en rendre                                X          X
   compte lors de la phase de l’évaluation
 - Le programme/projet est lié au moins à un objectif spécifique visant la
   promotion de l’égalité de genre auquel est associé au moins un indicateur
   sensible au genre (ou bien l’engagement de définir cet indicateur si le cadre                         X          X
   de résultats n’a pas encore été élaboré lors de l’évaluation du
   programme/projet moyennant le système du marquage genre)
 - La finalité première du programme/projet ou bien sa raison d’être est de
                                                                                                                    X
   promouvoir l’égalité de genre et l’autonomisation des femmes
 - Le cadre logique associé au programme/projet permet de mesurer le degré
   d’atteinte des objectifs escomptés en matière de promotion de l’égalité de                                       X
   genre, moyennant des indicateurs de résultat/d’impact sensibles au genre
Source : « Guide sur le marquage CAD/OCDE : outil pour l’intégration systématique du nexus genre et environnement/climat »,
Direction de la Coopération au Développement et de l’action humanitaire, Ministère des Affaires étrangères et Européennes du
Luxembourg.

    Tableau 2 : Les critères minimums à satisfaire par marqueur genre selon la
                             méthodologie CAD/OCDE
La fiabilité et la pertinence des résultats issus de l’utilisation de cette grille d’analyse exigent,
comme préalable, la disponibilité d’une analyse genre de l’ensemble des
programmes/projets soumis à l’évaluation y compris ceux notés 0 (programmes/projets qui
ne visent pas la promotion de l’égalité de genre) et ce, pour éviter que ces derniers ne
contribuent pas à une amplification des inégalités entre les femmes et les hommes.




                                                                                                                         9
     PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


Ainsi, la notation attribuée à chaque programme/projet est utilisée pour estimer la part des
financements consacrés à l’égalité de genre dans le total du budget qui lui a été dédié. Le
tableau ci-dessous met en exergue les pondérations adoptées à cet égard.
                                                                                    % du budget du programme/projet
     Notation/marqueur         Catégorisation du programme/projet                   considéré comme pertinent pour la
                                                                                      promotion de l’égalité de genre
                            Non orienté vers la promotion de l’égalité
             CAD 0                                                                                      0%
                            de genre
                            La promotion de l’égalité de genre est un
             CAD 1                                                                                     40%
                            objectif significatif
                            La promotion de l’égalité de genre est un
             CAD 2                                                                                     100%
                            objectif principal
Source : « Guide sur le marquage CAD/ OCDE : outil pour l’intégration systématique du nexus genre et environnement/climat »,
Direction de la Coopération au Développement et de l’action humanitaire, Ministère des Affaires étrangères et Européennes du
Luxembourg.


         Tableau 3 : Estimation des financements alloués à l’égalité de genre en
          fonction des marqueurs attribués par la grille des critères minimums
                                       CAD/OCDE
       2.2. Cas du Rwanda : Systématisation du marquage genre des
            budgets moyennant les déclarations de Budgétisation Sensible
            au Genre
La BSG au Rwanda a été initiée par le Ministère des Finances en 2008, en l’intégrant comme
une composante de la réforme budgétaire axée sur les résultats aux niveaux national et local.
Dans ce sillage, le Ministère des Finances a publié, durant la même année, les directives de la
BSG pour le Rwanda ainsi qu’une liste de contrôle pour l’intégration de la dimension genre
dans le développement économique et la stratégie de réduction de la pauvreté13. C’est, en
2012, qu’il a été décidé d’intégrer la dimension genre dans les circulaires annuelles relatives
au budget des ministères, des provinces et des districts14.
Ce processus a été couronné, en 2013, par la prise en compte de la BSG de manière explicite
dans la nouvelle Loi Organique de la Loi des Finances dépassant, ainsi, le cadre des circulaires
budgétaires qui était jusque-là le cadre référentiel de la BSG au Rwanda. Ainsi, en vertu de
l'article 32 de la nouvelle Loi Organique, tous les ministères, les départements et les agences
sont tenus à préparer et à soumettre des plans de Déclaration de Budgétisation selon le
Genre sous une forme qui comprend des sections sur l'analyse genre, les objectifs et les
résultats à atteindre en termes de réduction des inégalités de genre, les activités planifiées
pour pallier aux inégalités identifiées, les indicateurs de suivi et le budget approuvé15. Force
est de constater que l’élaboration des « Déclarations Budgétaires selon le Genre » par les
Ministères nécessite plusieurs étapes à savoir16 :
            L’identification des disparités entre les femmes et les hommes et leurs causes sous-
             jacentes moyennant une analyse genre ;
            La définition par les ministères/districts de leurs objectifs sensibles au genre, et ce
             en se basant sur les résultats de l’analyse genre ;
            L’identification des activités à entreprendre pour contribuer à l’atteinte des
             objectifs escomptés en matière de réduction des écarts de genre ;



13
    « Initiative de budget sensible au genre : profil du Rwanda », Ministère des Finances et de la Planification Economique, ONU
Femmes, Rwanda, 2012.
14
    « Guide du facilitateur formation des femmes en position de leadership sur la citoyenneté, la redevabilité, le leadership et la
budgétisation sensible au genre », Programme USAID de la gouvernance locale, 2020.
15
   https://www.orfonline.org/research/gender-responsive-budgeting-in-india-bangladesh-and-rwanda-acomparison/
16
    « Guide du facilitateur formation des femmes en position de leadership sur la citoyenneté, la redevabilité, le leadership et la
budgétisation sensible au genre », Programme USAID de la gouvernance locale, 2020.



        10
              RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


            La définition des indicateurs sensibles au genre afin de mesurer le niveau d’atteinte
             des objectifs retenus ;
            L’estimation du budget nécessaire pour le financement des activités identifiées.
Par le biais des Déclarations Budgétaires selon le Genre, le Rwanda s’est doté d’un dispositif
apte à systématiser le suivi des allocations budgétaires ex-ante dédiées à l’atteinte des
objectifs fixés en matière de réduction des inégalités de genre. En effet, ces déclarations
intègrent des rubriques liées aux budgets alloués aux activités visant la promotion de l’égalité
entre les femmes et les hommes, tout en spécifiant la totalité de l’enveloppe budgétaire qui
leur a été dédié et la part de cette enveloppe dans le budget total, Ci-après un exemple de
modèle spécifique de déclaration budgétaire selon le genre :
     Programme : Nom d'un Programme et allocation budgétaire totale allouée

     Sous-programme : Nom du sous-programme
     Analyse de la situation de
     genre (énoncer clairement le        Résultat               Activité          Indicateur                 Budget alloué
     problème)
     -
     -
     -…
     Budget total alloué aux activités sensibles au genre :
     % dans le Budget Total
Source : « Guide du facilitateur formation des femmes en position de leadership sur la citoyenneté, la redevabilité, le leadership
et la budgétisation sensible au genre », Programme USAID de la gouvernance locale, 2020.

Dans le même cadre, l'article 68 de la Loi Organique de la Loi des Finances incite les
ministères, les départements et les agences à préparer et à soumettre des rapports annuels
de mise en uvre des plans de déclaration de budgétisation selon le genre. Ces rapports
contiennent des sections sur les activités planifiées, les activités réalisées, les objectifs
atteints par rapport aux objectifs planifiés, le budget approuvé pour l'année budgétaire et le
budget exécuté, ainsi que les justifications des écarts constatés17. Ceci permet d’apporter les
informations nécessaires pour la réalisation de suivi ex-post des allocations budgétaires
destinées à la réduction des inégalités entre les femmes et les hommes.
Il est important de noter que le bureau de suivi genre (Gender Monitoring Office) est
mandaté pour assurer le suivi du niveau de réalisation par les départements ministériels de
leurs objectifs en termes de promotion de l’égalité entre les femmes et les hommes.
2.3. Cas du Mali : Application progressive d’une méthodologie basée sur
la catégorisation des dépenses budgétaires
La dynamique entreprise par le Mali pour l’implémentation d’une Planification et une
Budgétisation Sensible au Genre (PBSG) a été jalonnée par plusieurs phases d’actions
couronnées par l’initiation, en 2022, d’une méthodologie de suivi des allocations budgétaires
destinées à la promotion de l’égalité de genre. Cette méthodologie, appliquée, selon une
démarche progressive, est axée sur une catégorisation des dépenses budgétaires. Il est à
mentionner que six Ministères pilotes ont été sélectionnés pour tester la démarche arrêtée.
Il s’agit des Ministères de la Promotion de la Femme, de l’Enfant et de la Famille; de
l’Education Nationale; de la Santé et du Développement Social; des Mines, de l’Energie et de
l’Eau; du Développement Rural et de l’Economie et des Finances18.
L’édition du Rapport Genre19 annexée à la Loi des Finances 2023 a intégré, pour la première
fois, la déclinaison des principaux résultats émanant de l’expérimentation de la méthodologie

17
   https://www.orfonline.org/research/gender-responsive-budgeting-in-india-bangladesh-and-rwanda-acomparison/
18
   Rapport Genre 2023, Ministère de l’Economie et des Finances, Annexe à La loi de Finances 2023, Septembre 2022.
19
   Au Mali, le Rapport Genre est un document fondé sur l’obligation de rendre compte en matière de réduction des inégalités
de genre. Il intègre des analyses du degré de prise en compte des questions liées à l’égalité de genre déclinées dans le Plan


                                                                                                                              11
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


de catégorisation des dépenses qui est basée sur l’analyse de la nature et de l’ampleur du
lien/effet sur l’égalité de genre de chaque dépense inscrite dans le Document de
Programmation Pluriannuel des Dépenses (DPPD-PAP) du Ministère analysé. A cet effet,
cette démarche distingue trois catégories de dépenses découlant des DPPD-PAP comme
explicité dans le tableau suivant :

 Catégorisation des dépenses                                    Caractérisation des dépenses
 Les dépenses ciblant l’égalité
                                       Ces dépenses concernent celles allouées aux programmes/actions/
 de genre/dépenses ayant un
                                       activités/projets dont le principal objectif est de renforcer l’égalité de genre
 lien direct avec l’égalité de
                                       (exemple : un projet visant la promotion de l’entrepreneuriat féminin)
 genre
                                       Ces dépenses couvrent celles dédiées aux programmes/actions/
                                       activités/projets dont l’égalité de genre n’est pas le principal objectif, mais
 Les dépenses ayant un lien
                                       qui ont un impact sur la réduction des inégalités de genre et/ou
 indirect avec l’égalité de
                                       comprennent des objectifs liés à la promotion de l’égalité entre les femmes
 genre
                                       et les hommes (exemple : un projet d’électrification rurale dont l’un de ses
                                       objectifs cible l’amélioration de l’emploi féminin).
                                       Ces dépenses sont qualifiées de « dépenses neutres » allouées à des
 Les    dépenses  sans   lien
                                       programmes/actions/activités/projets qui n’ont pas d’effet sur l’égalité de
 explicite avec l’égalité de
                                       genre (il est difficile de catégoriser des dépenses comme étant neutres vis-
 genre
                                       à-vis de l’égalité de genre).
Source : Rapport Genre 2023, Ministère de l’Economie et des Finances du Mali, Annexe à La loi de Finances 2023, Septembre
2022.

   Tableau 4 : Catégorisation des allocations budgétaires en fonction de leurs
                    effets sur l’égalité de genre -cas du Mali-
L’attribution d’une catégorie de dépenses à chaque programme/action/activité/projet
inscrit dans le DPPD-PAP des ministères est effectuée par le biais d’une grille d’analyse qui
repose sur 3 trois questions mises en exergue dans le tableau qui suit :

    Question                     Contenu de la question                                       Réponses
                     L'égalité de genre est-elle ciblée/promue/
                     renforcée                 dans               le
   Question 1        programme/l'action/l'activité/le projet ?
                                                                                 Oui              Oui              Non
                     Quelles sont les mesures entreprises pour
                     promouvoir l'égalité de genre? Quels en sont
                     les effets?
                     Le programme/ l'action/ l'activité/ le projet
   Question 2        aurait-il été mis en uvre si l'égalité de genre             Non              Oui              Non
                     n'était pas un objectif?
                     L'égalité de genre est-elle mentionnée dans la
                     définition du programme/ de l'action/
   Question 3                                                                    Oui              Oui              Non
                     l'activité/ du projet de manière explicite et
                     formelle?
                                                                                             Dépenses
                                                                           Dépenses                          dépenses
                                                                                             ayant      un
  Catégorie de                                                             ayant un lien                     sans      lien
                                                                                             lien indirect
   dépenses                                                                direct avec                       explicite
                                                                                             avec
   attribuée*                                                              l’égalité  de                     avec l’égalité
                                                                                             l’égalité de
                                                                           genre                             de genre
                                                                                             genre
*Les dépenses sans lien explicite avec l’égalité de genre est la catégorie attribuée aux autres combinaisons de réponses.

      Tableau 5 : Grille d’évaluation développée pour la catégorisation des
  allocations budgétaires en fonction de leurs effets sur l’égalité de genre -cas
                                     du Mali- 20


d’action de la Politique Nationale Genre et intégrée par le Document de Programmation Pluriannuel des Dépenses (DPPD-PAP).
Il met en évidence les éléments des cadres de performance du DPPD-PAP et du Rapport Annuel de Performance (RAP) qui
contribuent à la mise en uvre du plan d’action de la Politique Nationale Genre.
20
   Rapport Genre 2023, Ministère de l’Economie et des Finances, Annexe à La loi de Finances 2023, Septembre 2022.



      12
            RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


L’application progressive par les ministères de la démarche développée par le Mali pour la
mise en place d’un système de marquage des dépenses allouées à la promotion de l’égalité
de genre a permis de mettre la lumière sur un certain nombre de préalables dont devraient
disposés ces ministères. Il s’agit, essentiellement, des analyses genre de leurs stratégies et
programmes.
2.4. Espagne   -cas  la  communauté      autonome                                                   d’Andalousie - :
Méthodologie de marquage basée sur le « projet G+ »
En Andalousie, l'égalité de genre est considérée comme un investissement d'avenir, en
mesure de consolider les progrès obtenus et de continuer à améliorer la richesse, le bien-
être social de la Région. C’est ainsi que la communauté autonome d’Andalousie a procédé,
dès le début des années 2000, à l'introduction de la perspective de genre dans le budget de
la communauté dans l’objectif d’appuyer et de consolider la mise en        uvre, à tous les
niveaux, des politiques visant l'égalité des hommes et des femmes21.
Le cadre référentiel régissant l’intégration d’une perspective de genre dans le processus
budgétaire repose sur la Loi de 2003 relative aux mesures budgétaires et administratives.
L’article 139 (1) de cette Loi rend obligatoire la réalisation d’un Rapport d’impact sous le
prisme genre des politiques qui doit accompagner le budget régional présenté au Parlement.
De plus, l’article 139 (2) de la même Loi stipule l’institution d’une commission spéciale au
Ministère régional des Finances qui sera chargée de la supervision, de l’élaboration et de
l’approbation des Rapports mentionnés par l’article 139 (1)22. En réponse à ces dispositions,
le rapport d’analyse de l’impact sous le prisme genre des politiques est devenu, à partir de
l’année 2005, une composante à part entière de la Loi de Finances en Andalousie23.
La publication, en octobre 2007, du troisième rapport annuel d’analyse de l’impact sous le
prisme genre des politiques marque un tournant en matière d’application de la BSG en
Andalousie. En effet, cette édition du rapport a mis la lumière sur une nouvelle démarche
méthodologique à déployer pour la prise en compte de la dimension genre dans
l’identification, la mise en uvre, le suivi et l’évaluation des politiques publiques.
Cette démarche appelée « Projet G+ » repose sur un système de classification des
programmes budgétaires en fonction de l’ampleur de leur impact/effet sur la réduction des
inégalités de genre. De fait, chaque programme/projet est évalué afin de le classer comme
étant un G0, G1, G et G+24. Il est important de signaler, à cet égard, que la méthodologie
développée par l’Andalousie se démarque des autres démarches de catégorisation des
dépenses budgétaires par la prise en compte dans la grille d’analyse de deux concepts, à
savoir :
 La sensibilité genre du programme/projet : qui analyse si le programme/projet affecte
  directement ou indirectement les dimensions liées l’égalité de genre ;
 La pertinence du programme/projet en termes de promotion de l’égalité de genre. Cette
  pertinence du programme/projet est évaluée en fonction de 4 critères qui sont déclinés
  comme suit :
          Pouvoir transformateur : capte le niveau de compétences de chaque programme
           budgétaire/projet. Un programme/projet est dit très pertinent au regard des
           questions liées à l’égalité de genre s’il dispose de toutes les compétences pour
           agir dans ce sens ;


21
   Rapport d’évaluation de l’impact de genre de l’avant-projet budgétaire de la communauté autonome d’Andalousie pour
l’année 2008, Département de l'Économie et des Finances de la communauté autonome d’Andalousie.
22
   « L'intégration d'une perspective de genre dans le processus budgétaire », congrès des pouvoirs locaux et régionaux, Conseil
de l’Europe, octobre 2016.
23
   « Initiative de budget sensible au genre : profil de l’Andalousie-Espagne », Ministère Régional d’Andalousie des Finances et
de l’Administration publique, 2012.
24
   « L’égalité dans les budgets : pour une mise en uvre pratique », Conseil de l’Europe, 2009.


                                                                                                                           13
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


           Capacité d'impact : elle mesure la taille de la population cible du
            programme/projet budgétaire. Ainsi, plus la population est importante, plus la
            pertinence est grande ;
           Pertinence fonctionnelle : ce critère rassemble les opinions des experts et
            expertes concernant le rôle du programme/projet dans la réduction des
            inégalités entre les femmes et les hommes ;
           Gestion du personnel : analyse l’effet du programme/projet sur la gestion du
            personnel.
Le tableau qui suit met en relief les critères de classement des programmes/projets selon la
grille d’évaluation développée par l’Andalousie dans le cadre du projet G+ :

                              Prise en compte des questions relatives à l’égalité entre les femmes et les
                              hommes
Pertinence en termes de
promotion de l’égalité de                         Oui                                          Non
genre
                              G1 : Programmes/projets ayant une             G0 :   Programmes/projets n’ayant
  Faible                      incidence sur la population, de nature        aucun effet direct sur les personnes et
                              essentiellement interne ou instrumentale      génèrent peu ou pas d’effet indirect
                              G Programmes/projets à faible impact,
  Moyenne                     ayant un pouvoir transformateur limité ou
                              une utilité fonctionnelle réduite
                              G+ Programmes/projets présentant un
                              intérêt majeur du fait de leur pouvoir
  Élevée
                              transformateur, de leur impact et de leur
                              utilité fonctionnelle reconnus
Source : Rapport d’évaluation de l’impact de genre de l’avant-projet budgétaire de la communauté autonome d’Andalousie
pour l’année 2008, Département de l'Économie et des Finances de la communauté autonome d’Andalousie.

       Tableau 6 : Grille d’évaluation des programmes/projets selon la grille
       d’évaluation développée par l’Andalousie dans le cadre du projet G+


En plus de l’analyse de leurs effets potentiels et leur capacité de transformation, les
programmes et projets soumis à l’approche G+ afin de leur attribuer une notation (G0, G1, G
et G+) sont amenés à vérifier une multiplicité d’exigences à savoir :




     14
             RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE




Classement                                            Exigences à vérifier


        G0      - Désagrégation par sexe des indicateurs relatifs à la population cible.

                - Désagrégation par sexe des indicateurs relatifs à la population cible ;
                - Analyse des actions qui ont un effet différentiel sur les hommes et les femmes en matière
                  de gestion du personnel des ministères régionaux et des organismes autonomes;
        G1
                - Analyse des actions destinées à la population cible;
                - Analyse et adaptation des outils d'information pour qu’ils intègrent davantage la dimension
                  genre

                - Désagrégation par sexe des indicateurs relatifs à la population cible;
                - Conception d'indicateurs pertinents sensibles au genre;
                - Analyse des actions destinées à la population cible;
         G      - Analyse et adaptation des outils d'information pour qu’ils intègrent davantage la dimension
                  genre ;
                - Développement d'études approfondies sur les causes des inégalités de genre soulevées
                  dans le cadre du périmètre du programme.


                - Désagrégation par sexe des indicateurs relatifs à la population cible;
                - Conception d'indicateurs pertinents sensibles au genre;
                - Analyse des actions destinées à la population cible ;
                - Analyse et adaptation des outils d'information pour qu’ils intègrent davantage la dimension
        G+        genre;
                - Développement d'études approfondies sur les causes des inégalités de genre soulevées
                  dans le cadre du périmètre du programme;
                - Définition d'objectifs et d'actions stratégiques et opérationnels en fonction du périmètre
                  du programme pour promouvoir l'égalité des sexes.

Source : Rapport d’évaluation de l’impact de genre de l’avant-projet budgétaire de la communauté autonome d’Andalousie
pour l’année 2008, Département de l'Économie et des Finances de la communauté autonome d’Andalousie.


L’attribution des notations aux programmes/projets est réalisée dans le cadre d’un processus
participatif avec l’implication de l’administration (départements ministériels/agences
concernés), les populations concernées et les chercheurs25. Il est à noter que l’approbation
des notations attribuées est prise en charge par la commission spéciale chargée de l’impact
du budget sur le genre qui relève du Ministère régional des Finances. Dans la continuité de
cette dynamique, l’année 2013 a été caractérisée par le lancement des audits de genre dans
le but d’évaluer la mise en uvre du Projet G+.
Partant de ces éléments, la méthodologie de catégorisation des allocations budgétaires
adoptée par l’Andalousie se démarque par rapport aux approches développées par les autres
pays analysés (Rwanda et Mali) et celle appliquée par le CAD/OCDE par le fait qu’elle ne
permet pas d’approcher de manière précise ni le degré de prise en compte de la dimension
genre dans les programmes budgétaires, ni leurs effets avérés sur la réduction des inégalités
de genre. Toutefois, cette démarche se focalise davantage sur les effets potentiels ou bien
transformationnels que les programmes et projets publics pourraient engendrer sur l’égalité
entre les femmes et les hommes.




25   Ibid.


                                                                                                                   15
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025



     3. CAS DU MAROC : CONCEPTION ET AFFINEMENT
        D’UNE METHODOLOGIE P OUR LE MARQUAGE DES
        DEPENSES ALLOUEES A      LA PROMOTION DE
        L’EGALITE    DE  GENRE   A LIGNEE   SUR  LES
        SPECIFICITES    DE    LA      P ROGRAMMATION
        BUDGETAIRE NATIONALE
La revue des principales expériences internationales en matière de conception et
d’application d’un système de marquage des allocations budgétaires destinées à la réduction
des inégalités de genre a permis de mettre en exergue un ensemble de conditions préalables
à établir pour respecter les engagements pris. Ces prérequis sont importants pour la mise en
place et l’opérationnalisation de mécanismes visant à assurer la traçabilité des dépenses
dédiées à la promotion de l’égalité entre les femmes et les hommes. Ils portent,
essentiellement, sur ce qui suit :
      Une bonne appropriation des outils et des instruments liés à la pratique de la BSG
       (gestion budgétaire axée sur les résultats intégrant la dimension genre, la pratique
       avancée de la démarche de performance, la production des directives à même de
       cadrer l’application de la BSG (circulaires budgétaires et autres) ainsi que des rapports
       évaluant le degré d’application de la BSG par les départements ministériels, …) ;
      Une systématisation de la réalisation des analyses genre sectorielles qui constituent
       un prérequis crucial conditionnant l’aboutissement des méthodologies de marquage
       des allocations budgétaires, ce qui sous-entend également un enrichissement continu
       des systèmes d’information par des données sensibles au genre en mesure de
       permettre la mise à jour continue de ces analyses ;
      Une implication de toutes les parties prenantes concernées par le dispositif du
       marquage genre des budgets (le MEF et les départements ministériels ainsi que les
       organismes sous leur tutelle) lors de sa conception et de son développement, tout en
       optant pour une démarche graduelle lors de sa mise en uvre…
A l’échelle nationale, notre pays dispose d’une expérience de plus de 20 années d’application
de la BSG, pilotée par le MEF et qui est qualifiée par plusieurs institutions internationales, à
l’instar du FMI, de l’OCDE et d’autres26, d’expérience réussie. Les résultats découlant de
l’évaluation de la performance du système de gestion des finances publiques sensible au
genre (PEFA Genre) effectuée, en 2023, confirment ce constat.
La dynamique qui a accompagné l’implémentation au Maroc de la BSG et l’appropriation
collective des enjeux y afférents a été rehaussée par la conception et le développement
d’outils et d’instruments (institutionnel, juridique, organisationnel et programmatique) à
même de réussir la prise en compte de la dimension genre dans les pratiques de
programmation et de budgétisation des départements ministériels. Ceci confère à
l’expérience marocaine la maturité requise pour le développement et le déploiement d’un
dispositif de marquage des budgets destinés à la réduction des inégalités entre les femmes
et les hommes.
Ainsi, dans la continuité de cette démarche et poursuivant sa quête de perfectionnement des
outils développés, tout en s’inspirant des bonnes pratiques en la matière à l’échelle mondiale,
le MEF, à travers le CE-BSG en partenariat avec ONU Femmes, s’est lancé, depuis 2022, dans
un projet ambitieux ayant pour objectif de mettre en place un système de marquage des

26
  J. Stotsky, «Gender Budgeting: Fiscal Context and Current Outcomes », FMI, 2016/ OCDE, « Bonnes pratiques de l’OCDE en
matière de budgétisation sensible au genre », revue de l'OCDE sur la gestion budgétaire, volume 2023, numéro 1, février 2023/
Edition 2024 du Rapport sur le Budget axé sur le Budget axée sur les Résultats tenant compte de l’aspect Genre.



      16
            RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


budgets alloués à la promotion de l’égalité de genre. La conception et l’opérationnalisation
d’un tel système acte le passage de notre pays vers un autre palier d’action pour la
concrétisation des engagements pris dans le cadre de l’Agenda 2030 pour le Développement
Durable et de la consolidation de la performance de la gestion des finances publiques
sensibles au genre, à travers l’adhésion au module complémentaire du PEFA (PEFA Genre).

 Encadré 3 : Principaux résultats émanant du premier exercice d’’évaluation de la performance
                du système de gestion des finances publiques sensible au genre
Comme précédemment signalé, le Maroc a pris l’initiative d’intégrer dans l’exercice d’évaluation de
performance des systèmes de gestion des finances publiques, au titre de l’année 2023, pour la première
fois le Cadre Complémentaire pour l’évaluation de la gestion des finances publiques sensible au genre
« PEFA Genre ». Cette évaluation a concerné 3 années (de 2020 à 2022) et s’est focalisée sur
l’administration centrale à l’image de l'évaluation PEFA principale.
Les notes obtenues par le Maroc selon les critères d’évaluation adoptée (voir le point 1.1 dédié à la
démarche méthodologique adoptée dans le cadre de l’évaluation PEFA Genre) sont déclinées dans le
tableau qui suit :

                                                     Méthode         Notes des composantes
  Indicateurs PEFA GFPSG                                                                            Note globale
                                                    de notation
                                                                         1              2
                  Analyse de l’incidence de
  CFPSG-1         genre       des     politiques         M1              D              D                 D
                  budgétaires proposées.
                  Gestion des investissements
  CFPSG-2                                                M1              D                                D
                  publiques sensibles au genre.
                  Circulaire         budgétaire
  CFPSG-3                                                M1              B                                B
                  sensible au genre.
                  Documentation budgétaire
  CFPSG-4                                                M1              A                                A
                  relative au genre.
                  Ventilation par genre des
                  informations       sur      la
  CFPSG-5                                                M2              A              A                 A
                  performance des services
                  publiques.
                  Suivi       des     dépenses
  CFPSG-6         budgétaires en faveur de               M1              C                                C
                  l’égalité femmes-hommes.

  CFPSG-7         Reporting sensible au genre.           M1              A                                A
                  Evaluation de l’impact de
  CFPSG-8                                                M1              C                                C
                  genre des services publics
                  Examen législatif de l’impact
  CFPSG-9                                                M2              A              C                 B
                  de genre du budget.
Source : Rapport du programme d’examen des dépenses publiques et d’évaluation de la responsabilité financière (PEFA) du
Maroc, Juin 2024.

D’après le Rapport du programme d’examen des dépenses publiques et d’évaluation de la responsabilité
financière (PEFA) du Maroc (juin 2024), notre pays a réussi à réaliser des progrès significatifs en matière
d’intégration de la dimension genre dans la gestion des finances publiques. Ces avancées réalisées sont
le fruit, selon le Rapport, d’une part, de l’adoption des Lois, essentiellement la LOF de 2015, qui appellent
à la prise en compte de l’égalité de genre dans la programmation budgétaire des départements
ministériels, et d’autre part, de l’institutionnalisation de l’obligation d’élaboration des rapports qui
assurent le suivi du niveau de prise en compte des préoccupations liées à l’égalité de genre dans les
exercices de programmation, de budgétisation et de suivi et évaluation des départements ministériels
(le Rapport sur le budget axé sur les résultats tenant compte de l’aspect genre et les projets ministériels
de performance qui accompagnent la présentation du projet de Loi de Finances ainsi que les Rapports
annuels de performance qui accompagnent le Projet de Loi de Règlement).
Ces efforts ont, de fait, permis au Maroc d’obtenir de bons résultats au niveau de 7 indicateurs
d’évaluation adoptés dans le cadre du PEFA Genre sur un total de 9 indicateurs (voir tableau ci-dessus).
En effet, l’évaluation du processus d’implémentation et d’application de la BSG au Maroc a été noté "A"



                                                                                                                     17
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


 pour 3 indicateurs (GFPSG 4,5 et 7), "B" pour 2 indicateurs (GFPSG 3 et 9), "C" pour 2 indicateurs (GFPSG
 6 et 8) et "D" pour 2 indicateurs (GFPSG 1 et 2). Il est à noter à cet égard que la note "C" correspond à la
 moyenne. Les notes A et B sont considérées comme des notes supérieures. Quant à la note D, elle est
 qualifiée de note inférieure à la moyenne.
 Ce faisant, le Maroc est interpelé à déployer des efforts supplémentaires en termes de réalisation des
 analyses ex-ante de l'incidence des dépenses publiques sur les inégalités de genre. De même, le recours
 à des analyses de l’impact des grands projets d’investissements sur l’égalité de genre est sollicité. Sur la
 base de ces constats, le Rapport PEFA propose à ce que le Maroc inscrive l’évaluation des impacts des
 politiques publiques sur l’égalité de genre dans les pratiques de gestion des finances publiques sensibles
 au genre appliquées.
 Il ressort, ainsi, de cette première évaluation de performance des systèmes de gestion des finances
 publiques sensibles au genre que le Maroc a obtenu une note C qualifiée de moyenne en matière de suivi
 des dépenses budgétaires en faveur de l’égalité femmes-hommes (GFPSG 6). Cette évaluation qui
 concerne l’année 2022 a attribué cette note au Maroc au regard de l’indisponibilité d’une méthodologie
 arrêtée de marquage des budgets alloués à la réduction des inégalités de genre. C’est dire que grâce à
 la méthodologie de marquage genre des budgets développée, en 2024, et testée sur deux départements
 ministériels, il est attendu à ce que le prochain exercice d’évaluation de performance des systèmes de
 gestion des finances publiques sensibles au genre révise à la hausse la note relative à l’indicateur GFPSG6.
Après près de 2 ans depuis le lancement dudit projet, jalonnés par plusieurs phases d’analyse,
de réflexion, de concertation et d’essais, l’année 2024 a été marquée par la conception d’une
méthodologie de marquage des allocations budgétaires dédiées à l’égalité entre les femmes
et les hommes alignée sur les spécificités de la gestion budgétaire nationale.
En adoptant une approche progressive et participative impliquant le MEF et plusieurs
départements ministériels, la démarche préconisée s’inspire du système de marquage genre
du CAD/OCDE et des expériences internationales réussies en la matière (Rwanda,
Andalousie et autres).
La partie qui suit décline les grandes lignes de la méthodologie de marquage développée
pour le cas du Maroc ainsi que les principaux résultats émanant de son application, à titre
expérimental, par le Département de la Jeunesse.
3.1. Marquage genre des budgets au Maroc : Approche axée sur un
système de catégorisation des programmes et des projets
En s’inspirant des expériences internationales réussies en matière de conception et
d’utilisation d’un système de marquage des allocations budgétaires destinées à la promotion
de l’égalité de genre et de celle appliquée par le CAD/OCDE, la méthodologie de marquage
développée pour le cas du Maroc est, à son tour, axée sur la notation ou la catégorisation
des dépenses allouées aux programmes budgétaires et aux projets. Cette méthodologie a la
particularité de travailler sur deux niveaux, en l’occurrence, le niveau des programmes pour
s’assurer de la prise en compte de la dimension genre dans la programmation des
départements ministériels. L’analyse des projets permet, à son tour, d’approcher le degré de
l’intégration des préoccupations liées à la réduction des inégalités de genre dans les actions
opérationnelles actées par les départements ministériels et en déduire, ainsi, les allocations
budgétaires effectivement allouées à la promotion de l’égalité de genre.
De fait, la méthodologie développée est scindée en plusieurs étapes :
Etape 1 : Attribution                  d’une       notation/marqueur               aux     programme
 budgétaires
Cette étape consiste à soumettre chaque programme budgétaire à une grille d’évaluation
qui intègre un ensemble de critères à vérifier. L’attribution d’une notation/marqueur à
chaque programme budgétaire est tributaire de plusieurs critères, appuyée par des sources
et des techniques de vérification (les PdPs sont la source de vérification par excellence des
critères d’évaluation pour la notation des programmes). Il est à mentionner que pour le cas
du Maroc, il a été décidé d’adopter une notation composée de 4 codes/marqueurs (G0 :


     18
            RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


aveugle au genre, G1 : faiblement sensible au genre, G2 : sensible au genre, G+ :
spécifiquement dédié à l’égalité de genre) à l’instar du cas de l’Andalousie, au lieu de 3 codes
du CAD/OCDE, pratiqués par le Mali et autres pays. Le tableau qui suit met en relief la
caractérisation des programmes budgétaires analysés en fonction des codes/marqueurs qui
leurs sont attribués.

     Code/marqueur                           Caractérisation du programme budgétaire/projet

 G+ : spécifiquement       L’égalité entre les femmes et les hommes et l’autonomisation des femmes constitue
 dédié à l’égalité de      la raison d’être du programme et sa recherche détermine de façon fondamentale la
 genre                     conception de ce dernier et les résultats qui en sont attendus.
                            L’égalité entre les femmes et les hommes et l’autonomisation des femmes est un
 G2 :  sensible       au    objectif important du programme parmi d’autres objectifs (l’égalité de genre n’est
 genre                      donc pas la principal motivation pour la conception et la mise en        uvre du
                            programme analysé).
                           La contribution du programme à la promotion de l’égalité de l'égalité entre les
 G1    :    faiblement
                           femmes et les hommes et l’autonomisation des femmes est mineure par rapport à
 sensible au genre
                           l’ampleur de sa contribution aux autres objectifs escomptés.
 G0 :    aveugle      au   Le programme ne vise pas l’égalité entre les femmes et les hommes et
 genre                     l’autonomisation des femmes.
Source : CE-BSG, 2024.

Tableau 7 : Notation des programmes en fonction du degré de prise en compte
                            de la dimension genre
Les critères d’évaluation adoptés pour attribution de notations précitées aux programmes
budgétaires analysés sont déclinés dans le tableau suivant :
 Critères                           Exigences à vérifier                                            Réponses
                              Existe-t-il une analyse genre actualisée (de 5 ans
1. Disponibilité       d’une   au maximum) au niveau du programme ?
   analyse       genre    du  Existe-t-il une étude spécifique incluant une
                                                                                            O       N       O       N
   programme        ou    du   analyse des enjeux genre / inégalités de genre
   secteur                     dans      le    domaine     d’intervention      du
                               programme?27
2.Prise en compte de
   l’égalité de genre dans  Est-ce que la stratégie du programme vise
                                                                                            O       O       O       N
   la       stratégie     du   l’égalité de genre/autonomisation des femmes ?
   programme
3.Pise en compte de
   l’égalité de genre dans  Un des objectifs du programme est-il de réduire
                                                                                            O       O       N       N
   les      Objectifs     du   les inégalités de genre ?
   programme
4.        Pise en compte de
   l’égalité de genre par un  Est-ce qu’au moins un des objectifs du
   ou plusieurs indicateurs    programme est mesuré par un indicateur (ou                       O   O       N       N
   de     performance     du   sous-indicateur) sensible au genre ?
   programme
     Notation/marqueur                                                                      G+      G2    G1      G0
- O : Oui/ N : Non
- Les différentes combinaisons de réponses déclinées dans le tableau ne sont pas exhaustives.
                                                                                                    Source : CE-BSG, 2024

     Tableau 8 : Grille d’évaluation développée pour la notation/marquage des
                               programmes budgétaires




27 L’étude devra contenir des informations et des données qui permettraient l’identification, la compréhension et
l’explication des inégalités entre les hommes et les femmes dans les périmètres d’action du programme analysé.


                                                                                                                        19
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


Etape 2 : Attribution d’une notation/marqueur aux projets découlant du
 programme budgétaire analysé
Comme précédemment traité, en renseignant la grille d’évaluation, moyennant l’exploitation
principalement les contenus des PdPs, la notation des programmes budgétaires permettrait
d’approcher le degré de prise en compte de la dimension genre dans la conception, le
déploiement et les mécanismes de suivi et d’évaluation des programmes budgétaires des
départements ministériels. Dans un souci de renforcement du niveau de précision et de
fiabilité de la méthodologie de marquage développée, il a été jugé opportun de procéder, en
outre, à la notation/marquage des projets relevant des programmes budgétaires, selon une
approche spécifique. Cette étape a pour objectifs, non seulement, d’assurer une traçabilité
ex-ante des budgets des projets dédiés à la promotion de l’égalité de genre, mais également
de confirmer ou d’ajuster la notation attribuée aux programmes budgétaires. Dès lors, la
notation/marquage des projets relevant de chaque programme budgétaire s’effectue, à son
tour, en 3 phases :
Phase 1 : Indentification des projets découlant de chaque programme budgétaire et des
budgets qui leurs sont alloués
Il est jugé crucial, durant cette étape, de s’assurer de la cohérence entre les projets physiques
découlant de chaque stratégie sectorielle et ceux inscrits dans la morasse budgétaire. Si
cette cohérence n’est pas vérifiée, il est, alors, nécessaire de procéder à l’élaboration d’un
tableau de concordance qui établit les liens entre les deux. Pour ce faire, les départements
ministériels sont appelés à exploiter les informations contenues dans les cadres logiques
associés à leur stratégie, les fiches projets élaborées et renseignées, les PdPs et les morasses
budgétaires.
Phase 2 : Notation/marquage des projets
Une fois le tableau de concordance élaboré et les projets, relevant des programmes
budgétaires précédemment notés, sont identifiés, il est alors question de procéder à
l’attribution de notation/marqueur à chaque projet. Le tableau ci-dessous met en relief la
caractérisation des projets selon les codes qui leur sont attribués.



      Code/marqueur                           Caractérisation du programme budgétaire/projet

 1. Spécifiquement
                              L’égalité entre les femmes et les hommes et l’autonomisation des femmes est
    dédié à l’égalité de
                              l’objectif stratégique et la raison d’être du projet.
    genre
                              L’égalité entre les femmes et les hommes et l’autonomisation des femmes est un
 2.      Sensible        au
                              objectif opérationnel du projet.
   genre
                              La contribution du projet aux objectifs l'égalité entre les femmes et les hommes et
 3.      Faiblement
                              l’autonomisation des femmes est mineure par rapport à l’ampleur de sa contribution
   sensible au genre
                              aux autres objectifs escomptés.
 4.     Aveugle          au   Le projet ne vise pas l’égalité entre les femmes et les hommes et l’autonomisation
  genre                       des femmes.
 5.        Non évalué         Le projet n’a pas été évalué.
Source : CE-BSG, 2024.

 Tableau 9 : Notation des projets en fonction du degré de prise en compte des
                      préoccupations liées l’égalité genre

A l’instar des programmes budgétaires, plusieurs critères ont été retenus pour servir de grille
d’évaluation à renseigner afin d’attribuer des notations/marqueurs aux projets analysés. Le
tableau qui suit met en exergue les détails relatifs à cette grille :


      20
             RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE



          Critères                            Exigences à vérifier                                  Réponses

                                L'objectif stratégique du projet est-il de réduire
Objectif     stratégique                                                                                           Non
                                 les inégalités de genre et/ou l'autonomisation         O       N      N      N
sensible au genre                                                                                                  évalué
                                 des femmes ?
                                Le projet est-il accompagné d’au moins un
Objectif    opérationnel                                                                                           Non
                                 objectif opérationnel pour réduire les inégalités      O       O      N      N
sensible au genre                                                                                                  évalué
                                 de genre et/ou l'autonomisation des femmes ?
Activité   ou    résultat  Le projet dispose-t-il d’une activité ou un                                            Non
                                                                                        O       O      O      N
sensible au genre           résultat spécifique au genre ?                                                         évalué

Indicateur       sensible   au  Le projet est-il accompagné à un indicateur                                       Non
                                                                                        O       O       O      N
genre                            sensible au genre ?                                                               évalué

                                                                                                                   Non
Notation/Marqueur                                                                        1      2       3      4
                                                                                                                   évalué
- O : Oui/ N : Non
- Les différentes combinaisons de réponses déclinées dans le tableau ne sont pas exhaustives.
                                                                                                       Source : CE-BSG, 2024

   Tableau 10 : Grille d’évaluation développée pour la nota tion/marquage des
                                      projets
Phase 3 : Estimation des allocations budgétaires allouées aux projets et destinées à la
promotion de l’égalité de genre
Sur la base de la notation/marqueur obtenu par chaque projet analysé, une part du budget
programmé pour ce projet est, alors, considérée comme dédiée à la promotion de l’égalité
entre les femmes et les hommes selon les pondérations suivantes :
                                 Catégorisation de la notation            % du budget du projet considéré comme
 Notation/marqueur
                                          marqueur                        pertinent pour la promotion de l’égalité
     du projet
                                                                                         de genre
                            Spécifiquement dédié à l’égalité de
             1              genre                                                               100%

             2              Sensible au genre                                                   70%
             3              Faiblement sensible au genre                                        30%
             4              Aveugle au genre                                                    0%
             5              Non évalué                                                          0%
Source : CE-BSG, 2024.

Tableau 11 : Estimation de la part du budget du projet qui est dédiée à l’égalité
                                    de genre
Etape 3 : Estimation des budgets des programmes                                                         budgétaires
 consacrés à l’égalité entre les femmes et les hommes
Partant des estimations des budgets de chaque projet qui sont dédiés à l’égalité de genre
obtenus par le biais des analyses effectuées lors de la deuxième étape de la méthodologie
développée, il s’en suit l’estimation de la part du budget relatif à chaque programme
budgétaire qui est effectivement alloué à la promotion de l’égalité de genre. Ce budget
correspond, dès lors, à la somme totale des parts des budgets relatifs aux projets découlant
dudit programme qui sont consacrées à l’égalité de genre (voir tableau ci-dessous).




                                                                                                                         21
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025



    Somme des parts des                       Totale des budgets des
 budgets des projets qui sont               projets pondérés en % de la                  Notation/marqueur du Programme
 destinées à l’égalité de genre             valeur totale du budget du                             budgétaire
                                                    programme*
                                                                                       G+ : spécifiquement dédié à l’égalité de
                                                        Plus 85 %
                                                                                       genre
   (Part du budget projet 1+
   Part du budget Projet 2+                        Entre 50 et 84 %                    G2 : sensible au genre
   Part du budget projet 3+                                                            G1: faiblement sensible au genre
                                                   Entre 20 et 49 %
  Part du budget projet 4...)
                                                     Entre 0 et 19 %                   G0: aveugle au genre
 *:
                     Σ des budgets pondérés des projets relvant du programme analysé
       ܶܽ‫ ݊݁ ݔݑ‬% =
                                      Total du budget du programme
Source : CE-BSG, 2024

Tableau 12 : Estimation de la part des budgets d’un programme budgétaire qui
           est consacrée à l’égalité entre les femmes et les hommes
Cette étape permet, ainsi, d’attribuer une nouvelle notation/marqueur à chaque programme
budgétaire selon la part de son budget programmé destinée à la promotion de l’égalité de
genre. Cette notation est, par la suite, menée à être confrontée avec celle obtenue lors de
l’étape 1 en utilisant la grille de notation des programmes budgétaires. Il est important de
noter que si des différences entre les deux notations sont constatées, la notation finale à
retenir est la plus basse.
Tenant compte de l’ensemble de ces étapes, il est clair que l’opérationnalisation de la
méthodologie de marquage des budgets développée pour le Maroc sollicite la disponibilité
d’un ensemble de préalables d’ordre :
       Informationnel : qui exige la disponibilité des analyses genre et des données sensibles
        au genre mises à jour… ;
       Programmatique : qui demande une bonne maitrise de la programmation budgétaire
        sensible au genre, de la démarche de performance sensible au genre, de la
        disponibilité des cadres logiques ainsi que des fiches projets dûment renseignées et
        mises à jour… ;
       Organisationnel : qui renvoie à la désignation des personnes ressources aptes à réussir
        l’opération du marquage, tout en engageant les mesures d’accompagnement à même
        de les appuyer pour maîtriser l’ensemble des étapes de cette opération en termes
        d’institutionnalisation, d’accès à l’information, d’accompagnement et de formation…
       Suivi et reporting : Les Rapports sur le budget axé sur les résultats tenant compte de
        l’aspect genre, les Rapports de performances ainsi que les PdPs sont amenés à adapter
        leur contenu afin d’y intégrer les résultats et les constats émanant de l’application par
        les départements ministériels de la méthodologie de marquage genre des budgets…
Conscient de ces enjeux et dans l’objectif de réussir l’implémentation progressive de ce
projet porteur d’innombrables opportunités pour perfectionner l’application de la BSG au
Maroc, le CE-BSG prévoit des séances de formation et d’accompagnement au profit des
départements ministériels, selon une démarche graduelle. Il est à noter dans ce cadre que les
Départements de la Jeunesse et de l’Education Nationale et du Préscolaire ont bénéficié,
durant l’année 2023, de séances de formation et d’accompagnement pour tester l’ensemble
des étapes de la méthodologie développée.
En outre, le CE-BSG prévoit le lancement, incessamment, d’un module dédié au marquage
genre des budgets, intégré au système d’information e-budget 2 qui sera en mesure de



       22
         RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


permettre aux départements ministériels impliqués de renseigner l’ensemble des étapes de
la méthodologie conçue.
Dans le même sillage, il est à rappeler que le suivi et le reporting du processus d’application
progressive de la méthodologie conçue et des résultats qui en découlent constituent des
sources d’information fort utiles dans la perspective d’améliorer et d’ajuster ladite
méthodologie au fur et à mesure de l’avancement de son opérationnalisation.
3.2. Application test de la méthodologie de marquage genre du budget
2024 du Département de la Jeunesse : Principaux résultats
La réduction des inégalités de genre est au c ur de la stratégie d’action du Département de
la Jeunesse, conformément à ses missions et à ses attributions. Dès lors, le Département
contribue considérablement aux efforts engagés par les pouvoirs publics en faveur de la
promotion de l’égalité de genre et de l’autonomisation des femmes. Le département a
entrepris une stratégie d’action qui repose sur deux programmes budgétaires à savoir : le
programme de pilotage et gouvernance et celui relatif à la jeunesse, l’enfance et les femmes.
Il convient de rappeler que le portefeuille des projets, relevant du programme relatif au
pilotage et à la gouvernance est composé de trois projets de regroupement, en l’occurrence,
celui portant sur «la modernisation de l'administration et des ressources humaines », le projet
lié au « soutien des missions » et celui consacré à « la coopération et au partenariat ». Quant
au programme dédié à la jeunesse, l’enfance et les femmes, il est articulé autour de deux
projets de regroupement relatifs à « la réalisation des programmes de la Jeunesse » et à « la
réalisation des programmes de l'enfance et des affaires féminines ». Cette déclinaison est le
résultat d’un processus de concordance entre les projets inscrits dans la feuille de route de
la stratégie du Département et ceux pris en compte dans les morasses budgétaires.
L’exploitation des informations contenues dans le PdP du Département de la Jeunesse au
titre de la Loi de Finances 2024 et dans d’autres sources d’informations, en lien avec la prise
en compte de la dimension genre dans sa chaîne de résultats, a permis de renseigner la grille
d’analyse de ses programmes budgétaires et leur attribuer, ainsi, des notations,
conformément à la méthodologie de marquage genre développée pour le cas du Maroc. Il
ressort, ainsi, de l’application de la grille d’évaluation que le programme relatif au pilotage et
à la gouvernance est noté comme étant un programme G1, soit faiblement sensible au genre.
Cette note est attribuable, essentiellement, à l’absence de la prise en compte de la dimension
genre aussi bien dans sa stratégie que dans ses objectifs. Ceci, malgré le fait que le
programme dispose d’analyse des enjeux liés à l’égalité de genre couvrant son périmètre
d’intervention. Toutefois, le programme est accompagné d’un seul sous-indicateur de
performance sensible au genre portant sur « le taux d’accès des femmes à la formation ».
Quant au programme dédié à la jeunesse, à l’enfance et aux femmes, bien qu’il vise la
réduction des inégalités de genre, cet objectif reste un parmi d’autres et n’est pas considéré
comme la raison d’être du programme. Il est à rappeler dans ce cadre que le programme
n’intègre qu’un seul objectif qui vise explicitement la promotion de l’égalité de genre et
l’autonomisation des femmes et qui porte sur « la contribution à l’autonomisation des
femmes et des filles à travers la formation et l’accompagnement ». Néanmoins, la chaine de
résultats dudit programme intègre plusieurs indicateurs et sous indicateurs de performance
sensibles au genre (voir le point consacré au Département de la Jeunesse dans la partie II du
présent Rapport pour plus de détails). Ainsi, ce programme vérifie trois critères de la grille
d’évaluation, à l’exception de la disponibilité d’une analyse genre des domaines de son
intervention, ce qui lui confère une notation G2 qui correspond à un programme sensible au
genre.
Pour ce qui est de la notation de projets qui a pour objectifs d’une part, d’estimer la part des
budgets des deux programmes budgétaires destinés à la promotion de l’égalité de genre au
titre de de l’année 2024, et d’autre part, de vérifier les notations ou les marqueurs qui leur


                                                                                               23
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


ont été précédemment attribués, l’application de la grille de notation des projets indique que
les projets portant sur la modernisation de l'administration et des ressources humaines et sur
la coopération et partenariat qui relèvent du programme « pilotage et gouvernance » sont
notés comme étant des projets sensibles au genre. Ces projets visent, entre autres, la
promotion de l’égalité de genre et intègrent des activités pour y parvenir. Quant au projet
qui concerne le soutien des missions, une note de 4 lui a été attribuée, signifiant qu’il est
aveugle à l’égalité de genre.
Dans le même cadre, le projet relatif à la réalisation des programmes de la Jeunesse,
découlant au programme 2 dédié à la jeunesse, l’enfance et les femmes, contribue à la
réduction de l’égalité de genre, par le biais de plusieurs activités qui sont associées à des
indicateurs sensibles au genre mesurant, à leur tour, le degré d’atteinte des objectifs
escompté en la matière. Ceci confère à ce projet une note de 2, en le catégorisant comme
un projet sensible au genre. Pour sa part, le projet portant sur la réalisation des programmes
de l'enfance et des affaires féminines est noté 1, ce qui correspond à un projet spécifiquement
dédié à l’égalité de genre. Cette note s’explique par le fait que la promotion de l’égalité entre
les femmes et les hommes ainsi que l’autonomisation des femmes constituent l’objectif
stratégique du projet. Le projet intègre un ou plusieurs objectifs opérationnels dans ce sens.
Ces derniers sont associés à des activités et à des indicateurs sensibles au genre (voir le point
consacré au Département de la Jeunesse dans la partie III du présent Rapport pour plus de
détails).
Tenant compte de la notation obtenue par chaque projet analysé, la part du budget
programmé pour chaque projet relevant des deux programmes du Département de la
Jeunesse destinée à la promotion de l’égalité de genre se présente comme suit :
                                                                       Montant du
                                                    % du budget du                        Total des
                                                                        budget du
                                                    projet considéré                    budgets des
                                                                      projet alloué à
                                         Notation comme pertinent                     projets pondérés     Code
  Programme              Projet                                        l’égalité de
                                         du projet       pour la                      en % de la valeur programme
                                                                        genre* (En
                                                      promotion de                    totale du budget
                                                                        millions de
                                                   l’égalité de genre                  du programme
                                                                         dirhams)
                   Modernisation de
                   l'administration
                                              2              70%        224,93
                   et des ressources
  Pilotage et
                   humaines
  gouvernanc                                                                               51%             G2
       e           Soutien     des
                                              4              0%            -
                   missions
                   Coopération et
                                              2              70%          11,3
                   partenariat

                   Réalisation des
                   programmes de              2              70%         536,4
                   la Jeunesse
  Jeunesse,
  enfance et                                                                               81%             G2
   femmes          Réalisation des
                   programmes de
                                              1              100%        442,2
                   l'enfance et des
                   affaires
                   féminines.
* : Seuls les crédits de paiement qui sont pris en compte.
Source : Département de la Jeunesse, 2024.

    Tableau 13 : Estimation de la part des budgets des projets et des programmes du
       Département de la Jeunesse destinée à la promotion de l’égalité de genre
L’estimation de la part des budgets des projets et des programmes budgétaires du
Département de la Jeunesse allouée à la réduction de inégalités de genre et à la promotion
de l’autonomisation des femmes confirme la notation attribuée au programme portant sur



      24
         RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


la jeunesse, l’enfance et les femmes qui est considéré comme un programme sensible au
genre avec une part de son budget dédiée à l’égalité située à près de 81%.
Au regard des notations attribuées aux projets relevant du programme relatif au pilotage et
à la gouvernance, il en découle que ce dernier est catégorisé comme étant sensible au genre
avec une notation de G2 et un budget alloué à l’égalité de genre qui avoisine 51% de son
budget total et non pas G1 obtenu en utilisant la grille de notation des programmes
budgétaires. En se référant aux règles adoptées par la méthodologie développée, dans le cas
où des différences sont constatées entre les notations des programmes budgétaires
obtenues selon la grille de notation et la démarche basée sur l’estimation des budgets
dédiées l’égalité, il est alors question de ne retenir que la notation la plus basse, soit G1
(faiblement sensible au genre).
Ces résultats attestent de manière claire de la portée de la méthodologie développée pour
le cas du Maroc et des perspectives prometteuses attendues de son application progressive
par les départements ministériels. Les travaux entrepris pour la mise en place et
l’opérationnalisation d’un module consacré au marquage genre des budgets, intégré au
système d’information e-budget 2, qui est parfaitement aligné sur la méthodologie
développée, constituent une étape jalon sur la voie de la généralisation de l’application et de
l’appropriation de ladite démarche. A cet égard, il convient de rappeler que la circulaire du
Chef du Gouvernement (n°4/2024) en date du 15 mars 2024 relative à l’établissement des
propositions de Programmation Budgétaire Triennale assortie des objectifs et des
indicateurs de performance au titre de la période de 2025 à 2027 a insisté sur l’importance
du suivi des allocations budgétaire destinées à la promotion de l’égalité de genre. Elle a,
également, souligné le rôle clé attribué au module marquage intégré au e-budget 2 genre
que les départements ministériels sont amenés à renseigner une fois celui-ci est
opérationnalisé.
Dans le même cadre, en parallèle avec la programmation d’un processus d’accompagnement
graduel des départements ministériels pour l’opérationnalisation et l’appropriation de la
méthodologie développée, le CE-BSG a initié les travaux visant la réalisation d’un guide qui
servira de référence méthodologique en mesure d’appuyer et d’orienter les départements
ministériels lors de l’application de la méthodologie du marquage genre des budgets.




                                                                                            25
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025



     II.    ASSISES JURIDIQUES ET INSTITUTIONNELLES EN
            FAVEUR DE L’EGALITE DE GENRE
Cet axe regroupe les Départements dont l’action concourt à la réalisation de l’ancrage
institutionnel de l’égalité entre les sexes et de l’accès équitable aux droits civils et politiques,
à savoir, les Droits de l’Homme, la Justice, la Délégation Générale à l’Administration
Pénitentiaire et à la Réinsertion, les Habous et Affaires Islamiques, la Solidarité, l’Insertion
Sociale, l’Economie et les Finances, la Réforme de l’Administration28, les Affaires Etrangères
et la Coopération Africaine et la Communication. Cet axe traite également l’apport, en la
matière, de certaines institutions qui se sont engagées dans la mise en uvre de la BSG à
l’instar du Haut-Commissariat au Plan et du Conseil Economique, Social et Environnemental.

1. DELEGATION INTERMINI STERIELLE AUX DROITS DE
L’HOMME
La Délégation Interministérielle aux Droits de l’Homme (DIDH), de par ses missions et
attributions, joue un rôle de premier ordre en matière de suivi du niveau de concrétisation
des engagements pris par notre pays en faveur de la réduction des inégalités entre les
femmes et les hommes et de la protection des droits des femmes.
1.1. Analyse genre : point de départ pour réussir une programmation
intégrant la dimension genre
La DIDH ne dispose pas encore d’une analyse genre de son fonctionnement et de ses
domaines d’intervention. De ce fait, les projets et actions mis en uvre par la Délégation
pour la promotion de l’égalité de genre et la protection des Droits des femmes se réfèrent à
sa stratégie d’action fondée, entre autres, sur la consolidation de l’intégration de la dimension
des droits de l’Homme dans les politiques publiques, le renforcement de l’interaction et de la
coopération avec les acteurs internationaux des droits de l’Homme et le développement de
la coopération et du dialogue avec la société civile.
1.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité et d’autonomisation économique des femmes
Comme précédemment signalé, la DIDH est chargée de la coordination et du suivi de la mise
en uvre des politiques et des actions en faveur du respect des droits de l'Homme. Elle joue,
également, un rôle majeur dans l’interaction avec le système onusien des droits de l’Homme
et le processus de l'Examen Périodique Universel (EPU) des Nations Unies et les autres
examens, en coordonnant avec les départements ministériels et les institutions nationales, la
préparation des rapports nationaux, des réponses aux recommandations émises et des plans
d’actions pour le suivi de l’opérationnalisation des recommandations retenues. Les questions
liées à la réduction des inégalités de genre et à la lutte contre les discriminations fondées sur
le genre sont au centre de la stratégie d’action de la Délégation.
Dans ce sillage, il est à noter que la DIDH prépare, actuellement, en partenariat avec les
départements ministériels, un projet de plan national pour l’opérationnalisation des
recommandations émises par les mécanismes internationaux des droits de l'Homme, y
compris celles liées à la réduction des inégalités de genre et à la protection des droits des
femmes29.



28 L’Annexe 1 met en exergue la présence quantitative des femmes dans les structures organisationnelles des
départements ministériels et des institutions publiques.
29 Ce processus a été initié à partir de juin 2023, juste après la présentation des résultats des interactions avec

les mécanismes internationaux des droits de l’Homme.


      26
         RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


Au regard de sa stratégie d’actions et tenant compte de ses projets déployés et en
perspectives, la DIDH est, alors, considérée comme étant une partie prenante de la mise en
  uvre du PGE III, particulièrement, ses volets en lien avec le renforcement du cadre juridique
relatif à la réduction des inégalités de genre et à la promotion des droits de l'homme.
1.3. Chaine de résultats sensibles au genre : application de la démarche
performance sensible au genre
Conformément à la circulaire du Chef du Gouvernement (n°4/2024) en date du 15 mars 2024
relative à l’établissement des propositions de Programmation Budgétaire Triennale assortie
des objectifs et des indicateurs de performance, au titre de la période 2025-2027, la DIDH a
mis en place une chaine de résultat qui intègre la dimension genre au niveau d’un seul
indicateur de performance. Cet indicateur, portant sur le taux de mise en          uvre des
recommandations des instances onusiennes relatives à l’égalité de genre, renseigne sur le
degré de réalisation de l’objectif du programme « Doits de l’Homme » qui vise à assurer le
respect des obligations liées à l'interaction internationale dans le domaine des droits de
l'Homme (voir le tableau ci-dessous).
                                                                                   Réalisation     LF
  Programme                Objectif                         Indicateur
                                                                                     2023         2024
                Assurer      le   respect    des   Taux de la mise en  uvre des
   Droits de    engagements         relatifs   à   recommandations           des
                                                                                     53,03%       30%
   l’Homme      l’interaction internationale en    mécanismes onusiens relatives
                matière des droits de l’homme      au genre

                                                                                       Source : DIDH, 2024

Tableau 14 : Chaîne de résultats sensibles au genre mises en place par le DIDH

2. MINISTERE DE LA JUST ICE
La lutte contre l’exclusion des femmes du système judiciaire est au c ur des préoccupations
du Ministère de la Justice (MJ). Pour y parvenir, le Ministère a acté plusieurs actions d’ordre
juridique, réglementaire, institutionnel et programmatique.         Cette dynamique a été
couronnée par la création au Ministère de l’Observatoire de la Justice sensible au Genre
(OJSG) qui a pour mission de consolider la prise en compte de l’approche genre dans les
pratiques de programmation du Ministère.
2.1. Analyse genre : point de départ pour réussir une programmation
intégrant la dimension genre
La pertinence et la fiabilité d’une programmation intégrant la dimension genre demeure
tributaire de la disponibilité des de donnée et d’analyses mises à jour. Partant de ce constat,
le MJ, à travers l’OJSG, en partenariat avec le CE-BSG, l’ONU Femmes, la Commission
Economique et Sociale pour l'Asie occidentale (ESCWA) et de l’Union Européenne (UE), a
lancé en 2024 les travaux de la réalisation d’une analyse genre du secteur de la justice qui
prend appui sur celle réalisée en 2019.
Cette analyse couvre les principaux intervenants dans secteur de la justice, en l’occurrence,
le MJ, le Conseil Supérieur du Pouvoir Judiciaire (CSPJ) et la Présidence du Ministère Public
(PMP). Elle a pour objectifs d’identifier les enjeux liés à l’égalité entre les femmes et les
hommes en matière d’accès à la justice, d’examiner les rôles et les responsabilités attribués
à l’ensemble des intervenants et d’émettre des recommandations et des orientations pour
un ancrage réussi de la dimension genre dans les pratiques législatives, judiciaires,
programmatiques et en matière de gestion et de valorisation des ressources humaines de
l’administrations judiciaire.
Pour y parvenir, l’étude repose sur l’analyse, d’une part, des dispositions juridiques, des


                                                                                                       27
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


politiques et des stratégies gouvernementales nationales et sectorielles existantes en
matière d’égalité de genre, et d’autre part, des capacités organisationnelles, structurelles et
techniques des acteurs du secteur de la justice. Elle intègre, également, un volet dédié à
l’étude de l’impact genre des lois, des politiques et des dispositions juridiques. Il est à
mentionner que cette analyse genre ne concerne pas que le niveau central, mais elle couvre
aussi le niveau territorial à travers 3 circonscriptions judiciaires près des Cours d’Appel de
Fès, d’Oujda et de Tanger en plus de celui de Rabat.
Dans le même sillage et dans le cadre de son partenariat avec le Fonds des Nations Unies
pour la Population (FNUAP), le MJ a initié la réalisation d’un baromètre de l’accès des femmes
à la justice. Ce baromètre constituerait la plateforme à même de mesurer et assurer le suivi
du niveau d’accès des femmes à la justice au Maroc, moyennant l’identification et la collecte
des données fiables, l’analyse de ces données, l’élaboration des indicateurs pertinents,
l’interprétation des résultats des analyses effectuées et la diffusion de ces analyses à un large
public.
En outre et en partenariat avec l’ONU Femmes et le FNUAP, le MJ prévoit la réalisation d’une
étude de faisabilité pour la mise en place d’un centre de prise en charge intégrée des femmes
victimes de violence (One Stop Center) au niveau de la Région de Rabat-Salé-Kénitra et la
Région de Fès-Meknès. Cette étude vise à fournir des informations clés pour y parvenir,
répondant aux normes de prise en charge minimales des Nations Unies et ce, dans la
perspective de généraliser ces centres de prise en charge intégrée des femmes victimes de
violence sur l’ensemble du territoire national.
2.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie du Dép artement et les plans nationaux pour la
promotion de l’égalité de genre et de l’autonomisation économique des
femmes
Le MJ poursuit son engagement en faveur de la facilitation de l’accès des citoyennes et des
citoyens à la justice et aux services judiciaires sans distinction aucune qui est au c ur de ses
priorités. Ce faisant, le MJ a rehaussé la qualité de ses interventions en la matière, en se
dotant, dès 2022, de l’OJSG qui est désormais la structure institutionnalisée pour consolider
la systématisation de la prise en compte des préoccupations liées à l’égalité de genre dans
la stratégie d’action du Ministère.
En effet, tenant compte de ses missions et attributions, l’OJSC est chargé d’accompagner la
mise en uvre de la stratégie du MJ pour faire progresser, dans le cadre de la compétence
du Ministère, la situation des femmes, des enfants et des groupes à besoins spécifiques et
faciliter leur accès à la justice .De même, l’OJSC contribue au soutien et à l'animation des
cellules d'accompagnement des femmes et des enfants victimes de violences. Il est aussi
impliqué dans l’accompagnement des différentes composantes du MJ pour réussir
l’intégration de la dimension genre dans leurs programmes d’action, le renforcer des
partenariats avec d’autres acteurs dans les domaines liés à la promotion et à la protection
des droits des femmes, des enfants et des groupes à besoins spécifiques et la réalisation des
études et des recherches en lien avec ses domaines de compétence.
Dès lors, l’OJSC a mis en place un plan d’action axé sur le renforcement du suivi de l’accès
des femmes à la justice et la modernisation et la mise à niveau des infrastructures judiciaires
pour répondre aux besoins spécifiques des femmes et des hommes, par le biais de la création
des crèches dans les tribunaux et à l’échelle du siège du Ministère, de la mise à niveau des
cellules de prise en charge des femmes victimes de violence (amélioration des installations
sanitaires, mise en place d’infirmeries…)…
Il est à rappeler que dans le cadre des actions lancées pour assurer le suivi du niveau d’accès
des femmes à la justice, le MJ a lancé, en 2022, la plateforme digitale
« femme.justice.gov.ma » de consultation nationale ayant pour but d’assurer la participation


    28
                                      RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


des citoyennes et des citoyens et des organisations de la société civile aux consultations
liées à la situation et des perspectives de l’accès des femmes à la justice au Maroc.
En parallèle, le MJ poursuit ses efforts en matière de recrutement et de formation des
assistantes et assistants sociaux afin de faciliter l’accès des femmes à la justice (y compris
les femmes amazighes et celles à besoins spécifiques). De plus, le MJ est fermement engagé
dans l’amélioration de l'accès des femmes aux professions juridiques et judiciaires et aux
postes de décision.
Par ailleurs, il est à rappeler qu’en réponses aux Orientations Royales 30, le MJ, le Conseil
Supérieur du Pouvoir Judiciaire et la Présidence du Ministère public ont été chargés de
piloter le processus des consultations menées pour la réforme du code de la famille. A l’issu
de ces consultations, l’Instance chargée de la révision du Code de la famille a remis son
Rapport au Chef du Gouvernement le 30 mars 2024. Poursuivant ce processus, Sa Majesté
le Roi a émis, le 28 juin 2024, ses Directives pour saisir le Conseil Supérieur des Oulémas afin
que cette institution contribue à la réflexion collective sur la révision du code de la famille.
Ainsi, l’ensemble des pratiques législatives, réglementaires, institutionnelles et
programmatiques actées par le MJ pour renforcer la prise en compte de la dimension genre
dans le secteur sont de nature à appuyer la mise en uvre du PGE III et l’atteinte des objectifs
qui lui sont assignés. Les différentes interventions du MJ déclinées par axe du PGE III sont
mises en exergue dans le tableau qui suit.

     Axes du
                                                                         Actions engagée et en perspective
     PGE III
                                          Mise en place d’un programme de formation des femmes fonctionnaires en matière
                                           d’informatique, de TIC et soft-skills ;
                                          Mise en place d’un programme de réintégration sociale des jeunes filles victimes/addiction de
                                           drogues ;
                                          Conception et mise en place d’une plateforme (ALLO TAMYIZ) de déclarations des violences et
                                           des discriminations faites aux femmes lors l’exercice de leurs fonctions soit par les collègues ou
                                           par des personnes tierces ;
                                          Compilation et dissémination des bonnes pratiques pour promouvoir un recrutement exempt de
                                           stéréotypes de genre ;
       Autonomisation et Leadership




                                          Communication autour des cas de jurisprudence / décisions des tribunaux sur des jugements en
                                           faveur de femmes ayant subies des discriminations en milieu du travail ;
                                          Organisation des journées de communication avec les avocats sur les arguments qui peuvent être
                                           soulevés devant le tribunal sur les cas de discrimination à l’égard des femmes ;
                                          Organisation de journées de sensibilisation des femmes employées/fonctionnaires sur leurs
                                           droits ;
                                          Mise en place d’un programme de développement du leadership des femmes fonctionnaires à fort
                                           potentiel pour faciliter leur accès aux postes de responsabilités et aux opportunités de
                                           développement de carrières ;
                                          Identification et révision des dispositions discriminatoires des femmes au niveau des différents
                                           textes législatifs, en priorisant celles ayant le plus d’impact sur l’autonomisation des femmes (code
                                           pénal, code famille, loi sur les peines alternatives) ;
                                          Facilitation de l’accès des femmes à l’assistance juridique (sensibilisation préparation des
                                           demandes…) ;
                                          Renfoncement et diversification des actions de communication autour des services du Fonds de
                                           l’Entraide Familiale (spot de sensibilisation, caravanes, mobilisation des bureaux d’assistance
                                           sociale) ;
                                             Simplification des procédures et réduction du nombre des pièces à fournir pour bénéficier
                                                des avances financières du Fonds de l’Entraide Familiale ;
                                             Digitalisation des services du Fonds de l’Entraide Familiale : plateforme digitale
                                                d’amélioration des services du fonds, de rapprochement auprès des bénéficiaires et

30Sa Majesté le Roi que Dieu l’Assiste a adressé, le 26 septembre 2023, une lettre au Chef de Gouvernement qui
décline les Orientations Royales pour la concrétisation de la réforme du code de la famille voulue par Sa Majesté.
A travers cette Lettre Royale, le Souverain a confié le pilotage du processus accompagnant la préparation de
cette importante réforme au Ministère de la Justice, au Conseil Supérieur du Pouvoir Judiciaire et à la Présidence
du Ministère public.


                                                                                                                                          29
PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


                                                    d’accélération des paiements dues à travers des échanges des données et des documents
                                                    par voie électronique ;
                                                Organisation de l'échange électronique de dossiers pour bénéficier d'avances financières
                                                    dans le cadre du Fonds d’Entraide Familial entre le MJ de la Justice et la CDG ;
                                             Généralisation des crèches au niveau du siège du MJ et des tribunaux (palais de justice, sections
                                              de la famille)…
                                             Organisation d’évènements de communication et de sensibilisation autour des dispositions
                                              législatives en lien avec les droits des femmes et les violences à leur encontre ;
                                             Mise en place du dispositif de protection et d’assistance (type « Téléphone Grave Danger ») pour
                                              lutter efficacement contre les violences faites aux femmes et assurer un soutien et un
    Prévention et Protection des Femmes




                                              accompagnement constant aux victimes les plus vulnérables ;
                                             Conception du portail de l’observatoire de la justice sensible au genre offrant les informations et
                                              services nécessaires pour un meilleur accès de la femme à la justice ;
                                             Création et opérationnalisation de centres pour les femmes et filles victimes des violences et de
                                              la traite des êtres humains ;
                                             Mise en place d’un mécanisme législatif spécial d’accélération de l’exécution des jugements
                                              rendus dans les affaires de violence à l’égard des femmes ;
                                             Renforcement du rôle des bureaux d’assistance sociale dans le domaine de l’accompagnement
                                              social juridique des Femmes Victimes de Violence ;
                                             Amélioration de la lisibilité et de l’efficacité du circuit de prise en charge des Femmes Victimes de
                                              Violence ;
                                             Introduction de dispositions spéciales pour les auteurs de violence à l’encontre des femmes, au
                                              niveau de la loi relative aux peines alternatives (Travaux d'intérêt général, bracelet électronique,
                                              restriction des droits) ;
                                             Mise en place, au niveau des bureaux d’assistance sociale aux tribunaux, d’un service de contrôle
                                              judiciaire et d’enquêtes pour les auteurs de violences faites aux femmes (aide à la prise en
                                              conscience, suivi, accompagnement lors des procédures judiciaires…) ;
                                             Mise en place d’un système d’information permanent d’observation et de collecte de données sur
                                              les femmes victimes de violences prises en charge par les services de la justice.

                                           Contribution à l’amélioration de l’image de la femme (divorcée, âgée, célibataire, résidente à
                                            l’étranger, migrante, détenue…) à travers la promotion des lois en faveur de son insertion sociale ;
                                           Mise en place d’un cursus de formation spécial sur les droits de l’Homme y compris l’égalité entre
                                            les deux sexes, et la lutte contre les discriminations à l’encontre des femmes ;
                                           Identification des textes législatifs et réglementaires en matière de promotion de l’égalité de genre
                                            et des droits des femmes à harmoniser avec les dispositions de la Constitution et les conventions
                                            internationales auxquelles le Maroc a adhéré, et mise en place d’un plan d’action pour leurs
                                            harmonisations ;
                                           Intégration de l’approche genre au niveau de la politique pénale ;
                                           Elaboration et mise à jour annuelle d’un baromètre d’accès des femmes à la justice ;
    Droits et valeurs




                                           Réalisation de sondages (ou bornes de sondage au niveau des tribunaux) d’évaluation du taux de
                                            satisfaction des femmes par rapport aux services de la justice ;
                                           Réalisation d’études spécifiques (la criminologie au féminin, l’addiction aux drogues, femmes et
                                            filles victimes la traite des êtres humains, l’accessibilité des femmes aux infrastructures) ;
                                           Intégration de l’approche genre au niveau des infrastructures de la justice (crèches, cellules de
                                            prise en charge des femmes et des enfants victimes de violences, espaces bleus pour enfants,
                                            sanitaires, infirmeries) ;
                                           Généralisation des tribunaux de la famille ;
                                           Renfoncement de l’accès à la justice pour la femme amazighe, de montagne et du milieu rural à
                                            travers la généralisation des centres judicaires ;
                                           Intégration au niveau de la loi relative au code pénal et la loi relative aux peines alternatives de
                                            dispositions spéciales pour les femmes en situation difficile (femmes mariées, enceintes, à charge
                                            d’enfants ou de personnes dépendantes…) ;
                                           Opérationnalisation des bureaux d’assistance sociale telle que stipulée au niveau de l’article 50 de
                                            la loi n° 38.15 relative à l’organisation juridique ;
                                           Opérationnalisation de l’Observatoire de la Justice Sensible au Genre.

                                                                                                                                Source : MJ, 2024

Tableau 15 : Implications du Ministère de la Justice dans le cadre de la mise en
                                  uvre du PGE III




   30
                            RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


2.3. Chaîne de résultats sensibles au genre : application de la démarche
performance sensible au genre
En ligne avec les dispositions de la circulaire du Chef du Gouvernement (n°4/2024) relative
à l’établissement des propositions de Programmation Budgétaire Triennale assortie des
objectifs et des indicateurs de performance au titre de la période 2025-2027, le MJ a
développé une chaîne de résultats sensibles au genre qui couvre 2 de ses programmes
budgétaires, en l’occurrence, les programmes relatifs au soutien et pilotage et au
renforcement des droits et des libertés.
La dimension genre est explicitement prise en compte dans la chaine de résultat du MJ, à
travers plusieurs objectifs, indicateurs et sous-indicateurs de performance sensibles au genre
qui reflètent les domaines et les leviers d’action mobilisés par le Ministère pour la promotion
de l’égalité de genre et la protection des droits des femmes.
 Ainsi, le programme relatif au soutien et au pilotage est associé à un objectif sensible au
genre portant sur le renforcement des compétences et le soutien de l'égalité des sexes. Le
degré de réalisation de cet objectif est approché d’une part, par deux sous indicateurs
intégrant la dimension genre en lien avec le taux d’accès des femmes à la formation (57% en
2023) et à la formation qualifiante pour accéder aux postes de responsabilités.
Quant au programme relatif au renforcement des droits et des libertés visant, entre autres,
la protection des droits de la femme et de l’enfant, le suivi de sa performance est assuré par
2 indicateurs de performance sensibles au genre à savoir : le taux des cellules de prise en
charge des femmes et d’enfants équipées qui a avoisiné 91% en 2023 et le taux de couverture
des sections de la famille par les espaces d’enfants qui ne dépasse pas 26% au titre de l’année
2023.

                                                                                                               Réalisations    LF
Programmes                          Objectifs              Indicateurs                 Sous indicateurs
                                                                                                                 2023         2024
                                                                                  Taux       d'accès     des
                                                                                  fonctionnaires femmes à la       57%        55%
                                                     Taux    d’accès     à   la   formation
                                                     formation                    Taux       d'accès     des
      Soutien et pilotage




                                                                                  fonctionnaires hommes à la       65%        55%
                                                                                  formation
                              Renforcer           les
                                                                                  Nombre de fonctionnaires
                              compétences          et
                                                                                  femmes bénéficiant d’une
                              soutenir l'égalité des Nombre                 de
                                                                                  formation qualifiante pour       123        75
                              sexes                   fonctionnaires
                                                                                  occuper les postes de
                                                      bénéficiaires      d'une
                                                                                  responsabilité
                                                      formation
                                                                                  Nombre de fonctionnaires
                                                      qualifiante pour occuper
                                                                                  hommes bénéficiant d’une
                                                      les       postes      de
                                                                                  formation qualifiante pour       266        75
                                                      responsabilité
                                                                                  occuper les postes de
                                                                                  responsabilité
                                                     Taux des cellules de
 Renforcemen
  t des droits




                                                     prise en charge des
    libertés




                              Protéger les droits de femmes et d’enfants                                           91%        89%
     et des




                              la femme et de équipées
                              l’enfant               Taux de couverture des
                                                     sections de la famille par                                    26%        26%
                                                     les espaces d’enfants
                                                                                                                    Source : MJ, 2024

  Tableau 16 : Chaîne de résultats sensibles au ge nre mise en place par le MJ




                                                                                                                                   31
     PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


2.4. Progrès législatif, réglementaire et institutionnel en faveur de la
promotion de l’égalité de genre
Dans le cadre de la dynamique lancée par le MJ pour la réforme du code pénal, l’année 2024
est marquée par l’adoption par le Conseil du Gouvernement, tenu le 29 août, du projet de loi
03-23 modifiant et complétant la loi 22-01 portant code de procédure pénale. Ce projet de
loi aspire à renforcer les garanties d'un procès équitable, à simplifier les procédures pénales
et à développer les mécanismes de lutte contre la criminalité, à moderniser les mécanismes
de justice pénale et améliorer leur efficacité, à protéger les droits des victimes à toutes les
étapes de la procédure publique, à renforcer la protection des mineurs et la rationalisation
de la détention préventive….

3. DELEGATION GENERALE        A L’ADMINISTRATION
PENITENTIAIRE ET A L A REINSERTION
La Délégation Générale à l’Administration Pénitentiaire et à la Réinsertion (DGAPR) ne cesse
de déployer les efforts nécessaires en vue de concrétiser les ambitions portées par sa
stratégie d’actions à l’horizon 2026 qui prend en compte les préoccupations liées à la
promotion de l’égalité de genre et à l’autonomisation des femmes.
3.1. Analyse genre : point de départ pour réussir une programmation
intégrant la dimension genre
Même si la DGAPR ne dispose à ce jour que d’une seule analyse genre, réalisée entre 2017 et
2018, la Délégation a, néanmoins, systématisé la prise en compte de la dimension genre dans
son système d’information lui permettant de produire des diagnostics et des rapports de
suivi de ses activités, à l’instar de ses rapports d’activité annuels, qui intègrent des analyses
sur l’évolution de l’accès des femmes aux services pénitenciers et de réinsertion31. Ces
rapports et analyses sont de nature à contribuer au suivi et à l’évaluation sous le prisme genre
de la stratégie d’action de la Délégation et ainsi à y consolider la prise en compte des
questions liées à la réduction des inégalités de genre et à la protection des droits des femmes
incarcérées et des femmes fonctionnaires de la Délégation.
3.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie de la DGAPR et les plans nationaux pour la
promotion de l’égalité et d’autonomisa tion économique des femmes
Le plan stratégique de la DGAPR au titre de la période 2022-2026 repose sur 5 axes dont un
relatif à la prise en compte de l’approche genre et la dimension environnementale dans la
gestion pénitentiaire. A cet égard, la Délégation           uvre, au quotidien, pour que les
préoccupations liées à l’égalité de genre et la protection des droits des femmes soient
intégrées dans les projets et les activités visant l’amélioration des conditions de détention, la
réinsertion, le renforcement de la sécurité et la lutte contre la violence. Dans le même cadre,
la Délégation s’est engagée dans une dynamique à même de promouvoir l’égalité de genre
dans la gestion et la valorisation de ses Ressources Humaines.
La forte implication de la DGAPR dans une diversité de projets pour assurer la réinsertion et
la protection des détenues s’aligne parfaitement sur les axes d’intervention du PGE III (2023-
2026), particulièrement, l’axe I portant sur l’autonomisation et leadership des femmes et l’axe
II relatif à la protection et le bien-être.


31Le Rapport d’activité de la DGAPR au titre de l’année 2023 indique que malgré une faible présence dans la
population pénitentiaire (2,5% du total des personnes incarcérées), le nombre de femmes détenues a, toutefois,
augmenté à un rythme plus élevé (7,8%) que celui des détenus homme (5,55%) entre 2022 et 2023, ce qui
représente les deux pourcentages les plus élevés, enregistrés au cours des dix dernières années.




        32
                                                          RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


3.3. Chaîne de résultats sensibles au genre mise en place par le
Département : application de la démarche performance sensible au
genre
La prise en compte de la dimension genre dans le plan stratégique de la DGAPR s’est traduite
par l’adoption d’une chaine de résultats qui intègre explicitement cette dimension,
essentiellement, au niveau des sous indicateurs de performance.
3.3.1. Chaîne de résultats sensibles au genre mise en place par le Département
Conformément à la circulaire du Chef du Gouvernement (n°4/2024) en date du 15 mars 2024
relative à l’établissement des propositions de Programmation Budgétaire Triennale assortie
des objectifs et des indicateurs de performance au titre de la période 2025-2027, la DGAPR
a développé une chaîne de résultat sensible au genre associée à son programme budgétaire
relatif à la politique pénitentiaire de réinsertion des détenu.e.s. La dimension genre est
explicitement prise en compte, essentiellement, dans les sous-indicateurs de performance
conçus pour assurer le suivi du degré d’atteinte des objectifs escomptés en termes
d’amélioration des conditions de détention, de promotion de la réinsertion des détenu.e.s et
de renforcement des capacités de l’administration pénitentiaire. Pour ce qui est du suivi du
niveau de concrétisation des objectifs fixés en matière d’intégration des aspects genre et de
la dimension environnementale dans la gestion pénitentiaire, il est assuré par un seul
indicateur de performance sensible au genre qui renseigne sur le taux d’accès des femmes
fonctionnaires de la DGAPR aux postes de responsabilités (voir tableau ci-dessous).
                                                                                                                                       Réalisations     LF
Programme                                                        Objectifs          Indicateurs            Sous-indicateurs
                                                                                                                                          2023         2024
                                                                                 Taux                Taux     d’occupation     des
                                                                                                     établissements pénitentiaires        163%         159%
                                                                                 d’occupation des
                                                                                                     - Hommes
                                                                                 établissements
                                                                                                     Taux     d’occupation     des
                                                             Amélioration des    pénitentiaires
                                                                                                     établissements                       80%          90%
                                                              conditions de      selon le sexe       pénitentiaires-Femmes
                                                                détention
                                                                                 Superficie          Superficie habitable moyenne
                                                                                                                                         1,69 m2      1,73 m2
     Politique Pénitentiaire de Réinsertion des Détenus




                                                                                 habitable           / détenu- Hommes
                                                                                 moyenne      par    Superficie habitable moyenne
                                                                                                                                         3,61 m2      3,33 m2
                                                                                 détenu              / détenu- Femmes
                                                                                                     Taux d’accès des détenus à
                                                                                 Taux d’accès des                                          98%        95,45%
                                                                                                     l’enseignement - Hommes
                                                                                 détenu.e.s     à
                                                                                                     Taux d’accès des détenus à
                                                                                 l’enseignement                                           99%         97,93%
                                                                                                     l’enseignement : Femmes
                                                                                                     Taux d’accès des détenus à la
                                                                                 Taux d’accès des    formation     professionnelle -     88,64%       94,98%
                                                                                 détenu.e.s à la     Hommes
                                                                                 formation           Taux d’accès des détenus à la
                                                                                 professionnelle     formation     professionnelle -     91,04%       93,69%
                                                              Promotion des                          Femmes
                                                              programmes de                          Taux d’accès des détenus à la
                                                                                 Taux d’accès des
                                                              préparation à la                       formation      artistique    et     10,07%        9,5%
                                                                                 détenu.e.s à la
                                                                réinsertion                          artisanale - Hommes
                                                                                 formation
                                                                                                     Taux d’accès des détenus à la
                                                                                 artistique    et
                                                                                                     formation      artistique    et     31,33%        25%
                                                                                 artisanale
                                                                                                     artisanale : Femmes
                                                                                                     Taux d’accès des détenus
                                                                                                     analphabètes              aux
                                                                                 Taux d’accès des                                        95,71%       94,5%
                                                                                                     programmes
                                                                                 détenu.e.s
                                                                                                     d’alphabétisation - Hommes
                                                                                 analphabètes aux
                                                                                                     Taux d’accès des détenues
                                                                                 programmes
                                                                                                     analphabètes              aux
                                                                                 d’alphabétisation                                       97,74%        93%
                                                                                                     programmes
                                                                                                     d’alphabétisation - Femmes




                                                                                                                                                        33
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


                                  Taux            de    Taux     de    fonctionnaires
                                  fonctionnaires        bénéficiaires de la formation    32%          48%
              Renforcement des
                                  bénéficiaires de la   continue-Hommes
                 capacités de
                                  formation             Taux     de    fonctionnaires
               l’administration
                                  continue selon le     bénéficiaires de la formation    40%          55%
                                  sexe                  continue-Femmes
               Intégration des    Taux d’accès des
              aspects Genre et    femmes         aux
                                                                                         7,14%        9,2%
               de la dimension    postes          de
              environnementale    responsabilités
                                                                                        Source : DGAPR 2024

Tableau 17 : Chaîne de résultats sensibles au genre mise en place par la DGAPR
3.3.2. Actions en faveur de la promotion d’égalité de genre non intégrées dans
les chaînes de résultats sensibles au genre
Il est à noter que la chaîne de résultats susmentionnée n’intègre pas plusieurs projets et
actions entrepris par la DGAPR au service de la promotion de l’égalité de genre et de la
protection des droits des femmes. Les projets les plus marquants en la matière portent sur
ce qui suit :
    Organisation en 2023 de 34 formations sur les droits de l'Homme, la prévention de la
     torture et d'autres formes de traitements cruels et dégradants au profit de 139
     fonctionnaires hommes et femmes. Il est à noter, à cet égard, que près de 1.251
     nouvelles recrues ont bénéficié de la même formation dans le cadre de leur formation
     de base. Ces actions de formations reflètent l’engagement de la DGAPR à renforcer
     davantage l’application de l'approche des droits de l'Homme dans sa stratégie
     d’action ;
    Lancement, dans le cadre de la stratégie nationale en santé pénitentiaire au titre de la
     période de 2022 à 2026, d’un programme à multiples composantes, en partenariat
     avec l’e FNUAP, visant la promotion de l’accès aux services de Santé Sexuelle et
     Reproductive (SSR), selon une approche promouvant l’égalité de genre. Ce
     programme aligné sur la Stratégie Nationale de Santé Sexuelle et Reproductive (2021-
     2030) a pour objectif de renforcer d’une part les capacités des professionnels de santé
     et d’autres part celles des détenu(e)s en se basant, entre autres, sur l’approche de
     l’éducation par les pairs en plus de leur permettre l’accès à des prestations sanitaires
     de qualité. Depuis le lancement de ce programme, des ateliers de formation sur la
     santé sexuelle et reproductive ont été organisés au profit de 292 éducatrices paires
     sélectionnées parmi les détenues dans 11 prisons. Ces éducatrices paires ont, à leur
     tour, sensibilisé 696 détenues ;
    Initiation, en 2023, par la DGAPR avec l’appui du FNUAP, d’une dynamique de prise
       en charge des femmes victimes de violence qui est adaptée au milieu carcéral,
       moyennant l’aménagement des unités pilotes pour une prise en charge intégrée
       médico-socio-psychologique de qualité, visant à leur offrir un soutien et des services
       adaptés.




    34
         RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


4. MINISTERE                 DES       HABOUS             ET       DES       AFFAIRES
ISLAMIQUES
Le Ministère des Habous et des Affaires Islamiques (MHAI) poursuit son engagement en
faveur de l’intégration de la dimension genre dans ses programmes d’actions et dans sa
chaîne de résultats et ce, conformément aux dispositions de la LOF et de celles des circulaires
du chef de Gouvernement en la matière.
4.1. Analyse genre : point de départ pour réussir une programmation
intégrant la dimension genre
A ce jour, le MHAI ne dispose pas encore d’analyse genre de ses domaines d’intervention. Ce
faisant, les actions entreprises par le Ministère pour promouvoir l’égalité entre les femmes et
les hommes et protéger les droits des femmes se réfèrent à la stratégie du Ministère qui,
toutefois, n’inclut pas des objectifs clairs en termes de réduction des inégalités de genre.
4.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité et d’autonomisation économi que des femmes
A travers les programmes mis en place, en l’occurrence ceux relatifs à l’encadrement
religieux, à l’enseignement traditionnel, à l'alphabétisation dans les mosquées et à la
formation continue, le MHAI est activement engagé à rendre visible l’apport des femmes au
développement du champ religieux, à renforcer leur autonomisation en valorisant leur capital
humain et à protéger leurs droits par la sensibilisation et la lutte contre la violence fondée
sur le genre. De par cet engagement, le MHAI est une partie prenante du PGE III (2023-2026)
4.3. Chaîne de résultats sensibles au genre : application de la démarche
performance sensible au genre
Conformément à la circulaire du Chef du Gouvernement (n°4/2024) relative à
l’établissement des propositions de Programmation Budgétaire Triennale assortie des
objectifs et des indicateurs de performance au titre de la période 2025-2027, le MHAI a
développé une chaine de résultats sensibles au genre qui couvre trois programmes
budgétaires à savoir : les programmes relatifs à l’encadrement religieux, aux lieux d’exercice
de culte islamique et lieux culturels et à la formation et l’enseignement religieux.
4.3.1. Chaîne de résultats sensibles au genre mise en place par le département
La chaîne de résultats sensibles au genre adoptée par le MHA (voir tableau ci-dessous) est
marquée par l’intégration d’un nouveau sous indicateurs sensible au genre qui mesure le taux
de satisfaction des besoins des femmes en salles de prière et qui renseigne sur le niveau de
réalisation de l’objectif portant sur la satisfaction de manière équitable des besoins de la
population en lieux d’exercice de culte islamique et en lieux culturels. Ce dernier est lié au
programme dédié aux lieux d’exercice de culte islamique et lieux culturels.
De même, cette chaîne de résultat intègre deux indicateurs de performance sensibles au
genre. Le premier qui mesure le niveau de concrétisation de l’objectif d’amélioration de la
situation sanitaire des préposés religieux et leur ayant droit et ce, en mesurant le taux des
conjointes, des veuves et des filles des préposés religieux bénéficiant du régime de la
couverture médicale qui a atteint 49,39% en 2023.
Pour ce qui de l’indicateur de performance lié au programme consacré à la formation et à
l’enseignement religieux et qui mesure le taux des morchidates et morchidines bénéficiant
du programme de formation, même si son intitulé est gendérisé, le fait que cet indicateur
n’apporte pas d’information claire par rapport à la part des Morchidates bénéficiant de la
formation par rapport aux Morchidines porte préjudice à sa pertinence quant aux exigences
de l’application de la démarche de performance sensible au genre.

                                                                                            35
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025



                                                                              Sous-           Réalisations     LF
      Programmes           Objectifs                Indicateurs
                                                                            indicateurs          2023         2024
                      Améliorer         la   Taux des conjointes, des
                      situation sanitaire    veuves et des filles des
      Encadrement                                                                                            49,66
                      des préposés           préposés         religieux                         49,39 %
        religieux                                                                                              %
                      religieux et leur      bénéficiant du régime de
                      ayant droit            la couverture médicale
                      Satisfaire       de
                      manière équitable                                   Taux           de
  Lieux d’exercice
                      les besoins de la                                   satisfaction des
      de culte                               Taux de construction de
                      population en lieux                                 besoins       des
 islamique et lieux                          nouvelles mosquées
                      d’exercice de culte                                 femmes en
      culturels
                      islamique et en                                     salles de prière
                      lieux culturels
                                             Taux des morchidates et
      Formation et    Mettre à niveau et
                                             morchidines bénéficiant
      enseignement    former           les                                                          -        92,8%
                                             du     programme     de
        religieux     préposés religieux
                                             formation
                                                                                                Source : MHAI, 2024.

     Tableau 18 : Chaîne de résultats sensibles au genre mise en place par le MHAI
4.3.2. Actions en faveur de la promotion d'égalité de genre non intégrées dans
les chaînes de résultats sensibles au genre
En plus des interventions mises en exergue dans sa chaine de résultats sensibles au genre, le
MHAI uvre à la promotion de l’égalité de genre et des droits des femmes à travers plusieurs
programmes et initiatives à savoir :
 Programme d’alphabétisation dans les mosquées du Royaume32 : la part des femmes dans
  le total de bénéficiaires de ce programme a atteint au titre de l’année scolaire 2022-203
  près de 89% des bénéficiaires. Le taux de féminisation du corps pédagogique chargé du
  programme s’est établi, pour sa part, à 85% au cours de la même période ;
 Programme de la formation des Imams Morchidines et morchidates33 : le nombre des
  morchidates lauréates de l’Institut Mohamed VI de la formation des Imams morchidines et
  morchidates s’est situé, au titre de l’année 2024, à 1.515 morchidates, soit 33,1% du total
  des lauréats ;
 Programme de l’enseignement traditionnel34 : la part des étudiantes dans les écoles
  d'enseignement traditionnel, tous cycles confondus, est passé de 13% au titre de l'année
  2011-2012 à 25,5% au titre de l'année scolaire 2022-2023. Quant aux taux de féminisation
  du corps professoral, des cadres et des agents administratifs chargés de l’exécution du
  programme, ils s'élèvent respectivement à 15,12%, à 9,36% et à 42,63%. Il est à noter qu’il
  a été procédé, dans le cadre de ce programme, à la révision des programmes et curricula
  scolaires, tous cycles confondus, pour intégrer dans les nouveaux manuels scolaires de
  l’enseignement traditionnel les éléments de la charia qui prônent la lutte contre les
  violences faites aux femmes.
 Poursuite des efforts de sensibilisation pour la lutte contre toutes les formes de violence
  fondées sur le genre, à travers les programmes audio-visuels en collaboration avec les
  médias audio-visuels publics.




32 Les détails relatifs aux objectifs du programme ainsi qu’à ses parties prenantes sont présentés dans l’édition
2023 du Rapport sur le budget axé sur les résultats tenant compte de l’aspect genre.
33 Ibid.
34 Ibid




       36
           RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


5. MINISTERE DE LA SOLIDARITE ,                                                   DE       L’INSERTION
SOCIALE ET DE LA FAMILLE
De par ses missions et attributions, le Ministère de la Solidarité, de l’Insertion Sociale et de la
Famille (MSISF) est un des acteurs clés de la dynamique actuelle que connait notre pays
visant l’édification d’un Etat Social qui promeut l’égalité de genre et la protection des droits
des femmes. Le MSISF assure, à cet effet, la coordination et le suivi de la mise en uvre du
Plan Gouvernemental pour l’Egalité dans sa troisième édition (PGE III) qui couvre la période
de 2023 à 2026 et qui implique une multiplicité de départements ministériels et d’institutions
publiques et privées.
5.1. Analyse genre : Point de départ pour réussir une programmation
intégrant la dimension genre
La conception du PGE III (2023-2026) s’est enrichie des conclusions et des orientations
issues de l’analyse genre qui a été effectuée à cet égard, ainsi que des enseignements tirés
de la mise en uvre des PGE I et PGE II.
5.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité et d’autonomisa tion économique des femmes
La troisième édition du PGE (2023-2026) est articulée autour de 3 axes qui s’alignent
parfaitement sur la stratégie « GISSR » du Ministère au titre de la période 2022-202535. Ces
axes portent sur l’autonomisation et leadership, la protection et bien être ainsi que les droits
et valeurs. De ses axes découlent trois programmes d’action à savoir : le programme
d’autonomisation économique et leadership, celui relatif à la prévention et à la protection
pour l’instauration d’un environnement protecteur des femmes et le programme de
promotion des droits des femmes et de lutte contre les discriminations et les stéréotypes. Le
PGE III intègre, également, un dispositif de pilotage et de suivi et d’évaluation, ainsi qu’un
système de gouvernance central et territorial.
Il est à rappeler que le pilotage du PGE III est assuré par la Commission Nationale pour
l'Egalité des Sexes et l'autonomisation des femmes (CNESAF)36, créée en 2022. La deuxième
réunion de la CNESAF, tenue le 25 mars 2024, a été présidée par M. le Chef du Gouvernement
qui a appelé les parties prenantes du PGE à finaliser l’élaboration du système de gouvernance
et des plans de financement des mesures qui leur incombent et ce, dans la perspective de
présenter le PGE III à l’adoption du Conseil de Gouvernement. Dans le même sillage, la
circulaire du Chef du Gouvernement (n°4/2024) relative à l’établissement des propositions
de Programmation Budgétaire Triennale assortie des objectifs et des indicateurs de
performance au titre de la période 2025-2027 a appelé à une implication active des
départements ministériels dans la mise en uvre du PGE III et à prendre en compte leurs
engagements dans le cadre dudit Plan dans leur programmation budgétaire.
En plus du PGE III, le MSISF a acté, dans le cadre de la stratégie GISSR, de nouveaux services
sociaux pour les personnes vulnérables, dont les femmes en situation difficile. Ces services
s'appuient sur la digitalisation comme levier de modernisation des interventions et de

35 Pour plus de détails relatifs au processus d’élaboration et au contenu du PGE III et à la stratégie GISSR, voir
l’édition 2024 du Rapport sur le Budget axé sur les Résultats tenant compte de l’aspect Genre.
36 La Commission nationale de l'égalité de genre et l’autonomisation de la femme créée en juin 2022 offre un

cadre garantissant l'harmonie et la convergence des différentes initiatives selon une nouvelle approche d’action
et de gouvernance fondée sur la démarche participative qui implique l’ensemble des parties prenantes actives
dans les domaines liés à la promotion de l’égalité de genre. Elle est composée de 3 instances de gouvernance à
savoir : une commission nationale présidée par le Chef du Gouvernement, un comité technique présidé par Mme.
La Ministre de la Solidarité, de l’insertion Sociale et de la famille ainsi que des groupes de travail thématiques. La
première réunion du CNESAF s’est tenue, sous la présidence de M. le Chef du Gouvernement, le mois de mars
2023.


                                                                                                                  37
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


facilitation de l'accès aux services offerts aux femmes victimes de violence ainsi qu’aux
services d'autonomisation par le biais de la plateforme digitale « GISSR AMANE » et les
plateformes « GAWA » dédiées aux actions de renforcement des capacités. Il est à noter que
le recours à ces plateformes de digitalisation a bénéficié à près de 84.000 femmes.
5.3. Chaîne de résultats sensibles au genre : application de la démarche
performance sensible au genre
Conformément aux missions et attributions du MSISF et aux dispositions de la circulaire du
Chef du Gouvernement (n°4/2024) en date du 15 mars 2024 relative à l’établissement des
propositions de Programmation Budgétaire Triennale assortie des objectifs et des
indicateurs de performance au titre de la période 2025-2027, le Ministère a développé une
chaîne de résultats sensibles au genre37 qui couvre l’ensemble de ses programmes à savoir :
le programme relatif au pilotage et Support, celui portant sur l’égalité entre les femmes et
les hommes, l’autonomisation et leadership et la promotion des droits et le programme lié
au développement social, à la promotion des droits des personnes en situation de handicap
et à la protection de la famille, de l'enfance et des personnes âgées. Ces programmes sont
associés à plusieurs objectifs et indicateurs de performance sensibles au genre (voir le
tableau ci-dessous).

                                                                                                                                             LF
                                                                                                                             Réalisations
Programmes                                           Objectifs                  Indicateurs              Sous indicateurs                   202
                                                                                                                                2023
                                                                                                                                             4
                                                                                                        Taux d’accès   des
                                                                                                        femmes    à     la     41,01%       48%
                                               Institutionnaliser une Taux d’accès à la                 formation
           Pilotage et
            support




                                               administration          formation                        Taux d’accès   des
                                               publique      équitable                                  hommes     à    la     41,49%       42%
                                               basée sur un système                                     formation
                                               de compétences          Taux d’accès des femmes
                                                                       aux         postes          de                            35%        45%
                                                                       responsabilité et assimilés
                                                                       Taux de mise en           uvre
                                                                       des     engagements         du
                                                                       Ministère au niveau du                                    25%        50%
                                                                       plan gouvernemental de
     Egalité entre les femmes et les hommes,




                                                                       l’égalité
       leadership et promotion des droits




                                                                       Taux de territorialisation
                                                                       des      programmes         de                           100%        70%
                                                                       l’égalité
                autonomisation et




                                               Concevoir et piloter la Nombre        de       centres
                                               mise en       uvre du d'écoute et d’orientation
                                               plan gouvernemental des femmes victimes de                                        79         85
                                               pour l’égalité          violence ayant développé
                                                                       des services de qualité
                                                                       Taux de couverture au
                                                                       niveau      territorial    des
                                                                       espaces multifonctionnels
                                                                                                                                            100
                                                                       pour les femmes institués                                100%
                                                                                                                                             %
                                                                       et opérationnels selon les
                                                                       cahiers de charges y
                                                                       afférents
                                               Renforcer               Taux      d’exécution      des
                                               l’autonomisation        mesures programmées au
                                                                                                                                 25%        60%
                                               économique          des projet         «        Maroc
                                               femmes et des filles    autonomisation »




37   Ladite chaîne de résultats sensibles au genre est en cours de finalisation.


                   38
                                                                                          RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


                                                                                                                                                     Nombre de projets-
                                                                                                                                                     associations destinés
   Développement social, promotion des droits des personnes en situation de handicap et

                                                                                                                                                     à      l'autonomisation
                                                                                            Renforcer            la
                                                                                                                      Nombre       de     projets    des femmes et des
                                                                                            participation      des                                                                  -          50
                                                                                                                      associatifs appuyés            filles appuyés par le
                                                                                            associations,         y
                                                                                                                                                     Ministère      dans   le
                                                                                            compris             les
                                                                                                                                                     cadre de chacune des
                                                                                            associations       des
                                                                                                                                                     politiques publiques
              protection de la famille, de l'enfance et des personnes âgées




                                                                                            femmes, à la mise en
                                                                                                                                                     Nombre
                                                                                              uvre des politiques
                                                                                                                                                     d´associations
                                                                                            publiques conduites
                                                                                                                      Nombre       des    acteurs    inscrites     dans   un
                                                                                            par le Ministère et au
                                                                                                                      associatifs bénéficiaires du   processus            de
                                                                                            ciblage des femmes                                                                      -          40
                                                                                                                      renforcement             des   renforcement         de
                                                                                            et des filles
                                                                                                                      capacités                      capacités en matière
                                                                                                                                                     de       ciblage    des
                                                                                                                                                     femmes et des filles
                                                                                            Concevoir,
                                                                                                                      Nombre d'acteurs ayant
                                                                                            coordonner et mettre
                                                                                                                      introduit les normes de
                                                                                            en        uvre    des
                                                                                                                      qualité dans les structures
                                                                                            politiques publiques
                                                                                                                      et pour les prestations
                                                                                            efficaces    dans   le
                                                                                                                      destinées aux enfants et à                                    -          10
                                                                                            domaine       de    la
                                                                                                                      leurs familles en tenant
                                                                                            protection         de
                                                                                                                      compte      des     besoins
                                                                                            l’enfance en tenant
                                                                                                                      spécifiques des garçons et
                                                                                            compte la dimension
                                                                                                                      des filles
                                                                                            genre
                                                                                                                   Taux d´instauration de la
                                                                                                                   démarche      qualité    au
                                                                                            Protéger            et niveau des centres de
                                                                                            promouvoir la famille protection sociale des
                                                                                                                                                                                  30%          5%
                                                                                            et    les   personnes personnes âgées en tenant
                                                                                            âgées                  compte      des     besoins
                                                                                                                   spécifiques des femmes et
                                                                                                                   des hommes âgés
                                                                                            Promouvoir les droits
                                                                                            des personnes en
                                                                                            situation de handicap
                                                                                            en tenant compte des
                                                                                            besoins    spécifiques
                                                                                            des femmes et des
                                                                                            hommes
                                                                                                                                                                                Source : MSISF, 2024

Tableau 19 : Chaîne de résultats sensibles au genre mise en place par le MSISF
La chaîne de résultats sensibles au genre établie par le MSISF fait état d’un taux de réalisation
des engagements du Ministère inscrits dans le cadre du PGE III qui avoisine 25% au titre de
l’année 2023. Les détails relatifs aux mesures et actions entreprises par le Ministère dans ce
sens sont déclinés comme suit :




                                                                                                                                                                                                 39
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


 Axes du
                                                Programme                              Actions entreprises et prévues
 PGE III
 Autonomisa




                                                                      - Signature de 12 conventions de partenariat impliquant les
  leadership
    tion et
    Axe 1 :




                                                                        différents acteurs territoriaux pour mettre en       uvre le
                                              Autonomisation
                                                                        « programme d'accompagnement pour renforcer la qualification
                                         économique et leadership :
                                                                        et l'autonomisation économique des femmes porteuses de projets
                                                                        » au profit de 36.000 femmes porteuses de projet.

                                                                      - Création de 105 Etablissements multifonctionnels pour la prise en
                                                                        charge des femmes victimes de violence (EMF) offrant des
                                                                        services     d'écoute,     d'orientation,   d’hébergement,      dont
                                                                        l'hébergement d'urgence et d'accompagnement des femmes dont
                                                                        celles victimes de violences. Près de 79 centres d'écoute ont été
                                                                        appuyés au cours de l’année 2023 ;
       Axe 2 : Protection et Bien être




                                                                      - Lancement de la 21ème campagne de lutte contre la violence
                                                                        l’égard des femmes par le MSISF en partenariat avec les
                                                                        Départements ministériels et la société civile et avec l'appui de
                                                                        partenaires techniques et financiers ;
                                         Protection et prévention :   - Poursuite de l’apport d'appui à la plateforme "Kolona Maak" pour
                                            environnement sans          le signalement l'écoute, le soutien et l’orientation des femmes et
                                           violence à l’égard des       des filles en situation de vulnérabilité ;
                                                  femmes              - Mise en place de la plateforme Digitale « GISSR AMANE » pour la
                                                                        prise en charge des Femmes Victimes de Violence et le
                                                                        renforcement du maillage et de la coordination entre le MSISF,
                                                                        l’Entraide Nationale, les établissements multifonctionnels et les
                                                                        centres d'écoute ;
                                                                      - Réalisation d'une étude portant sur le suivi de la mise en uvre
                                                                        de la loi 103-13 relative à la lutte contre les violences faites aux
                                                                        femmes et de son décret d'application et opérationnalisation de
                                                                        la cellule de prise en charge des femmes victimes de violences
                                                                        créée au niveau du MSISF, en application de l'article 10 de la loi
                                                                        103-13.
                                                                      - Suivi et mise en uvre des recommandations de la Commission
                                                                        de la CEDEF (CEDAW) ;
   Axe 3 : Droits et




                                                                      - Suivi et mise en uvre des recommandations du système onusien
                                                                        en matière de réduction des inégalités de genre et de protection
                                          Promotion des droits et
      Valeurs




                                                                        des droits des femmes ;
                                              lutte contre les
                                                                      - Suivi et mise en uvre des engagements du MSISF dans le cadre
                                           discriminations et les
                                                                        de la résolution 1325 du programme des Nations Unies sur les
                                                stéréotypes
                                                                        femmes, la paix et la sécurité ;
                                                                      - Elaboration d’un plan de communication autour de l'image de la
                                                                        femme dans les médias et d’un autre plan de communication
                                                                        traitant la masculinité positive.
                                                                                                                        Source : MSISF, 2024

Tableau 20 : Déclinaison des mesures et actions entreprises pat le MSISF dans
          le cadre de la mise en   uvre du déploiement du PGE III
Il y a lieu de noter qu’en plus des réalisations des programmes et projets pris en compte dans
la chaîne de résultats sensible au genre du MSISF, l’année 2023 a été marquée par une
mobilisation exceptionnelle du Ministère en faveur des victimes du Séisme d’Al Haouz. Le
Ministère a alloué, à cet égard, une enveloppe budgétaire de 32,7 millions de dirhams pour
financer diverses actions. Il s’agit, principalement, des actions suivantes :
   La mobilisation de plus de 400 assistants sociaux et psychologues pour assurer
    l’assistance sociale et l’accompagnement psychologique au profit des personnes
    touchées par le séisme, en apportant un intérêt particulier aux femmes et aux enfants ;
   L’octroi des produits alimentaires (6.507 paniers), des vêtements (35.602 unités), des
    couvertures (20.161 couvertures) et des meubles (17.221 unités) ;




          40
         RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


   L’octroi de 3.100 tentes, de générateurs électriques, de matériel d’éclairage, d’ustensiles
    de cuisine et de tentes en plastique ;
   La mobilisation de 1.808 unités d’assistance sociale dédiées à l’accompagnement des
    personnes en situation de handicap ;


Ainsi, les interventions du MSISF se sont reposées sur différentes opérations d’assistance
sociale visant notamment l’accompagnement psychologique des populations touchées par
le séisme. L’octroi des aides en nature au niveau de 89 provinces les plus touchées par le
séisme a profité à 42.204 familles. Près de 46.744 familles ont, pour leur part, bénéficié de
l’appui sociale et 15.861 familles ont bénéficié de l’accompagnement psychologique.

6. MINISTERE DE L’ECONOMIE ET DES FINA NCES
La dynamique qui accompagne l’implémentation au Maroc de la BSG et l’appropriation
collective des enjeux y afférents, pilotée par le Ministère de l’Economie et des Finances, ne
cesse de progresser, comme en témoigne la consolidation de l’accompagnement technique
rapproché des départements ministériels acté par le CE-BSG pour renforcer l’ancrage de la
dimension genre dans leurs pratiques de programmation et de budgétisation. De ce sillage,
le CE-BSG a initié, en 2024 et à titre expérimental, l’application de la méthodologie du
marquage des allocations budgétaires dédiées à la promotion de l’égalité de genre budgets
développée pour le cas du Maroc. En parallèle, le MEF poursuit ses efforts pour enrichir
davantage sa chaîne de résultats sensibles au genre à la lumière des conclusions et des
recommandations issues de l’analyse genre relative à certains domaines d’interventions du
Ministère finalisée en 2023.
6.1. Analyse genre : point de départ pour réussir une programmation
intégrant la dimension genre
L’année 2023 a été marquée par la finalisation de l’analyse genre du système fiscal et
douanier national, lancée en 2022 par le MEF à travers le CE-BSG en partenariat avec l’ONU
Femmes. Dès lors, cette analyse a permis d’établir un état des lieux des inégalités de genre
dans les domaines d’intervention (législatif, opérationnel et institutionnel) de l’administration
fiscale et douanière. Elle a, également, apporté un ensemble de recommandations à même
de renforcer la prise en compte de la dimension genre dans l’action fiscale et douanière. Ces
recommandations ont permis l’enrichissement de la chaîne de résultats sensibles au genre
du MEF par l’intégration d’un nouveau sous-indicateur de performance qui prend en compte
la dimension genre (voir le point 6.3)
6.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité de genre et l’autonomisation économique des
femmes
Le MEF assure, depuis 2002, le pilotage du déploiement de la BSG par les départements
ministériels. Ce processus est rehaussé par la conception et le développement d’outils et
d’instruments (juridique, institutionnel, organisationnel et programmatique) à même de
réussir la prise en compte de la dimension genre dans la programmation et la budgétisation
des départements ministériels. C’est dire que le MEF est un acteur fermement engagé et
fortement impliqué en faveur de l’effectivité de l’égalité entre les femmes et les hommes.
Cette mobilisation s’est aussi traduite par une quête continue pour la prise en compte des
préoccupations liées à la réduction des inégalités entre les femmes et les hommes dans la
gestion et la valorisation des ressources humaines du Ministère. C’est dans ce cadre que
l’Observatoire de l’Approche Genre a été créé au MEF. Cette structure, qui relève de la
Direction des Affaires Administratives et Générales (DAAG), est chargée de suivre la


                                                                                              41
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


situation de l’égalité de genre au sein des structures organisationnelles du Ministère et
d’ uvrer à la conciliation de la vie privée et la vie professionnelle des femmes du Ministère
ainsi qu’à leur épanouissement professionnel.
Ce faisant, l’engagement ferme du MEF pour une action publique qui prend en compte
systématiquement les préoccupations en lien avec la réduction des inégalités entre les
femmes et les hommes, moyennant entre autres l’accompagnement et le renforcement des
capacités des départements ministériels pour une application réussie de la BSG, lui confère
un rôle central dans la mise en    uvre du PGE III, particulièrement, son axe 1 relatif à
l’autonomisation économique et au leadership des femmes.
6.3. Chaîne de résultats sensibles au genre : application de la démarche
performance sensible au genre
En ligne avec les dispositions de la circulaire du Chef du Gouvernement (n°4/2024) relative
à l’établissement des propositions de Programmation Budgétaire Triennale assortie des
objectifs et des indicateurs de performance au titre de la période 2025-2027, le MEF a
développé une chaîne de résultats sensibles au genre qui couvre trois de ses programmes
budgétaires, en l’occurrence, les programmes portant sur le support et le pilotage, les
politiques économiques et stratégies des finances publiques ainsi que la facilitation,
sécurisation des échanges et protection du consommateur. Ce dernier programme a été
nouvellement intégré à ladite chaîne et ce, à partir de la Loi de Finances 2024, en réponse
aux orientations de l’analyse genre de l’administration fiscale et douanière finalisée en 2023.
La chaîne de résultats sensibles au genre adoptée par le MEF traduit, ainsi, les leviers d’action
mis en uvre par le Ministère pour la promotion de l’égalité de genre et de l’autonomisation
des femmes (voir tableau ci-dessous).
De fait, le niveau de réalisation de l’objectif du programme « support au pilotage » portant
sur l’institutionnalisation d’une administration publique équitable basée sur un système de
compétences est assuré d’une part, par un indicateur de performance sensible au genre, en
l’occurrence, l’effectif formé sur la budgétisation sensible au genre qui a avoisiné 28
personnes en 2023, et d’autre part, par un sous indicateur prenant en compte la dimension
genre qui renseigne sur le taux d’accès des femmes à la formation qui a atteint 54% en 2023.
Quant au programme budgétaire portant sur les politiques économiques et les stratégies des
finances publiques, il intègre parmi ses objectifs un seul qui prend explicitement en compte
la dimension genre. Il s’agit de l’objectif relatif à l’intégration de la sensibilité genre dans le
processus budgétaire des départements ministériels. Le niveau de concrétisation de cet
objectif est mesuré par un indicateur qui renseigne sur le nombre de départements
ministériels ayant adopté la Budgétisation Sensible au Genre. Ce nombre s’est établi à 35
départements au titre de l’année 2023. De plus, les objectifs liés à ce même programme
portant sur l’amélioration des analyses relatives à l'environnement et au développement
durable et sur l’optimisation du portefeuille public et l’amélioration des performances des
Etablissements et Entreprises Publics (EEP) y afférent sont, à leur tour, accompagné
respectivement de deux indicateurs de performance sensibles au genre qui mesurent le
nombre d’études réalisées tenant compte de l’aspect genre (5 en 2023) et la part des femmes
représentant l’Etat au niveau des conseils d’administration des EEP (50% en 2023).
Pour ce qui est du programme budgétaire « facilitation, sécurisation des échanges et
protection du consommateur » qui fait partie, désormais, de la chaine de résultats sensibles
au genre du MEF, il est accompagné d’un sous indicateur de performance qui mesure le taux




    42
                                  RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


de satisfaction des usagers femmes par rapport au traitement des requêtes et du courrier38.
Ce taux a atteint en 2023 près de 86%.
                                                                                                                 Réalisations    LF
Programmes                                  Objectifs                  Indicateurs            Sous-indicateurs
                                                                                                                    2023        2024
                                                                                              Taux d’accès des
                                     Institutionnaliser  une     Taux    d’accès     à   la
          Support et




                                                                                              femmes    à   la      54%         49%
           Pilotage




                                     administration publique     formation
                                                                                              formation
                                     équitable basée sur un
                                                                 Effectif formé sur la
                                     système              de
                                                                 budgétisation sensible                              28          25
                                     compétences
                                                                 au genre
                                     Intégrer la sensibilité     Nombre               de
                                     genre dans le processus     départements
      Politiques économiques et




                                     budgétaire          des     ministériels      ayant                             35          35
       stratégies des finances




                                     départements                adopté la Budgétisation
                                     ministériels                Sensible au Genre
                                     Améliorer les analyses
               publiques




                                                                 Nombre          d’études
                                     relatives               à
                                                                 réalisées tenant compte                              5           5
                                     l'environnement et au
                                                                 de l’aspect genre
                                     développement durable
                                     Optimiser le portefeuille
                                                                 Part    des     femmes
                                     public et améliorer les
                                                                 représentant l’Etat au
                                     performances        des
                                                                 niveau des conseils                                50%         10%
                                     Etablissements        et
                                                                 d’administration   des
                                     Entreprises      Publics
                                                                 EEP
                                     (EEP) y afférent
 et protection du
 sécurisation des




                                                                                              Taux          de
  consommateur
    Facilitation,




                                                                                              satisfaction des
     échanges




                                     Améliorer la qualité de     Taux de satisfaction
                                                                                              usagers femmes
                                     service et les conditions   global des usagers par
                                                                                              par rapport au        86%
                                     de      passage       aux   rapport au traitement
                                                                                              traitement   des
                                     frontières                  des requêtes en ligne
                                                                                              requêtes et du
                                                                                              courrier
                                                                                                                    Source : MEF, 2024

     Tableau 21 : Chaîne de résultats sensibles au genre mise en place par le MEF
En lien avec l’objectif du programme « Politiques économiques et stratégies des finances
publiques » qui porte sur l’intégration de la sensibilité genre dans le processus budgétaire
des départements ministériels, l'analyse genre des projets de performance (PdP) de 35
départements ministériels au titre de la Loi de Finances 2024 a révélé les constats suivants :
        43 programmes n’identifient aucun objectif ni indicateurs sensibles au genre contre
         54 en 2023 ;
        64 programmes considérés sensibles au genre incluent au moins un objectif explicite
         concernant l'égalité homme femme, accompagné d'au moins un indicateur désagrégé
         par sexe contre 56 en 2023 ;
        10 programmes ont pour objectif principal la promotion de l'égalité entre les sexes
         et/ou l'autonomisation des femmes.
Le tableau qui suit décline les détails des résultats issus de la grille d’analyse sous le prisme
genre des PdPs des départements ministériels:




38Le traitement des requêtes en question couvre les aspects liés à l’accessibilité au formulaire en ligne, au délai
de traitement de la requête et du courrier, à la clarté de la réponse apportée et à l’impression générale de l’usager
femme sur le processus de prise en charge de sa requête.


                                                                                                                                   43
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


                                                                                     Nombre
                            Nombre        Part         Nombre                                    Part dans le
                                                                     Part dans       des sous
           Nombre de      d’objectifs    dans le    d’indicateurs                                 total des
 Année                                                              le total des   indicateurs
          départements     sensibles    total des   sensibles au                                    sous
                                                                    indicateurs     sensibles
                           au genre     objectifs       genre                                    indicateurs
                                                                                    au genre
  2024          35            114         30%           179            23%             178            51%

  2023          35            105         27%            181           23%             212            61%

  2022          35            110         28%           184            23%             178            47%
                                                                         Source : Direction du Budget/MEF, 2024


    Tableau 22 : Analyse genre des chaînes de résultats dé veloppées par les
         départements ministériels au titre de la Loi de Finances 2024
Dans le même sillage et dans le cadre de l’accompagnement technique déployé par le CE-
BSG au profit des départements ministériels pour la réalisation des analyses genre qui sont
considérées comme des impératifs à une application réussie de la BSG (circulaires du chef
de Gouvernement relatives à la programmation triennale assorties des objectifs et des
indicateurs de performance), le CE-BSG a appuyé, durant l’année 2024, les Ministère de la
Justice et du Transport et de la Logistique ainsi que le Département du Tourisme pour le
lancement des travaux de réalisation des analyses genre de leurs domaines d’intervention.
De même, le CE-BSG a appuyé le Ministère de l'Aménagement du Territoire National, de
l’Urbanisme, de l'Habitat et de la politique de la Ville (MATNUHPV) pour la conception d’un
cadre logique accompagnant la mise en                  uvre de la feuille de route pour
l’institutionnalisation de l’aspect genre dans la stratégie d’action du Ministère durant les
années 2024-2025.
En outre et comme précédemment signalé (partie I traitant le marquage genre des budgets),
l’année 2024 est marquée par l’application à titre expérimental de la méthodologie
développée par le MEF/CE-BSG pour assurer la traçabilité des allocations destinées à la
promotion de l’égalité de genre et de l’autonomisation des femmes. Des réunions et des
séances d’accompagnement ont été organisées au profit des départements de la Jeunesse
et de l’Education Nationale et du Préscolaire identifiés comme départements pilotes de ce
projet. Un atelier de restitution des résultats de l’opérationnalisation de ladite méthodologie
par des deux départements a été organisé le 19 mars 2024. Les travaux sont, en cours, pour
affiner davantage la méthodologie et renforcer son adaptabilité aux spécificités du système
de programmation budgétaire national. Il est à noter dans ce cadre que des séances de
sensibilisation et d’accompagnement sont prévues, à partir de la fin du mois de septembre
2024, au profit du Ministère de la Solidarité, de l’Inclusion Sociale et de la Famille (MSISF) et
du Ministère de l'Aménagement du Territoire National, de l’Urbanisme, de l'Habitat et de la
politique de la Ville (MATNUHPV) pour l’implémentation de la méthodologie de marquage
genre des budgets.
En relation avec les efforts actés par le CE-BSG ciblant la formation et le renforcement de
capacités des départements ministériels, le Centre a organisé, entre 2023 et 2024, près de
10 cycles de formation spécifiques sectorielles à destination de 8 départements ministériels.
Le tableau qui suit met en exergue les principales réalisations accomplies en termes de
formations des départements ministériels, des établissements publics, des collectivités
territoriales et même de la société civile durant les 7 premiers mois de l’année 2024 :




    44
          RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


Entité bénéficiaire    de     la
                                                             Objectifs de la formation
formation
                                   Organisation en juillet 2024 d’une session de formation au profit de 31
Inspection   Générale       des    inspecteurs·trices des finances. La session de formation a porté sur les aspects
Finances                           liés à l’intégration du prisme genre dans les missions de l’IGF, notamment, celle
                                   relative à l’Audit de performance des départements ministériels.
                                   Tenue les 27 et 28 mai 2024 d’une session de renforcement des capacités de
Agence Nationale des Eaux
                                   23 responsables et cadres de l’Agence en matière de BSG. Cette formation
et Forêts (ANEF)
                                   s’inscrit dans le cadre de la mise en uvre du plan d’action genre de l’ANEF
                                   Organisation en janvier 2024, en partenariat avec le Forum des Fédérations
                                   Canadien-Maroc, une session de formation en matière de BSG au profit de 28
Collectivités Territoriales
                                   participant e·s (23 femmes et 5 hommes) provenant de 9 collectivités
                                   territoriales.
                                   Organisation, les 11 et 12 juillet 2024, d’une formation portant sur le plaidoyer
Société civile                     citoyen sur l’égalité de genre en s’appuyant sur la BSG comme outil d’analyse
                                   genre des politiques publiques.

Concernant l’indicateur de performance relatif à la part des femmes représentant l’Etat au
niveau des conseils d’administration des EEP qui relève du programme « politiques
économiques et stratégies des finances publiques » et qui suit le degré d’optimisation du
portefeuille public et d’amélioration des performances des Etablissements et Entreprises
Publics (EEP) y afférent, le MEF à travers la Direction des Entreprises Publiques et de la
Privatisation s’engage à continuer la dynamique lancée en faveur du renforcement de la
présence des femmes dans les instances de gouvernance des EEP.
S’agissant de l’accès des femmes à la formation, le MEF prévoit l’élargissement des
programmes de formations spécialisées pour développer les capacités et les compétences
des femmes fonctionnaires du Ministère, en s’appuyant sur 2 projets en partenariat avec
l’ONU Femmes. Le premier projet concerne l’élaboration d’une ingénierie de formation au
profit des femmes fonctionnaires du MEF et le deuxième porte sur la conception d’un
programme de mentorat au profit des femmes fonctionnaires du Ministère.
6.4. Progrès législatif, réglementaire et institutionnel en faveur de la
promotion de l’égalité de genre
Les mesures juridiques et institutionnelles phares, qui ont été actées entre 2023 et 2024, afin
d’appuyer les actions du MEF pour la consolidation de sa contribution en faveur de
l’effectivité de l’égalité entre les femmes et les hommes et la protection des droits des
femmes, sont déclinées comme suit :
    La diffusion de la circulaire du Chef de Gouvernement n°4/2024 en date du 15 mars
     2024 relative à l’établissement des propositions de Programmation Budgétaire
     Triennale 2025-2027 assortie des objectifs et des indicateurs de performance. La
     circulaire appelle les départements ministériels et les institutions à renforcer la prise
     en compte de la dimension genre dans la conception et la mise en uvre de leurs
     stratégies et à poursuivre leur engagement actif dans le déploiement des actions qui
     leur incombent dans le cadre de la mise en uvre du PGE III (2023-2026) et de son
     premier axe stratégique relatif à l’autonomisation économique et au leadership des
     femmes. La circulaire incite, également, les départements ayant réalisé des analyses
     genre à mettre en         uvre leurs différentes recommandations et à identifier des
     indicateurs sensibles au genre pour suivre les progrès accomplis en matière de
     réduction des inégalités de genre. En outre, cette circulaire a insisté sur l’importance
     du suivi des allocations budgétaires destinées à la promotion de l’égalité de genre et
     sur le rôle qui est attribué, pour y parvenir, au module marquage genre des budgets
     intégré au e-budget 2 genre que les départements ministériels sont amenés à utiliser
     une fois opérationnalisé ;



                                                                                                                  45
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


      Le lancement du centre Ens@te, le 16 octobre 2023, qui vise à fournir des prestations
       d’écoute et d’accompagnement au profit des femmes fonctionnaires du MEF pour les
       soutenir dans leur développement professionnel et personnel. Pour y parvenir, le
       Centre s’appuie sur une équipe multidisciplinaire de professionnels qualifiés,
       composée des conseiller.e.s, de coachs, de psychologues et d’expert.e.s en ressources
       humaines.

     7. DEPARTEMENT CHARGE                                      DE       LA        REFORME                 DE
        L’ADMINISTRATION
Au regard de ses missions et attributions, le Département chargé de la Réforme de
l’Administration (DRA) est fermement engagé en faveur de la réduction des inégalités de
genre et de la promotion de la culture d'équité au sein de l’administration publique.
7.1. Analyse genre : Point de départ pour réussir une programmation
intégrant la dimension genre
L’année 2024 a été marquée par la finalisation d’une nouvelle analyse genre sectorielle en
plus de celle réalisée en 2019 dans le cadre du programme d’appui de l’UE à la mise en uvre
du PGEII.
Cette nouvelle analyse genre réalisée, en partenariat avec le CE-BSG et avec l'appui de l'AFD
et de l'ONU Femmes, s’est intéressée aux domaines liés aux nouvelles technologies (AGS-
TN). Cette étude s’est focalisée sur l’analyse, sous le prisme genre, des effets de la
digitalisation et du développement des nouvelles technologies sur l’accès aux différents
services publics et sur les modalités de travail des fonctionnaires. Ladite analyse a permis de
mettre la lumière sur un ensemble de leviers d’actions à opérationnaliser pour réussir
l’intégration de la dimension genre dans la politique de transition numérique de
l’administration publique.
7.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité et d’autonomisation économique des femmes
Le DRA poursuit l’opérationnalisation des projets inscrits dans le plan d’action élaboré, en
partenariat avec ONU Femmes, pour la promotion de l’égalité de genre dans la fonction
publique, au titre de la période 2023-202639, qui s’aligne parfaitement sur l’objectif
stratégique du DRA portant sur la consolidation de l’approche genre dans l’administration
publique, ainsi que sur les objectifs du PGE III. Il est à rappeler que ce plan d’action est articulé
autour de 4 axes à savoir :
      Axe 1 : Mise en place des mesures facilitant la conciliation vie privée - vie
       professionnelle pour les fonctionnaires du secteur public ;
      Axe 2 : Opérationnalisation de l’Observatoire Genre de la Fonction Publique (OGFP) ;
      Axe 3 : Renforcement des capacités des fonctionnaires (membres Réseau de
       Concertation interministériels (RCI40) et acteurs des Ressources Humaines) en matière
       d’égalité des sexes dans la fonction publique ;
      Axe 4 : Renforcement de la communication institutionnelle pour promouvoir la culture
       de l’égalité et lutter contre les stéréotypes de genre.
Il convient de noter que plusieurs régions disposent, désormais, de leurs propres réseaux de
concertation interministériels de l’égalité des sexes dans la fonction publique. Ainsi, quatre

39 Les détails relatifs à ce plan d’action sont déclinés dans l’édition 2024 du Rapport sur le budget axé sur les
résultats tenant compte de l’aspect genre.
40 Pour plus de détails concernant le RCI, voir les précédentes éditons du Rapport sur le budget axé sur les

résultats tenant compte de l’aspect genre


      46
                                       RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


  réseaux régionaux ont été formés qui couvrent les régions de Fès-Meknès, de l'Oriental, de
  Souss-Massa, et de Tanger-Tétouan-El Hoceima. Cette initiative s’inscrit dans le cadre du
  programme « Autonomisation des Femmes pour des Rôles de Leadership dans la Région
  MENA », initié en partenariat entre le DRA et le Forum des Fédérations Canadien. Ces réseaux
  sont appelés à créer une dynamique collective pour promouvoir l'égalité entre les hommes
  et les femmes et ancrer la culture de l'égalité dans les administrations publiques à l’échelle
  déconcentrée et ce, en s'appuyant sur l'expérience du RCI formé à l’échelle centrale.
  7.3. Chaîne de résultats sensibles au genre : application de la démarche
  de performance
  En ligne avec les dispositions de la circulaire du Chef du Gouvernement (n°4/2024) relative
  à l’établissement des propositions de Programmation Budgétaire Triennale assortie des
  objectifs et des indicateurs de performance au titre de la période 2025-2027, le DRA a
  développé une chaîne de résultats sensibles au genre qui couvre le programme budgétaire
  relatif à la réforme de l’administration et à l’amélioration des services publics (voir tableau
  ci-dessous).

                                                                                                                           Réalisations
Programmes                                     Objectifs                 Indicateurs              Sous-indicateurs                      LF 2024
                                                                                                                              2023
                                                                 Taux       de      femmes
                                       Institutionnaliser une    fonctionnaires aux services
   amélioration des services publics




                                       fonction publique         déconcentrés    bénéficiant
    Réforme de l’administration et




                                                                                                                              17,7%        57%
                                       équitable basée sur un    des     formations    pour
                                       système de compétences    occuper les postes de
                                                                 responsabilité
                                                                                                Taux      d’application
                                                                Taux de réalisation de sites
                                                                                                effective des normes
                                                                pilotes conformément au
                                       Améliorer,    élargir et                                 relatives au genre et
                                                                cadre Référentiel d’accueil
                                       diversifier des services                                 des     personnes      à      75%          98%
                                                                pour     garantir   l’égalité
                                       publics rendus                                           mobilité réduite au
                                                                d’accès des personnes aux
                                                                                                niveau des sites pilotes
                                                                services publics
                                                                                                d’accueil
                                       Institutionnaliser      une
                                       administration     publique
                                                                                          Taux   d’accès    des
                                       équitable basée sur un Taux d’accès à la formation                                    49,27%        59%
                                                                                          femmes à la formation
                                       système de compétences
                                       au niveau du ministère
                                                                                                                             Source : DRA, 2024

        Tableau 23: Chaîne de résultats sensibles au genre mise en place par le DRA
  Cette chaîne intègre effectivement un indicateur et deux sous-indicateurs de performance
  sensibles au genre. En effet, le niveau de réalisation de l'objectif visant l’institutionnalisation
  d’une fonction publique équitable basée sur un système de compétences est apprécié par
  l’indicateur de performance relatif à la part des femmes fonctionnaires, des services
  déconcentrés, bénéficiaires de formations pour accéder aux postes de responsabilité qui
  s’élève à 17,7% au titre de l’année 2023.
  Le niveau de concrétisation de l’amélioration, de l’élargissement et de la diversification des
  services publics rendus est approché, pour sa part, par le sous-indicateur relatif au taux
  d’application effective des normes relatives au genre et aux personnes à mobilité réduite au
  niveau des sites pilotes d’accueil qui a atteint 75% en 2023.
  Quant à l’objectif portant sur l’institutionnalisation d’une administration publique équitable
  basée sur un système de compétences au niveau du ministère, le suivi de son niveau de
  réalisation est assuré par le sous-indicateur relatif aux taux d’accès des femmes à la
  formation qui s’est établi à 49,27% en 2023.




                                                                                                                                            47
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025



8. DEPARTEMENT CHARGE DES AFFAIRES ETRANGERES
ET DE LA COOPERATION AFRICAINE
Le Département des Affaires Etrangères et de la Coopération Africaine (DAECA) poursuit
son engagement pour réussir l’ancrage de la dimension genre dans ses pratiques de
programmation et de budgétisation, comme en témoigne le lancement, en 2024, des travaux
pour la réalisation de la première analyse genre des domaines d’intervention du Ministère liés
à la gestion des ressources humaines et des affaires consulaires.
8.1. Analyse genre : point de départ pour r éussir une programmation
intégrant la dimension genre
En ligne avec des circulaires du Chef de Gouvernement relatives à la programmation
budgétaire triennale qui incitent les départements ministériels à mettre en        uvre les
recommandations issues des analyses genre sectorielles pour réussir l’application de la BSG,
le DAECA en partenariat avec le CE-BSG a entamé, en 2024, la réalisation de la première
analyse genre des domaines d’intervention du département, particulièrement, ceux en lien
avec la gestion des ressources humaines et des affaires consulaires.
Ce diagnostic genre a pour objectifs d'identifier les enjeux liés à l’égalité de genre dans la
gestion des ressources humaines et des affaires consulaires, d’en appréhender les contours
et les facettes ainsi que leurs parties prenantes et ce, afin de mettre en place des leviers
d'action en mesure de renforcer l'intégration du genre dans les processus de gestion des
ressources humaines du département et dans ses prestations consulaires. Ce faisant, les
recommandations et les orientations issues de l’analyse permettraient de renforcer la
pratique de la BSG par le DAECA et ainsi, consolider la pertinence de sa chaîne de résultats
sensibles au genre.
8.2. Alignement des priorités en termes de réduction des inéga lités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité de genre et l’autonomisation économique des
femmes
De par ses missions et ses attributions, le DAECA est activement impliqué dans la prise en
compte des préoccupations liées à la réduction des inégalités de genre et à la protection des
droits des femmes dans ses actions visant le développement de la coopération internationale
et la coordination de l’ensemble des relations extérieures. Dès lors, les interventions du
DAECA sont soucieuses des questions liées à l’égalité de genre en termes d’action
diplomatique, de coopération avec les Etats et les organisations bilatérales et multilatérales
et leurs représentations au Maroc, ainsi qu’en termes de gestion et de valorisation de ses
ressources humaines à l’intérieur et à l’extérieur du pays.
Ces domaines d’action du DAECA font de ce département une partie prenante à même de
contribuer à la concrétisation des objectifs du PGE III, en termes d’autonomisation des
femmes et de lutte contre toutes les formes de violence basées sur le genre.
8.3. Chaîne de résultats sensibles au genre : application de la démarche
performance sensible au genre
En réponse aux dispositions de la circulaire du Chef du Gouvernement (n°4/2024) relative à
l’établissement des propositions de Programmation Budgétaire Triennale assortie des
objectifs et des indicateurs de performance au titre de la période 2025-2027, le DAECA a
adopté une chaîne de résultats qui intègre la dimension genre41 et qui couvre ses trois
programmes budgétaires, en l’occurrence, le programme d’action diplomatique et

41Ladite   chaîne de résultats sensibles au genre est en cours de finalisation.




     48
                                           RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


rayonnement du Maroc, celui relatif aux affaires consulaires et sociales et le programme lié
au support et au pilotage (voir le tableau ci-dessous). Cette chaîne est marquée par
l’intégration de 4 nouveaux sous-indicateurs prenant en compte la dimension genre.
Ainsi, le suivi de la concrétisation de l’un des objectifs du programme d’action diplomatique
et rayonnement du Maroc qui vise la promotion des relations bilatérales et multilatérales, la
consolidation des acquis du Maroc en matière d’intégrité territoriale et la promotion du
modèle marocain et des grandes réformes engagées, est assuré par un sous-indicateur qui
renseigne sur le nombre de femmes diplomates étrangères bénéficiant de la formation à
l’Académie Marocaine des Etudes Diplomatiques. Ce nombre s’est d’ailleurs situé à 20 au
titre de l’année 2023. De plus, ce programme intègre, désormais, un nouveau sous-indicateur
de performance sensible au genre associé à l’objectif portant sur l’assistance des acteurs non
étatiques en matière de diplomatie parallèle. Ce sous-indicateur mesure le taux de réponses
aux demandes d’acteurs non Etatiques, pour bénéficier de l’appui financier du Ministère pour
participer aux événements internationaux, travaillant sur les questions de la femme et du
genre.
Pour ce qui est du programme relatif aux affaires consulaires et sociales, il est, à son tour,
accompagné d’un nouveau sous-indicateur intégrant la dimension genre et qui mesure le
nombre de prestations à caractère social fournies aux femmes. Ce sous-indicateur renseigne
sur le niveau de réalisation de l’objectif dudit programme et qui est relatif à la garantie des
droits sociaux des Marocains Résidant à l’Etranger (MRE).
Quant au troisième programme dédié au support et au pilotage, l’un de ses objectifs, qui
ambitionne à institutionnaliser une administration publique équitable basée sur un système
de compétences, est associé à un sous-indicateur sensible au genre qui mesure le taux
d’accès des femmes à la formation. Il est à noter dans ce sens que le DAECA prévoit la mise
en place d’un programme de formation et de mentorat au profit des femmes ainsi que des
séances de formation au profit du personnel du département traitant les thématiques en
relation avec la prévention et la lutte contre la violence basée sur le genre.
De plus, cet objectif est suivi par un indicateur de performance sensible au genre qui mesure
le taux d’accès des femmes aux postes de responsabilité. Cet indicateur est, désormais,
accompagné de deux nouveaux sous-indicateurs. Le premier porte sur le pourcentage de
femmes dans les postes de management intermédiaire. Le second mesure la part des femmes
dans les postes de pilotage.
                                                                                                                             Réalisations    LF
Programmes                                          Objectifs                Indicateurs            Sous-indicateurs
                                                                                                                                2023        2024
                                             Promouvoir        les
                                             relations bilatérales et
   Action diplomatique et Rayonnement du




                                             multilatérales,             Nombre         de
                                                                                                 Nombre      de  femmes
                                             consolider les acquis       diplomates étrangers
                                                                                                 diplomates étrangères
                                             du Maroc en matière         bénéficiant   de   la
                                                                                                 bénéficiant    de   la
                                             de     son      intégrité   formation           à                                   20          53
                                                                                                 formation à l’académie
                                             territoriale           et   l’académie marocaine
                                                                                                 marocaine des études
                                             promouvoir le modèle        des           études
                                                                                                 diplomatiques
                                             marocain       et     les   diplomatiques
                   Maroc




                                             grandes        réformes
                                             engagées
                                                                                                 Taux de réponses aux
                                                                                                 demandes d’acteurs non
                                                                                                 Etatiques,          pour
                                             Assister les acteurs        Nombre d’acteurs
                                                                                                 bénéficier de l’appui
                                             non     étatiques en        non Etatiques
                                                                                                 financier du Ministère                     15%
                                             matière de diplomatie       bénéficiaires de
                                                                                                 pour     participer  aux
                                             parallèle                   l’appui financier
                                                                                                 événements
                                                                                                 internationaux,
                                                                                                 travaillant     sur   les




                                                                                                                                              49
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


                                                                              questions de la femme et
                                                                              du genre




                          Assurer la protection
consulaire




                                                     Nombre            de
 sociales
 Affaires




                          et garantir les droits                              Nombre de prestations à
                                                     prestations        à
   s et




                          sociaux des Marocains                               caractère social fournies                86.000
                                                     caractère      social
                          Résidant à l’Etranger                               aux femmes
                                                     fournies aux MRE
                          (MRE)

                                                     Taux d'accès    à   la   Taux    d'accès     des
    Support et pilotage




                                                                                                                        42%
                                                     formation                femmes à la formation
                          Institutionnaliser une
                          administration                                      Pourcentage       des
                          publique       équitable                            femmes dans les postes
                                                                                                                        39%
                          basée sur un système       Taux d'accès des         du         management
                          de compétences             femmes aux postes        intermédiaire
                                                     de responsabilité        Pourcentage de femmes
                                                                              dans les postes de                        22%
                                                                              Pilotage
                                                                                                          Source : DAECA, 2024

              Tableau 24 : Chaîne de résultats sensibles au genre mise en place par le
                                              DAECA
8.4 Progrès législatif, réglementaire et institutionnel en faveur de la
promotion de l’égalité de genre
L’engagement du DAECA en faveur de la promotion de l’égalité entre les femmes et les
hommes dans la gestion et la valorisation de ses ressources humaines s’est traduit par la
programmation d’une multiplicité d’actions d’ordre organisationnel et institutionnel à savoir :
        Création d'une crèche dans les locaux du Ministère pour permettre à ses
         fonctionnaires de concilier entre leur vie professionnelle et vie personnelle ;
        Élaboration d'une charte propre au Ministère pour la lutte contre la violence dans les
         lieux de travail.

9. DEPARTEMENT CHARGE DE LA COMMUNICATION
Le département de la Communication (DC) poursuit son engagement en faveur de la lutte
contre les stéréotypes liés au genre et l’amélioration de l’image de la femme dans les médias.
De même, le département poursuit ses efforts afin de renforcer la présence des femmes dans
ses structures organisationnelles et dans les postes de responsabilité.
9.1. Analyse genre : Point de départ pour réussir une programmation
intégrant la dimension genre
En plus de la réalisation d’une analyse genre du secteur de la communication et de
l’élaboration d’un guide pour lutter contre les stéréotypes sexistes dans les médias au Maroc
en 2019, le DC envisage la réalisation d’une nouvelle étude afin d’enrichir les analyses
existantes et de produire des connaissances et des données fiables traitant les questions
liées à l’égalité de genre dans le secteur de la communication. En outre, cette nouvelle étude
prévoit de procéder à une évaluation de l'impact et des effets des mesures déjà entreprises,
notamment, en ce qui concerne la situation des femmes journalistes en termes de conditions
de travail, d’accès à la formation et aux postes de responsabilités. Les résultats et les
recommandations attendus de cette étude sont amenés à servir une feuille de route cadrant



              50
            RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


l'ensemble des actions et initiatives futures dans le but de renforcer la position des femmes
journalistes dans du paysage médiatique national.
9.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité de genre et l’autonomisation économique des
femmes
L’amélioration de l’image de la femme et la lutte contre les stéréotypes liés au genre dans le
paysage médiatique écrit et audiovisuel ainsi que la promotion de la place des femmes dans
les métiers du journalisme sont au c ur de priorités du DC. Pour ce faire, le Département
s’appuie sur divers leviers juridique et programmatique, en étroite collaboration avec les
opérateurs publics de l’audiovisuel. Cet engagement s’aligne parfaitement sur les objectifs
du PGE III, particulièrement, ceux en lien avec la promotion des droits des femmes et la lutte
contre les discriminations et les stéréotypes.
9.3. Chaîne de résultats sensibles au genre : application de la démarche
performance sensible au genre
Conformément aux dispositions de la circulaire du Chef du Gouvernement (n°4/2024)
relative à l’établissement des propositions de Programmation Budgétaire Triennale assortie
des objectifs et des indicateurs de performance au titre de la période 2025-2027, le DC a
adopté une chaîne de résultats sensibles au genre qui couvre son programme budgétaire
relatif à la communication, au développement des médias et aux relations publiques. Ce
dernier est accompagné d’un objectif portant sur l’amélioration l'image de la femme dans les
médias et la lutte contre les stéréotypes sexistes dans les médias nationaux dont le niveau
de réalisation est mesuré par l’indicateur de performance qui renseigne sur le nombre
d'activités réalisées pour la lutte contre les Stéréotypes sexistes dans les médias.
En outre, les niveaux de concrétisation de l’’objectif relatif au développement des
compétences du personnel et l’optimisation de l’efficience de la gestion des ressources
humaines sont, à leur tour, mesurés entre autres par le sous indicateur qui renseigne sur le
taux d’accès des femmes à la formation (voir tableau le tableau ci-dessous).
                                                                                    Sous       Réalisations     LF
Programmes                 Objectifs                     Indicateurs
                                                                                 indicateurs      2023         2024
                  Améliorer l'image de la         Nombre         d'activités
 Communication,




                  femme dans les médias et        réalisées pour la lutte
 développement
  des médias et




                  lutter      contre        les   contre les                                        0            1
    publiques
    relations




                  stéréotypes sexistes dans       Stéréotypes sexistes dans
                  les médias nationaux            les médias
                  Développer                les
                                                                                Taux d’accès
                  compétences du personnel        Taux    d’accès      à   la
                                                                                des femmes à       18%        26,8%
                  et Optimiser l'efficience de    formation
                                                                                la formation
                  la GRH
                                                                                                     Source : DC, 2024

   Tableau 25 : Chaîne de résultats sensibles au genre mise en place par le DC
En relation avec les efforts déployés visant l’amélioration de l'image de la femme et la lutte
contre les stéréotypes sexistes dans les médias, il est à rappeler que le DC apporte son appui
aux opérateurs publics de l’audiovisuel (Société nationale de radiodiffusion et de télévision -
SNRT- et 2M) pour y parvenir, moyennant divers leviers de sensibilisation tels que l’édition,
l’organisation d’événements et les plateformes digitales.




                                                                                                                     51
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025



10. HAUT-COMMISSARIAT AU PLAN
Le Haut-Commissariat au Plan (HCP) continue de déployer les efforts nécessaires en termes
de collecte, de traitement, d’analyse et de diffusion de données sensibles au genre qui
constituent un préalable crucial pour la conception, la mise en uvre et le suivi-évaluation
de toute action publique soucieuse des questions liées à la réduction des inégalités de genre.
10.1. Analyse genre : point de départ pour réussir une programmation
intégrant la dimension genre
Au regard de ses missions et de ses attributions, le HCP est le principal producteur de la
statistique officielle au Maroc. En effet, le HCP est l’entité publique chargée de la collecte,
l’analyse et la dissémination des informations couvrant les domaines démographiques,
économiques et sociaux, tout en y intégrant la dimension genre. Force est noter que le HCP
est une partie prenante incontournable de toute intervention visant la réalisation d’une
analyse genre sectorielle pour cerner les inégalités de genre touchant un secteur donné et
les actions à prévoir pour les réduire. Ceci dénote le rôle extrêmement important attribué au
HCP, en termes de production de données nécessaires à la mise en place, par les
départements ministériels, de chaînes de résultats sensibles au genre fiables et pertinentes.
 10.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie d u Département et les plans nationaux pour la
promotion de l’égalité de genre et l’autonomisation économique des
femmes
Les interventions du HCP qui prennent en compte la dimension genre se réfèrent aux
missions et attributions qui lui sont confiées. Ces interventions portent, essentiellement, sur
la réalisation des enquêtes sur le budget temps des femmes et des hommes, sur l’emploi en
y intégrant un module spécifique sur l’emploi des femmes, sur la prévalence de la violence
basée sur le genre, sur la migration internationale et sur la famille. De même, le HCP est
fortement engagé en faveur de l’intégration des questions liées à l’égalité de genre dans les
enquêtes de grandes envergues qu’il mène, en l’occurrence, celles sur le niveau de vie des
ménages, sur les structures économiques et sur le secteur informel...
Il est à préciser à cet égard que le Recensement Général de la Population et de l’Habitat
(RGPH 2024), lancé en septembre 2024, prend en compte la dimension genre avec la
particularité de recourir à des approches et à des outils de collecte et d’analyse qualifiés de
modernes et d’innovants. De fait, les résultats qui découleraient dudit Recensement
permettraient, sans aucun doute, d’assurer un meilleur suivi de la réalisation de l’égalité entre
les femmes et les hommes à l’échelle nationale et territoriale.
Poursuivant ses efforts pour renforcer la disponibilité et l’accessibilité des données sensibles
au genre, le HCP continue d’alimenter la plateforme « genre.hcp.ma » par des données
statistiques et des études traitant les dimensions en relation avec l’égalité de genre. Cette
plateforme interactive et conviviale a pour objectif de faciliter l’accès des utilisateurs/trices
à un recueil d’indicateurs genre, à des publications portant sur les questions liées à la
réduction des inégalités entre les femmes et les hommes, à des vidéos, à l’actualité en relation
avec l’égalité de genre… Il est à rappeler que les indicateurs déclinés au niveau de cette
plateforme s’alignent sur les référentiels internationaux cadrant les indicateurs genre et ils
sont enrichis et adaptés aux besoins du contexte national. Ces indicateurs genrés couvrent
les domaines en relation avec la population, la santé, l’éducation, le marché du travail, l’emploi
du temps, la prise de décision, la violence basée sur genres...
Dans le même sillage, il est à rappeler que le HCP est l’entité publique chargée, depuis 2019,
d’assurer le suivi et le reporting de la mise en uvre des ODD au Maroc y compris l’ODD 5
dédié à l’égalité des sexes et ce, en concertation avec les différents départements



    52
         RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


ministériels, ce qui confère au HCP une mission essentielle en matière de suivi de la réalisation
de l’égalité de genre au Maroc.
Ce faisant, les domaines d’action et d’intervention du HCP en faveur de la promotion de
l’égalité entre les femmes et les hommes font de ce département un acteur clé dans la mise
en uvre des programmes et des projets inscrits dans le PGE III.
10.3. Chaîne de résultats sensibles au genre : application de la démarche
performance sensible au genre
En ligne avec les dispositions de la circulaire du Chef du Gouvernement (n°4/2024) relative
à l’établissement des propositions de Programmation Budgétaire Triennale assortie des
objectifs et des indicateurs de performance au titre de la période 2025-2027, le HCP a
développé une chaine de résultats sensibles au genre qui couvre deux de ses programmes
dédiés au pilotage et au soutien ainsi qu’à la formation des cadres dans les domaines de la
statistique, de l'économie appliquée et des sciences de l'information (voir tableau ci-
dessous).
10.3.1. Chaine de résultats sensibles au genre mise en place par le Département
La chaîne de résultats sensibles au genre développée par le HCP reflète les leviers d’action
actés par cette institution en faveur de la prise en compte de la dimension genre dans les
processus de recrutement et de formation des ressources humaines. Elle intègre, également,
les efforts entrepris pour assurer un accès équitable des étudiantes et des étudiants aux
études dans les domaines de la statistique, de l’économie appliquée et des sciences de
l’information ainsi qu’aux prestations sociales fournies par l’Institut National Supérieur de
l’Economie Appliquée (INSEA).
Ainsi, le niveau de réalisation de l’objectif du programme consacré au pilotage et au soutien
qui vise l’institutionnalisation d’une administration publique équitable basée sur un système
de compétences est approché par deux indicateurs de performance qui mesurent
respectivement la part des femmes bénéficiaires de la formation (58% en 2023) et le taux de
féminisation du personnel du HCP (48% en 2023).
Quant au programme relatif à la formation des cadres dans les domaines de la statistique, de
l'économie appliquée et des sciences de l'information, le degré de concrétisation de son
objectif qui ambitionne de répondre à la demande croissante dans les domaines de la
statistique, de l’économie appliquée et des sciences de l’information est mesuré par 2 sous-
indicateurs sensibles au genre à savoir : le taux des femmes diplômées de l’INSEA (48% en
2023) et le taux des femmes diplômées de l’Ecole Supérieur de l’Information (46% en 2023).
Le niveau d’amélioration de la qualité des prestations sociales fournies aux étudiants de
l’INSEA qui est un des objectifs du même programme est, à son tour, approché par un sous-
indicateur de performance sensible au genre qui mesure le taux de satisfaction des nouvelles
demandes d’hébergement des étudiantes (100% en 2023).




                                                                                              53
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


                                                                                                                     Réalisations     LF
Programmes                                Objectifs                Indicateurs              Sous indicateurs
                                                                                                                        2023         2024
                                                                Part des femmes
                                   Institutionnaliser une
         Pilotage et


                                                                bénéficiaires de la                                      58%         53%
           soutien


                                   administration
                                                                formation
                                   publique       équitable
                                                                Taux            de
                                   basée sur un système
                                                                féminisation    du                                       48%         48%
                                   de compétences
                                                                personnel du HCP
                                                                                       Taux de diplômés hommes
                                   Répondre         à      la                                                            52%         52%
  Formation des cadres dans les




                                                                                       INSEA
  domaines de la statistique, de
   l'économie appliquée et des




                                   demande        croissante
                                                                                       Taux de diplômées Femmes
     sciences de l'information




                                   dans les domaines de         Taux              de                                     48%         48%
                                                                                       INSEA
                                   la     statistique,    de    diplomation      par
                                                                                       Taux de diplômés hommes
                                   l’économie appliquée         sexe                                                     54%         40%
                                                                                       ESI
                                   et des sciences de
                                                                                       Taux de diplômées Femmes
                                   l’information                                                                         46%         60%
                                                                                       ESI
                                                                                       Taux de satisfaction des
                                                                Taux           de
                                                                                       nouvelles        demandes
                                   Améliorer la qualité         satisfaction  des                                       100%         100%
                                                                                       d’hébergement           des
                                   des        prestations       nouvelles
                                                                                       étudiantes
                                   sociales fournies aux        demandes
                                                                                       Taux de satisfaction des
                                   étudiants de l’INSEA         d’hébergement par
                                                                                       nouvelles        demandes        100%         100%
                                                                sexe
                                                                                       d’hébergement des étudiants
                                                                                                                     Source : HCP, 2024

 Tableau 26 : Chaîne de résultats sensibles au genre mises en place par le HCP
10.3.2. Actions en faveur de la promotion de l’égalité de genre non intégrées
dans les chaînes de résultats sensibles au genre
En plus des actions mises en exergue dans sa chaîne de résultats sensibles au genre, le HCP
a lancé une multiplicité de projets et d’activités pour une meilleure compréhension des
facettes des inégalités de genre et pour une consolidation de la pertinence des interventions
à prévoir pour les réduire. Les principaux projets entrepris, à cet égard, sont déclinés comme
suit :
 Réalisation en 2024 de l'étude sur " L'autonomisation économique et l'inclusion sociale
    des femmes rurales au Maroc " : cette étude a mis en exergue le coût économique
    engendré par les inégalités entre les femmes et les hommes dans les zones rurales. En
    effet, ces inégalités sont à l’origine, selon l’étude, d’une perte de 2,2% du PIB en 2019. En
    outre, l’étude a indiqué que l'investissement dans l'autonomisation économique des
    femmes rurales stimule, non seulement, la croissance économique, mais contribue
    significativement à l’instauration des bases d’un développement inclusif ;
 Réalisation, en 2024, d’une consultation portant sur « les inégalités de genre sous le
    prisme des objectifs du développement durable au Maroc : production d’indicateurs
    sensibles au genre » ;
 Développement en cours d’un indice composite des inégalités de genre : cette action a
    pour objectif de développer un indice multidimensionnel d’égalité de genre au Maroc
    (IMEG). Cet indicateur permettrait d’assurer le suivi des politiques publiques dédiées à la
    promotion l’égalité entre les sexes ;
 Lancement, en 2024, d’une analyse genre du questionnaire de l’enquête nationale sur la
    famille : cette analyse vise à renforcer la prise en compte de la dimension genre dans le
    questionnaire qui sera renseigné lors de ladite enquête et ce, afin de produire des
    données sensibles au genre utiles à l’action publique, aux études et aux recherches ainsi
    qu’à la société civile ;
 Publication en 2024 de l’étude relative à « l’analyse intersectionnelle de la participation
    des femmes au marché du travail marocain : une étude comparative entre la région de
    Casablanca-Settat et de l’Oriental » ;



           54
          RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


 Publication, à l’occasion de la commémoration de la journée nationale de la femme
  marocaine célébrée le 10 octobre 2023, du rapport relatif à « la Femme Marocaine en
  chiffres » …

11.   CONSEIL   ECONOMIQUE,                                                       SOCIAL                 ET
ENVIRONNEMENTAL
Le Conseil Economique, Social et Environnemental (CESE) est fermement engagé dans la
dynamique initiée par le Maroc en faveur de la promotion de l’égalité de genre et la
protection des droits des femmes. Dès lors, le Conseil prend en compte dans ses analyses,
les questions liées à la réduction des inégalités entre les femmes et les hommes en vue de
soutenir les politiques publiques qui promeuvent l’égalité de genre.
11.1. Analyse genre : point de départ pour réussir une programmation
intégrant la dimension genre
En raison de l’indisponibilité d’une analyse genre de ses domaines d’interventions, le CESE
s’appuie sur ses priorités et sur sa stratégie d’action pour identifier les thématiques liées à
l’égalité de genre à analyser et à traiter dans ses rapports, ses avis et ses auto-saisines.
11.2. Alignement des priorités en termes de réductio n des inégalités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité de genre et l’autonomisation économique des
femmes
Conformément à ses missions en tant qu’institution constitutionnelle chargée de donner un
avis sur toutes les questions d’ordre économique, sociale et environnementale, le CESE, à
travers ses rapports, ses avis et ses auto-saisines, émis des recommandations et propositions
à même de consolider l’inclusivité des politiques publiques. C’est dire que la promotion de
l’égalité de genre et de la protection des droits des femmes sont au c ur des priorités du
Conseil.
11.3. Chaîne de résultats sensibles au genre : application de la démarche
performance sensible au genre
En réponse aux orientations énoncées dans la circulaire du Chef du Gouvernement
(n°4/2024) relative à l’établissement des propositions de Programmation Budgétaire
Triennale assortie des objectifs et des indicateurs de performance au titre de la période
2025-2027, le CESE a développé une chaîne de résultats sensibles au genre qui couvre le
programme budgétaire du conseil relatif à la contribution à l'amélioration des politiques
publiques et à la promotion de la démocratie participative. Ce programme est associé à un
objectif visant à rehausser la qualité des productions du CESE et à renforcer l’applicabilité
de ses recommandations dont le niveau de réalisation est mesuré par un indicateur de
performance qui renseigne sur le pourcentage des productions du CESE qui prennent en
considération la question du genre. Ainsi, 60% des productions du CESE réalisées, en 2023,
prennent en considération la question du genre.
                                                                                         Réalisations     LF
         Programmes                     Objectifs                   Indicateurs
                                                                                            2023         2024
 Contribution                à
                                 Rehausser la qualité des    Pourcentage          des
 l’amélioration des politiques
                                 productions du CESE et      productions du CESE qui
 publiques et à la promotion                                                                60%          60%
                                 renforcer l’applicabilité   prennent en considération
 de        la      démocratie
                                 de ses recommandations      la question du genre
 participative
                                                                                            Source : CESE, 2024

       Tableau 27 : Chaîne de résultats sensibles au genre relative au CESE
En relation avec les productions réalisées par le CESE en 2023 qui prennent en considération


                                                                                                            55
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


l’égalité de genre, le Conseil a élaboré plusieurs travaux qui traitent une multiplicité de
dimensions liées à la réduction des inégalités entre les femmes et les hommes. Il s’agit de :
 La réalisation d’un avis sur « le mariage des filles et ses répercussions négatives sur leur
   situation économique et sociale » : en se basant sur les conséquences du mariage des
   enfants, notamment, l’exclusion des filles du système éducatif et de formation et des
   opportunités de participation économiques, le CESE recommande d’accélérer le
   processus visant à mettre fin à la pratique du mariage d'enfants sous toutes ses formes.
   Ceci passe à travers plusieurs leviers à savoir : le renforcement de la pratique
   conventionnelle du Maroc en matière de lutte contre le mariage forcé et le mariage des
   mineurs, la promotion d’une politique d'éducation en mesure de garantir une éducation
   civique à la citoyenneté qui met l’accent sur la connaissance des droits et le portage d’une
   politique ambitieuse d’égalité entre les femmes et les hommes ;
 L’élaboration du Rapport annuel du CESE au titre de l’année 2022 : ce rapport a mis en
   avant le constat portant sur la nécessité de renforcer l’autonomisation économique des
   femmes. Le Rapport a émis un certain nombre de mesures afin d’assurer une intégration
   active des femmes dans le marché du travail telles que l’engagement d’une réflexion sur
   la valorisation du travail domestique des femmes, allégement des responsabilités pesant
   sur les femmes en garantissant la disponibilité des services de garde des enfants à bas
   âge, la réduction des écarts salariaux entre les hommes et les femmes, … ;
 La réalisation d’une auto-saisine traitant la question de la mendicité au Maroc « Pour une
   société cohésive exempte de mendicité » : Cette auto-saisine basée sur un diagnostic a
   apporté un ensemble de recommandation pour mettre fin au fléau de la mendicité dont,
   essentiellement, la protection des personnes vulnérables (les femmes, les personnes
   âgées, les personnes en situation de handicap) contre l’exploitation à des fins de
   mendicité, la révision de certains disposition de la Moudawana pouvant favoriser la
   précarité des femmes veuves ou divorcées... ;
 La réalisation d’une auto-saisine sur les jeunes NEET et intitulée « les jeunes NEET: Quelles
   perspectives d’inclusion socio-économique ? »: le CESE par le biais des analyses
   effectuées dans le cadre de cette auto-saisine a émis un certain nombre de propositions
   à même de renforcer l’intégration des femmes NEET, qui représentent 38,8% des NEET au
   Maroc, au marché du travail. Ces propositions ont trait, entre autres, à fournir des
   incitations financières aux jeunes femmes au foyer NEET souhaitant s’engager dans l’auto-
   emploi, à lancer un plan national pour ouvrir des crèches publiques ainsi qu’au sein des
   entreprises privées en échange d’incitations, à renforcer les compétences professionnelles
   des femmes au foyer au sein de la catégorie des jeunes NEET en particulier en milieu rural…




    56
          RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


   III.   EFFORTS CONTINUS POUR UN ACCES EQUITABLE
          AUX SERVICES SOCIAUX ET AUX INFRASTRUCTURES
          DE BASE
Cet axe met en exergue les progrès accomplis en matière d'accès équitable aux services
sociaux, à savoir, l'accès aux infrastructures de base (énergie, eau, logement …), ainsi que
l'accès aux services de santé, à l’éducation, à l’enseignement supérieur, à la formation
professionnelle et aux activités de développement et d’épanouissement des jeunes.

   1. DEPARTEMENT                   CHARGE             DE       LA       TRANSITION
      ENERGETIQUE
Le Département de la Transition Énergétique (DTE) continue sa mobilisation pour une
application réussie de la BSG, comme en témoigne l’enrichissement de sa chaîne de résultats
par un nouvel indicateur de performance intégrant la dimension genre, relatant le degré de
prise en compte des questions liées à l’égalité entre les femmes et les hommes dans les
actions visant le renforcement de l’efficacité énergétique.
1.1. Analyse genre : point de départ pour ré ussir une programmation
intégrant la dimension genre
La seule analyse genre dont dispose le DTE est celle réalisée, en 2019, en partenariat avec
l’AFD avec l’appui du CE-BSG. Cette analyse s’est focalisée sur l’examen sous le prisme genre
de la chaîne de résultats du département.
1.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité de genre et l’autonomisation économique des
femmes
Le Maroc poursuit ses efforts pour développer et intégrer l’efficacité énergétique comme
levier clé pour accélérer la transition énergétique. Par conséquent, compte tenu de
l’importance de l’efficacité énergétique et de l’intérêt accru des parties concernées, la
stratégie d’action du DTE se réfère à la vision stratégique propre à l’efficacité énergétique
développée par notre pays, dans le cadre d’une concertation nationale globale et
participative, dans laquelle tous les acteurs concernés ont été impliqués, en particulier les
départements ministériels, les institutions publiques, les régions et les collectivités
territoriales, le secteur privé, la société civile et les syndicats sectoriels concernés. Les
questions liées à l’égalité de genre et à l’autonomisation de femmes sont prises en compte
dans le cadre de déploiement de cette stratégie, à travers plusieurs leviers dont la formation
et autres.
En outre, le département poursuit ses efforts pour une intégration systématique de la
dimension genre dans la gestion et la valorisation de ses ressources humaines. En effet, le
DTE a entrepris plusieurs mesures visant le renforcement de l’accès des femmes
fonctionnaires à la formation et aux postes de responsabilités et d’autres qui ambitionnent
la mise à niveau des espaces du travail en tenant compte des besoins spécifiques des femmes
et la conciliation entre vie professionnelle et vie privée de ces fonctionnaires.
1.3. Chaine de résultats sensibles au genre : application de la démarche
performance sensible au genre
Conformément aux dispositions de la circulaire du Chef du Gouvernement (n°4/2024)
relative à l’établissement des propositions de Programmation Budgétaire Triennale assortie
des objectifs et des indicateurs de performance au titre de la période 2025-2027, le DTE a



                                                                                           57
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


mis en place une chaîne de résultats intégrant la dimension genre42 qui couvre deux de ses
programmes budgétaires, en l’occurrence, celui relatif au pilotage et support et le
programme dédié à l’énergie (voir tableau ci-dessous).

                                                                                                 Réalisations    LF
Programmes             Objectifs               Indicateurs              Sous-indicateurs
                                                                                                    2023        2024
                 Institutionnaliser      Pourcentage des femmes
                 une administration      occupant des postes de                  -                   32%         33%
Support et       publique égalitaire     responsabilité
 pilotage        basée      sur     un
                 système            de   Taux    d’accès     à   la Taux d’accès des femmes
                                                                                                     5%          50%
                 compétence              formation                  à la formation
                                                                     Nombre      de    femmes
                                                                     bénéficiant            de
                                         Nombre       de   femmes
                                                                     l’accompagnement et de                       5
                                         bénéficiant          d’un
                                                                     la formation dans le
                 Améliorer               accompagnement         et
                                                                     secteur du bâtiment
     Energie     l’efficacité            d’une formation dans le
                                                                     Nombre      de    femmes
                 énergétique             cadre du Projet d’Appui à
                                                                     bénéficiant            de
                                         l’Efficacité  Énergétique
                                                                     l’accompagnement et de                       5
                                         au Maroc (PEEM)
                                                                     la formation dans le
                                                                     secteur de l’industrie
                                                                                                     Source : DTE, 2024

     Tableau 28 : Chaîne de résultats sensibles au genre mise en place par le DTE
Ainsi, le niveau de réalisation de l’objectif du programme « support et pilotage » visant
l’institutionnalisation d’une administration publique égalitaire basée sur un système de
compétence est approché par un indicateur de performance qui renseigne sur le taux de
féminisation des postes de responsabilité du département qui est situé à 32%. De même, le
suivi du degré d’atteinte de même objectif est aussi assuré par un sous indicateur de
performance renseignant sur le taux d’accès des femmes à la formation.
Quant au programme relatif à l’énergie, l’année 2024 marque son intégration dans la chaîne
de résultats sensibles au genre du département. En effet, le suivi du degré de réalisation de
son objectif lié à l’efficacité énergétique est renseigné par l’indicateur de performance
mesurant le nombre de femmes bénéficiant d’un accompagnement et d’une formation dans
le cadre du Projet d’Appui à l’Efficacité Énergétique au Maroc (PEEM). Ce même indicateur
est associé à deux sous-indicateurs sensibles au genre qui concernent respectivement le
nombre de femmes bénéficiant de l’accompagnement et de la formation dans le secteur du
bâtiment et le nombre de femmes bénéficiant de l’accompagnement et de la formation dans
le secteur de l’industrie.




42   Ladite chaîne de résultats sensibles au genre est en cours de finalisation.




        58
         RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


   2. DEPARTEMENT                   CHARGE            DU        DEVELOPPEMENT
      DURABLE
L’intégration des préoccupations liées à la réduction des inégalités de genre dans les
programmes visant la durabilité environnementale est une étape jalon vers l’atteinte des
objectifs de développement tels qu'ils sont inscrits dans l'Agenda 2030 pour le
développement durable. A cet effet, le Département chargé du Développement Durable
(DDD) gagnerait à consolider la prise en compte de la dimension genre dans ses pratiques
de programmation et de budgétisation et, ainsi, enrichir pertinemment sa chaîne de résultats
sensibles au genre.


2.1. Analyse genre : point de départ pour réussir une programmation
intégrant la dimension genre
La seule analyse genre dont dispose le DDD a été conduite, en partenariat avec l’ONU
Femmes. Les résultats et les recommandations issus de cette analyse ont servi à la
conception de la Stratégie de l’Institutionnalisation de l’Egalité de Genre (SIEG) dans le
secteur de l’environnement lancée en 2018.
2.2. Alignement des priorité s en termes de réduction des inégalités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité de genre et l’autonomisation économique des
femmes
Les questions liées à la promotion de l’égalité de genre et de l’autonomisation des femmes
sont intégrées dans les programmes de valorisation et de protection de l’environnement
pilotés par le DDD en partenariat avec plusieurs institutions nationales et organismes
internationaux. Cet intérêt porté aux questions d’inclusivité et de durabilité ne peut que
conforter la contribution du Département à la mise en uvre du PGE III.
2.3. Chaîne de résultats sensibles au genre : application de la démarche
performance sensible au genre
En application des dispositions de la circulaire du Chef du Gouvernement (n°4/2024) relative
à l’établissement des propositions de Programmation Budgétaire Triennale assortie des
objectifs et des indicateurs de performance au titre de la période 2025-2027, le DDD a
développé une chaîne de résultats intégrant la dimension genre qui couvre un seul
programme, en l’occurrence, celui relatif au pilotage et au support (voir tableau ci-dessous).
2.3.1. Chaîne de résultats sensibles au genre mise en place par le Département
Les aspects liés à l’égalité de genre mis en exergue par cette chaîne demeurent limités aux
dimensions liées à la gestion et à la valorisation des ressources humaines. En effet, le degré
de réalisation de l’objectif du programme dédié au pilotage et au support, et qui vise
l’institutionnalisation d’une administration publique équitable basée sur un système de
compétences, est approché par un sous-indicateur mesurant le taux d’accès des femmes à
la formation qui a atteint 50% en 2023 et par un indicateur de performance mesurant la part
des femmes candidates aux postes de responsabilité qui s’est établi à 36,36% en 2023.




                                                                                           59
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025



                                                                                             Réalisations
Programmes             Objectifs                Indicateurs            Sous indicateurs                     LF 2024
                                                                                                2023
                 Institutionnaliser  une   Taux   d’accès     à   la Taux  d’accès     des
   Pilotage et



                                                                                                50%          50%
    Support



                 administration publique   formation                 femmes à la formation
                 équitable basée sur un    Part    des     femmes
                 système              de   candidates aux postes                               36,36%        48%
                 compétences               de responsabilité
                                                                                                  Source : DDD, 2024

 Tableau 29 : Chaîne de résultats sensibles au genre mise en place par le DDD
2.3.2. Actions en faveur de la promotion de l’égalité de genre non intégrées dans
les chaînes de résultats sensibles au genre
Comme signalé précédemment, la chaîne de résultats sensibles au genre adoptée par le DDD
ne reflète pas l’ensemble des leviers d’actions menés par le Département pour promouvoir
l’égalité de genre et l’autonomisation des femmes. En effet, le DDD est partie prenante de
plusieurs programmes et projets en partenariat avec des organismes internationaux qui
intègrent la dimension genre. Ci-après une déclinaison de ces principaux programmes :
 Le programme de subventions aux associations environnementales : piloté par le DDD,
  ce programme est fondé sur l’apport d’appui aux projets associatifs visant la valorisation
  et la protection de l’environnement. Ainsi, à fin 2023, le DDD a financé 179 projets
  associatifs dont 16 % sont portés par des femmes, ce qui a nécessité la mobilisation d’un
  budget totalisant 3,8 millions de dirhams.
 Le programme d’appui à la société civile en partenariat avec le programme de Micro-
  Financement pour l’Environnement Mondial (PEM/FEM). Ce programme apporte un
  appui aux projets portés par les femmes rurales et qui sont en mesure de contribuer à
  l’amélioration de leur cadre de vie. La part de projets portés par les femmes dans le total
  des projets appuyés en 2023 s’élève à 33,5%. De plus, un groupement d’intérêt
  économique (GIE) dont lequel les femmes sont majoritaires est actuellement en cours de
  formation ;
 Le programme pour l’Innovation dans les Technologies Propres et l’Emploi Vert «
  Cleantech Maroc » : lancé en partenariat entre le DDD, le Fonds pour l’Environnement
  Mondial (FEM) et l’Organisation des Nations Unies pour le Développement Industriel
  (ONUDI). Ce programme vise la promotion de l’entrepreneuriat vert, à travers
  l’organisation de compétitions annuelles ciblant les porteurs de projets dans les
  domaines liés à la valorisation des déchets, l’utilisation rationnelle de l’eau, l’efficacité
  énergétique, les énergies renouvelables, et les bâtiments verts. Les projets les plus
  innovants et présentant des perspectives de développement et de création d’emplois
  sont retenus pour bénéficier de Prix octroyés par ledit programme. Le programme
  intègre également un Prix intitulé « Women Lead Team » qui est dédié aux femmes
  entrepreneurs. Le bilan des réalisations de ce programme indique que 32% des mentors
  formés sont des femmes, 49% des demi-finalistes du programme sont des femmes et
  32% des finalistes sont des femmes ;
 Projets de biodiversité en partenariat avec le PNUD : le Département uvre actuellement
  en partenariat avec le PNUD pour le renforcement de l’alignement des objectifs
  nationaux de la biodiversité sur les cibles du Cadre Mondial de la Biodiversité Kunming-
  Montréal, notamment ses cibles 22 et 23, qui insistent sur la participation équitable,
  inclusive et effective des femmes à la prise de décision, ainsi que sur la prise en compte
  des questions liées à l’égalité des sexes dans la mise en uvre du CMB-KM moyennant
  l’application d’approche genre.




      60
           RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


     3. MINISTERE DE L’AMENAGEMEN T DU TERRITOIRE
        NATIONAL, DE L’URBAN ISME, DE L’HABITAT E T DE
        LA POLITIQUE DE LA V ILLE
L’année 2023 marque la réalisation d’une analyse genre du secteur de l’habitat et de la
politique de la ville dont les recommandations ont permis de mettre en place, en 2024, une
feuille de route pour l’institutionnalisation de la prise en compte de la dimension genre dans
la stratégie d’action du Ministère de l’Aménagement du Territoire National, de l’Urbanisme,
de l’Habitat et de la Politique de la Ville (MATNUHPV). La mise en uvre de cette feuille de
route ne peut que consolider la pratique de la BSG par le Ministère et conforter son
engagement en faveur de l’amélioration des conditions de vie des citoyennes et des citoyens
sur l’ensemble du territoire national.
3.1. Analyse genre : point de départ pour réussir une programmation
intégrant la dimension genre
Après l’élaboration, en 2019, d’un diagnostic genre de la politique de la ville en partenariat
avec l’ONU Femmes qui a permis la conception d'un guide référentiel pour des espaces
publics plus accessibles aux femmes et aux filles et la production, en 2020, d’un guide
pratique pour des espaces verts durables et accessibles à toutes et à tous, le MATNUHPV a
procédé, en 2023, à la réalisation d’une analyse genre du secteur de l’habitat et de la politique
de la ville dans le cadre d’un partenariat tripartite entre le Ministère, le CE-BSG et l’ONU-
Femmes43.
Les recherches et les réflexions qui ont jalonné cette analyse ont permis d’identifier 6
principaux enjeux liés à l’égalité de genre, à savoir :
      Modalités d’identification des bénéficiaires et d’attribution des offres amenées à
       intégrer davantage la dimension genre ;
      Nécessité de prendre en compte des besoins des femmes en matière d’accessibilité à
       l’information relative aux des démarches et aux procédures d’acquisition et d’utilisation
       des offres ;
      Persistance du biais de genre en matière d’accès aux crédits Fogarim pour le
       financement de l’acquisition des logements ;
      Utilité de consolider la concordance entre les offres et les besoins spécifiques des
       femmes (transport, sécurité et équipements…) ;
      Renforcement de l’implication des femmes dans le processus de prise de décision pour
       l’acquisition, l’usage et la gestion des offres;
      Nécessité de la prise en compte des préoccupations liées à l’égalité de genre dans les
       études des effets socio-économiques induits par les offres (phase post-réinstallation) ;
Tenant compte de ces enjeux, l’analyse a émis trois orientations stratégiques qui constituent
les fondements d’une intégration réussie de la dimension genre dans les stratégie d’action
du MATNUHPV. Ces axes portent sur ce qui suit :
 Axe 1 : Adoption des modes d’intervention privilégiant et formalisant davantage la
  dimension sociale des populations cibles au lieu des approches d’intervention techniques
  centrée sur les logements ;




43 Cette analyse a couvert 7 sites dans trois régions ciblées, en l’occurrence, Marrakech-Safi, Casablanca-Settat
et l'Oriental. Ces sites sont caractérisés par le déploiement d’un ou plusieurs programmes d'habitat et de politique
de la ville à savoir : Programme Villes sans bidonvilles, Programme du logement social, Programme du logement
social à faible valeur immobilière totale, Programme relatif à l’habitat menaçant de ruine et le Programme lié à la
valorisation des Ksours et Kasbah.


                                                                                                                 61
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


 Axe 2 : Elargissement de l’échelle d’intervention en privilégiant une approche d’action
  axée sur la dimension qualitative de « l’habitat » au lieu de celle centrée sur « le logement
  »;
 Axe 3 : Déploiement d’une véritable approche d’intervention collaborative, partenariale
  et managériale.
Partant des recommandations issues de l’analyse genre, une feuille de route pour
l’institutionnalisation de l’aspect genre dans la stratégie d’action du MATNUHPV a été
élaborée. Dès lors, des ateliers ont été organisés les 16 et 17 mai 2024 au Ministère en
partenariat avec le CE-BSG qui ont permis de développer un cadre logique pour la mise en
   uvre de ladite feuille de route durant les années 2024 et 2025. Ce cadre décline les activités
à mettre en place, leurs parties prenantes ainsi que les indicateurs de suivi du niveau de leur
réalisation et ce, selon 4 objectifs spécifiques à savoir :
    Objectif spécifique 1 : promouvoir l’institutionnalisation de l’intégration de la
     dimension genre dans les structures organisationnelles du MATNUHP et dans la
     gestion et la valorisation de ses ressources humaines ;
    Objectif spécifique 2 : promouvoir le partenariat avec le milieu professionnel et
     académique pour renforcer la prise en compte de la dimension genre dans le secteur ;
    Objectif spécifique 3 : mettre en place un cadre règlementaire régissant le secteur qui
     est sensible au genre ;
    Objectif spécifique 4 : renforcer la prise en compte du genre dans les programmes et
     projets du Ministère.
Pour s’assurer de l’opérationnalisation des activités inscrites dans le cadre logique associé à
la feuille de route pour l’institutionnalisation de l’intégration de la dimension genre dans la
stratégie d’action du MATNUHP, une note du Secrétariat Générale du Ministère a été
adressée à l’ensemble des structures du Département et des Organismes sous sa tutelle
sollicitant leur engagement dans la mise en uvre des activités qui leur incombent.
Dans le même cadre, un audit intra-organisationnel sous le prisme genre du MATNUHPV a
été mené en 2023. Cet audit avait pour objectif de recueillir un maximum d'informations,
auprès du personnel du Département, en lien avec leurs perceptions en rapport avec la prise
en compte de l’égalité de genre dans le fonctionnement interne de leurs structures. Cet audit
a révélé des défis liés, notamment, à la difficulté pour les femmes fonctionnaires de concilier
leur vie professionnelle et vie privée et à leur sous-représentation dans les postes de
responsabilité et dans les formations continues y compris dans les formations traitant des
thématiques liées à l’égalité de genre.
En parallèle à ces études et analyses entreprises pour renforcer l’ancrage systématique de la
dimension genre dans sa programmation, le MATNUHPV est en cours de finalisation d’un
système d’information « SMART-Conventionnement » qui est en mesure de produire des
données désagrégées par sexe des bénéficiaires de ses programmes.
3.2. Alignement des priorités en termes de rédu ction des inégalités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité de genre et l’autonomisation économique des
femmes
Les interventions du MATNUHPV, qui intègrent la mise à disposition d’une offre de logement
décent diversifiée et abordable, la rénovation des bâtiments menaçant ruine et la mise à
niveau urbaine, visent à rehausser la qualité du cadre de vie de l’ensemble des citoyennes et
citoyens et à garantir l’égalité des chances en termes d’accès aux services convenables de
logement et d’urbanisme sans distinction aucune. Ces interventions sont amenées à prendre
davantage les questions liées à l’égalité de genre à la lumière de l’opérationnalisation


    62
             RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


progressive de la feuille de route pour l’institutionnalisation de l’intégration de la dimension
genre dans la stratégie d’action du Ministère.
Il est à mentionner, dans ce sillage, le lancement en 2024 d’un nouveau programme d’aide
pour l’accès au logement, en réponse aux Orientations Royales insistant sur le déploiement
des efforts nécessaires pour renforcer la capacité des citoyen.e.s, particulièrement, ceux et
celles des classes sociales à faible revenu et de la classe moyenne à accéder à un logement
décent. Ce programme, qui s’aligne parfaitement sur la vision du MATNUHPV s’étale sur la
période 2024-2028 et repose sur un dispositif d’octroi d’aide financière directe à
l’acquéreur/se (marocain.e.s résidant au Maroc ou à l’étranger qui ne sont pas propriétaires
au Maroc et qui n’ont jamais bénéficié d’une aide au logement). Les montants d’aides
financières ainsi établies différent, en fonction de la valeur de logement à acquérir. En effet,
une aide financière directe de 100.000 dirhams est accordée pour l’acquisition d’un logement
dont le prix de vente est inférieur ou égal à 300.000 dirhams et de 70.000 dirhams en cas
d’achat d’un logement dont la valeur est comprise entre 300.000 dirhams 700.000 dirhams.
Il est à noter que dès le lancement de l’opérationnalisation de ce programme jusqu’ au 30
septembre 2024, le nombre de demandes pour bénéficier de l’aide directe au logement
réceptionnées par le biais de la plateforme « Daam Sakane » a atteint 104.560 demandes.
Près de 24.238 demandeurs/ses ont effectivement bénéficié de cette aide dont 45% sont des
femmes.
De même, le MATNUHPV poursuit son engagement pour renforcer l’accessibilité des femmes
et des filles aux espaces publics urbains, à travers des formations et de l’accompagnement
des acteurs locaux et aménageurs urbains en matière d’intégration la dimension genre dans
les projets d’aménagements urbains. De plus, le Ministère est activement impliqué, au regard
de ses missions et attributions, à assurer un développement territorial qui répond aux besoins
des citoyennes et des citoyens selon une approche participative et ce, afin de poser les jalons
d’un aménagement durable et inclusif des territoires.
Ce faisant, ces chantiers lancés par le MATNUHPV sont amenés à consolider son implication
dans la concrétisation des objectifs assignés au PGE III, en termes d’amélioration des
conditions de vie des femmes, de la protection de leurs droits et de leur autonomisation
économique.
3.3. Chaîne de résultats sensibles au genre : application de la démarche
performance sensible au genre
Conformément à la circulaire du Chef du Gouvernement (n°4/2024) relative à
l’établissement des propositions de Programmation Budgétaire Triennale assortie des
objectifs et des indicateurs de performance au titre de la période 2025-2027, le MATNUHPV
a élaboré une chaîne des résultats sensible au genre44 qui couvre ses 6 programmes
budgétaires, en l’occurrence, le programme portant sur l’aménagement du territoire national,
celui dédié à l’urbanisme et l’architecture, celui lié à l’habitat et la promotion immobilière,
celui relatif à la politique de la ville et appui au développement territorial, celui consacré à la
gouvernance et l’encadrement du secteur, ainsi que le programme relatif au soutien et aux
services polyvalents.
C’est dire que la dimension genre est désormais ancrée dans l’ensemble des programmes
d’action du Ministère et ce, conformément aux recommandations de l’analyse genre du
secteur et en ligne avec la feuille de route développée pour l’institutionnalisation de l’aspect
genre dans la stratégie d’action du Ministère (voir tableau qui suit).




44
     Ladite chaîne de résultats sensibles au genre est en cours de finalisation.



                                                                                                63
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


                                                                                                Réalisations  LF
   Programmes             Objectifs               Indicateurs            Sous-indicateurs
                                                                                                   2023      2024
                     Appui        à    la
                                                                       Nombre d’outils de
                     planification
                                                                       planification
                     stratégique            Nombre       d’outils  de
                                                                       territoriale
                     territoriale et à la   planification territoriale                              12
                                                                       stratégique réalisés
                     convergence      des   stratégique réalisés
 Aménagement du                                                        intégrant l’approche
                     interventions
 territoire national                                                   de genre
                     publiques
                     Promotion de la
                                                                        Taux de projets de
                     cohésion      et  la   Taux de projets       de
                                                                        territoire  élaborés        7%
                     valorisation     des   territoire élaborés
                                                                        sensibles au genre
                     territoires
                                                                     Taux             des
                                                                     équipements publics
                     Développement          Taux des espaces publics programmés par les
   Urbanisme et      durable d’une offre projetées par les plans plans
                                                                                                    9%
   architecture      territoriale planifiée d’aménagement            d’aménagement
                     d’investissement       homologués               homologués        en
                                                                     tenant compte de
                                                                     l’approche genre
                                            Taux     d’accès    aux
     Habitat et
                     Faciliter l’accès au programmes             de Taux d’accès au
     promotion
                     logement               logements    aidés  par logement par sexe
    immobilière
                                            l’Etat
  Politique de la
                     Renforcer              Taux de mise en uvre
 ville et appui au                                                      Taux    de    projets
                     l’intégration urbaine des Projets de Politique
 développement                                                          sensibles au genre
                     et l’inclusion sociale de la Ville
     territorial
                                            Taux de diplomation au
                     Développer       la    niveau                des
                     formation    et  la    établissements
                     recherche au sein      d’enseignement
                     des établissements     supérieur relevant du
 Gouvernance et
                     d’enseignement         ministère par sexe
 encadrement du
                     supérieur   et  de     Taux de diplomation au
     secteur
                     formation              niveau                des
                     professionnelle        établissements         de
                     relevant        du     formation
                     ministère              professionnelle relevant
                                            du ministère par sexe
                    Institutionnaliser
                    une         fonction
                                          Taux d’accès des femmes
Soutien et services publique équitable
                                          aux      postes      de                                  38%
   polyvalents      basée      sur     un
                                          responsabilité
                    système            de
                    compétences
                                                                                                Source : DHPV, 2024

   Tableau 30 : Chaîne de résultats sensibles au genre relative au MATNUHPV
En relation avec les efforts entrepris par MATNUHPV pour le renforcement de l'accessibilité
des projets de mise à niveau urbaine à toutes et à tous, l’année 2023 a été marquée par
l’organisation d’ateliers régionaux de formation et de renforcement des capacités en matière
d’intégration de la dimension genre dans le cadre de projets d’aménagements urbains au
profit des acteurs locaux et aménageurs urbains. De plus, cette année a connu l’identification,
le lancement des études et la réalisation de plusieurs projets d’aménagements urbains
sensibles au genre à Larache, Imintanoute, Kalaa Maggouna, Dar El Gueddari, Tifelt, Tiznite,
Fès et Safi. Quant à la ville d’Agadir, un partenariat tripartite spécifique entre le Ministère,
l’ONU Femmes et la Mairie de la ville a été initié en vue de fournir un accompagnement et
une assistance technique pour rendre la ville plus accessible et sûre.




    64
         RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


   4. MINISTERE DU TRANSPORT ET DE LA LOGISTIQUE
Il est communément admis que la disponibilité d’une offre d’infrastructure et de service de
transport suffisamment développée, sûre et accessible contribue significativement à la
réduction des inégalités de genre et l’autonomisation des femmes. Conscient de ces enjeux
et dans la perspective de consolider l’intégration des préoccupations liées à l’égalité entre
les femmes et les hommes dans sa stratégie d’action, le Ministère du Transport et de La
Logistique (MTL) prévoit le lancement, en 2024, de sa première analyse genre relative à ses
domaines d’intervention.
4.1. Analyse genre : point de départ pour réussir une programmation
intégrant la dimension genre
Conscient de l’importance de la prise en compte des enjeux liés à la réduction des inégalités
de genre dans la stratégie d’action du MTL en vue de renforcer son rôle en tant qu’acteur clé
de la dynamique de développement que connait notre pays, le Ministère a acté, en 2024, les
travaux précédant le lancement de la réalisation d’une analyse genre du secteur des
transports en milieu rural, en partenariat avec CE-BSG et la Banque Mondiale. Cette analyse
a pour objectif d’établir un diagnostic détaillé des causes et des manifestations des inégalités
de genre dans le secteur du transport particulièrement dans le milieu rural, tout en procédant
à l’évaluation sous le prisme genre de l’ensemble des domaines d’intervention du Ministère
en la matière (volets législatif, réglementaire et programmatique).
4.2. Alignement des priorités en t ermes de réduction des inégalités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité de genre et l’autonomisation économique des
femmes
En attendant les résultats ainsi que les recommandations de l’analyse genre du secteur du
transport pour promouvoir l’égalité de genre dans le secteur du transport surtout rural, le
MTL ne cesse de déployer les efforts nécessaires pour renforcer la sécurité et l’adaptation
des infrastructures et des services de transports aux besoins spécifiques des femmes,
moyennant la mise place d’une panoplie de mesures dont, entre autres, la sensibilisation et
la formation et ce, en vue de soutenir et faciliter l’accès des femmes aux transports et
d’encourager leur emploi dans le secteur. Il est à rappeler à cet égard que le plan d’action de
la stratégie nationale de la sécurité intègre des actions au service de la protection de la
mobilité des femmes. Dès lors, les interventions du MTL en faveur de la promotion de l’égalité
de genre s’alignent sur ses engagements pris dans le cadre du PGE III, en termes de
renforcement de l’autonomisation économique des femmes et de leur protection contre
toute forme de violence.
4.3. Chaîne de résultats sensibles au genre : application de la démarche
performance sensible au genre
Conformément à la circulaire du Chef du Gouvernement (n°4/2024) relative à
l’établissement des propositions de Programmation Budgétaire Triennale assortie des
objectifs et des indicateurs de performance au titre de la période 2025-2027, le MTL a mis
en place une chaîne de résultats sensibles au genre qui couvre deux de ses programmes
budgétaires. Il s’agit du programme relatif à la conduite et au pilotage et celui portant sur le
transport terrestre et logistique auxquels sont adossés des objectifs, des indicateurs et des
sous indicateurs sensibles au genre (voir tableau ci-dessous).




                                                                                             65
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


                                                                                              Réalisations
Programmes         Objectifs              Indicateurs               Sous indicateurs                         LF 2024
                                                                                                 2023
                                                               Taux     de   fonctionnaires
                                                               bénéficiaires     de      la
                                   Taux de fonctionnaires      formation      continue    -        -          30%
                                   bénéficiaires   de     la   Femmes
                                   formation continue selon    Taux     de   fonctionnaires
                                   le sexe                     bénéficiaires     de      la
                                                               formation      continue    -        -          30%
            Institutionnaliser une                             Hommes
            administration                                     Homme jour formation -
Conduite et publique     équitable Homme jour formation        Femmes                              -          7.000
 Pilotage   égalitaire basée sur selon le sexe                 Homme jour formation -
            un     système      de                             Hommes                              -          11.000
            compétences                                        Taux de représentativité
                                                               des femmes aux postes de
                                   Taux de représentativité                                        -          36,6%
                                                               responsabilité au niveau
                                   des femmes aux postes
                                                               central
                                   de responsabilité (Chef
                                                               Taux de représentativité
                                   de division / Chef de
                                                               des femmes aux postes de
                                   services)                                                       -          11,6%
                                                               responsabilité au niveau
                                                               territorial
                                   Taux de réalisation de
                                   campagnes             de
                                   sensibilisation prenant                                         -          63%
                                   en compte la dimension
              Amélioration de la
  Transport                        genre
              sécurité routière en
 terrestre et                                                  Nombre           d’auteurs
              prenant en compte
  Logistique                                                   d’accidents de la route -        14.304        8.187
              les questions genre Nombre           d’auteurs
                                                               Femmes
                                   d’accidents de la route
                                                               Nombre           d’auteurs
                                   par sexe
                                                               d’accidents de la route -        188.627      110.123
                                                               Hommes
                                                                                                 Source : MTL, 2024

  Tableau 31 : Chaîne de résultats sensibles au genre mise en place par le M TL
Cette chaîne de résultat sensible au genre, qui traduit fidèlement les points d’ancrage actuels
de la dimension genre dans la stratégie d’action du MTL, est amenée à s’enrichir par les
éléments qui émaneraient de l’analyse genre du secteur du transport en perspective.


5. DEPARTEMENT CHARGE DE L’EAU
Le Département de l’Eau (DE) poursuit la mise en uvre de plusieurs actions d’envergure
pour la consécration de l’égalité de genre dans ses domaines d’actions, en s’alignant sur sa
Stratégie d’Institutionnalisation de l’Intégration du Genre dans le Secteur de l’Eau (SIIGSE)
et sur les impératifs liés au stress hydrique et aux changements climatiques.
5.1. Analyse genre : point de départ pour réussir une programmation
intégrant la dimension genre
Le DE dispose, à ce jour, de deux analyses genre de ses domaines d’intervention, une réalisée
en partenariat avec ONU Femmes qui a servi de base pour la conception de la SIIGSE et une
autre, élaborée en 2019, avec l’appui de l’AFD et du CE-BSG et dont l’objectif était d’enrichir
la chaîne de résultats sensible au genre du Département.




     66
          RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


5.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité de genre et l’autonomisation économique des
femmes
Au regard du défi majeur auquel est confronté notre pays en lien avec le stress hydrique, il
est impératif, comme souligné par Sa Majesté le Roi à l’occasion du 25ème anniversaire de
l’accession du Souverain au Trône, de repenser et de mettre à jour les leviers de la politique
nationale de l’eau. A cet effet et en réponse aux Orientations Royales, l’intégration de
l’approche genre dans les programmes afférents à la politique de l’eau, en s’inspirant des
acquis cumulés de l’opérationnalisation de la SIIGSE, ne peut que consolider la pertinence de
cette politique et la fiabilité des mesures engagées et prévues.
La mobilisation et l’engagement du DE pour passer à un nouveau palier d’action à la hauteur
de ces défis et attentes est aussi un gage du Département pour renforcer son implication
dans le PGE III, particulièrement, ses axes relatifs à l’autonomisation des femmes et à la
protection de leurs droits et bien être.
5.3. Chaîne de résultats sensibles au genre : application de la démarche
performance sensible au genre
Conformément à la circulaire du Chef du Gouvernement (n°4/2024) en date du 15 mars 2024
relative à l’établissement des propositions de Programmation Budgétaire Triennale assortie
des objectifs et des indicateurs de performance au titre de la période 2025-2027, le DE a
développé une chaîne de résultat associée à son programme budgétaire relatif à l’eau qui
intègre explicitement la dimension genre au niveau d’un seul sous-indicateur de
performance. Ce dernier, qui renseigne sur le pourcentage des femmes bénéficiaires de la
protection contre les inondations, est lié à l’objectif du programme « eau » visant à lutter
contre la pollution et participer à réduire les risques liés à l’eau (voir tableau ci-dessous).

                                                                                     Réalisations      LF
Programme        Objectifs             Indicateurs           Sous-indicateurs
                                                                                        2023          2024

                                   Proportion des zones
             Lutter contre la
                                   menacées par les       Pourcentage         des
             pollution        et
                                   inondations            femmes bénéficiaires de
    Eau      participer        à                                                       28,36%        29,58%
                                   bénéficiaires    des   la protection contre les
             réduire les risques
                                   opérations        de   inondations
             liés à l’eau
                                   protection
                                                                                             Source : DE, 2024

  Tableau 32 : Chaîne de résultats sensibles au genre mise en place par le DE
La prise en compte de la dimension genre à l’échelle d’un seul sous-indicateur de
performance ne reflète pas les efforts déployés et attendus du DE, en faveur de la promotion
de l’égalité de genre dans ses domaines d’intervention et dans ses structures
organisationnelles.




                                                                                                          67
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025



   6. MINISTERE DE LA SANTE ET DE LA PROTECTION
      SOCIALE
Le Ministère de la Santé et de la Protection Sociale poursuit ses efforts pour un ancrage
systématique de la dimension genre dans sa stratégie d’action, conformément aux principes
guidant le système national de santé déclinés dans le Dahir n°1-22-77 portant promulgation
de la loi-cadre n° 06-22 relative au système national de santé.
6.1 Analyse genre : Point de départ pour réussir une programmation
intégrant la dimension genre
En plus de l’analyse genre du secteur de la santé réalisée par le MSPS, entre 2019 et 2020,
avec l'appui du CE-BSG et de l'AFD, le Ministère a procédé à l’élaboration d’un « Référentiel
genre et santé » dans le cadre de la troisième phase du programme d’appui de l’Union
Européenne à la réforme du secteur de la santé. Ce référentiel a pour objectifs de faciliter la
compréhension des dimensions liées à la prise en compte l’égalité de genre dans le domaine
de la santé et de mettre à la disposition des responsables du Ministère des outils pratiques
facilitant l’intégration de la dimension genre dans les stratégies et les programmes
prioritaires de santé. Ce référentiel cible l’ensemble des structures et des professionnel.le.s
de santé aux niveaux central et régional ainsi que les professionnel.le.s en charge de la
programmation et de la budgétisation.
De même, le Ministère procède à l’alimentation continue de son système d’information,
moyennant un certain nombre d’enquêtes qui tiennent compte de l’aspect genre. Il est à
noter à cet égard le Ministère a lancé les préparatifs pour la réalisation de la septième
Enquête Nationale Population et Santé de Famille (ENPSF) au titre de l’année 2024 qui
prévoit la prise en compte de la dimension genre.
En outre, dans le cadre de la mise en uvre du quatrième pilier de la réforme du secteur
relatif à la digitalisation du système de santé, le MSPS a lancé le projet de création d’un
système d’information intégré basé sur le dossier médical du patient.e. Ce système, grâce au
principe d’identifiant unique attribué à chaque patient.e, permettrait de collecter, de traiter
et d’exploiter toutes les informations essentielles liées à l’accès aux services de santé et les
intégrer aux autres systèmes de protection sociale de manière sûre et sécurisée. Ces
fonctionnalités sont amenées à générer des informations fiables désagrégées par sexe et
ainsi contribuer à l’élaboration d’analyses genre robustes et mises à jour, en mesure
d’appuyer la consolidation de la prise en compte de la dimension genre dans les actions du
Ministère.
 6.2 Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie du Département et les plans nationaux p our la
promotion de l’égalité de genre et l’autonomisation économique des
femmes
L’adoption de l’approche genre dans l’élaboration des politiques, des programmes et des
stratégies de santé est désormais un principe cadrant l’action du MSPS et ce, conformément
au Dahir n°1-22-77 portant promulgation de la loi-cadre n° 06-22 relative au système national
de santé entré en vigueur le 16 mars 2023. Dès lors, le Ministère s’est engagé dans plusieurs
programmes qui sont spécifiquement dédiés à l’égalité de genre et à l’autonomisation des
femmes, en l’occurrence, le programme national de la santé pour la prise en charge des
femmes et enfants victimes de violence, le programme de la santé maternelle et infantile et
d’autres. De plus, le Ministère uvre à la prise en compte des besoins spécifiques des femmes
et des hommes par rapport aux prestations des programmes de santé octroyés en lien avec
la surveillance épidémiologique, veille et sécurité sanitaires, prévention et contrôle des
maladies (stratégie intégrée sur les droits humains, le VIH/sida, la Tuberculose et les
hépatites virales 2024-2030) …


    68
           RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


Dans le même sillage, le MSPS est activement engagé à prendre en compte les
préoccupations relatives à la réduction des inégalités de genre et à la promotion de
l’autonomisation des femmes dans les prestations offertes dans le cadre de
l’opérationnalisation du chantier Royal relatif à la généralisation de la protection sociale et
ce, en termes d’accès à la couverture médical et aux aides sociales directes destinées aux
familles vulnérables (voir encadré ci-dessous).
                             Opérationnalisation des aides sociales directes
 Les aides sociales directes ont été instaurées, conformément aux Hautes Instructions Royales et en
 application des dispositions de la Loi-cadre n° 09.21 relative à la généralisation de la protection sociale.
 Ce régime national vise à améliorer les conditions de vie des familles ayant des enfants en âge d’être
 scolarisés ou celles en situation de fragilité et qui ne bénéficient actuellement d'aucune aide familiale, dans
 le but de leur offrir un filet de protection sociale et soutenir leur pouvoir d'achat. Les familles ciblées sont
 éligibles à un soutien financier qui varie, selon la composition de chaque famille et la situation de ses
 membres et qui est conditionné par la satisfaction des critères d’éligibilité et la vérification d’un seuil
 déduit du Registre Social Unifié (RSU). En effet, les grandes lignes cadrant l’opérationnalisation de l’octroi
 des aides familiales ont été définies par la Loi 58-23 entrée en vigueur à la fin de l’année 2023 et par ses
 décrets d’application.
 Il est à mentionner que ces aides sont scindées en deux catégories :
      Aides relatives à la protection contre les risques liés à l’enfance : ces aides sont constituées
       d’allocation mensuelle attribuée à la famille en fonction du nombre d'enfants de moins de 21 ans
       dans la limite de six enfants et d’allocations de naissance. Le montant de l’allocation mensuelle est
       alors déterminé en fonction de l'âge de l'enfant et de sa scolarisation. La famille continue, jusqu'à
       l'âge précité, de bénéficier de cette aide pour chaque enfant à charge, tant qu'elle remplit les
       conditions d'éligibilité au régime. Il est à noter qu’une aide mensuelle complémentaire est octroyée
       pour chaque enfant en situation de handicap sans limite en termes du nombre d’enfants par foyer
       et pour chaque enfant orphelin de père (trois premiers enfants) au profit des veuves avec enfants.
       Les détails relatifs à ces allocations mensuelles sont déclinés dans le tableau qui suit :
   Les enfants moins de 5 ans et les
                                         Les enfants non scolarisés âgés
   enfants scolarisés âgés de 6 ans a                                             Les veuves avec enfants
                                                    de 6 à 21 ans
                  21 ans
  Pour les trois premiers enfants :      Pour les trois premiers enfants      Pour les trois premiers enfants :
  - 200 dirhams pour chaque enfant - 150 dirhams pour chaque enfant - 350 dirhams pour chaque
  dès décembre 2023                      dès décembre 2023                    enfant dès décembre 2023
  - 250 dirhams pour chaque enfant à - 175 dirhams pour chaque entant - 375 dirhams pour chaque
  partir de 2025                         à partir de 2025                     enfant dès 2025
  - 300 dirhams pour chaque enfant - 200 dirhams pour chaque - 400 dirhams pour chaque
  partir de 2026                         enfant à partir de 2026              enfant à partir de 2026
  Du quatrième au sixième enfant :       Du quatrième au sixième enfant :     Du quatrième au sixième enfant :
  36 dirhams pour chaque enfant          24 dirhams pour chaque enfant        36 dirhams pour chaque entant
  Les enfants en situation de handicap, scolarisés ou non scolarisés, reçoivent une aide supplémentaire de 100
  dh.
                                                     Source : Portail dédiées aux aides sociales directes -www.asd.ma-

         Quant aux allocations de naissance, elles sont accordées en une seule fois à chaque famille éligible,
         à l'occasion des deux premières naissances, indépendamment du nombre de nouveaux-nés à
         chaque naissance. La famille éligible à cette allocation bénéficie de 2.000 dirhams pour la
         première naissance et de 1.000 dirhams pour la deuxième.
      Aide forfaitaire : cette aide forfaitaire d’un montant de 500 dirhams par mois est attribuée aux
       familles sans enfants ou ayant des enfants de 21 ans et plus. Les contions d’éligibilité à ces aides
       insistent sur la nécessité que le chef de famille et les membres de la famille concernée soient
       marocains résidants au Maroc, qu’ils soient inscrits au Registre Social Unifié, que l’'indice socio-
       économique du ménage, calculé au niveau du Registre Social Unifié, soit inférieur au seuil
       d'éligibilité du régime des aides sociales directes (ce seuil est fixé à 9,743001 selon le décret
       d’application de la Loi 58.23).
 Il y a lieu de mentionner qu’il n’est pas permis de cumuler entre l’aide liée à la protection contre les risques
 liés à l’enfance et l’aide forfaitaire.




                                                                                                                   69
   PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


   En termes de réalisations, le nombre des bénéficiaires de ces aides a atteint, au titre du mois de septembre
   2024, plus de 3,9 millions de familles. Il est important de mentionner que le mondant de cette aide sera
   valorisé, à partir de janvier 2025, pour s’établir à 250 dirhams pour chacun des trois premiers enfants
   scolarisés, ou âgés de moins de 6 ans. Pour les enfants en situation de handicap, cette aide se situerait à
   350 dirhams. Pour ce qui est des enfants non scolarisés, le montant de l’aide serait de 175 dirhams. Quant
   aux enfants orphelins du père, âgés de moins de six ans ou qui poursuivent leurs études, cette aide
   s'élèvera à 375 dirhams pour chacun des trois premiers enfants. Ceci dit, le montant minimum de l’aide
   forfaitaire à allouer à chaque famille éligible sera maintenu à 500 dirhams par mois. Dès lors, le coût du
   programme des aides sociales se situerait à 26,5 milliards de dirhams à l'horizon 2025.


  Par ailleurs, il y a lieu de signaler, que le MSPS uvre à l’intégration des thématiques traitant
  les différentes dimensions liées à l’égalité de genre et à la lutte contre la violence faites aux
  femmes et aux enfants dans les programmes de formation de base et de formation continue.
  Ces programmes et projets engagés et prévus par le MSPS s’alignent parfaitement sur les
  objectifs du PGE III au titre de la période de 2023-2026, en termes de renforcement de
  l’autonomisation des femmes et de lutte contre les violences basées sur le genre.
  6.3 Chaîne de résultats sensibles au genre : application de la démarche
  de performance sensible au genre
  Conformément à la LOF et aux dispositions à la circulaire du Chef du Gouvernement
  (n°4/2024) relative à l’établissement des propositions de Programmation Budgétaire
  Triennale assortie des objectifs et des indicateurs de performance au titre de la période
  2025-2027, le MSPS a développé une chaîne de résultats sensibles au genre qui couvre les
  programmes relatifs aux ressources humaines et renforcement des capacités du système de
  santé, à la planification, programmation, coordination et soutien des missions du système de
  santé, à la santé reproductive, santé de la mère, de l'enfant, du jeune et des populations à
  besoins spécifiques, à la surveillance épidémiologique, veille et sécurité sanitaires, prévention
  et contrôle des maladies et aux actions et prestations de soins primaires, pré-hospitaliers et
  hospitaliers (voir tableau ci-dessous).
                                                                                                                                                   Réalisations    LF
Programmes                                                         Objectifs                    Indicateurs               Sous-indicateurs
                                                                                                                                                      2023        2024
                                                          Optimiser la gestion des       Part    des   postes    des   Pourcentage des postes         79%         75%
   Ressources humaines et renforcement des capacités du




                                                          établissements de santé        médecins généralistes et      occupés par des femmes
                                                          ainsi que leur dotation en     des infirmiers polyvalents
                                                          ressources        humaines     affectés aux établissements   Pourcentage des postes          21%        25%
                                                          qualifiées et motivées pour    de santé en milieu rural et   occupés par des hommes
                                                          une meilleure offre de soins   dans les zones enclavées.
                                                                                         Nombre des lauréats des       Part des lauréates des         80%         80%
                                                                                         Instituts Supérieurs des      ISPITS
                                                                                         Professions Infirmières et
                                                                                                                       Part des   lauréats   des      20%         20%
                    système de santé




                                                                                         Techniques      de    Santé
                                                                                                                       ISPITS
                                                                                         (ISPITS)
                                                          Augmenter la capacité de
                                                                                                                       Part des fonctionnaires
                                                          formation de base et les
                                                                                                                       femmes bénéficiaires des                   56%
                                                          bénéficiaires    de    la                                                                   65%
                                                                                                                       sessions de la formation
                                                          formation continue        Nombre de fonctionnaires
                                                                                                                       continue
                                                                                    bénéficiaires des sessions
                                                                                                                       Part des fonctionnaires
                                                                                    de la formation continue
                                                                                                                       hommes bénéficiaires des
                                                                                                                                                      35%         44%
                                                                                                                       sessions de la formation
                                                                                                                       continue

                                                          Améliorer les conditions de
                                                                                      Part des Femmes nommées
                                                          travail des fonctionnaires                                                                  24%         27%
                                                                                      pour occuper des postes de
                                                          avec     l’intégration   de
                                                                                      responsabilité
                                                          l’approche genre




                                              70
                                                              RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


                                                                                                                               Pourcentage des femmes         50%       50%
système de santé
 programmation,
 coordination et


                                                                                                                               bénéficiaires de l’AMO
  Planification,



   missions du
   soutien des



                                                                                              Pourcentage      de      la
                                                              Généraliser   la   protection
                                                                                              population bénéficiaire de
                                                              sociale
                                                                                              l’AMO                       Pourcentage des hommes              50%       50%
                                                                                                                          bénéficiaires de l’AMO


                                                                                              Nombre de régions qui ont
    Santé reproductive, santé de la mère, de




                                                                                              implanté     le     dépistage
     l'enfant, du jeune et des populations à




                                                                                                                                                                6        7
                                                                                              néonatal de l’hypothyroïdie
                                                                                              congénitale
                                                              Améliorer la santé de la
                                                                                              Nombre de sorties réalisées
                                                              mère     et   la   santé
                                                                                              par les Unités Sanitaires                                       11.146   13.000
                besoins spécifiques




                                                              reproductive
                                                                                              Mobiles
                                                                                              Taux     d’utilisation     des
                                                                                              méthodes contraceptives                                         9,61%     16%
                                                                                              modernes
                                                              Assurer     l’accès     aux     Effectif    des       femmes
                                                              prestations sanitaires pour     victimes    de       violences
                                                              les populations à besoins       fondées sur le genre prises
                                                              spécifique notamment les        en charge au niveau des
                                                              personnes en situation du       unités intégrées de prise en                                    31.779   30.500
                                                              handicap, les personnes         charge des femmes et
                                                              âgées et les femmes et          enfants      victimes       de
                                                              enfants     victimes     de     violence implantées dans
                                                              violences                       les hôpitaux
                                                                                                                               Pourcentage des femmes
           Surveillance épidémiologique, veille et sécurité
           sanitaires, prévention et contrôle des maladies




                                                                                                                               vivant    avec    le    VIH    95%       94%
                                                                                              Pourcentage de personnes         recevant un traitement
                                                                                              (adultes et enfants) vivant      antirétroviral
                                                                                              avec le VIH recevant un          Pourcentage des hommes
                                                                                              traitement antirétroviral        vivant    avec    le    VIH    93%       94%
                                                                                                                               recevant un traitement
                                                                                                                               antirétroviral
                                                                                                                               Taux        de       succès
                                                                                                                               thérapeutique      de     la   88%       92%
                                                              Renforcer la prévention et Taux       de      succès             tuberculose toute forme
                                                              le contrôle des maladies   thérapeutique    de    la             (TTF) pour les femmes
                                                                                         tuberculose toute forme               Taux        de       succès
                                                                                         (TTF)                                 thérapeutique      de     la   88%       92%
                                                                                                                               tuberculose toute forme
                                                                                                                               (TTF) pour les hommes
                                                                                                                               Taux de participation au
                                                                                                                               dépistage du cancer du                   40%
                                                                                              Taux de participation au         sein en milieu urbain
                                                                                              dépistage du cancer du sein      Taux de participation au
                                                                                                                               dépistage du cancer du                   40%
                                                                                                                               sein en milieu rural
                                                                                                                               Taux de réponse aux
prestations de soins




                                                                                                                               requêtes médico-sociales
                                                                                                                                                              66%       87%
  primaires, pré-

   et hospitaliers




                                                                                          Taux de réponse aux                  émanant des particuliers
    hospitaliers
     Actions et




                                                                                          requêtes médico-sociales             et différentes institutions
                                                                                          émanant des particuliers et          (Femmes)
                                                                                          différentes   institutions           Taux de réponse aux
                                                              Améliorer l’accès aux soins
                                                                                          selon le sexe                        requêtes médico-sociales
                                                              et la prise en charge
                                                                                          (homme-Femme)                        émanant des particuliers       67%       92%
                                                              hospitalière
                                                                                                                               et différentes institutions
                                                                                                                               (Hommes)
                                                                                                                                                       Source : MSPS, 2024

       Tableau 33 : Chaine de résultats se nsibles au genre mise en place par le MSPS


                                                                                                                                                                       71
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


Ce faisant, la chaine de résultats sensibles au genre adoptée par le MSPS traduit les leviers
d’actions engagés en faveur de la promotion d’un accès équitable des femmes et des
hommes aux soins et aux services de santé, à la prévention contre les maladies et à la
couverture médicale.
Il est important de noter, à cet égard, que le taux global de la population bénéficiaire de
l’Assurance Maladie Obligatoire (AMO) se rapproche à grand pas de la cible ultime qui est
celle de la généralisation de la couverture médicale. Il est à rappeler l’année 2023 a été
marquée par l’entrée en vigueur de l’AMO au profit des personnes ne pouvant pas s’acquitter
des cotisations (AMO-TADAMON) et à la mise en            uvre de l’AMO des travailleurs non-
salariés (AMO-TNS). Force est de noter que la part des femmes dans la population totale
bénéficiaire de l’AMO a atteint, au titre de l’année 2023, près de 50%.
De même, cette chaîne de résultats reflète les efforts déployés par le MSPS pour la prise en
charge des femmes et des enfants victimes de violence dans le cadre du programme national
de la santé pour la prise en charge des femmes et enfants victimes de violence. Il est à
mentionner, dans ce sens, que l’effectif des femmes victimes de violences fondées sur le
genre prises en charge au niveau des unités intégrées de prise en charge des femmes et
enfants victimes de violence implantées dans les hôpitaux a atteint, en 2023, près de 31.779
femmes.
En outre, ladite chaîne met, également, en exergue les résultats des actions entreprises en
matière de renforcement de l’accès des femmes à la formation ainsi qu’aux postes de
responsabilité. Ainsi, la part des femmes dans les postes des médecins généralistes et des
infirmiers polyvalents affectés aux établissements de santé en milieu rural et dans les zones
enclavées a avoisiné, en 2023, près de 79%, soit plus que la parité. Quant à la part des
lauréates des Instituts Supérieurs des Professions Infirmières et Techniques de Santé (ISPITS)
dans le total des lauréats, il s’est établi à 80%. Toutefois, la part des femmes dans les postes
de responsabilités ne dépasse pas 24% au titre de l’année 2023.
6.4 Progrès législatif, réglementaire et institutionnel en faveur de la
promotion de l’égalité de genre
En plus des Lois adoptées et mises en              uvre durant l’année 2023 pour consolider
l’opérationnalisation du chantier Royal portant sur la généralisation de la protection sociale,
l’année 2024 a été marquée par l’entrée en vigueur de l’AMO-ACHAMIL qui est un régime de
couverture médicale dédié au profit des personnes n’exerçant aucune activité rémunérée ou
non rémunérée et capable de s’acquitter des cotisations de l’AMO et n’appartenant à aucun
autre régime AMO et ce, en application des dispositions la Loi n°21.24 (publiée dans le
bulletin officiel du 22 août 2024). A cet effet, le nombre des bénéficiaires du régime « AMO-
TADAMON » a atteint, à fin août 2024, plus de 11,3 millions de bénéficiaires et les régimes
«AMO-TNS» et «AMO-ACHAMIL» ont donné la possibilité, à près de 11 millions d’individus,
d’adhérer à l’AMO.




    72
           RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


     7. DEPARTEMENT     CHARGE    DE                                                  L’EDUCATION
        NATIONALE ET DU PRESCOLAIRE
Le Département de l’Education Nationale et du Préscolaire (DENP) poursuit le déploiement
des programmes et des projets inscrits dans le cadre de la feuille de route du système
éducatif (2022-2026) qui ambitionne de garantir un accès équitable aux filles et aux garçons
à une école de qualité. Ce faisant, le département joue un rôle central dans la valorisation du
capital humain des femmes qui est un prérequis incontournable à même de promouvoir leur
autonomie et la protection de leurs droits.
7.1. Analyse genre : Point de départ pour réussir une programmation
intégrant la dimension genre
En 2019, une analyse genre des domaines d’interventions du DENP a été réalisée avec l’appui
de l’Expertise France et de l’AFD. Cette étude, effectuée dans le cadre du programme de
l’Union Européenne pour la mise en uvre du PGE II, a permis d’identifier les principales
facettes des inégalités de genre dans le secteur de l’éducation nationale et de mettre en
lumière les principaux leviers d’action pour les réduire.
Il est important de noter à cet égard que le DENP, grâce à son système d’information «
MASAR » riche en informations et régulièrement alimenté et qui couvre l’ensemble des
dimensions liées au système éducatif national y compris la dimension genre, dispose d’un
grand atout lui permettant de réaliser une diversité d’analyses qui intègrent la dimension
genre (recueil des statistiques de l’éducation nationale, tableaux de bord…).
7.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité de genre et l’autonomisation économique des
femmes
La stratégie d’action du DENP se focalise sur l’opérationnalisation des programmes et projets
inscrits dans la feuille de route du système éducatif national au titre de la période de 2022 à
202645. Il est à rappeler que cette feuille de route s’aligne sur les dispositions de la Loi-Cadre
n° 51-17 relative au système d’éducation, de formation et de recherche scientifique, qui a
érigé les principes d'égalité des chances et d’équité au rang des principes fondamentaux
cadrant la philosophie du travail et le fonctionnement du système éducatif.
Dès lors, les interventions du DENP dans le cadre du déploiement de la feuille de route du
système éducatif national constituent les domaines d’action pris en charge par le
département dans le cadre de la mise en uvre du PGE III. En effet, le DENP est impliqué
dans l’opérationnalisation des trois programmes stratégiques du Plan (autonomisation
économique des femmes et leadership, prévention et protection des femmes et promotion
des droits des femmes), moyennant 18 mesures déclinées en 45 activités.
7.3. Chaine de résultats sensibles au genre : application de la démarche
performance sensible au genre
En ligne avec les dispositions de la circulaire du Chef du Gouvernement (n°4/2024) relative
à l’établissement des propositions de Programmation Budgétaire Triennale assortie des
objectifs et des indicateurs de performance au titre de la période 2025-2027, le DENP a mis

45 La feuille de route pour la réforme du système éducatif national pour la période 2022-2026 définit trois axes
principaux : l’élève, l’enseignant et l’établissement scolaire. Cette stratégie ambitieuse aspire à réaliser trois
objectifs stratégiques d’ici 2026, à savoir : la réduction de 30% de la déperdition scolaire, la consolidation de
l'apprentissage des savoirs et des compétences et les apprentissages de base au cycle primaire et la consécration
de l'ouverture et des valeurs de citoyenneté en portant au double le pourcentage des élèves bénéficiaires des
activités parascolaires. Les détails relatifs à cette feuille de route sont déclinés dans l’édition 2024 du Rapport
sur le Budget axé sur les Résultats tenant compte de l’aspect genre.


                                                                                                                73
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


en place une chaîne de résultats sensibles au genre qui concerne 3 de ses programmes
budgétaires dédiés à la gouvernance du système de mobilisation des acteurs, à l’équité,
l’égalité et l’obligation de la scolarité ainsi qu’à l’enseignement qualifiant et post secondaire
pour la promotion de l’individu et de la société.
7.3.1. Chaine de résultats sensibles au genre mise en place par le département
La chaîne de résultats sensibles au genre développée par le DENP assure le suivi du degré
de la mise en uvre des efforts déployés par le département en faveur de la réduction des
inégalités de genre en matière d’accès au préscolaire, aux cycles primaire, collégial et
qualifiant ainsi qu’aux services d’appui social (voir tableau ci-dessous).
Ainsi, le degré de concrétisation des objectifs du programme relatif à l’équité, l’égalité des
chances et l’obligation de scolarité est approché par plusieurs sous indicateurs de
performance sensibles au genre qui renseignent, entre autres, sur le taux net de scolarisation
des filles au préscolaire (77% en 2023), l’indice de parité global filles/garçons au préscolaire
(1,02 en 2023), le taux net de scolarisation des filles au primaire (100% en 2023), le taux net
de scolarisation des filles au collégial (80,7% en 2023), le nombre des filles du cycle collégial
bénéficiaires des services de l’appui social…
Quant au programme dédié à l’enseignement qualifiant et post-secondaire pour la
promotion de l'individu et de la société, le degré de réalisation de son objectif visant à
garantir aux élèves la poursuite de leurs études au secondaire qualifiant est mesuré par une
multiplicité de sous-indicateurs prenant en compte la dimension genre à l’instar du taux net
de scolarisation des filles au qualifiant (52,7% en 2023), le nombre des filles du cycle
qualifiant bénéficiaires des services de l’appui social, le nombre d’élèves filles ayant
abandonné au qualifiant,…
De même, cette chaîne reflète l’état d’avancement des actions entreprises par le
département pour l’institutionnalisation de l’approche genre au niveau du système éducatif
relevant du programme lié à la gouvernance du système et à la mobilisation des acteurs.
Ces mesures portent, essentiellement, sur l’organisation des formations sur des thématiques
liées à la lutte contre la violence fondée sur le genre au profit des responsables des
établissements scolaires (près de 30% des responsables des établissements scolaires ont
bénéficié de ces formations en 2023) et sur le renforcement de l’accès des femmes aux
postes de responsabilité.

                                                                                                    Réalisations    LF
Programmes                 Objectifs             Indicateurs              Sous-indicateurs
                                                                                                       2023        2024

                                           Part des responsables des
 Gouvernance du

 mobilisation des




                                           établissements scolaires
                                           bénéficiaires formés à la                                   30%          32%
   système et




                       Institutionnaliser
     acteurs




                                           lutte contre la violence
                       l'approche genre
                                           basée sur le genre
                       au     niveau    du
                       système éducatif Taux de représentativité
                                          de la femme dans les                                           -         18,61%
                                          postes de responsabilité

                                                                    Taux net de scolarisation
 Equité, égalité des




                                          Taux net de scolarisation                                    77%          81%
                                                                    filles au préscolaire
   obligation de




                       Accélérer       la au préscolaire (4ans à
    chances et




                                                                    Indice de parité global
      scolarité




                       généralisation du 5ans)                                                          1,02         1
                                                                    filles/garçons au préscolaire
                       préscolaire pour
                                                                    Nombre        d'enfants  par
                       les enfants de 4-5                                                                           22
                                          Nombre d'enfants par      éducatrice   rural
                       ans
                                          éducatrice                Nombre        d'enfants  par
                                                                                                                     21
                                                                    éducatrice urbain




         74
                              RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


                                                                              Taux net de scolarisation
                                                                                                                    100%         81%
                                                    Taux net de scolarisation filles –total-
                                                    au primaire               Indice          de     parité
                                                                                                                       1           1
                                 Scolariser                                   filles/garçons
                                 l’ensemble     des                           Nombre        d’élèves ayant
                                 élèves à la fin du                           abandonnés au primaire -                          32.714
                                 cycle primaire     Nombre d’élèves ayant filles-
                                                    abandonnés au primaire    Nombre        d’élèves ayant
                                                                              abandonnés au primaire -                          35.048
                                                                              garçons-
                                                                                   Taux net de scolarisation
                                                                                                                    80,7%        81%
                                                                                   des filles -total-
                                                       Taux net de scolarisation Taux net de scolarisation
                                                       au collégial                                                 74,7%        79%
                                                                                 garçons –total-
                                                                                 Indice          de       parité
                                 Garantir         la                                                                 0,95          1
                                                                                 filles/garçons global
                                 scolarisation     à   Nombre de bénéficiaires Nombre de bénéficiaires
                                 tous les élèves de    des services de l’appui des services de l’appui                          67.811
                                 l'enseignement        social au collégial       social –filles-
                                 collégial                                       Nombre       d’élèves     ayant
                                                                                 abandonnés au collège -                       48.000
                                                       Nombre d’élèves ayant filles-
                                                       abandonnés au collège     Nombre       d’élèves     ayant
                                                                                 abandonnés au collège -                        94.223
                                                                                 garçons-
                                                                                 Taux net de scolarisation
                                                                                                                    52,7%        54%
 Enseignement qualifiant et

 promotion de l'individu et




                                                       Taux net de scolarisation filles total
  post-secondaire pour la




                                                       au qualifiant             Taux net de scolarisation
                                                                                                                    38,1%        40%
                                                                                 garçons total
                                 Garantir       aux
       de la société




                                                       Nombre de bénéficiaires Nombre des bénéficiaires
                                 élèves           la
                                                       des services de l’appui des services de l’appui                          41.249
                                 poursuite de leurs
                                                       social au qualifiant      social au qualifiant-filles-
                                 études          au
                                                                                 Nombre       d’élèves     ayant
                                 secondaire
                                                                                 abandonnés au qualifiant -                    23.000
                                 qualifiant
                                                       Nombre d’élèves ayant filles-
                                                       abandonnés au qualifiant Nombre        d’élèves     ayant
                                                                                 abandonnés au qualifiant -                    34.000
                                                                                 garçons-
                                                                                                                   Source : DENP, 2024

       Tableau 34 : Chaines de résultats sensibles au genre mises en place par le
                                         DENP
7.3.2. Actions en faveur de la promotion d’égalité de genre non intégrées dans
les chaines de résultats sensibles au genre
En plus des leviers d’action mis en exergue dans sa chaîne de résultats sensibles au genre, le
DENP a entrepris d’autres programmes et projets visant la réduction des inégalités de genre
et la lutte contre la violence fondée sur le genre. Il s’agit des programmes et projets suivants
:
 Programme d’Education Non Formelle : à travers ce programme, le département a mis en
  place un plan d’action de remédiation individualisé pour les élèves à risque et assure la
  coordination des caravanes de mobilisation communautaires pour l’identification des
  enfants en rupture de scolarisation et l’inscription et le retour à l’école des déscolarisés.
  En 2024, le nombre d’établissements participants à l’opération caravane de mobilisation
  communautaire a atteint 7.555 établissements. Le nombre total d’enfants réinsérés, au
  titre de l’année scolaire 2023-2024, s’élève à 71.662 enfants dont 27.150 sont des filles ;
 Poursuite des efforts pour la lutte contre les violences basées sur le genre (VBG),
  moyennant la généralisation des cellules d'écoute dans tous les établissements scolaires


                                                                                                                                   75
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


  et le développement d'actions de sensibilisation et/ou d'éducation sur les risques, les
  conséquences des VBG et les dispositifs de protection et de prise en charge ciblant les
  élèves et leurs parents… ;
 Déploiement des actions de communication pour renforcer l’accès des filles à la
  scolarisation, par le biais de lancement d’actions médiatiques sur les effets néfastes du
  mariage des filles mineures et d’autres actions qui encouragent la scolarisation des filles…
 Projet d’insertion socioprofessionnelle des adolescentes et des jeunes en dehors du
  système éducatif et dans une situation de précarité: en partenariat avec l’UNICEF, ce projet
  a permis l’élaboration d’un plaidoyer pour la scolarisation des filles dans le milieu rural, la
  réalisation d’une enquête auprès des apprenantes et apprenants et de leurs parents sur
  leurs perceptions de l'égalité de genre, l’organisation de sessions de formation dans
  certaines AREF autour de l'approche genre et la masculinité positive…

   8. MINSITERE DE L’ENSEIGNEMENT SUPER IEUR ET DE
      LA RECHERCHE SCIENTI FIQUE ET DE L’INNOVATION
Le Ministère de l’Enseignement Supérieur, de la Recherche Scientifique et de l’Innovation
(MESRSI) s'est engagé résolument en faveur de la promotion de l'égalité de genre et de
l'inclusion sociale dans ses domaines d’action et ce, conformément à la vision cadrant le
Plan National d’Accélération de la Transformation de l’Ecosystème de l’Enseignement
Supérieur, de la Recherche Scientifique et de l’Innovation (ESRI) à l’horizon 2030 (PACTE
ESRI 2030).
8.1. Analyse genre : Point de départ pour réussir une programmation
intégrant la dimension genre
Au regard de l’indisponibilité, à ce jour, d’une analyse genre de ses domaines d’intervention,
le MESRSI prend appui sur les orientations stratégiques de son plan de transformation
(PACTE ESRI 2030) pour toute action visant la promotion de l’égalité de genre et de
l’inclusion sociale.
8.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité de genre et l’autonomisation économique des
femmes
Le plan de transformation de l’écosystème de l’ESRI à l’horizon 2030 (PACTE ESRI 2030)
est axé sur un socle de 6 valeurs fortes, à savoir : la transparence, l'éthique, l'excellence,
l'équité et l'égalité des chances, la résilience par la capacitation ainsi que l'ouverture. Ce
faisant, les préoccupations liées à l’égalité de genre sont, désormais, une partie intégrante
de la stratégie d’action du Ministère qui est amenée à être davantage prise en compte dans
l’ensemble de son périmètre d’intervention en relation avec l’enseignement supérieur,
l’infrastructure de recherche scientifique et d'innovation, l'offre de logements
universitaires, les bourses universitaires, les métiers d’enseignement ainsi que
l’administration universitaire. Cet engagement du MESRSI en faveur de la capitalisation du
capital humain des femmes s’aligne sur les trois axes du PGE III relatifs à l’autonomisation
économiques des femmes, à la lutte contre les discriminations fondées sur le genre et à la
promotion des droits des femmes.
8.3. Chaîne de résultats sensibles au genre : application de la démarche
performance sensible au genre
Conformément à la circulaire du Chef du Gouvernement (n°4/2024) relative à
l’établissement des propositions de Programmation Budgétaire Triennale assortie des
objectifs et des indicateurs de performance au titre de la période 2025-2027, le MESRSI a



    76
                  RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


mis en place une chaîne de résultats sensible au genre qui couvre un seul de ses programmes
budgétaires, en l’occurrence, celui relatif à l’enseignement supérieur.
8.3.1. Chaîne de résultats sensibles au genre mise en place par le Département
La chaîne de résultats sensibles au genre développée par MESRSI (voir tableau ci-dessous)
demeure limitée au programme relatif à l’enseignement supérieur. Ce dernier est, en effet,
associé à deux objectifs qui sont liés à leur tour à plusieurs indicateurs et sous indicateurs
sensibles au genre. Dès lors, le degré de réalisation de l’objectif portant sur les réponses à la
demande croissante pour l’enseignement est mesuré par deux sous-indicateurs sensibles au
genre, en l’occurrence, la part des nouvelles inscrites dans l’enseignement supérieur
universitaire public et la part des étudiantes dans l’enseignement supérieur universitaire
public dont les niveaux ont atteint, en 2023, respectivement 54,5% et 53,6%, signifiant que
la parité est atteinte dans les universités à l’échelle nationale.
Quant à l’objectif lié à l’amélioration du rendement interne du système de l’enseignement
supérieur, le suivi du niveau de sa concrétisation s’effectue par le biais de deux sous-
indicateurs désagrégés par sexe à savoir : le taux apparent de diplomation des filles au cycle
de licence qui a avoisiné 41,5% en 2023 contre 32% chez les garçons (soit un surcroit de 9,5
points de pourcentage) et le taux d’abandon de la première année de la licence des
étudiantes situé, en 2023, à 21,9% étant plus élevé de 2,2 points de pourcentage que celui
des étudiants qui s’est établie à 19,7%.
                                                                                                    Réalisations    LF
Programmes                Objectifs               Indicateurs             Sous-indicateurs
                                                                                                       2023        2024
                                             Effectif           des    Pourcentage           des
                                             nouveaux       inscrits   nouvelles inscrites dans
                                             dans l’enseignement       l’enseignement                  54,5%       53,4%
                    Répondre       à    la   supérieur                 supérieur universitaire
                    demande     croissante   universitaire public      public
                    pour   l’enseignement    Effectif global des       Pourcentage           des
                    supérieur                étudiants         dans    étudiantes          dans
                                             l’enseignement            l’enseignement                  53,6%        52%
                                             supérieur                 supérieur universitaire
   Enseignement




                                             universitaire public      public
     Supérieur




                                             Taux apparent de          Taux     apparent      de
                                             diplomation au cycle      diplomation des filles au       41,5%        49%
                                             de     licence    dans    cycle de licence
                                             l’enseignement
                    Améliorer          le    supérieur                 Taux     apparent    de
                    rendement interne du     universitaire public      diplomation des garçons          32%         41%
                    système           de     selon le sexe             au cycle de licence
                    l’enseignement                                     Taux d'abandon       de la
                    supérieur                                          première année       de la      21,9%        16%
                                             Taux d'abandon de la
                                                                       licence – Filles -
                                             première année de la
                                                                       Taux d'abandon       de la
                                             licence par sexe
                                                                       première année       de la      19,7%        18%
                                                                       licence –Garçons-
                                                                                                               MESRSI, 2024

     Tableau 35 : Chaîne de résultats sensibles au genre mise en place par le
                                     MESRSI
8.3.2. Actions en faveur de la promotion d’égalité de genre non intég rées dans
les chaînes de résultats sensibles au genre :
En plus des actions entreprises pour promouvoir l’accès des étudiantes à l’enseignement
supérieur sur le même pied d’égalité que les étudiants, le MESRSI a acté d’autres projets et
mesures visant la prise en compte des besoins des étudiantes en termes d’accès aux services
d’hébergement, à la restauration, à la bourse et à la couverture médicale. De même, le


                                                                                                                          77
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


MESRSI poursuit ses efforts en matière de promotion de l’égalité de genre, à travers des
formations octroyées sur les questions liées à l’égalité entre les femmes et les hommes et à
la protection des droits des femmes et sur le leadership féminin. Les principales actions mises
en place, dans ce cadre, sont déclinées comme suit :
 Réservation de 63% du total des lits offerts par les cités universitaires au profit des
    étudiantes ;
 Satisfaction de 39% des nouvelles demandes d’hébergement émanant des étudiantes ;
 Augmentation durant l’année universitaire 2023-2024 du quota réservé aux étudiants
    internationaux pour atteindre 800 lits dont 51% sont réservés aux filles ;
 Forte présence des étudiantes dans le total des étudiants servis par les restaurants
    universitaires, avec une part dans le total des repas servis durant l’année universitaire
    2023-2024 qui avoisine 60% ;
 Poursuite de la dynamique d’octroi des bourses aux étudiant.e.s en s’appuyant
    davantage sur les plateformes électroniques conçues à cet égard. La part des
    étudiantes dans le total des bénéficiaires de bourse s’est situé à 58,4% au titre de
    l’année universitaire 2023-2024 ;
 Organisation des cycles de formation « LeaderShe Courses » au profit des femmes
    responsables du MESRSI et des universités afin de promouvoir l'accès des femmes aux
    postes de direction et de contribuer à la capacitation du capital humain du MESRI, plus
    particulièrement, des femmes du Ministère ;
 Organisation des séries de « LeaderSheTalks » au sein des universités visant la mise en
    place d’un programme d’accompagnement intégré pour renforcer le leadership et la
    culture de créativité et d’innovation chez les étudiantes ;
 Organisation de campagne de sensibilisation en milieu universitaire sur la prévention
    des violences, y compris celles basées sur le genre, sur la lutte contre les stéréotypes
    et la prévention de la cyberviolence ;
 Généralisation des cellules d'écoute et d'accompagnement dans toutes les cités
    universitaires pour renforcer le soutien psychologique aux étudiants.
 Mise en place de dispositif de signalement des cas violences, en particulier, le
    harcèlement sexuel ;
 Intégration de la lutte contre les stéréotypes et les discriminations de genre dans les
    cursus universitaires ;
 Promotion de la recherche scientifique liée au genre ;
 Institutionnalisation de la Responsabilité Sociétale dans l’administration centrale, les
    universités et les établissements publics sous la tutelle du MESRSI, intégrant le volet
    dimension genre dans tous ses aspects.

   9. DEPARTEMENT   CHARGE                             DE       LA       FORMATION
      PROFESSIONNELLE
De par ses missions et ses attributions, le Département de la Formation Professionnelle (DPF)
joue un rôle clé dans la dynamique lancée par le Maroc pour promouvoir l’accès des femmes
à l’activité et à l’emploi. A cet effet, le DFP poursuit ses interventions en faveur de la
valorisation du capital humain des femmes et de leurs compétences techniques et
professionnelles et ce, en ligne avec sa stratégie d’action visant, entre autres, la promotion
de l'inclusion sociale et l'égalité des sexes dans le système de formation professionnelle.
9.1. Analyse genre : Point de départ pour réu ssir une programmation
intégrant la dimension genre
Le DPF est parmi les départements ministériels les plus dotés d’analyses genre de ses
domaines d’intervention réalisées en partenariat avec plusieurs institutions nationales (CE-
BSG) et organismes internationaux (AFD, Millenium challenge corporation (MCC)…). Ces
analyses se sont intéressées à l’étude sous le prisme genre d’une multiplicité d’aspects en


    78
                          RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


relation avec la formation professionnelle d’ordre institutionnel, organisationnel, éthique…46
Ces analyses ont permis de prendre conscience des enjeux liés à l’égalité de genre et à
l’autonomisation des femmes dans le secteur de la formation professionnelle et d’enrichir la
chaîne de résultats sensibles au genre du Département.
9.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité et d’autonomisation économique des femmes
L’un des piliers de la stratégie du DFP est d’assurer une offre de formation professionnelle
de qualité étendue sur l’ensemble du territoire national et inclusive qui est accessible, sur le
même pied d’égalité, aux citoyennes et aux citoyens. Pour y parvenir le Département prend
appui sur plusieurs leviers d’action qui prennent en compte la dimension genre, en termes
d’accès aux programmes de formation professionnelle, aux structures d’hébergement, aux
informations liées à l’orientation et en termes de mobilisation continue pour la lutte contre la
violence fondée sur le genre et les stéréotypes liés au genre.
Ces interventions confèrent au DFP un rôle central dans la concrétisation des objectifs du
PGE III en matière d’autonomisation économique des femmes, de protection de leurs droits
et de lutte contre la violence fondée sur le genre. En effet, le département est impliqué, en
partenariat avec plusieurs départements, dans plusieurs mesures dans le cadre de la mise en
  uvre du PGE III, comme décliné dans le tableau qui suit :
     Axes du
                                       Programme                                Actions entreprises/prévues
     PGE III
                                                                 Amélioration des conditions d’hébergement des jeunes
                                                                  filles dans les établissements de formation relevant du
      Autonomisation et




                                                                  département de la pêche maritime ;
                                                                  Adaptation des équipements et aménagement des centres
         leadership
           Axe 1 :




                                                                  de formation visant à renforcer les effectifs des filles
                             Autonomisation économique et
                                                                  lauréates de la formation professionnelle agricole ;
                             leadership
                                                                 Renforcement de l’application de l’approche genre par les
                                                                  établissements de formation professionnelle hôtelière et
                                                                  touristique;
                                                                 Mise en uvre des programmes de formation résidentielle
                                                                  et par apprentissage au profit des jeunes filles ;
     Protectio
     n et Bien
      Axe 2 :




                             Protection     et  prévention :     Mise en place d’un mécanisme de lutte contre la violence et
       être




                             environnement sans violence à        le harcèlement basés sur le genre au sein des
                             l’égard des femmes                   établissements de formation professionnelle
      Droits et
       Axe 3 :

      Valeurs




                             Promotion des droits et lutte       Mise en place d’un dispositif de lutte contre les
                             contre les discriminations et les    discriminations et les stéréotypes de genre dans les
                             stéréotypes                          établissements de formation professionnelle

                                                                                                             Source : DFP, 2024

9.3. Chaîne de résultats sensibles au genre : application de la démarche
performance sensible au genre
Conformément à la circulaire du Chef du Gouvernement (n°4/2024) relative à
l’établissement des propositions de Programmation Budgétaire Triennale assortie des

46 Il s’agit d’une analyse institutionnelle du système de la formation professionnelle en matière du genre et
d’inclusion sociale réalisée en partenariat avec le Millenium challenge corporation (MCC) en 2017, d’un référentiel
des normes et des valeurs en matière d’égalité et d’équité genre dans le système de la formation professionnelle
a été élaboré par le DFP, de Plusieurs autodiagnostics genre destinés aux établissements de formation
professionnelle (EFP) ont été réalisés et d’une analyse genre réalisée au profit du DFP, en 2019, en partenariat
avec le CE-BSG et l’AFD.


                                                                                                                            79
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


objectifs et des indicateurs de performance, au titre de la période 2025-2027, le DFP a
adopté une chaîne de résultats sensibles au genre qui couvre deux de ses trois programmes
budgétaires, en l’occurrence, les programmes relatifs à la gouvernance du système de la
formation professionnelle et la mobilisation des acteurs et partenaires ainsi qu’à la conduite
et au pilotage du système de la formation professionnelle (voir tableau ci-dessous).
La chaîne de résultats développée par le DFP intègre explicitement la dimension genre au
niveau de plusieurs objectifs, indicateurs et sous indicateurs de performance associés aux
deux programmes susmentionnés. De fait, cette chaîne met en exergue un ensemble
d’indicateurs et sous indicateurs qui renseignent sur le niveau d’accès des filles aux
différentes offres de formation professionnelle et à la contribution de l’Etat aux frais de
formation au profit des populations éligibles des établissements privés de formation
professionnelle accrédités. Il en ressort que la parité est presque atteinte, en 2023, en termes
d’accès aux offres de formations professionnelles (la part des filles a atteint 42% dans le total
des bénéficiaires de la formation professionnelle, 45% des bénéficiaires de la formation
résidentielle, 57% des bénéficiaires de la formation par apprentissage). Toutefois, la part des
filles dans le total des bénéficiaires de la formation alternée ne dépasse pas 20%. De même,
la part des filles bénéficiaires de la contribution de l’Etat aux frais de formation pour les
populations éligibles des établissements privés de formation professionnelle accrédités est
située à 60% (dépassant le seuil de la parité).
En matière de prise en compte de la dimension genre dans la gestion et la valorisation des
ressources humaines du DFP, cette chaine de résultats intègre un objectif sensible au genre
relatif à l’égalité professionnelle au DFP dont le niveau de concrétisation est mesuré par un
sous-indicateur de performance portant sur la part des femmes dans les postes de
responsabilité qui s’est établi à 43% au titre de l’année 2023.

                                                                                                                                 Réalisations LF
Programmes                                        Objectifs                Indicateurs                Sous indicateurs
                                                                                                                                     2023    2024
 mobilisation des acteurs
 système de la formation
    professionnelle et
     Gouvernance du



      et partenaires




                                            Assurer      l'égalité
                                            professionnelle    au Part     des       femmes
                                            Département de la                                                                       43%      42%
                                                                   responsables
                                            Formation
                                            Professionnelle




                                                                    Effectif des bénéficiaires   Le pourcentage des filles
       Conduite et pilotage du système de




                                                                    de       la     formation    bénéficiaires     de       la      42%      43%
                                                                    Professionnelle –global-     formation professionnelle
          la formation professionnelle




                                                                    Effectif des bénéficiaires   Le pourcentage des filles
                                                                    de       la     formation    bénéficiaires     de       la
                                                                                                                                    45%     44%
                                            Assurer            le   professionnelle     :   la   formation professionnelle :
                                            rapprochement entre     formation résidentielle      La formation résidentielle
                                            le      besoin    en    Effectif des bénéficiaires   Pourcentage      des   filles
                                            compétences       et    de       la     formation    bénéficiaires     de       la
                                                                                                                                    20%      21%
                                            l'offre de formation    professionnelle              formation professionnelle
                                            en tenant compte de     - formation alternée-        - formation alternée-
                                            l'aspect genre
                                                                    Effectif des bénéficiaires   Pourcentage     des   filles
                                                                    de       la    formation     bénéficiaires     de      la
                                                                    professionnelle              formation professionnelle -        57%      62%
                                                                    - La formation par           La       formation      par
                                                                    apprentissage-               apprentissage-




              80
            RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


                                         Effectif des populations
                                                                     Pourcentage des filles à
                                         à besoins spécifiques
                                                                     besoins         spécifiques
                                         bénéficiaires    de    la                                  7,7%           8%
                                                                     bénéficiaires     de      la
                                         formation
                                                                     formation professionnelle
                                         professionnelle
                                         Effectifs des populations
                                         à besoins spécifiques       -Pourcentage des filles à
                                         bénéficiaires    de    la   besoins         spécifiques
                                         formation                   bénéficiaires     de      la    6%            6%
                                         professionnelle             formation professionnelle
               Élargir l’accessibilité   -      Formation      des   - Formation des détenus-
               au secteur pour les       détenus-
               personnes à besoins       Effectifs des populations
               spécifiques en tenant     à besoins spécifiques       Pourcentage des filles à
               compte des besoins        bénéficiaires    de    la   besoins          spécifiques
               spécifiques       des     formation                   bénéficiaires     de      la
                                                                                                     41%       35%
               femmes      et    des     professionnelle             formation professionnelle
                                         - Formation           des   - Formation des personnes
               hommes
                                           personnes         avec      avec handicap-
                                           handicap-
                                         Nombre                des
                                         bénéficiaires    de    la   Pourcentage     des   filles
                                         contribution de l’Etat      bénéficiaires     de      la
                                         aux frais de formation      contribution de l’Etat aux
                                         pour les populations        frais de formation pour les
                                                                                                    60%        55%
                                         éligibles             des   populations éligibles des
                                         établissements privés de    établissements privés de
                                         formation                   formation professionnelle
                                         professionnelle             accrédités
                                         accrédités
               Améliorer la qualité
               de formation et la        Taux d’insertion des        Taux      d’insertion    des
               performance      des      lauréats de la formation    lauréates     filles  de  la
                                                                                                      -        -
               opérateurs en tenant      professionnelle dans le     formation professionnelle
               compte      de    la      tissu économique            dans le tissu économique
               dimension genre
                                                                                                    Source : DFP, 2024

     Tableau 36 : Chaîne de résultats sensibles au genre mise en place par le DFP

      10.      DEPARTEMENT CHARGE DE LA JEUNESSE
Le Département de la Jeunesse (DJ) poursuit ses efforts pour une consolidation de la prise
en compte de la dimension genre dans sa stratégie d’action et, ainsi, asseoir les bases d’une
pratique réussie de la BSG. Le département s’est engagé, à cet égard, dans plusieurs
chantiers, en l’occurrence, la réalisation d’un audit genre et l’application, pour la première
fois, d’une méthodologie de marquage des allocations budgétaires dédiée à la promotion de
l’égalité entre les femmes et les hommes.


10.1. Analyse genre : Point de départ pour réussir une programmation
intégrant la dimension genre
Dans le cadre d’un plan de travail conjoint signé, en 2023, entre le département et 6 Agences
du Système des Nations Unies, le DJ a initié, en août 2023, la réalisation d’un audit genre en
partenariat avec ONU Femmes47. Cet audit s’est focalisé sur l’évaluation du niveau
d’intégration de la dimension genre dans les domaines d’intervention du Département y

47Le DJ a procédé à la réalisation d’une analyse genre du secteur de la jeunesse, en 2019, en partenariat avec le
CE-BSG et l'AFD.


                                                                                                                    81
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


compris dans la gestion de ses ressources humaines. De cet exercice d’évaluation ont émané
plusieurs constats et orientations qui devraient guider le département à mieux cerner ses
priorités en termes de réduction des inégalités de genre. Ces orientations sont déclinées
comme suit :
 La nécessité d'un renforcement des capacités des ressources humaines du DJ en matière
  des concepts et des approches liées à la prise en compte de la dimension genre dans les
  politiques publiques;
 Le renforcement des actions à même d’assurer un accès inclusif et équitable aux services
  offerts à travers les programmes mis en uvre par le DJ;
 L’application d’une programmation en mesure d’engager une dynamique transformatrice
  favorisant la promotion de l’égalité de genre ;
 La systématisation de la prise en compte de la dimension genre dans les exercices de
  suivi et d'évaluation, moyennant la conception des indicateurs sensibles au genre ;
 La priorisation des critères liés à la disponibilité de l’expertise en matière de l’égalité de
  genre lors des opérations de sélection des organisations de la société civile partenaires ;
 L’amélioration de l’accès des femmes aux postes de direction au sein du DJ et les
  structures sous sa tutelle ;
 Le renforcement des opérations de sensibilisation aux protocoles relatifs à la lutte contre
  le harcèlement sexuel ;
 Le renforcement de la coordination interministérielle.
10.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité et d’autonomisation économique des femmes
En ligne avec ses missions et attributions, le DJ est fermement engagé dans la dynamique
nationale en faveur de la promotion de l’égalité de genre et de la protection des droits des
jeunes filles et des femmes, moyennant une diversité de programmes et services dont le
développement d’une infrastructure diversifiée dédiée aux jeunes, aux jeunes filles et aux
femmes (à l’instar de maisons de jeunes, des foyers féminins, des centres d’accueil et autres).
De même, le programme relatif aux colonies de vacances prend en compte les questions
liées à l’équité en termes d’accès des jeunes filles et garçons aux services offerts, tout en
mettant l’accent sur les aspects liés à la sensibilisation et à la formation des encadrant.e.s
chargé.e.s de sa mise en uvre. En outre, le DJ est l’initiateur de plusieurs programmes de
partenariat avec des institutions nationales et internationales pour appuyer l’inclusion des
femmes dans le marché du travail et le renforcement de leurs compétences et leur
autonomisation économique.
Il est aussi à mentionner que le DJ s’est lancé dans plusieurs projets en faveur de la petite
enfance et ce, par le biais de l’amélioration des services, de la qualité d’accueil et
l’élargissement de l’offre des crèches, ce qui ne peut que contribuer à l’amélioration de
l’accès des femmes à l’emploi. En effet, en se référant à une récente étude du HCP (mars
2024) portant sur l’analyse intersectionnelle de la participation des femmes au marché du
travail marocain, il en ressort que la décision des femmes de participer à la population active
demeure fortement dépendante de leur capacité de concilier entre vie professionnelle et
obligations familiales en termes de prise en charge des enfants (voir encadré 3 ci-dessous).
Ce constat soulève, ainsi, l’intérêt que représente le développement des services du
préscolaire et de garde d’enfants, comme étant un levier d’actions pour stimuler l’activité des
femmes et favoriser leur maintien dans le marché du travail.




    82
           RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


    Encadré 3 : Analyse intersectionnelle de la participation des femmes au marché du travail
    marocain : la prise en charge des enfants un facteur déterminant de l’accès des femmes à
                                             l’activité
 Le HCP a rendu public, en mars 2024, une étude relative à l’analyse intersectionnelle de la participation
 des femmes au marché du travail marocain. Cette étude a pour objectifs d’identifier les déterminants
 structurels de l’inactivité des femmes au Maroc, tout en mettant la lumière sur les interactions entre les
 contraintes individuelles, sociales et contextuelles auxquelles elles sont confrontées.
 Cette étude s’est reposée sur une approche quantitative déterminant les profils des femmes âgées entre
 25 et 60 ans aussi bien à l'échelle nationale que régionale, en utilisant les données de l'Enquête Nationale
 sur l'Emploi au titre de l’année 2021. L’étude s’est aussi appuyée sur une approche qualitative fondée sur
 l'analyse des témoignages recueillis, moyennant 22 focus groupes impliquant près de 274 femmes rurales
 et urbaines des régions de l'Oriental et de Casablanca-Settat.
 Les principaux résultats émanant de cette étude sont déclinés comme suit :
 A l’échelle nationale :
      La probabilité d'inactivité des femmes au Maroc avoisine 73%, bien plus élevée que celle des
       hommes, estimée à 7,5% ;
      Les femmes au foyer représentent 74% des femmes inactives au Maroc et 54% de ces femmes
       déclarent que la garde des enfants et les tâches domestiques sont les raisons principales de leur
       inactivité ;
      La présence d'enfants dans le ménage ne semble pas influencer de manière significative les
       décisions de participation des femmes mariées, âgées de 25 à 34 ans, et qui ont un diplôme moyen
       ou bien sans aucun diplôme ;
      Les jeunes femmes mariées, âgées de 25 à 34 ans, diplômée du supérieur et ayant au moins un
       enfant présentent un risque considérable d'inactivité.
 A l’échelle des régions de l'Oriental et de Casablanca-Settat :
      Les jeunes femmes mariées, âgées de 25 à 34 ans, sans diplôme ou titulaires d'un diplôme de
       niveau moyen, vivant avec au moins un enfant dans leur foyer, présentent la probabilité
       d’inactivité la plus élevée parmi l’ensemble des profils analysés à l’échelle des deux régions ;
      La présence d’enfants dans le ménage des femmes mariées, ayant un diplôme supérieur, a un
       impact important sur la probabilité qu’elles soient inactives tant bien pour les femmes âgées de
       25 à 34 ans que pour celles âgées de 35 à 59 ans.
 Source : « Analyse intersectionnelle de la participation des femmes au marché du travail marocain », HCP, mars 2024.

Ce faisant, le DJ a acté le lancement d’une multiplicité de projets visant l’amélioration de
l’accès aux services de garde d’enfant de qualité à savoir :
 La digitalisation de la procédure d’octroi des autorisations d’ouverture, d’exploitation et
  de gestion des crèches privés ;
 L’élaboration des normes et des standards cadrant les crèches publiques et privées et ce,
  en établissant des critères liés aux infrastructures, aux programmes éducatifs, à la
  formation du personnel et aux mesures de sécurité ;
 L’élargissement de l'offre de crèches à travers des partenariats régionaux.
Ces programmes, projets et activités entreprises par le DJ s’alignent parfaitement sur les
priorités du PGE III en termes de renforcement de l’autonomisation économique des femmes,
de promotion de leurs droits et de lutte contre les discriminations et les stéréotypes.
10.3. Chaîne de résultats sensibles au genre : application de la démarche
performance sensible au genre
Conformément à la circulaire du Chef du Gouvernement (n°4/2024) relative à
l’établissement des propositions de Programmation Budgétaire Triennale assortie des
objectifs et des indicateurs de performance, au titre de la période 2025-2027, le DJ a adopté
une chaîne de résultats sensibles au genre qui couvre ses deux programmes budgétaires, en
l’occurrence, le programme relatif au pilotage et à la gouvernance et celui lié à la jeunesse, à
l’enfance et aux femmes.


                                                                                                                  83
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


10.3.1. Chaîne de résultats sensibles au genre mise en place par le Département
Le Projet de Loi des Finances 2025 marque l’apport de certains changements à la chaîne de
résultats du DJ en termes de choix d’objectifs, d’indicateurs et de sous indicateurs de
performance. Ces changements ont également concerné la chaîne de résultats sensibles au
genre. Celle-ci, même si elle concerne encore l’ensemble des programmes du département,
elle connait, néanmoins, l’intégration de nouveaux objectifs, indicateurs et sous indicateurs
de performance prenant en compte la dimension genre.
De fait, l’objectif relatif à l’institutionnalisation d’une administration publique équitable basée
sur un système de compétences demeure associé à un sous-indicateur sensible au genre qui
renseigne sur le taux d’accès des femmes à la formation qui, d’ailleurs, dépasse le seuil de
parité en 2023, en se situant à 54%.
Quant au programme portant sur la jeunesse, l’enfance et les femmes, il est accompagné
d’un seul objectif qui intègre explicitement la dimension genre et qui concerne la contribution
à l’autonomisation de la femme et de la jeune fille au moyen de l’accompagnement et de la
formation. Le degré de réalisation de cet objectif est mesuré par deux sous-indicateurs de
performances qui sont le taux de lauréates qualifiées professionnellement et le taux des
femmes bénéficiaires de la formation pour créer des Activités Génératrices de Revenu (AGR).
Pour leur part, les objectifs relatifs respectivement au renforcement de l'encadrement et de
l’animation des jeunes et des enfants, la contribution au développement des services de
qualité au profit de l’enfance et au développement des infrastructures et des équipements
pour améliorer la qualité des services sont associés à de multiples indicateurs et sous-
indicateurs de performance sensibles au genre qui renseignent sur le degré de leur atteinte,
tels que le taux de filles bénéficiaires des activités de colonies des vacances, le taux de
cadres femmes bénéficiaires de formations à l’encadrement et à l’animation, le nombre des
établissements féminins aménagés et/ou équipés, le nombre des petites filles bénéficiaires
de prestations des crèches gérées par le département….
Il est clair que les changements opérés au niveau de la chaîne de résultats sensibles au genre
ont surtout concerné les indicateurs et les sous-indicateurs de performance qui ont été
reformulés de telle manière à assurer le suivi de l’évolution des inégalités de genre au lieu de
se contenter juste d’une désagrégation par sexe comme appliqué auparavant (voir le tableau
ci-dessous).




    84
                                    RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE



                                                                                                                    Réalisations    LF
                                              Objectifs               Indicateurs           Sous-indicateurs
Programmes                                                                                                             2023        2024
             Institutionnaliser une
 Pilotage et administration     publique Taux     d’accès     à   la                      Taux   d’accès    des
gouvernance équitable basée sur un formation                                              femmes à la formation        54%         50%
             système de compétences
                                         Nombre de jeunes et
                                                                                          Taux       de    filles
                                         d’enfants bénéficiaires
                                                                                          bénéficiaires     des
                                         du     programme       des                                                    32,9%       22%
                                                                                          activités de colonies
                                         colonies de vacances par
                                                                                          des vacances
             Renforcer l'encadrement sexe et par milieu
             et l’animation des jeunes Nombre de cadres des
                                                                                          Taux      de    cadres
             et des enfants              colonies des vacances
                                                                                          femmes bénéficiaires
                                         bénéficiaires        d’une
                                                                                          de     formations    à       48,0%       30%
                                         formation                 à
                                                                                          l’encadrement et à
                                         l’encadrement       et    à
                                                                                          l’animation
                                         l’animation par sexe
      Jeunesse, Enfance et Femmes




                                         Taux      de     lauréates
             Contribuer                à qualifiées                                                                     93%        54%
             l’autonomisation de la professionnellement
             femme et de la jeune fille Taux       des      femmes
             au         moyen         de bénéficiaires     de     la
             l’accompagnement et de formation pour créer des                                                            72%        78%
             la formation                Activités    Génératrices
                                         de Revenu (AGR)
                                         Nombre          d’enfants
                                                                                          Nombre        d’enfants
             Contribuer               au bénéficiaires           de
                                                                                          bénéficiaires        de
             développement           des prestations des crèches                                                                   2.40
                                                                                          prestations         des      2.582
             services de qualité au gérées             par        le                                                                 0
                                                                                          crèches gérées par le
             profit de l’enfance         département par sexe et
                                                                                          département-filles-
                                         par milieu
                                                                                          Nombre            des
                                                                                          établissements
                                                                                                                        75         40
                                      Développer              les                         féminins    aménagés
                                      infrastructures    et   les                         et/ou équipés
                                                                  Nombre des structures
                                      équipements            pour                         Nombre des crèches
                                                                  mise à niveau
                                      améliorer                                           gérées      par     le
                                      la qualité des services                             département                   163        40
                                                                                          aménagées       et/ou
                                                                                          équipés
                                                                                                                      Source : DJ, 2024

   Tableau 37 : Chaîne de résu ltats sensibles au genre mise en place par le DJ
Dans le même sillage, il est à rappeler que le DJ a fait l’objet d’un accompagnement en 2023
et 2024 pour l’application de la nouvelle méthodologie développée pour le marquage genre
des allocations budgétaires allouées à la promotion de l’égalité de genre (voir la partie I du
présent Rapport). L’opérationnalisation de l’ensemble des étapes de cette méthodologie a,
en effet, permis de quantifier les enveloppes programmées pour la promotion de l’égalité
entre les femmes et les hommes au titre de la Loi de Finances 2024. Il en ressort que la part
du budget du programme budgétaire relatif à la jeunesse, l’enfance et les femmes dédiée à
l’égalité de genre est située à près de 81%. Pour ce qui est du programme portant sur le
pilotage et la gouvernance, cette part avoisine 51%.
10.3.2. Actions en faveur de la promotion de l’égalité de genre non intégrées
dans les chaînes de résultats sensibles au genre
En plus de ceux inscrits dans sa chaîne de résultats sensibles au genre, le tableau ci-dessous
décline une multiplicité de programmes et de projets portés par le DJ et qui visent la
promotion de l’égalité entre les femmes et les hommes et la protection des droits des
femmes.


                                                                                                                                    85
PROJET DE LOI DE FINANCES POUR L’ANNEE 2025




  Programmes/projets                           Objectifs et contenu du programme/projet

                             La première édition du programme national de volontariat « Motatawi3 » a été
                             lancée, en 2023, au profit des jeunes âgés de 18 ans à 22 ans. Il vise à renforcer
 Programme national de       la participation citoyenne des jeunes, à stimuler leur esprit critique et à
volontariat « Motatawi3 »    renforcer leur sentiment d’appartenance. A cet effet, 11 conventions de
pour les jeunes âgés de 18   partenariat ont été signées avec différents partenaires en vue d’assurer la
       ans à 22 ans          formation théorique et pratique des jeunes volontaires dans plusieurs domaines
                             à savoir : la santé, l'entrepreneuriat, l’art, la culture Amazigh, les coopératives,
                             la protection des données personnelles, les droits de l’Homme…
 Programme "YA3NI" en
                             Ce programme consiste à renforcer la capacité des jeunes de 15 à 30 ans en
    partenariat avec le
                             matière d’innovation sociale et leur résilience communautaire. Le programme
Programme des Nations
                             met l’accent sur le renforcement de l’engagement des femmes en faveur de la
      Unies pour le
                             réduction des inégalités de genre.
Développement (PNUD)
       Programme
d’entreprenariat social et   Ce programme, qui cible les jeunes âgés de 15 à 24 ans, a pour objectifs de
  innovation « UPSHIFT       promouvoir l'inclusion socio-économique des jeunes et de favoriser l'égalité de
 Maroc » en partenariat      genre en créant un environnement sûr et épanouissant.
      avec l'UNICEF
                             Ce programme destiné aux jeunes marocain.e.s et étrangers résidant au Maroc,
                             âgé.e.s entre 16 et 30 ans, a pour objectif de mettre en place une plateforme
   Programme « Pass          numérique spécifiques aux jeunes, offrant des réductions, des gratuités et
       Jeunes »              divers avantages pour faciliter leur accès à une gamme étendue de services
                             culturels, sportifs, commerciaux, bancaires, de transport, et d'hébergement sur
                             l’ensemble du territoire national.
                                                                                                  Source : DJ, 2024

Tableau 38 : Programmes et projets entrepris par le DJ pour la promotion de
            l’égalité de genre et de l’autonomisation des femmes




   86
         RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


   IV. ACCES EQUITABLE AUX FACTEURS DE PRODUCTION
       POUR   UNE   AUTONOMISATION    ECONOMIQUE
       RENFORCEE DES FEMMES
L’accès équitable des femmes aux facteurs de production repose sur un meilleur accès au
marché du travail et aux activités génératrices de revenu et par une participation accrue à la
prise de décision. Cet axe passe en revue le volet transversal de l’emploi avant de se pencher
sur les opportunités sectorielles porteuses de perspectives de renforcement de
l’autonomisation économique des femmes.

1. MINISTERE DE L’INCLUSION ECONOMIQUE , DE LA
PETITE    ENTREP RISE, DE   L’EMPLOI ET    DES
COMPETENCES
Conformément aux Directives Royales visant la consolidation des fondements de l’Etat
social, le Gouvernement a érigé la question de l’emploi parmi ses priorités majeures pour la
seconde moitié de son mandant. Dès lors, une nouvelle feuille de route pour la promotion de
l’emploi est en cours de préparation. Celle-ci intègre des leviers d’action opérationnels en
lien avec la promotion de l’emploi rural, la restructuration des programmes actifs de l’emploi,
l’accompagnement des TPME, tout en mettant l’accent sur l’amélioration de l’emploi des
femmes et le renforcement de leur accès au marché du travail. Ce faisant, le Ministère de
l’Inclusion Economique, de la Petite Entreprise, de l’Emploi et des Compétences (MIEPEEC),
au regard de ses missions et attributions, est amené à jouer un rôle central dans la
concrétisation des objectifs assignés à cette feuille de route et ce, en partenariat avec toutes
les parties prenantes des secteurs publics et privés.
1.1. Analyse genre : point de départ pour réussir une programmation
intégrant la dimension genre
Le MIEPEEC poursuit une dynamique ininterrompue pour s’acquérir des études et des
analyses nécessaires afin de cerner l’évolution de la situation des inégalités de genre dans
le marché du travail. Ainsi, le Ministère, en plus de l’analyse genre sectorielle réalisée en
partenariat avec le CE-BSG et l’AFD, a procédé en 2023 à l’élaboration d'un guide sur
l'approche genre et l'autonomisation économique des femmes dans le cadre de la mise en
   uvre de la troisième édition du programme « Min Ajliki ».
1.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité et d’autonomisation écono mique des femmes
Conscient de la nécessité de renforcer l’intégration des femmes dans le marché du travail
dont les niveaux actuels demeurent encore faibles et en baisse, et afin de leur assurer un
accès à leur droits économiques et sociaux sur le même pied d’égalité que les hommes, le
MIEPEEC a acté et prévoit plusieurs leviers d’actions en vue de promouvoir la participation
des femmes à la populations active et à l’emploi
A cet effet, le Ministère ambitionne d’améliorer les opportunités d'emploi au profit des
femmes, en soutenant la création et le développement d'entreprises dirigées par celles-ci, en
particulier, les Petites et Moyennes Entreprises (PME). De même, le Ministère est fermement
engagé en faveur de l’amélioration des conditions de travail des femmes et du renforcement
de leur droit d’accès au travail décent, en leur assurant la protection sociale. Il est à signaler,
à cet égard, que des réflexions sont menées par le Ministère pour proposer des nouvelles
formes de travail flexibles au profit des femmes.




                                                                                                87
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


Dans le même sillage, le Ministère uvre pour consolider la facilitation de l’accès des femmes
au marché du travail, en se mobilisant pour l’élimination de toutes les formes de
discrimination auxquelles elles pourront faire face en cherchant à accéder à un emploi ou
bien dans l’exercice de leur travail. De plus, le Ministère soutient l’accès des femmes aux
formations et aux renforcements de capacités afin de renforcer leurs compétences
techniques et managériales.
La femme rurale n’est aucunement exclue de la stratégie d’action du MIEPEEC, comme en
témoigne l’implication du Ministère auprès de Bank Al-Maghrib et de la GIZ (Coopération
Allemande) dans la conception et la mise en                uvre d’une feuille de route pour
l’autonomisation des femmes rurales qui ambitionne de soutenir l'inclusion économique et
financière des femmes rurales et de contribuer à améliorer les revenus de leurs familles. Cette
feuille de route s'articule autour de 4 leviers d’actions qui portent sur ce qui suit :
    Levier 1 : Améliorer et accroître les opportunités économiques pour les femmes
     rurales ;
    Levier 2 : Développer et améliorer les compétences techniques des femmes rurales ;
    Levier 3 : Promouvoir l'inclusion financière pour renforcer la capacité des ménages à
     relever les défis et à développer des activités génératrices de revenus ;
    Levier 4 : lutter contre les stéréotypes de genre.
Ces actions entreprises et prévues par le MIEPEEC pour l’amélioration de la participation des
femmes à la population active et la protection de leur droit d’accéder à un travail décent et
ainsi contribuer significativement à la dynamique du développement à laquelle aspire notre
pays et comme voulu par Sa Majesté le Roi rejoignent les engagements pris par le Ministère
dans le cadre du PGE III, en particulier, ses programmes visant l'autonomisation et le
leadership des femmes et la prévention et l’instauration d’un environnement sans violences
à l’égard des femmes.
1.3. Chaîne de résultats sensibles au genre : application de la démarche
performance sensible au genre
Conformément aux dispositions de la circulaire du Chef de Gouvernement (n°4/2024)
relative à l’établissement des propositions de Programmation Budgétaire Triennale assortie
des objectifs et des indicateurs de performance au titre de la période de 2025 à 2027
insistant sur l’importance de la mise en place des objectifs et des indicateurs sensibles au
genre pour une application réussie de la BSG, le MIEPEEC a développé une chaîne des
résultats sensible au genre qui couvre l’ensemble des programmes budgétaires du Ministère.
1.3.1. Chaîne de résultats sensibles au genre mise en place par le Département
Poursuivant sa quête pour une prise en compte systématique de la dimension genre dans sa
stratégie d’action, le MIEPEEC a, effectivement, intégré les questions liées à l’égalité de genre
dans l'ensemble de ses programmes budgétaires, en l’occurrence, les programmes relatifs au
pilotage et à l'appui, à l'inclusion économique, à l'emploi, à l'observation du marché de travail
et celui lié au travail (voir le tableau ci-dessous).




    88
                                 RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


                                                                                                                         Réalisations    LF
Programmes                                Objectifs                 Indicateurs                Sous-indicateurs
                                                                                                                            2023        2024
                                   Institutionnaliser une
                                   administration
                                                            Taux    d’accès       à    la Taux d’accès des femmes
                                   publique       équitable                                                                  25%        25%
                                                            formation                     à la formation
                                   basée sur un système
                                   de compétences
                                                                                            Taux      des     femmes
                                                                                            bénéficiaires    de     la
                                                                                            formation dans le cadre          31%        40%
            Pilotage et Appui




                                                                                            de     la     coopération
                                                           Nombre       des     cadres
                                   Appuyer              et                                  internationale au Maroc
                                                           bénéficiaires            de
                                   accompagner         les                                  Taux      des     femmes
                                                           formations au Maroc et à
                                   programmes          du                                   bénéficiaires    de     la
                                                           l’étranger
                                   Ministère            et                                  formation dans le cadre
                                                                                                                             44%        30%
                                   promouvoir           le                                  de     la     coopération
                                   rayonnement         du                                   internationale           à
                                   Maroc aux niveaux                                        l’Etranger
                                   international        et Nombre de participants           Taux de participation des
                                   continental             aux         manifestations       femmes                aux
                                                           internationales, dont la         manifestations dont la
                                                                                                                             35%        31%
                                                           coordination est assurée         coordination est assurée
                                                           par     le    département        par le département de
                                                           d’Emploi                         l'Emploi
                                   Promouvoir l’inclusion
  Inclusion économique, emploi




                                   économique           et
    et observation du marché




                                   l’emploi pour tous, y
                                   compris les femmes et
                                   les jeunes
             du travail




                                   Promouvoir              Nombre         d’entreprises
                                   l’entrepreneuriat    et créées par les femmes
                                                                                                                             639        600
                                   appuyer la très petite accompagnées dans le
                                   entreprise              cadre du projet "Min Ajliki"
                                   Développer         un                                    Part des publications
                                   système       intégré
                                                         Nombre de publications             contenant des données à          67%        70%
                                   d’observation      du
                                                                                            aspect genre
                                   marché du travail
                                                            Nombre        d'associations
                                                                                            Nombre      d'associations
                                   Développer             laconventionnées            en
                                                                                            contractées      dans   le
                                   législation du travail etmatière de promotion de
                                                                                            domaine de la protection          7          12
                                   promouvoir      l’égalitél’égalité professionnelle et
            Travail




                                                                                            des droits de la femme au
                                   professionnelle et les   des droits fondamentaux
                                                                                            travail
                                   droits fondamentaux      des catégories spécifiques
                                   des          catégories Nombre           d’entreprises
                                   spécifiques               candidates au trophée de                                         -         110
                                                             l’égalité professionnelle
                                                                                                                    Source : MIEPEEC, 2024

            Tableau 39 : Chaîne de résultats sensibles au genre mise en place par le
                                           MIEPEEC
En effet, le niveau de réalisation des objectifs du programme de pilotage et d'appui portant
respectivement sur l’institutionnalisation d’une administration publique équitable fondée sur
un système de compétences et sur le renforcement des capacités des cadres et partenaires
du Ministère dans les domaines de l'emploi et du travail, est mesuré à travers 3 sous-
indicateurs sensibles au genre. Ces derniers mesurent le taux d’accès des femmes à la
formation, le taux des femmes bénéficiaires de la formation dans le cadre de la coopération
internationale au Maroc et le taux des femmes bénéficiaires de la formation dans le cadre de
la coopération internationale à l’étranger. Les niveaux enregistrés par ces sous indicateurs


                                                                                                                                              89
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


au titre de l’année 2023 avoisinent respectivement 25%, 31% et 44%, ce qui dénote de la
nécessité de déployer davantage d’efforts en la matière pour atteindre la parité. Il est à
rappeler à cet égard que les décisions du Conseil d’Administration de l’OIT datées de mars
2018 ont fixé le seuil minimal de participation des femmes, dans les délégations nationales
qui prennent part aux évènements officiels de l’organisation, à 30% avec l’ambition
d’atteindre la parité.
Pour ce qui est du programme budgétaire relatif à l'inclusion économique, à l'emploi et à
l'observation du marché du travail, qui intègre d’innombrables programmes et projets
entrepris par le Ministère pour la promotion de l’emploi y compris des femmes, est associé à
un objectif intégrant explicitement la dimension genre et qui porte sur la promotion de
l’inclusion économique et l’emploi pour tous, y compris les femmes et les jeunes. Toutefois,
aucun indicateur ni sous-indicateurs de performance sensibles au genre n’a été conçu pour
suivre le degré de réalisation de cet objectif.
Ce programme est associé, par ailleurs, à un autre objectif intégrant la dimension genre visant
la promotion de l’entrepreneuriat et l’apport d’appui aux TPE très petite entreprise dont les
niveaux de concrétisation sont renseignés par un indicateur de performance sensible au
genre qui mesure le nombre d’entreprises créées par les femmes accompagnées dans le
cadre du projet "Min Ajliki" qui s’est situé à 639 entreprises en 2023. Il est à noter à cet égard
que le projet « Min Ajliki », mis en uvre par le MIEPEEC en partenariat avec la coopération
Belge, est à sa troisième édition qui couvre la période de 2022 à 202648. Les principales
réalisations de ce projet concernent, en outre, l’accompagnement de 5.408 femmes en phase
de pré-création, le suivi du développement de 588 entreprises, l’orientation professionnelle
pour 1.259 femmes (sans emploi, sans éducation, sans formation), l’accompagnement de
l'intégration de 786 femmes NEET dans le marché du travail, la création de 1.572 emplois au
profit des femmes et l’élaboration d'un guide sur l'approche genre et l'autonomisation
économique des femmes.
Le suivi du degré de réalisation de l’objectif du programme relatif à l'inclusion économique,
à l'emploi et à l'observation du marché du travail visant le développement d’un système
intégré d’observation du marché du travail est accompagné, pour sa part, par un sous
indicateur de performance sensible au genre qui renseigne sur la part des publications
contenant des données à aspect genre qui s’est établie à près de 67% en 2023.
Le programme relatif au travail est accompagné d’un objectif sensible au genre portant sur
le développement de la législation du travail et la promotion de l’égalité professionnelle et
des droits fondamentaux des catégories spécifiques. Le suivi des niveaux de réalisation de
cet objectif est assuré par un indicateur et un sous-indicateur de performance sensibles au
genre. Ces derniers portent respectivement sur le nombre d’entreprises candidates au
trophée de l’égalité professionnelle et sur le nombre des associations contractées dans le
domaine de la protection des droits de la femme au travail (7 associations en 2023).
 1.3.2. Actions en faveur de la promotion d’égalité de genre non intégrées dans
les chaînes de résultats sensibles au genre
La chaine de résultats sensibles au genre susmentionnée ne couvre pas l’ensemble des
programmes, des projets et initiatives entreprises par le MIEPEEC pour la promotion de
l’égalité de genre en matière d’accès à l’emploi et aux opportunités économiques et de
protection des droits des femmes travailleuses. D’autres interventions sont actées, à cet
égard, par le MIEPEEC. Elles sont déclinées comme suit :



48Ce programme vise l’accompagnement et le renforcement des capacités des femmes porteuses de projets, des
cheffes d’entreprises pour développer leurs activités entrepreneuriales et des femmes en situation de NEET afin
d’améliorer leur employabilité et accéder au marché de l’emploi.


     90
             RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


 Programmes actifs de l’emploi : Le MIEPEEC poursuit la mise en uvre des programmes
  actifs de l’emploi bénéficiant aux femmes et hommes. La part des femmes dans le total
  des bénéficiaires de ces programmes est mise en exergue dans le tableau qui suit :
                                                                         Part des femmes dans le total des
      Programmes                        Objectifs
                                                                                     bénéficiaires
                       La Deuxième édition de ce programme a         Résultats au titre de l’année 2023 :
                       pour objectifs de promouvoir l’emploi en      - 31% des bénéficiaires des chantiers
                       encourageant les entreprises à recruter         provisoires sont des femmes;
                       activement les chercheurs d’emplois par le    - 55% de bénéficiaires des chantiers
 AWRACH 2              biais de contrat de travail durables. Cette     provisoires prioritaires au niveau national
                       édition intègre un nouveau dispositif           sont des femmes ;
                       relatif à l’octroi d’une prime d’appui à      - 42% des bénéficiaires du programme
                       l’emploi qui s’adresse aux chercheurs           prime à l’emploi durable sont des femmes.
                       d’emploi y compris les non diplômés49.
                                                                     48% des bénéficiaires du programme au
                                                                     titre de l’année 2023 sont des femmes. Le
                       Faciliter   l’insertion   des   chercheurs
     IDMAJ                                                           premier trimestre 2024 a enregistré
                       d’emploi
                                                                     l’insertion de 39.359 personnes dont 61,4%
                                                                     sont des femmes
                                                                     6.456 entreprises bénéficiaires à titre de
                                                                     l’année 2023, employant 18.639 chercheurs
                       Promouvoir l’emploi dans les entreprises,     d'emploi dont 32% de femmes.
 TAHFIZ                associations      et        coopératives      Le premier trimestre 2024 a été marqué par
                       nouvellement créées                           la validation de 5.313 protocole TAHFIZ au
                                                                     profit de 5.313 salarié.e.s dont 31% sont des
                                                                     femmes.
                       Améliorer l’employabilité des chercheurs      40% des bénéficiaires de la formation
 TAEHIL
                       d’emploi                                      contractuelle sont des femmes
                                                                                           Source : MIEPEEC, 2024

 Tableau 40 : Part des femmes dans le total des bénéficiaires des programmes
                              actifs de l’emploi
       Programme « Auto-Emploi » : Ce programme permet d’accompagner les porteurs de
        projets dans toutes les étapes de la création d'entreprise, de l'élaboration du business
        plan jusqu’aux démarches administratives et à la recherche des sources de
        financement disponibles au niveau territorial. Ce programme a bénéficié à 7.976
        porteurs de projets, en 2023, dont les femmes représentent 36%. Au cours du premier
        trimestre 2024, près de 1.450 candidats ont été accompagnés dans le cadre du
        programme dont 35% sont des femmes.
       Programme « Wafira » : poursuite de la mise          uvre de ce programme initié en
        partenariat entre MIEPEEC, la Coopération Espagnole, l’OIT et l'UE. Ce programme
        vise à accompagner les travailleuses saisonnières rurales participant à la migration
        circulaire entre le Maroc et l'Espagne, en leur offrant un accompagnement technique
        et un soutien financier pour la création de projets générateurs de revenus et de
        coopératives au Maroc. Le programme vise également à les sensibiliser aux services
        offerts par la CNSS dans le cadre de l’AMO ;
       Programmes régionaux de promotion de l'emploi : à l’instar du programme relatif à
        l’accompagnement de l’inclusion économique des jeunes dans la région Marrakech-
        Safi50, de nouveaux programmes sont lancés dans les régions de Souss, Massa-Beni
        Mellal-Khénifra et Fès-Meknès, en coopération avec l’AFD et l’Union Européenne. Ces

49 Ce dispositif permet d’encourager les entreprises à recruter les chercheurs d’emploi dans le cadre de contrats
de travail dits « durables » et selon des besoins précis de ces entreprises. Ce mécanisme permet à l’entreprise
d’enrichir son capital humain, tout en bénéficiant d’un appui financier d’un montant de 1.500 dirhams par mois,
pendant une durée de 9 mois pour chaque chercheur d’emploi inséré en contrepartie d’un recrutement pendant
au moins 12 mois.
50 Le premier programme régional d'appui à l'inclusion économique des jeunes au titre de la période de 2019 à

2024 a été lancé dans la région Marrakech-Safi en partenariat avec la Banque mondiale.


                                                                                                               91
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


       programmes qui prennent en compte la dimension genre s'appuient sur une approche
       intégrée et régionale pour promouvoir l'inclusion économique des jeunes, à travers
       deux dispositifs :
          Un dispositif régional pour améliorer l’employabilité et soutenir l’insertion
           professionnelle qui ambitionne de renforcer l’adéquation des compétences aux
           besoins du marché du travail, moyennant des formations qualifiantes et des
           formations par apprentissage ;
          Un dispositif régional de développement de l'entrepreneuriat, qui s’appuie sur la
           création d’un réseau de centres d'appui à l'entrepreneuriat et de développement
           de l'économie locale en mesure de fournir des services intégrés et diversifiés
           dans le but de renforcer le soutien à la création de petites entreprises et de
           promouvoir l’esprit entrepreneurial.
    Programme spécial de formation et d'insertion des éducateurs : Ce programme est
     inscrit dans le cadre de la convention de partenariat signée en 2022 entre le MIEPEEC,
     le Ministère de l’Education Nationale, du Préscolaire et des Sports, le Ministère de
     l’Economie et des Finances, l’Initiative Nationale pour le Développement Humain et la
     Fondation Marocaine du Préscolaire (FMPS). Ce programme engage ladite fondation
     à assurer une formation initiale aux éducateurs et éducatrice avec un volume horaire
     de 400h, à travers le Fonds de l’Emploi des Jeunes (FEJ). Les éducatrices
     représentent 84% du total des bénéficiaires des formations octroyées par le FMPS ;
     Consolidation des interventions de l’ANAPEC grâce à son réseau constitué, de 81
       agences locales, 12 agences régionales et 11 agences universitaires, l'ANAPEC a acté
       une multiplicité de réalisation au titre de l’année 2023 au profit des femmes
       chercheuses d’emploi. Ces réalisations sont présentées comme suit :
        Les femmes représentent 44% du nombre total des personnes nouvellement
           inscrites à l’ANAPEC;
        La part des femmes dans le nombre total des bénéficiaires d’entretiens de
           placement avoisine 49% (soit 81.638 femmes bénéficiaires) ;
        La part des femmes dans le total des bénéficiaires des ateliers de recherche
           d’emploi est située à 52% (soit 54.778 femmes bénéficiaires).
En matière de renforcement de la protection des droits des femmes employées, salariées et
entrepreneuses, le MIEPEEG a entrepris le Plan Nationale d’Inspection du Travail (PNIT) qui
intègre les préoccupations liées au contrôle des conditions du travail des femmes. A cet effet,
632 observations relatives à la situation de la femme au travail ont été adressées par les
inspecteurs du travail entre 2023 et 2024 et ont concerné 141 établissements. De même, près
de 511 observations ont été émises portant sur la discrimination en matière de travail et
d’emploi et près de 96 observations émises concernent des inégalités salariales entre les
femmes et les hommes.

2. DEPARTEMENT CHARGE DE L’AGRICULTURE,                                                   DU
DEVELOPPEMENT RURAL ET EAUX ET FORETS
La stratégie « Génération Green 2020-2030 », élaborée par le Département de l’Agriculture,
du Développement Rural et des Eaux et Forêts (DADREF), vise à poursuivre l'élan du
développement agricole et rural, en consolidant les acquis du Plan Maroc Vert. Cette
stratégie s’appuie sur plusieurs axes dont le développement du capital humain qui est
considéré comme un prérequis nécessaire à la modernisation du secteur agricole et au
développement rural. Dès lors, cette stratégie intègre des leviers d’action soutenant les
femmes rurales dans leurs activités afin d’en faire des actrices de la dynamique de
développement agricole et rural souhaitée.




    92
         RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


2.1. Analyse genre : Point de départ pour réussir une programmation
intégrant la dimension genre
Le DA a élaboré, en 2019, une analyse sectorielle genre dans le cadre du programme d’appui
de l’AFD à la BSG au Maroc, en partenariat avec le CE-BSG. De plus, une évaluation genre du
secteur de l’agriculture a été réalisée en partenariat avec la FAO en 2023. Cette évaluation a
analysé les inégalités de genre existantes dans plusieurs sous-secteurs de l’agriculture et les
institutions et services ruraux qui y sont liés, en mettant l’accent sur leurs causes et leur
impact sur le développement économique et social des zones rurales, sur la gestion des
ressources naturelles ainsi que sur la sécurité alimentaire.
Dans ce sillage il est important de mentionner que le DADREF a mis en place le Registre
National Agricole qui est considéré comme l’instrument par excellence à même de
perfectionner le ciblage des bénéficiaires des programmes du département. Ainsi, le RNA
permettrait d'améliorer l'accès des femmes exploitantes agricoles aux différents services
offerts par le département, notamment, en matière d’organisation agricole, d’encadrement,
de financement et autres.
2.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie du Département et les plans nationaux pour la
promotion de l’égalité et d’ autonomisation économique des femmes
La stratégie agricole « Génération Green 2020-2030 » a été conçue pour insuffler une
nouvelle dynamique au secteur agricole en renforçant son caractère inclusif. A cet effet, elle
inclut un ensemble d'actions prennent en compte les besoins spécifiques des femmes rurales
en matière d’appui technique, de formation, d’encadrement et de renforcement de leurs
capacités productives et en matière de gestion des projets agricoles. De fait, cette stratégie
vise l’inclusion des femmes au niveau de l’ensemble des projets relatifs à l’entreprenariat, la
formation et l’accès aux incitations.
Dans le même cadre, le DADREF a lancé une stratégie de développement des zones
oasiennes et de l’arganier qui couvre la période de 2023 à 2030 et qui prend en compte la
dimension genre. En effet, cette stratégie intègre une multiplicité d’actions et de mesures
pour dépasser les contraintes auxquelles les femmes font face dans les zones oasiennes et
de l’arganier, en lien avec l’accès à l’éducation, à la santé, aux infrastructures, à l’eau, à
l’emploi et aux opportunités économiques.
En outre, le DADREF poursuit le déploiement du Programme de Réduction des Disparités
Territoriales et Sociales (PRDTS) qui intègre des projets visant le renforcent de l’accès des
filles à l’éducation et de l’accès des filles et des femmes rurales aux services de santé. Ce
faisant, près de 264 actions ont été entreprises à ce jour à cet égard.
Le suivi de l’opérationnalisation de ces actions et du niveau de concrétisation des objectifs
fixés par lesdites stratégies en termes de promotion de l’égalité de genre et d’autonomisation
des femmes est assuré pat le Comité Technique Genre (CTG), composé des points focaux
genre des directions centrales et régionales ainsi que ceux émanant des institutions sous la
tutelle du département.
Les stratégies et programmes mis en place pour le DRADREF en faveur de la consolidation
de la contribution des femmes rurales et agricultrices à l’édification d’un développement
agricole et rural inclusifs lui confèrent un rôle clé dans la mise en      uvre du PGE III. Le
département est, en effet, partie prenante de plusieurs actions inscrites dans le cadre de l’axe
I dudit Plan et qui est relatif à l’autonomisation économique et au leadership des femmes.
Ces actions portent sur ce qui suit :
    Adaptation des équipements et des aménagements des centres de formation pour
     accroître les effectifs des filles lauréates de la formation professionnelle agricole ;



                                                                                             93
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


    Apport de soutien et d’appui à l’organisation des productrices agricoles et à la
     promotion du leadership féminin dans les organes décisionnels des organisations
     professionnelles ;
    Mise en place de programme de soutien à la consolidation et à l’augmentation de
     revenus des femmes agricultrices cheffes d’exploitation par le développement et la
     reconversion dans l’arboriculture fruitière, le développement de l’apiculture la
     valorisation et la commercialisation des productions ;
    Renforcement de la participation des femmes aux programmes de développement du
     conseil agricole ;
    Elaboration de banque d'idées de projets en consacrant 25% de ces projets aux
     femmes au titre de la période 2023-2026.
    Renforcement de l'accès des femmes à l'accompagnement et à la formation technique
     en agriculture et élevage ;
    Intégration de la dimension genre dans les projets de l’agriculture solidaire ;
    Renforcement de la mise en          uvre du programme d’appui aux coopératives du
     secteur agricole, tout en ciblant les coopératives féminines.
    Mise en place de projets de développement socio-économiques des femmes rurales.
    Amélioration des conditions de travail des femmes rurales et celles en situation de
     précarité travaillant dans les différentes filières agricoles.
2.3. Chaîne de résultats sensibles au genre : application de la démarche
performance sensible au genre
Conformément aux dispositions de la circulaire du Chef de Gouvernement (n°4/2024)
relative à l’établissement des propositions de Programmation Budgétaire Triennale assortie
des objectifs et des indicateurs de performance au titre de la période de 2025 à 2027, le
DRADREF a mis en place une chaîne de résultats prenant en compte les enjeux liés à l’égalité
de genre et qui couvre trois de ses programmes budgétaires, en l’occurrence, le programme
relatif au développement des filières de production, celui dédié à l'enseignement, à la
formation et à la recherche, et enfin le programme consacré au soutien et aux services
polyvalents.
La chaîne de résultats sensibles au genre adoptée par le DRADREF traduit les efforts
entrepris par le département en faveur de la promotion de l’égalité de genre et de
l’autonomisation des femmes en matière de conseil agricole, d’encadrement de groupements
professionnels et d’accès à la formation professionnelle agricole, à la formation sur les
thématiques liées au genre et aux postes de responsabilité (voir tableau ci-dessous).
Ainsi, le degré de concrétisation de l’objectif du programme dédié au développement des
filières de production et visant l’amélioration du taux d’encadrement des agriculteurs et le
renforcement l’intégration de genre est approché par un indicateur de performance sensible
au genre qui renseigne sur le taux d’encadrement de groupements professionnels féminins
dans le cadre des programmes de développement des produits de terroir dont le niveau a
atteint 39% en 2023. En outre, le suivi du niveau de réalisation de cet objectif est, également,
assuré par deux sous-indicateurs de performance qui mesurent le nombre d’agricultrices
encadrées par chaque conseiller agricole, situé à 802 agricultrices par conseiller agricole en
2023 et le nombre d’agriculteurs encadrés par chaque conseiller agricole qui a avoisiné 4.924
agriculteurs au titre de l’année 2023.
Pour ce qui est du programme relatif à l’enseignement, la formation et la recherche, le niveau
de réalisation de son objectif portant sur l’amélioration de la qualité de l’enseignement
technique et de la formation professionnelle agricole est mesuré par deux sous-indicateurs
intégrant la dimension genre et qui portent sur le taux cumulé des filles et celui des garçons
diplômé.e.s des établissements de la formation professionnelle agricole qui ont atteint
respectivement 6% en 2023 et 16% en 2023. Quant à l’objectif relatif à l’intégration de la
dimension genre dans les programmes de développement agricole, le degré de sa


    94
                                RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


concrétisation est approché par deux sous-indicateurs sensibles au genre et qui mesurent
respectivement le nombre de femmes rurales bénéficiaires de formations intégrant le genre
(250 femmes rurales en 2023) et le nombre de points focaux et cadres bénéficiaires de
formations intégrant le genre (50 points focaux genre en 2023).
Le programme relatif au support et aux services polyvalents vise, entre autres,
l’institutionnalisation d’une administration publique équitable basée sur un système de
compétences dont le degré de réalisation est mesuré par un indicateur de performance
renseignant sur la part des femmes candidates aux postes de responsabilité qui a avoisiné
46,5% en 2023.
                                                                                                                      Réalisations    LF
Programmes                              Objectifs                Indicateurs               Sous-indicateurs
                                                                                                                         2023        2024
                                                                                      Nombre        d’agricultrices
   Développement des filières




                                                                                     encadrées par chaque                 802        109
                                                             Nombre d’agriculteurs
                                                                                     conseiller agricole
                                                            encadrés par conseiller
                                                                                      Nombre        d’agriculteurs
         de production




                                                            agricole
                                 Améliorer      le    taux                           hommes encadrés par                 4.924       572
                                 d’encadrement         des                           chaque conseiller agricole
                                 agriculteurs            et Taux d’encadrement de
                                 renforcer l’intégration groupements
                                 de genre                   professionnels féminins
                                                            dans le cadre des                                             39%        50%
                                                            programmes            de
                                                            développement        des
                                                            produits de terroir
                                                                                     Taux cumulé des diplômés
                                 Améliorer la qualité de                             des établissements de la
                                                            Taux     cumulé      des formation professionnelle            6%          7%
                                 l’enseignement
   Enseignement, formation et




                                                            diplômés             des agricole – filles-
                                 technique et de la
                                                            établissements de la Taux            cumulé         des
                                 formation
                                                            formation                diplômés                   des
                                 professionnelle
                                                            professionnelle agricole établissements       de     la       16%        19%
           Recherche




                                 agricole                                            formation professionnelle
                                                                                     agricole – garçons-
                                                                                     Nombre        de     femmes
                                                                                     rurales bénéficiaires de
                                 Intégrer la dimension                                                                    250        250
                                                             Nombre               de formations intégrant le
                                 genre       dans       les
                                                            bénéficiaires         de genre
                                 programmes             de
                                                            formations intégrant le Nombre de points focaux
                                 développement                                       et cadres bénéficiaires de
                                                            genre                                                         50          50
                                 agricole                                            formations intégrant le
                                                                                     genre
                                  Institutionnaliser une
polyvalen
 Support

 services




                                 administration              Part    des     femmes
    et




                                 publique        équitable candidates aux postes                                         46,5%       45%
    ts




                                 basée sur un système de responsabilité
                                 de compétences
                                                                                                                          Source : DA, 2024

             Tableau 41 : Chaîne de résultats sensibles au genre mise e n place par le
                                             DADREF
La chaîne de résultats sensibles au genre susmentionnée n’intègre, toutefois, pas l’ensemble
des leviers d’action actés par le DRADREF pour la réduction des inégalités de genre et la
promotion de l’autonomisation des femmes agricultrices et rurales.




                                                                                                                                        95
     PROJET DE LOI DE FINANCES POUR L’ANNEE 2025



3. MINISTERE DE L’INDUSTRIE ET DU COMMERCE
Le Ministère de l'Industrie et du Commerce (MIC) joue un rôle clé dans la consolidation des
efforts entrepris par notre pays pour promouvoir l'emploi, l'entrepreneuriat et le leadership
féminin au sein des secteurs de l'industrie et du commerce.
3.1. Analyse genre : point de départ pour réussir une programmation
intégrant la dimension genre
Le MIC ne dispose à ce jour que d’une seule analyse genre des secteurs de l’industrie et du
commerce réalisée, en 2019, dans le cadre du programme d’appui à la mise en uvre du PGE
II. Néanmoins, il est important de noter, dans ce cadre, la publication en 2024 des principaux
résultats de l’édition 2023 de l’enquête industrielle qui intègre une analyse genre du secteur.
En effet, ces résultats incluent une analyse de la ventilation par genre et par région de
l’emploi dans les différentes branches industrielles. De même, ces analyses ont traité l’emploi
féminin par âge des entreprises industrielles. La question liée au leadership féminin dans le
secteur industriel, approchée par le niveau de présence des femmes dans les postes de
direction selon la taille du chiffre d’affaires et l’âge des entreprises industrielles, a été
également couverte par ces analyses51.
Dans le même sillage, le MIC s’est lancé dans le développement d’une base de données
statistiques sur l'emploi et l’entreprenariat féminin. Cette initiative vise à fournir, selon une
cadence régulière, les analyses genre nécessaires pour tout exercice de suivi et d’évaluation
du degré de la prise en compte des questions liées à l’égalité de genre dans la stratégie
d’action du Ministère.
3.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie du Ministère et les plans nationaux pour la
promotion de l’égalité de genre et l’autonomisation économique des
femmes
De par ses missions et ses attributions, le MIC       uvre activement au renforcement de
l’employabilité et de l’entreprenariat féminin dans les différentes activités industrielles et
commerciales. Cette implication fait du Ministère un acteur clé dans le processus de mise en
   uvre du PGE III (2023-2026), principalement, son axe I relatif à l’autonomisation et au
leadership des femmes.
3.3. Chaîne de résultats sensibles au genre : application de la démar che
performance sensible au genre
Le MIC s’est engagé dans une dynamique continue pour l’enrichissement de sa chaîne de
résultats sensibles au genre à même de refléter les efforts déployés par le Ministère en faveur
de la promotion de l’égalité de genre et de l’autonomisation des femmes dans les secteurs
de l’Industrie et du Commerce. Cet engagement s’est, en effet, traduit par l’intégration de
deux nouveaux sous-indicateurs de performance sensibles au genre qui relèvent des
programmes du développement industriel et du développement du commerce et de la
qualité. Il s’agit, en l’occurrence, de la part des femmes dans l'effectif du secteur de l'industrie
et du taux des femmes fondatrices/Co-fondatrices/Présidentes Directrices Générales des
startups accompagnées dans le cadre du Moroccan Retail Tech Builder52.



51https://www.mcinet.gov.ma/sites/default/files/Rapport%20Enquete%20industrielle_VF-
D%C3%A9f_compressed.pdf
52 Ce programme est lancé en partenariat entre le Ministère de l’Industrie et du Commerce, l’Université

Mohammed VI Polytechnique et la Fondation OCP. Ce programme vise à faire émerger des champions nationaux,
de stimuler le développement de solutions digitales innovantes, créatrices de valeur pour les commerçants et
destinées à améliorer l’expérience des consommateurs.


        96
            RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


 Conformément aux dispositions de la circulaire du Chef du Gouvernement (n°4/2024)
 relative à l’établissement des propositions de Programmation Budgétaire Triennale assortie
 des objectifs et des indicateurs de performance au titre de la période de 2025 à 2027
 insistant sur l’importance de la mise en place des objectifs et des indicateurs sensibles au
 genre pour une application réussie de la BSG, le MIC a développé une chaîne de résultats
 sensibles au genre au titre du PLF 2025 qui couvre ses trois programmes budgétaires à savoir
 : les programmes relatifs au support et pilotage, au développement industriel et au
 développement du commerce et de la qualité. Chaque programme est associé à un sous-
 indicateur sensibles au genre, comme détaillé dans le tableau qui suit :
                                                                                                  Réalisations LF
 Programmes              Objectifs              Indicateurs            Sous indicateurs
                                                                                                     2023     2024
               Institutionnaliser      une
               administration publique
Support     et                               Taux d’accès à la Taux d’accès des femmes à la
               équitable basée sur un                                                                40%        45%
pilotage                                     formation         formation
               système                  de
               compétences
               Assurer la création de
                                             Nombre d'emplois
               400.000            emplois
Développement                                créés     dans  le Part des femmes dans l'effectif
               industriels en tenant                                                                   -        30%
industriel                                   secteur        de du secteur de l'industrie
               compte      de     l’aspect
                                             l'industrie
               genre
                                                                  Taux        de        femmes
                                                                  fondatrices/Co-
                                             Taux
Développement Accompagner                 le                      fondatrices/Présidentes
                                             d’accompagnemen
du commerce et développement         du   e-                      Directrices  Générales   des         -          -
                                             t de startup dans le
de la qualité  commerce                                           startups accompagnées dans
                                             cadre du MRTB
                                                                  le cadre du Moroccan Retail
                                                                  Tech Builder
                                                                                                  Source : MIC, 2024

      Tableau 42 : Chaîne de résultats sensibles au genre mise en place par le MIC
 Afin de concrétiser les objectifs escomptés en matière d’amélioration de l’employabilité et
 de l’entreprenariat des femmes dans les activités industrielles et commerciales, le MIC s’est
 lancé dans plusieurs projets et activités à savoir :
  Signature d’une convention de partenariat avec l'Association des Femmes Chefs
   d'Entreprises du Maroc (AFEM) pour le lancement d'un programme visant à renforcer
   l'entrepreneuriat féminin dans le secteur industriel national, intitulé « She Industriel». Ce
   programme a pour ambition d’encourager 2.200 femmes à créer leurs propres entreprises
   dans les différents secteurs industriels en leur fournissant un soutien complet et adapté
   durant 2 ans et ce, afin de leur permettre de mettre en place leurs projets
   d’investissement ;
  Encouragement de l'adhésion des femmes aux chambres de Commerce, d’Industrie et
   des Services afin de faciliter leur accès à l'accompagnement et à l'appui de proximité ;
  Mise en    uvre d’un programme d'appui aux femmes à revenu faible opérant dans le
   secteur du commerce afin de consolider la digitalisation de leurs activités ;
  Lancement d’actions de communication et de sensibilisation des jeunes filles et des
   femmes visant à les encourager et à les motiver afin de s’orienter vers les métiers et
   l’entreprenariat industriels, et lutter contre les stéréotypes liés aux métiers industriels ;
  Opérationnalisation du programme We-Fi (Women Entrepreneurs Finance Initiative53)
   pour soutenir les femmes entrepreneurs et membres des coopératives ;



 53Les détails relatifs à ce programme sont présentés dans l’édition 2024 du Rapport sur le Budget axé sur les
 Résultats tenant compte de l’Aspect Genre.


                                                                                                                 97
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


 Implication au côté de plusieurs départements ministériels dans la mise en       uvre du
  programme « Douar Attamkine » qui ambitionne de fournir une formation qualifiante au
  profit des femmes pour leur faciliter l'accès au marché du travail, de créer des espaces
  dédiés au développement du leadership chez les femmes rurales et de promouvoir leur
  indépendance financière en encourageant la création de petites entreprises, de
  coopératives, ainsi que d'activités génératrices de revenus.
3.4. Progrès législatif, réglementaire et institutionnel en faveur de la
promotion de l’égalité de genre
L’année 2024 est marquée par l’entrée en vigueur de la Loi n°19-20 qui constitue une avancée
majeure en faveur de la consolidation de la mixité dans les conseils d'administration des
Sociétés Anonymes faisant appel public à l’épargne. En vertu de cette Loi, les femmes
devront représenter, à partir de l’année 2024, au moins 30% des membres des organes de
gestion et de contrôle des entreprises, avec une ambition d'atteindre 40% à l’horizon 2027.

4. MINISTERE DU TOURISM E, DE L’ARTISANAT ET D E
L’ECONOMIE SOCIALE E T SOLIDAIRE
    Département du Tourisme
De par ses missions et attribution, le Département du Tourisme (DT) joue un rôle clé dans le
renforcement de l’autonomisation économique des femmes et la consolidation de leur
contribution à la création de la richesse. Conscient de ces enjeux, le département a lancé, en
juin 2024, une analyse genre de ses domaines d’interventions en partenariat avec le CE-BSG.
Cette analyse a pour objectif d’établir un diagnostic détaillé des enjeux de genre dans le
secteur du tourisme, accompagné de recommandations opérationnelles pour renforcer la
pertinence de l’ancrage de la dimension genre dans les pratiques de programmation et de
budgétisation du département et, ainsi, enrichir sa chaîne de résultats sensibles au genre.
    Département de l’Artisanat, de l’E conomie Sociale et Solidaire
     (DESS)
Le Département de l’Artisanat, de l’Economie Sociale et Solidaire (DESS) poursuit son
engagement en faveur de la valorisation de la contribution des femmes artisanes à l’essor de
l’artisanat marocain. De même, la stratégie pour la promotion de l’économie sociale et
solidaire mise en place par le département intègre les préoccupations liées à la réduction des
inégalités de genre et à la promotion de l’autonomie des femmes.
4.1. Analyse genre : point de départ pour réussir une programmation
intégrant la dimension genre
Au regard de l’indisponibilité d’une analyse genre des domaines d’interventions du DAESS,
les actions entreprises par le département pour la promotion de l’égalité entre les femmes
et les hommes se réfèrent à ses priorités identifiées et à ses objectifs stratégiques arrêtés. Il
serait, toutefois, judicieux de procéder à l’élaboration d’une analyse sous le prisme genre de
la stratégie du département pour consolider la fiabilité et la pertinence de sa chaîne de
résultats sensibles au genre.
4.2. Alignement des priorités en termes de réduction des inégalités de
genre avec la stratégie du Ministère et les plans nationaux pour la
promotion de l’égalité de genre et l’autonomisation économique des
femmes
La stratégie d’action du DAESS pour le développement du secteur de l’artisanat intègre un
ensemble de mesures en faveur des femmes artisanes qui concernent les aspects en relation




    98
              RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


avec la fourniture d’infrastructure répondant à leurs besoins, l’accompagnement et l’appui
pour la commercialisation de leurs produits ainsi que les aspects liés à l’accès à la formation...
De même, les orientations stratégiques du Département en matière d’économie sociale et
solidaire prennent en compte la dimension genre, à travers plusieurs leviers d’actions qui
concernent la promotion du domaine de l’économie sociale et solidaire et de ses valeurs
auprès des femmes, l’apport d’appui aux régions pour la mise en place d’incubateurs dédiés
aux femmes et la sensibilisation des donneurs d’ordre et acheteurs publics pour la prise en
compte de la dimension genre dans la sélection des prestataires. Il est à noter que les
conventions cadres et spécifiques signées entre le département et les Conseils des Régions,
dans le cadre de l’opérationnalisation des Plans de Développement Régionaux de l'Économie
Sociale (PDRES), intègrent la dimension genre et ce, en se focalisant sur le renforcement de
l’autonomisation économiques des femmes à l’échelle territoriale.
L’ensemble de ces interventions en faveur de la promotion de l’égalité de genre et de
l’autonomisation s’alignent parfaitement sur les objectifs du PGE III en termes de
renforcement de l’autonomisation économique des femmes et de protection de leurs droits.
4.3. Chaîne de résultats sensibles au g enre : application de la démarche
performance sensible au genre
Conformément aux dispositions de la circulaire du Chef du Gouvernement (n°4/2024)
relative à l’établissement des propositions de Programmation Budgétaire Triennale assortie
des objectifs et des indicateurs de performance au titre de la période de 2025 à 2027, le
DAESS a développé une chaîne de résultats sensibles au genre54 qui couvre ses deux
programmes budgétaires relatifs à l’artisanat et à l’économie sociale (voir tableau 44).
4.3.1. Chaîne de résultats sensibles au genre mise en place par le Département
Ainsi, le degré de réalisation de l’objectif du programme budgétaire dédié à l’artisanat visant
l’amélioration des moyens de production et la promotion de la qualité est mesuré par
plusieurs sous-indicateurs de performance sensibles au genre qui renseignent sur la part des
femmes dans le total des bénéficiaires d’appui (78% en 2023), le nombre de femmes
bénéficiaires des infrastructures mises en service (2.888 femmes bénéficiaires en 2023) et le
taux des unités d’artisanat portées par des femmes auditées. En matière d’appui dont
bénéficie les femmes les femmes artisanes, le tableau qui suit décline l’état d’avancement
des principales mesures actées par le DAESS dans ce sens.


Mesures entreprises                       Réalisations au profit des artisanes
                                        Le DAESS a contribué, de 2012 à 2023, à la création de 102 Dars Sanaa
Dars Sanaa                              dans le milieu rural et périurbain, au profit de 3.884 femmes exerçant les
                                        métiers du tapis rural, de la broderie et la couture.
Labellisation,  certification       et
                                       Le secteur de l’artisanat dispose aujourd’hui de 33 labels et marques
innovation pour la promotion        de
                                       d’artisanat relatifs à des biens produits principalement par les femmes
la qualité des produits             de
                                       artisanes, ce qui représente environ 50% du total des labels et marques
l’artisanat et la protection        du
                                       élaborés par le Département.
patrimoine artisanal marocain
                                                                                              Sources : DAESS, 2024

     Tableau 43 : Mesures d’appui et d’accompagnement actées par le DAESS en
                            faveur des femmes ar tisanes
Quant à l’objectif du même programme portant sur la formation et le renforcement des
capacités des acteurs du secteur de l’artisanat, le suivi du niveau de sa réalisation est
approché par trois sous-indicateurs de performance, en l’occurrence, le taux de lauréates de

54   Ladite chaîne de résultats sensibles au genre est en cours de finalisation


                                                                                                                99
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025


la formation professionnelle dans les métiers de l’artisanat (61% en 2023), le taux des
artisanes formées (35% en 2023) et le taux de couverture des places des établissements de
la formation professionnelle relevant du département de l’artisanat qui sont destinées aux
femmes (61% en 2023).
En outre, le niveau de concrétisation de l’objectif du programme relatif à l’économie sociale
visant le renforcement et l’harmonisation d’une économie sociale et solidaire performante
est mesuré par un sous-indicateur sensible au genre. Ce dernier renseigne sur le nombre des
femmes bénéficiaires des sessions de formation organisées en marge des salons nationaux,
régionaux et des marchés itinérants locaux de l’économie sociale et solidaire et dans le cadre
des programmes de renforcement des capacités organisés au niveau des régions. Le nombre
des femmes bénéficiaires de ces formations a atteint 1.184 bénéficiaires au titre de l’année
2023.
                                                                                                          Réalisations    LF
                                  Objectifs               Indicateurs             Sous-indicateurs
Programmes                                                                                                   2023        2024
                                                    Nombre     des      unités Taux     des     unités
                                                                                                                         20%
                                                    auditées                   féminines auditées

                           Améliorer les moyens de Nombre                 des   Taux    des     femmes
                                                                                                              78%        60%
                           production            et bénéficiaires d'appui       bénéficiaires d'appui
                           promouvoir la qualité                                Nombre de femmes
          Artisanat




                                                    Nombre
                                                                                bénéficiaires       des
                                                    d'infrastructures mises                                  2.888       3.756
                                                                                infrastructures mise en
                                                    en service
                                                                                service
                                                    Nombre de lauréats          Taux de lauréates             61%        61%
                           Former et renforcer les                              Taux de couverture -
                           capacités des acteurs du Taux de couverture          Femmes
                                                                                                              61%        62%
                           secteur                  Nombre des artisans         Taux des artisanes
                                                                                                              35%        35%
                                                    formés                      formées
   Economie
                 Sociale




                           Renforcer et harmoniser Nombre      global   des Nombre des femmes
                           une économie sociale et bénéficiaires        des bénéficiaires  de                 1.184      1.650
                           solidaire performante   sessions de formation    formation

                                                                                                          Source : DAESS, 2024

        Tableau 44 : Chaîne de résultats sensibles au genre, mise en place par le
                                         DAESS
4.3.2. Actions en faveur de la promotion d’égalité de genre non intégrées dans
les chaînes de résultats sensibles au genre
Au-delà des leviers d’actions pris en compte dans la chaîne de résultats sensibles au genre
adoptée par le DAESS, d’autres programmes, projets et actions sont déployés par le
département et qui ambitionnent la promotion de l’égalité de genre. Il s’agit principales de
ce qui suit :
 Programme national MOAZARA : l’année 2024 marque l’opérationnalisation de la 5ème
  édition du programme. Ces quatre premières éditions ont bénéficié à 52.506 personnes
  dont les femmes représentent 62%. Il est à rappeler que ce programme vise à cofinancer
  des projets de développement portés par des associations, des réseaux d’associations et
  des coopératives actives dans le secteur de l’économie sociale et solidaire ;
 Programme d’autonomisation des femmes à travers l’entreprenariat durable (AFED), en
  partenariat avec le Département des Affaires Étrangères du Commerce et du
  Développement du Canada (MAECD) ;
 Programme TAHFIZ-NISWA, en partenariat avec l’Agence Espagnole pour la Coopération
  internationale au développement (AECID) : ce programme déployés dans 4 régions


       100
      RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


(Tanger-Tétouan-Al Hoceima, l’Oriental, Casablanca-Settat et Souss-Massa) a pour
objectif de renforcer l’autonomisation des femmes par le biais de l’entreprenariat dans le
domaine de l’économie sociale et solidaire…




                                                                                       101
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025



          ANNEXES :
          ANNEXE 1 : PRESENCE DES FEMMES DANS LES
            STRUCTURES     ORGANISATIONNELLES     DES
            DEPARTEMENTS MINISTERIELS ET INSTITUTIONS
            PUBLIQUES
                                                                                        Taux d’accès des femmes aux postes
Département/institution publique                           Taux de féminisation
                                                                                                 de responsabilité

Délégation Interministérielle aux Droits de
                                                                  45,24%                                 30,43%
l’Homme

Ministère de la Justice                                             50%                                    18%

Délégation Générale à l’Administration
                                                                   13,3%                                  7,14%
Pénitentiaire et à la Réinsertion55

Ministère des          Habous       et    des   Affaires                                -    46% (Administration centrale)
                                                                    36%
Islamiques                                                                              -    53% (Services extérieurs)

Ministre de la Solidarité, de l’Insertion Sociale
                                                                   49,6%                                  36%
et de la Famille

Ministère de l’Economie et des Finances                             40%                                   27%

Département      de            la        Réforme     de
                                                                    52%                                  40,6%
l’Administration
                                                                                       - Service central : 44%
Département des Affaires Etrangères et de
                                                                    43%                - Missions Diplomatiques et
la Coopération Africaine
                                                                                        Consulats (MDPC) : 37%

Département de la Communication                                    43,5%                                 46,2%


Haut-Commissariat au Plan                                           48%                                   45%

Conseil    Economique,                    Social     et
                                                                    42%
Environnemental

Département de la Transition Energétique                            39%                                   33%

Département chargé du Développement
                                                                    54%                                  42,4%
Durable
Ministère de l’Aménagement du Territoire
National, de l’Urbanisme, de l’Habitat et de la                   46,86%                                 39,73%
Politique de la Ville

Ministère du Transport et de la Logistique                          33%                                  26,4%


Département chargé de l’Eau                                       30,3%56                                31,25%




55
     Ces données concernent l’année 2023.
56
      L’effectif total de la police des eaux, ayant pour mission principale le contrôle du domaine public hydraulique (DPH), s’élève
     à 208 en 2024 dont 30 femmes policières de l’eau (soit un taux de féminisation de la police des Eaux de 14,4%).




        102
               RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


Ministère de la Santé et de la Protection
                                                             69%                         25%
Sociale
                                                      42,6%
       Département chargé de l’Education
                                                  (administration                        19%
                  Nationale
                                                     centrale)
                                             -34% de l’effectif des        -Administration   Centrale :   50
Ministère de l’Enseignement Supérieur, de la enseignants chercheurs        femmes responsables
Recherche Scientifique et de l’Innovation57 -45%      de      l’effectif   -Universités :   86        femmes
                                             administratif                 responsables
Département chargé             de    la   Formation
                                                             45%                         46%
Professionnelle58

Département chargé de la Jeunesse                            49%                        24,7%

Ministère d’Inclusion Economique de la
Petite   Entreprise,  d’Emploi et  des                      41,4%                       25,4%
Compétences
Département    de     l’Agriculture,              du
                                                            39,2%
Développement Rural et Eaux et Forêts

Ministère de l’Industrie et du Commerce                     41,53%                      29,02%

Département chargé de l’Artisanat et de
                                                             42%                         24%
l’Economie Sociale




57
     Données relatives à l’année universitaire 2022-2023.
58
     Données relatives à l’année 2024.


                                                                                                         103
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025



          ANNEXE 2 : ANNEXES STATISTIQUES
1- Démographie
                                                                                 2015    2016    2017    2018    2019    2020    2021    2022    2023    2024

   1-1 Population par sexe (En milliers) (1)                                     34125 34487 34852 35220 35587           35952   36313   36670 37022     37370

    Femmes                                                                       17123   17306 17490 17676       17861   18045   18227   18406   18583   18758
    Hommes                                                                       17002   17181   17362 17544     17726   17907   18086   18264   18439   18611

    Taux de féminité                                                             50,2    50,2    50,2    50,2    50,2    50,2    50,2    50,2    50,2    50,2

       0 - 14 ans                                                                48,9    48,9    48,9    48,9    48,9    48,9    48,9    48,9    48,9     48,9

      15 - 24 ans                                                                50,0    49,8    49,7    49,5    49,4    49,3    49,2     49,1   49,0    49,0
      25 - 34 ans                                                                50,8    50,8    50,8    50,8    50,7    50,7    50,6    50,5    50,4     50,3

      35 - 44 ans                                                                51,4    51,4    51,4    51,3    51,3     51,3   51,2     51,2    51,1    51,1
      45 ans et plus                                                             50,7    50,8    50,8    50,9    51,0     51,1    51,2   51,3     51,4    51,4
                                                                                 2012    2013    2014    2015    2018    2019    2020    2021    2022    2023

   1-2 Fécondité

    Indice synthétique de fécondité                                              2,20    2,10    2,20    2,19    2,38     2,12   2,10    2,10    2,07    2,05

     Urbain                                                                      1,80    1,80    2,00    1,99    2,12     1,93   1,90    1,90     1,89    1,87
     Rural                                                                       2,70    2,63    2,50    2,49    2,80    2,42    2,40    2,40    2,40     2,36
                                                                                 14/15   15/16   16/17   17/18   18/19   19/20   20/21   21/22   22/23   23/24

   1-3 Natalité
    Taux brut de natalité (pour mille)                                           17,8    17,6    17,4    17,2    16,9    16,7    16,5    16,2    16,0     15,7
     Urbain                                                                      16,7    16,6    16,5    16,4    16,2     16,1   15,9     15,7    15,5    15,2

     Rural                                                                       19,5     19,1   18,8    18,5     18,1    17,8   17,5     17,2   16,9     16,7
                                                                                 2004 2009       2010    2011    2012    2013    2014    2020    2021    2022

   1-4 Nuptialité

    Etat matrimonial de la population feminine âgée de 15 ans et plus (%)
     Célibataires                                                                34,0    33,9    33,2    32,0     31,1   30,7    28,9     28,1    28,1    28,3

     Mariés                                                                      52,8    54,3    55,0    55,8    56,5    56,9    58,0    57,8    57,6     57,2
     Veufs                                                                        10,1    9,3     9,2     9,3     9,5     9,4     9,8     10,8   10,8     10,8
     Divorcés                                                                     3,1     2,5     2,6     2,9     2,9     3,0     3,3     3,3     3,5     3,7

                                                                                 1982    1993    1994    1999    2001    2003    2004    2007    2010    2014

   Proportions de femmes célibataires aux groupes d’âge 15-19 et 20-24 ans
     15 - 19                                                                     81,5    87,5    87,2    91,4    92,4    89,0    88,9    92,9    90,7     87,1
     20 - 24                                                                     40,5    56,0    55,6    67,2    69,8     61,7   61,3    65,3    61,4     53,0

                                                                                 1971    1982    1994    2004    2007    2009    2010    2011    2014    2018(1)

    Age moyen au premier mariage
     National
       Hommes                                                                    25,0    27,2    30,0    31,2    31,8     31,6   31,4     31,2    31,4    31,9
       Femmes                                                                    19,3    22,3    25,8    26,3    27,2    26,6    26,6    26,3    25,8     25,5
     Urbain
       Hommes                                                                    26,0    28,5    31,2    32,2    32,9    32,5    32,5    32,5     32,1    33,1
       Femmes                                                                    20,9    23,8    26,9    27,1    27,9    27,0    27,4    27,2    26,4     26,6
     Rural
       Hommes                                                                    24,2    25,6    28,3    29,5    30,2    29,9    30,0    29,5    30,3    30,0
       Femmes                                                                    18,5    20,8    24,2    25,5    26,3    25,7    25,6    25,3    24,9     23,9
                                                                                 2015    2016    2017    2018    2019    2020    2021    2022    2023    2024

   Répartition des ménages selon le sexe du chef de ménage (2)
     Femmes                                                                      16,3    16,4    16,5    16,6    16,7     16,7   16,9     17,0    17,1    17,2
       Urbain                                                                    18,7    18,8    18,9    19,0     19,1    19,1   19,3     19,4    19,5    19,6
       Rural                                                                      11,6    11,5    11,5    11,5    11,5    11,4    11,4    11,4    11,4    11,4
     Hommes                                                                      83,7    83,6    83,5    83,4    83,3    83,3    83,1    83,0    82,9     82,8
       Urbain                                                                    81,3    81,2     81,1   81,0    80,9    80,9    80,7    80,6    80,5    80,4
       Rural                                                                     88,4    88,5    88,5    88,5    88,5    88,6    88,6    88,6    88,6     88,6
Source : Haut commissariat au Plan
 (1) ENPSF 2018
 (2) Projections de la population CERED 2014-2050, ENDP 2009-2010 et RGPH 2014




       104
                   RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


2- Education et formation
                                                                                             14/15     15/16      16/17     17/18      18/19   19/20   20/21   21/22   22/23   23/24
 Taux spécifique de scolarisation dans l’enseignement
                                                                                              99,1      97,4      99,1      99,5       99,8    100     104     108      110    111,6
 primaire % (6-11 ans)
      Masculin                                                                               99,7       98,0      99,6      99,9       100,0   100,0   103,7   107,6   109,7    111,3
      Féminin                                                                                98,5       96,7      98,5      99,0       99,7    100,0   103,7   107,9   110,3   112,0
      Urbain : Masculin                                                                       101,1     96,0      97,7       97,2       97,1   96,7    98,7    101,6   103,1   103,5
          Féminin                                                                            98,5       95,6       97,1      96,8      97,0    96,8    99,0    102,1   103,8   104,3
      Rural :     Masculin                                                                    98,2     100,6      102,0     103,5      103,9   104,3   110,6   115,9   119,3   122,8
          Féminin                                                                            98,4       98,2      100,3     101,9      103,3   104,2   110,3   116,0   119,8   123,6
 Taux spécifique de scolarisation dans l’enseignement                                        90,4       85,2      87,6      89,7        91,8   94,2    94,7    99,1    100,6   101,1
 secondaire collégial (12-14 ans) (%)
      Urbain : Masculin                                                                      105,1      95,2      97,0       98,2      99,7    101,4   102,0   105,2   106,0   105,5
          Féminin                                                                             101,1     94,7      96,7       97,9      99,4    101,4   102,0   105,5   106,7   106,9
      Rural :     Masculin                                                                    81,3      79,1       81,9     85,0       87,0    89,3    89,6    94,7    95,9    96,5
          Féminin                                                                            68,9       66,3      69,4       72,4      75,8    79,8    80,1    86,5    89,4     91,7
   Taux spécifique de scolarisation dans l’enseignement
                                                                                              70,1      65,3      66,6      65,8       66,9    69,6     71,1   75,7    76,9    80,2
   secondaire qualifiant (15-17 ans) (%)
      Urbain : Masculin                                                                      100,9      86,1      86,3       83,8      83,7    85,7    87,0    89,9    89,6    92,4
          Féminin                                                                            90,5       83,8      86,3       86,7      87,8    90,5    92,5    96,1    97,4    100,4
      Rural :     Masculin                                                                   49,6       48,7      49,0      47,0       47,9    50,5    50,3    56,4     57,1   60,0
          Féminin                                                                            29,4       30,1      32,0       33,1      35,6    39,2    41,4    47,6    50,8    55,0
                                                                                             14/15     15/16      16/17     17/18      18/19   19/20   20/21   21/22   22/23   23/24
   Effectif des éléves dans le préscolaire
                                                                                              736       659        727       699       800     894     875     915      931    952
   (En milliers)
      Filles                                                                                  320       292        321       313        367     417    425      451     461     472
     Garçons                                                                                  416       367       405        386        433    477     450     464     470     480
   Effectif des élèves dans l'enseignement primaire
                                                                                             4039      4102       4211      4323       4432    4536    4553    4675    4683    4607
   (public+privé) (En milliers)

      Filles                                                                                  1915      1947     2000       2058        2117   2173    2185    2246    2252    2219
     Garçons                                                                                 2125       2155       2211     2265       2315    2363    2367    2430    2431    2387
   Effectif des élèves dans l'enseignement secondaire collégial
                                                                                             1627      1645       1681      1695       1737    1791    1781    1984    2062    2154
   (public+privé) (En milliers)

      Filles                                                                                  734       748        769       784        809    839     836     930     980     1028
      Garçons                                                                                 893       897        912        911       928    952     946     1053    1082     1126

   Effectif des élèves dans l'enseignement secondaire                                         975       980       1012      1014       1018    1039    1168    1161    1187    1243
   qualifiant (public+privé) (En milliers)
      Filles                                                                                  465       477       499        510        518    533     602     608      627     658
      Garçons                                                                                 510       503        513       505        501    505     567     552     560      585
                                                                                             14/15     15/16      16/17     17/18      18/19   19/20   20/21   21/22   22/23   23/24
   Effectif des étudiants dans l'enseignement
                                                                                              677       750        782       820        876    922     990     1061    1096    1106
   supérieur (Public) (En milliers)(1)
      Filles                                                                                  327       359        377       400        432    466      512    559      587     610

      Garçons                                                                                 351       392       405        420        420    420     478     503     509      497

   Effectif en formation professionnelle (en milliers)(2)                                     360       389       392        396        387     361    338     336

   Taux de technicité (%) (3)                                                                 67,2      67,6      66,7       65,4      64,8    66,1    68,1    70,2
                                                                                             1994      2004       2013      2014       2017    2018    2019    2020    2021    2022

   Taux d'analphabétisme de la population âgée de 15 ans et
   plus (En %) (4)

      Ensemble                                                                               58,4       47,7      39,2      35,8       38,3    37,2    35,9    34,9    34,2    32,7

        Femmes                                                                                71,3      60,4      50,5       46,7      48,8    47,5    46,1    45,0    43,9    42,3

        Hommes                                                                               44,8       34,4       27,1      24,6      27,5    26,6    25,4    24,5     24,1   22,9

        Femmes âgées de 15-24 ans                                                            42,0       39,6       18,2      14,8       13,3    11,4    9,5     7,8     7,2     4,6

        Femmes âgées de 25-49 ans                                                                       62,8       51,7      46,7      48,2    46,2    43,6    41,5    40,2    38,4

        Femmes âgées de 50 ans et plus                                                       97,0       90,9      80,0       76,9      78,6    77,5    76,5    76,3    74,4    72,9
Source : Département de l'Education Nationale, Ministère de l'Enseignement Supérieur, de la Recherche Scientifique et de l'Innovation, HCP
 (1) Effectifs des inscrits aus universités au Maroc
 (2) Source : Département de la Formation Professionnelle. Il s'agit de la formation résidentielle et altérnée public et privé
 (3) ll s'agit du taux de technicité dans la formation résidentielle et alternée public et privé
 (4) Source : RGPH 1994;2004, 2014, ENCDM 1998/1999 , Rapports "Indicateurs Sociaux" et "Femmes marocaines en chiffres", HCP



                                                                                                                                                                                105
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025



3- Activité, emploi et chômage
                                                                 2014    2015   2016   2017    2018   2019    2020   2021    2022   2023


   Population active féminine 15 ans et plus (En milliers)       3212    3203   3095   2909    2879   2877    2703   2881    2761   2684
    Urbain                                                       1378    1373   1337   1538    1554   1621    1605   1715    1708   1767
    Rural                                                        1834    1830   1758    1371   1325   1256    1098   1166    1052    917

                                                                 2014    2015   2016   2017    2018   2019    2020   2021    2022   2023
   Structure de la population active féminine selon les groupes d'âges (En %)
     National
      15 - 24 ans                                                 17,2   16,6   16,0   15,1    14,3   13,3    12,2   12,1    12,2   12,3
      25 - 34 ans                                                28,8    29,1   23,2   28,4    28,6   29,1    29,1   29,5    30,3   31,8
      35 - 44 ans                                                22,5    22,7   19,2   23,5    23,4   23,7    24,4   24,3    23,8   23,1
      45 ans et plus                                              31,5   31,6   34,8   33,0    33,8   33,9    34,3   34,0    33,7
     Urbain
      15 - 24 ans                                                 13,9   14,3   21,0   15,6    14,6   13,3    12,8   12,6    12,7
      25 - 34 ans                                                34,9    35,2   22,5   35,1    35,7   36,3    35,9   36,6    37,2
      35 - 44 ans                                                24,4    24,2   19,9   24,5    24,2   24,2    24,8   24,8    24,1
      45 ans et plus                                             26,7    26,3   36,6   24,7    25,6   26,2    26,5   26,0    26,0
     Rural
      15 - 24 ans                                                 19,6   18,4   25,9   14,6    13,9   13,3    11,9   11,3    11,4
      25 - 34 ans                                                24,2    24,4   24,2   20,9    20,1   19,9    19,1   19,1    19,1
      35 - 44 ans                                                 21,1   21,6   18,0   22,3    22,5   22,9    23,6   23,5    23,3
      45 ans et plus                                              35,1   35,6   31,9   42,3    43,3   43,8    45,4   45,9    46,2

                                                                 2014    2015   2016   2017    2018   2019    2020   2021    2022   2023
Taux d'activité des femmes (En %)

      National                                                   25,3    24,8   23,6   22,4    21,8   21,5    19,9   20,9    19,8   19,0

        Urbain                                                    17,8   17,4   16,6   18,4    18,1   18,5    17,9   18,7    18,3   18,5

        Rural                                                    36,9    36,6   34,6   29,6    28,6   27,1    23,7   25,2    22,8   19,9

   Population active occupée féminine 15 ans et plus (En
   milliers)                                                     2877    2867   2757   2483    2469   2489    2265   2398    2287   2192

    Urbain                                                       1076    1075   1041   1153    1178   1268    1209   1276    1277   1326
    Rural                                                        1801    1793   1716   1329    1291    1221   1056    1122   1009   866

                                                                 2014    2015   2016   2017    2018   2019    2020   2021    2022   2023
   Taux d'emploi de la population féminine selon les groupes d'âges (En %)
    National
    15 - 24                                                       14,5   13,8   12,0   9,8     9,2    8,8     6,7    7,0     6,5
    25 - 34                                                      25,7    25,7   24,6   22,0    22,0   22,3    20,0   21,3    20,6
    35 - 44                                                      28,3    27,8   27,7   25,8    25,2   25,4    23,7   24,5    22,9
    45 et plus                                                   23,2    22,5   21,0   19,8    19,3   18,7    16,9   17,5    16,3
     Urbain
    15 - 24                                                       6,0    5,8     5,1    6,1    5,8    6,0      5,1   5,3      5,1
    25 - 34                                                       18,6   18,9   18,1   19,0    19,3   20,7    19,2   20,3    20,2
    35 - 44                                                       19,1   18,6   19,0   20,2    19,8   20,7    19,9   20,4    19,6
    45 et plus                                                    12,8   12,1   10,9   11,8    11,8   12,1    11,3   11,4    11,2
     Rural
    15 - 24                                                      25,2    24,0   20,8   15,4    14,4   13,0    9,2    9,7     8,6
    25 - 34                                                      36,2    35,8   34,4   27,8    27,3   25,7    21,7   23,8    21,5
    35 - 44                                                      44,6    44,3   43,0   36,9    36,3   35,3    31,8   33,7    30,6
    45 et plus                                                      41,5  41,1  39,5   34,7    33,3   31,2    27,9   29,5    26,6
   Taux de féminisation de l'emploi selon les secteurs d'activité économique (En %)
    National
         Agriculture, forêt et pêche                              41,7   41,4   40,9   34,2    33,6   32,7    30,8   32,0    30,1   37,0
         Industrie (y compris l’artisanat)                       26,3    26,3   24,9   25,9    25,9   26,4    25,2   25,9    26,1   15,0
         Bâtiments et travaux publics                             0,8     1,0    1,2    1,0     1,1    1,0     1,0    1,3     1,2   0,6
         Services                                                 19,0   19,0   18,2   19,0    18,7   19,5    19,0   19,8    19,3   47,3
     Urbain
         Agriculture, forêt et pêche                              21,5   20,7   19,6   19,5    20,0   19,2    17,8   16,9    15,5
         Industrie (y compris l’artisanat)                       26,7    26,3   25,2   26,6    26,4   26,7    26,0   27,6    27,5
         Bâtiments et travaux publics                             1,2    1,6     1,9   1,4      1,6   1,4      1,5    1,9    1,8
         Services                                                 21,2   21,2   20,5   21,3    20,9   21,8    21,4   22,4    21,7

Source : - Haut commissariat au Plan



        106
                   RAPPORT SUR LE BUDGET AXE SUR LES RESULTATS TENANT COMPTE DE L’ASPECT GENRE


3- Activité, emploi et chômage (suite )
                                                                 2014    2015   2016    2017    2018    2019    2020    2021   2022   2023
   Taux de féminisation de l'emploi selon les secteurs d'activité économique (En %)
     Rural
         Agriculture, forêt et pêche                             43,0    42,8   42,3    35,4    34,8    34,0     32,1   33,4   31,5
         Industrie (y compris l’artisanat)                       24,6    26,2   23,7    22,0    22,9    24,9    20,8    16,9   18,8
         Bâtiments et travaux publics                             0,3    0,3     0,1     0,2     0,2     0,3
         Services                                                 7,8    8,5     7,6     7,4     6,9     7,2     6,5    7,3    7,4
                                                                 2014    2015   2016    2017    2018    2019    2020    2021   2022   2023

  Population active en chômage féminine
  (En milliers)                                                  334     336    338     427     410     388     438     483    474    492
   Urbain                                                        302     298    296     385     376     353      44      44    431    441
   Rural                                                          33      38     42     42      34      34       42      44    43      51
  Taux de féminité de la population active
  en chômage (En %)                                              28,6    29,2   30,6    35,1    35,1    35,0    30,7    32,0   32,9   31,1
   Urbain                                                        32,3    32,2   33,7    37,9    37,9    38,1     3,8    3,5    35,9   34,0
   Rural                                                         14,0    16,8   18,5    20,9    19,0    19,2     15,3   18,6   17,8    18,1

  Taux de chômage des femmes par milieu
  de résidence (En %)                                            10,4    10,5   10,9    14,7    14,1    13,5    16,2    16,8   17,2   18,3
   Urbain                                                        21,9    21,7   22,2    25,0    23,9     21,8   24,7    25,6   25,2   25,0
   Rural                                                          1,8    2,1    2,4      3,1     2,6     2,7    3,9      3,8    4,1    5,5

                                                                 2014    2015   2016    2017    2018    2019    2020    2021   2022   2023

  Taux de chômage des femmes au niveau national selon l'âge (En %)
   15 - 24                                                        19,1   21,4   23,3    34,3    33,6    33,4     41,2   41,9   44,4   47,5
   25 - 34                                                       17,0    16,8   17,6    23,8    23,0    22,9    26,2    26,9   28,0   28,8
   35 - 44                                                        7,0    6,3     6,5     8,0     7,6     6,6     8,9    9,7     9,1    9,1
   45 et plus                                                     2,1    2,0     2,1     2,5     2,5     2,3     4,0    4,0    3,2
  Taux de chômage des femmes selon le Diplôme (En %)
   Sans diplôme                                                   2,9    3,0     2,8     3,7     3,3     2,9     4,8    4,5    3,8    4,4
   Ayant un diplôme: Niveau moyen                                21,8    21,1   19,1    25,8    23,6    21,3    24,6    24,5   21,5   23,3
   Ayant un diplôme: Niveau supérieur                            28,3    27,3   29,8    33,0    32,6    29,5    31,8    32,8   34,8   33,3

4- Santé
                                                                 2014    2015   2016    2017    2018    2019    2020    2021   2022   2023
  Espérance de vie à la naissance (En années)                    75,5    75,8   75,9    76,1    76,3    76,4    76,6    76,7   76,9   77,0

   Femmes                                                        76,4    77,4   77,6    77,8    78,0    78,2    78,3    78,5   78,6   78,8

   Hommes                                                        74,5    74,2   74,3    74,5    74,6    74,8    74,9    75,1   75,2   75,3
                                                                         1979   1983    1987    1992    1995    1997    2004   2011   2018

  Taux de prévalence contraceptive (En %)                                19,4   25,5    35,9    41,5    50,3    58,4    63,0   67,4   70,8
   Urbain                                                                36,0   42,5    51,9    54,4    64,2    65,8    65,5   68,9    71,1
   Rural                                                                  9,7   15,2    24,9    31,6    39,2    51,7    59,7   65,5   70,3

                                                                                1972    78-84   85-91   92-96   94-03 04-09    2010   2018

  Taux de mortalité maternelle (pour 100 000 naissances
  vivantes)                                                                     631     359     332     228     227     132    112    72,6
   Urbain                                                                               249     284      125     187            73    44,6
   Rural                                                                                423     362     307      267           148    111,1

                                                                                87-91   1994    1995    2002    2004    2010   2011   2018

  Proportion d’accouchements assistés
   Ensemble                                                                     31,0    31,0    39,6    45,6    62,6    74,1   73,6   86,6
    Urbain                                                                      64,0    63,7    80,3    75,2    85,3    93,0   92,1   96,6
    Rural                                                                       14,0    13,8    19,3    26,6    39,5    56,7   55,0   74,2

  Proportion de femmes ayant fait au moins une consultation prénatale une consultation prénatale (En %)
   Ensemble                                                                      33     32,3    44,7            68,0    80,2   77,1   88,4
    Urbain                                                                       61     60,6    78,9             85,1   94,0   91,6   95,6
    Rural                                                                        18     17,6    27,6            48,3    68,3   62,7   79,6




Sources : - Haut commissariat au Plan

        - Département de la Santé




                                                                                                                                        107
 PROJET DE LOI DE FINANCES POUR L’ANNEE 2025




4- Santé (suite)
                                                                                                 2013       2014          2015    2016    2017    2019     2020    2021      2022    2023

   Personnel du Ministère de la Santé (hors CHU) (1)

         Total                                                                                  47637       47111     47331 47364 48418           49492    52319   55633     59109   62651
          Personnel médical                                                                      10638 10973          10091       10514   11204   12034    11953   12896     14359   15249
          Personnel paramédical (Infirmiers et techniciens de la santé)26036 25902 25899 25951                                            29738   31657    33837   35789     37376   38725

          Personnel administratif et technique                                                   10963 10236              11341   10899   7476    5801     6529    6948      7374    8677


  Indicateurs relatifs aux principaux programmes sanitaires

                                                                                                                                  2018            2019             2020              2021
  Couverture médicale de base

  Population marocaine bénéficiant d’une couverture médicale                                                                      68,8%           69,9%            70,2%             74,2%
       AMO salariés                                                                                                               28,6%            29,8%           30,4%             32,1%
       RAMED                                                                                                                      31,0%            30,5%           30,6%             32,1%
       AMO étudiants                                                                                                               0,2%             0,7%            0,7%             1,0%
       Population bénéficiant des dispositions de l’article 114 de la Loi 65.00                                                    4,4%             4,4%            4,0%             4,2%
       Mutuelle des Forces Armées Royales                                                                                          3,6%             3,6%            3,5%             3,5%
       Régimes spécifiques                                                                                                         1,0%             1,0%             1,0%            1,2%
                                                                                                                                                     2018
  Santé maternelle
                                                                                                                                    National        Urbain            Rural
    Taux de mortalité maternelle (100.000 naissances vivantes)                                                                     72,6             44,6             111,1
    Couverture par les soins prénatals qualifiés (1 visite)                                                                        88,4             95,6             79,6
    Couverture par les soins prénatals selon le niveau d’instruction de la mère :
        Secondaire et plus                                                                                                           99,6%
        Aucun                                                                                                                        82,6%

     Couverture par les soins prénatals selon quintile de bien-être :
        Quintile le plus riche                                                                                                       96,0%
        Quintile le plus pauvre                                                                                                      75,5%

    Couverture par les soins postnatals qualifiés :                                                                                  21,9%           27,1%            15,6%

    Couverture par les soins postnatals qualifiés                         par niveau d’instruction mère :
        Secondaire et plus                                                                                                           42,8%
        Aucun                                                                                                                        16,5%

    Proportion des accouchements assistés par du personnel qualifié                                                                  86,6%           96,6%            74,2%

    Proportion des accouchements assistés par du personnel qualifié selon le niveau d’instruction :
        Secondaire et plus                                                                                                           99,8%
        Aucun                                                                                                                        80,0%
    Lieu d’accouchement :
        Etablissement sanitaire                                                                                                      86,1%           96,0%            73,7%
        A domicile                                                                                                                   13,9%           4,0%             26,3%




Sources : - Département de la Santé

 (1) sources: Ressources humaines de la santé en chiffres, carte sanitaire- situation de l'offre de soins de santé 2020

         
"""
    conversation_history = StreamlitChatMessageHistory()  # Créez l'instance pour l'historique

    st.header("PLF2025: Explorez le rapport sur le budget axe sur les résultats tenant compte de l'aspect genre à travers notre chatbot 💬")
    
    # Load the document
    #docx = 'PLF2025-Rapport-FoncierPublic_Fr.docx'
    
    #if docx is not None:
        # Lire le texte du document
        #text = docx2txt.process(docx)
        #with open("so.txt", "w", encoding="utf-8") as fichier:
            #fichier.write(text)

        # Afficher toujours la barre de saisie
    st.markdown('<div class="input-space"></div>', unsafe_allow_html=True)
    selected_questions = st.sidebar.radio("****Choisir :****", questions)
        # Afficher toujours la barre de saisie
    query_input = st.text_input("", key="text_input_query", placeholder="Posez votre question ici...", help="Posez votre question ici...")
    st.markdown('<div class="input-space"></div>', unsafe_allow_html=True)

    if query_input and query_input not in st.session_state.previous_question:
        query = query_input
        st.session_state.previous_question.append(query_input)
    elif selected_questions:
        query = selected_questions
    else:
        query = ""

    if query :
        st.session_state.conversation_history.add_user_message(query) 
        if "Donnez-moi un résumé du rapport" in query:
            summary="""Le rapport de genre du Projet de Loi de Finances (PLF) 2025 pour le Maroc présente les avancées du pays en matière d’égalité de genre dans la gestion des finances publiques. À travers la Budgétisation Sensible au Genre (BSG), le Maroc renforce son engagement pour l'autonomisation des femmes et la réduction des inégalités, conformément aux orientations royales et aux objectifs du Nouveau Modèle de Développement. Le rapport détaille la mise en place de mécanismes de suivi budgétaire et d’indicateurs de performance, facilitant l'alignement des ressources avec les objectifs d’égalité. En collaboration avec des organismes comme l'ONU Femmes, le Maroc a adopté le cadre international PEFA Genre pour une plus grande transparence et efficacité dans les dépenses publiques dédiées à l’égalité, consolidant ainsi sa position parmi les pays engagés dans des pratiques budgétaires innovantes et inclusives."""
            st.session_state.conversation_history.add_ai_message(summary) 

        else:
            messages = [
                {
                    "role": "user",
                    "content": (
                        f"{query}. Répondre à la question d'apeés ce texte repondre justement à partir de texte ne donne pas des autre information voila le texte donnee des réponse significatif et bien formé essayer de ne pas dire que information nest pas mentionné dans le texte si tu ne trouve pas essayer de repondre dapres votre connaissance ms focaliser sur ce texte en premier: {text} "
                    )
                }
            ]

            # Appeler l'API OpenAI pour obtenir le résumé
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages
            )

            # Récupérer le contenu de la réponse

            summary = response['choices'][0]['message']['content']
           
                # Votre logique pour traiter les réponses
            #conversation_history.add_user_message(query)
            #conversation_history.add_ai_message(response)
            st.session_state.conversation_history.add_ai_message(summary)  # Ajouter à l'historique
            
            # Afficher la question et le résumé de l'assistant
            #conversation_history.add_user_message(query)
            #conversation_history.add_ai_message(summary)

            # Format et afficher les messages comme précédemment
                
            # Format et afficher les messages comme précédemment
        formatted_messages = []
        previous_role = None 
        if st.session_state.conversation_history.messages: # Variable pour stocker le rôle du message précédent
                for msg in conversation_history.messages:
                    role = "user" if msg.type == "human" else "assistant"
                    avatar = "🧑" if role == "user" else "🤖"
                    css_class = "user-message" if role == "user" else "assistant-message"

                    if role == "user" and previous_role == "assistant":
                        message_div = f'<div class="{css_class}" style="margin-top: 25px;">{msg.content}</div>'
                    else:
                        message_div = f'<div class="{css_class}">{msg.content}</div>'

                    avatar_div = f'<div class="avatar">{avatar}</div>'
                
                    if role == "user":
                        formatted_message = f'<div class="message-container user"><div class="message-avatar">{avatar_div}</div><div class="message-content">{message_div}</div></div>'
                    else:
                        formatted_message = f'<div class="message-container assistant"><div class="message-content">{message_div}</div><div class="message-avatar">{avatar_div}</div></div>'
                
                    formatted_messages.append(formatted_message)
                    previous_role = role  # Mettre à jour le rôle du message précédent

                messages_html = "\n".join(formatted_messages)
                st.markdown(messages_html, unsafe_allow_html=True)
if __name__ == '__main__':
    main()
