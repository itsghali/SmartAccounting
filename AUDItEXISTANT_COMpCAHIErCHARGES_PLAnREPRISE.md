Tu es un architecte logiciel senior, product manager ERP, tech lead full-stack et expert en comptabilité marocaine, paie marocaine, fiscalité marocaine, FastAPI, React/Next.js, PostgreSQL, moteurs de règles métier et SaaS B2B.

Je vais te redonner :
- les fichiers markdown que tu as déjà générés pour ce projet,
- le cahier des charges,
- les modules Atlas,
- et les captures d’écran de l’état actuel de la plateforme.

Ta mission n’est PAS de repartir de zéro.
Ta mission est de **reprendre l’existant**, de l’**auditer**, de le **comparer au besoin réel**, puis de me proposer et implémenter la **suite correcte du build** pour aller vers un **SaaS ERP marocain complet, fonctionnel et cohérent**.

==================================================
1. CONTEXTE GLOBAL DU PROJET
==================================================

Le projet s’appelle :

EASYACCOUNTING
ERP SaaS marocain unifié inspiré d’AtlasCompta, AtlasPaie et AtlasCom

Le produit cible doit être un **ERP SaaS marocain complet**, moderne, cloud, multi-tenant, multi-sociétés, multi-dossiers, destiné à :
- cabinets comptables,
- fiduciaires,
- PME marocaines,
- groupes multi-entités.

Le produit doit couvrir :
- comptabilité,
- TVA,
- fiscalité,
- immobilisations,
- analytique,
- budgets,
- reporting,
- paie marocaine,
- déclarations sociales,
- gestion commerciale,
- facturation,
- stock,
- documents,
- imports/exports,
- audit log,
- notifications,
- moteur de règles,
- et une couche IA transverse d’assistance.

Le produit ne doit pas être un simple outil OCR.
Le produit ne doit pas être un simple mini-dashboard comptable.
Le produit doit devenir un **ERP transactionnel complet**.

==================================================
2. EXIGENCE ABSOLUE
==================================================

Tu dois respecter sans exception les documents que je t’ai donnés :
- le cahier des charges,
- les modules Atlas,
- les documents PRD / architecture / backlog / starter que tu as déjà produits,
- les visuels actuels de la plateforme.

Tu dois considérer que :
- le cahier des charges est la référence fonctionnelle,
- les modules Atlas sont la référence de couverture métier,
- les screenshots représentent l’état réel actuel du produit,
- les fichiers markdown existants représentent la conception déjà produite,
- ton travail maintenant consiste à faire la jonction entre la vision cible et l’état réel actuel du build.

==================================================
3. CE QUE TU DOIS FAIRE EN PREMIER
==================================================

Avant de proposer du code, je veux que tu fasses une **analyse structurée de l’existant**.

Je veux que tu commences par :

### A. Analyse de l’état actuel du produit
En te basant sur les captures d’écran et les fichiers existants, dis clairement :
- ce qui est déjà présent dans la plateforme,
- ce qui est seulement maquetté en UI,
- ce qui semble réellement branché au backend,
- ce qui est encore absent,
- ce qui est placeholder,
- ce qui est incohérent avec le cahier des charges,
- ce qui est trop minimal pour un vrai MVP ERP.

Je veux aussi que tu identifies explicitement les problèmes visibles dans le dashboard actuel, notamment :
- aucun nombre ne s’affiche dans les cartes de synthèse,
- les cartes **Plan de comptes**, **Journaux**, **Écritures** et **Exercices** affichent un tiret au lieu de vraies métriques,
- le dashboard est donc visuellement propre mais fonctionnellement trop pauvre,
- il ne donne pas une vraie vue de pilotage utilisateur.

Tu dois analyser pourquoi ces chiffres ne remontent pas :
- endpoint manquant,
- agrégation backend absente,
- requête frontend non branchée,
- problème de state management,
- problème de mapping des données,
- ou placeholder laissé en place.

### B. Analyse de conformité avec le cahier des charges
Compare l’état actuel du produit avec le besoin attendu :
- socle plateforme,
- comptabilité,
- TVA,
- clôture / réouverture / à-nouveaux,
- immobilisations,
- analytique,
- budgets,
- reporting,
- paie,
- déclarations sociales,
- commercial,
- stock,
- documents,
- audit,
- notifications,
- moteur de règles,
- IA transverse.

Pour chaque bloc, je veux :
- conforme,
- partiellement conforme,
- absent,
- ou insuffisant.

### C. Analyse de conformité avec AtlasCompta / AtlasPaie / AtlasCom
Je veux que tu vérifies si les modules réellement présents ou commencés couvrent :
- AtlasCompta,
- AtlasPaie,
- AtlasCom.

Tu dois lister :
- les modules déjà amorcés,
- les modules manquants,
- les modules critiques non commencés,
- les sous-modules oubliés.

### D. Analyse de conformité au contexte marocain
Je veux que tu vérifies si l’existant prend réellement en compte :
- PCM / CGNC,
- exercices,
- périodes,
- journaux,
- à-nouveaux,
- clôture,
- réouverture,
- TVA,
- comptes de personnel,
- organismes sociaux,
- immobilisations,
- amortissements,
- analytique,
- reporting marocain,
- paie marocaine,
- déclarations sociales et fiscales.

==================================================
4. CE QUE TU DOIS PRODUIRE APRES L’ANALYSE
==================================================

Après l’audit de l’existant, je veux que tu produises un **plan de continuation du projet** extrêmement clair.

Je veux les sections suivantes :

### 1. Diagnostic global
- niveau de maturité actuel du produit,
- ce qui est bon,
- ce qui est trompeur visuellement,
- ce qui manque vraiment,
- plus gros écarts avec la cible ERP.

### 2. Ce qu’il faut corriger dans l’existant
Je veux la liste détaillée de :
- problèmes d’architecture,
- problèmes de modélisation,
- problèmes de périmètre,
- problèmes UX/UI,
- problèmes de cohérence métier,
- problèmes de priorisation.

Dans cette section, tu dois inclure explicitement :
- l’absence de vraies métriques dans le dashboard,
- l’absence d’affichage des nombres pour plan comptable, journaux, exercices et écritures,
- le fait que le dashboard actuel n’exploite pas encore correctement les données existantes,
- le besoin de transformer ce dashboard en véritable écran de pilotage.

### 3. Ce qu’il faut garder
Je veux identifier :
- les éléments UI réussis,
- les composants réutilisables,
- les patterns de navigation à garder,
- les modules déjà assez propres pour servir de base.

### 4. Ce qu’il faut refondre
Je veux identifier clairement :
- ce qu’il faut corriger légèrement,
- ce qu’il faut restructurer,
- ce qu’il faut refaire proprement.

### 5. Nouveau plan de build réaliste
Je veux une roadmap d’exécution adaptée à l’état réel du projet, et pas seulement à la vision théorique.

==================================================
5. PRIORISATION OBLIGATOIRE
==================================================

Tu dois me proposer un ordre de build réaliste à partir de l’état actuel.

Je veux que tu classes les prochaines étapes en :

### Bloc 1 — Fondations critiques à terminer
Par exemple :
- seed CGNC / PCM complet,
- seed journaux par défaut,
- exercices / périodes / statut ouverture / fermeture,
- moteur de règles minimal,
- audit log,
- notifications propres,
- socle paramètres,
- dashboard branché sur de vraies métriques backend.

### Bloc 2 — Comptabilité cœur exploitable
Par exemple :
- plan comptable complet,
- journaux,
- saisie d’écriture,
- modèles d’écriture,
- import d’écritures,
- validation,
- contrepassation,
- liste d’écritures,
- équilibre débit/crédit.

### Bloc 3 — Comptabilité réglementaire
Par exemple :
- balance générale,
- grand livre,
- bilan,
- CPC,
- reporting CGNC,
- déclaration TVA,
- liasse fiscale,
- clôture,
- à-nouveaux,
- réouverture.

### Bloc 4 — Modules métier majeurs
Par exemple :
- immobilisations,
- lettrage,
- rapprochement bancaire,
- analytique,
- budgets.

### Bloc 5 — Paie marocaine
- salariés,
- rubriques,
- calcul brut/net,
- cotisations,
- IR,
- congés,
- prêts,
- bulletins,
- DAMANCOM,
- état 9421,
- BDS,
- écritures de paie.

### Bloc 6 — Gestion commerciale
- clients,
- produits,
- devis,
- commandes,
- livraisons,
- factures,
- paiements,
- stock,
- valorisation,
- intégration comptable.

### Bloc 7 — IA et automatisations avancées
- OCR,
- extraction,
- classification,
- suggestions,
- détection d’anomalies,
- assistance clôture,
- assistance documentaire.

==================================================
6. TU DOIS EGALEMENT TENIR COMPTE DU VISUEL ACTUEL
==================================================

À partir des captures d’écran, je veux que tu analyses aussi la partie design et UX actuelle.

Je veux que tu me dises :
- ce qui est bien dans le shell actuel,
- ce qui fait trop “starter admin template”,
- ce qui manque pour une vraie UX ERP,
- ce qu’il faut améliorer dans :
  - dashboard,
  - navigation latérale,
  - densité d’information,
  - gestion des tableaux,
  - affichage des KPI,
  - feedback utilisateur,
  - hiérarchie visuelle,
  - gestion des états vides,
  - workflow comptable.

Je veux aussi que tu prennes en compte explicitement que :
- le dashboard actuel affiche des cartes de synthèse mais sans métriques réelles,
- cela donne une impression de produit inachevé,
- ces cartes doivent afficher de vraies données :
  - nombre de comptes du plan comptable,
  - nombre de journaux,
  - nombre d’écritures,
  - nombre d’exercices,
- idéalement avec une meilleure présentation visuelle et un vrai rôle de pilotage.

Je veux que tu proposes une amélioration UX/UI sans casser la logique métier.

==================================================
7. ATTENTES SUR LE CODE
==================================================

Après ton audit et ton plan d’exécution, je veux que tu commences à coder la suite.

Mais attention :
- tu ne dois pas tout coder d’un coup,
- tu dois partir de l’existant,
- tu dois respecter les fichiers et la structure déjà produits,
- tu dois proposer des modifications incrémentales propres.

Pour chaque prochaine étape, je veux :
- les fichiers à créer ou modifier,
- les changements backend,
- les changements frontend,
- les migrations DB,
- les validations métier,
- les tests à ajouter.

==================================================
8. PREMIERE LIVRAISON QUE JE VEUX MAINTENANT
==================================================

Dans cette réponse, je veux que tu me livres exactement dans cet ordre :

1. Analyse détaillée de l’état actuel du projet à partir des fichiers et screenshots
2. Comparaison avec le cahier des charges
3. Comparaison avec AtlasCompta / AtlasPaie / AtlasCom
4. Comparaison avec les exigences marocaines PCM / paie / TVA / fiscalité
5. Liste des écarts et problèmes critiques
6. Ce qu’il faut garder
7. Ce qu’il faut refondre
8. Roadmap réaliste mise à jour
9. Priorisation détaillée des prochains sprints
10. Première étape de build à implémenter maintenant
11. Code réel pour cette première étape
12. Étapes suivantes après cette première implémentation

Dans la première étape de build, tu dois privilégier un correctif utile et visible, par exemple :
- brancher le dashboard sur de vraies métriques,
- corriger l’affichage des nombres,
- améliorer la valeur du dashboard,
- tout en gardant la cohérence avec la structure existante.

==================================================
9. REGLES IMPORTANTES
==================================================

- Ne repars pas de zéro sans justification.
- Ne me redonne pas juste une roadmap vague.
- Ne te contente pas de répéter le cahier des charges.
- Appuie-toi sur l’existant réel.
- Distingue toujours :
  - ce qui existe déjà,
  - ce qui est maquetté,
  - ce qui est partiellement implémenté,
  - ce qui manque complètement.
- Ne réduis pas le produit à la comptabilité.
- N’oublie pas la paie, le commercial, l’analytique, les budgets, la fiscalité et les documents.
- Ne traite pas l’IA comme priorité absolue avant le cœur ERP.
- Fais passer la solidité métier avant les gadgets.
- N’oublie pas que le dashboard actuel a un défaut fonctionnel visible : absence de chiffres réels sur les cartes principales.

==================================================
10. STYLE DE REPONSE ATTENDU
==================================================

Je veux une réponse :
- en français,
- très structurée,
- professionnelle,
- critique,
- détaillée,
- exploitable par un développeur et un architecte,
- avec du vrai code quand tu arrives à la partie implémentation.

Commence directement par l’analyse détaillée de l’état actuel du projet.