# EASYACCOUNTING — Product Requirements Document (PRD)

## ERP SaaS marocain unifié — Comptabilité · Paie · Gestion Commerciale · Fiscalité · IA

**Version** : 1.0
**Date** : 18 mars 2026
**Statut** : Draft initial
**Auteur** : Direction Produit EasyAccounting
**Classification** : Confidentiel — Usage interne et investisseurs

---

## Table des matières

1. [Executive Summary](#1-executive-summary)
2. [Vision Produit](#2-vision-produit)
3. [Problème adressé](#3-problème-adressé)
4. [Proposition de valeur](#4-proposition-de-valeur)
5. [Cibles utilisateurs](#5-cibles-utilisateurs)
6. [Personas détaillés](#6-personas-détaillés)
7. [Cas d'usage principaux](#7-cas-dusage-principaux)
8. [Objectifs produit](#8-objectifs-produit)
9. [Non-objectifs](#9-non-objectifs)
10. [Positionnement marché](#10-positionnement-marché)
11. [Périmètre fonctionnel complet](#11-périmètre-fonctionnel-complet)
12. [Contraintes métier marocaines](#12-contraintes-métier-marocaines)
13. [Contraintes réglementaires](#13-contraintes-réglementaires)
14. [Rôle de l'IA](#14-rôle-de-lia)
15. [Rôle du moteur de règles](#15-rôle-du-moteur-de-règles)
16. [Principes d'architecture produit](#16-principes-darchitecture-produit)
17. [Workflows métier principaux](#17-workflows-métier-principaux)
18. [Flux inter-modules](#18-flux-inter-modules)
19. [Critères de succès](#19-critères-de-succès)
20. [Hypothèses](#20-hypothèses)
21. [Risques métier et produit](#21-risques-métier-et-produit)
22. [Conclusion stratégique](#22-conclusion-stratégique)

---

## 1. Executive Summary

**EasyAccounting** est un ERP SaaS cloud-native, conçu et localisé pour le marché marocain, qui unifie dans une seule plateforme la comptabilité générale et analytique, la paie, la gestion commerciale, la fiscalité, la TVA, les immobilisations, les budgets, le reporting financier et la gestion documentaire.

Le produit s'adresse en priorité aux **cabinets comptables**, **fiduciaires**, **PME marocaines** et **groupes multi-entités**. Il est architecturé en mode **multi-tenant**, **multi-sociétés** et **multi-dossiers**, avec une couche IA transverse d'assistance qui accélère la saisie, détecte les anomalies et facilite la conformité réglementaire, tout en maintenant le contrôle humain sur toute validation officielle.

EasyAccounting capitalise sur les acquis fonctionnels des solutions AtlasCompta, AtlasPaie et AtlasCom, tout en les dépassant par :

- une architecture cloud moderne (SaaS, API-first, microservices),
- une expérience utilisateur unifiée et responsive,
- une intégration native inter-modules (compta ↔ paie ↔ commercial ↔ fiscal),
- un moteur de règles métier configurable sans code,
- une couche d'intelligence artificielle transverse,
- une conformité native et maintenue aux normes marocaines (CGNC, IR, CNSS, AMO, CIMR, EDI XML, DAMANCOM, liasse fiscale).

Le produit vise à devenir **la référence SaaS de gestion intégrée au Maroc** en remplaçant l'empilement de logiciels hétérogènes par une plateforme unique, cohérente et évolutive.

---

## 2. Vision Produit

> **"Offrir aux professionnels du chiffre et aux entreprises marocaines une plateforme unique, intelligente et conforme, qui simplifie radicalement la gestion comptable, sociale et commerciale."**

### Axes stratégiques de la vision

| Axe | Ambition |
|-----|----------|
| **Unification** | Un seul produit remplace AtlasCompta + AtlasPaie + AtlasCom + outils tiers (Excel, Word, envois manuels). |
| **Cloud natif** | Zéro installation, mises à jour automatiques, accès partout, collaboration temps réel. |
| **Conformité marocaine de naissance** | Le CGNC, l'IR, la CNSS, la TVA, la liasse fiscale et l'EDI XML ne sont pas des adaptations : ils sont le socle. |
| **IA responsable** | L'IA assiste, suggère, détecte. L'humain valide, clôture, dépose. |
| **Multi-dossiers / Multi-sociétés** | Un cabinet gère 200 dossiers. Un groupe consolide 15 filiales. L'architecture supporte les deux. |
| **Ouverture** | API REST publique, webhooks, intégrations bancaires, import/export dans tous les formats attendus. |

### Horizon produit

- **V1 (MVP)** : Comptabilité + TVA + Immobilisations + Reporting de base + Multi-dossiers — cible cabinets comptables.
- **V2** : Paie marocaine complète + Intégration compta-paie — cible fiduciaires et PME.
- **V3** : Gestion commerciale + Stock + Facturation + Intégration compta-commercial — cible PME et groupes.
- **V4** : IA avancée + Analytique + Budgets + Consolidation + Portail collaboratif.

---

## 3. Problème adressé

### 3.1 Constats terrain

Le paysage logiciel de gestion au Maroc souffre de **fragmentation structurelle** :

1. **Empilement d'outils déconnectés** : Un cabinet typique utilise un logiciel comptable (souvent desktop), un outil de paie séparé, Excel pour la gestion commerciale, Word pour les bulletins, et des envois manuels pour l'EDI.

2. **Logiciels vieillissants** : Les solutions historiques (y compris les gammes Atlas) sont majoritairement des applications desktop Windows, mono-poste ou client-serveur, avec des interfaces datées et une absence de collaboration temps réel.

3. **Risque de non-conformité** : Les mises à jour réglementaires (barème IR, taux CNSS, seuils TVA, format liasse fiscale) arrivent en retard ou nécessitent des mises à jour manuelles coûteuses.

4. **Ressaisie et erreurs** : L'absence d'intégration entre les modules oblige à ressaisir les écritures de paie en comptabilité, à recalculer manuellement la TVA, à recopier les factures commerciales dans le journal.

5. **Gestion multi-dossiers pénible** : Les cabinets gèrent des dizaines voire des centaines de dossiers clients. Les outils actuels ne permettent pas une vision transversale, un suivi d'avancement par dossier, ni une industrialisation des travaux récurrents.

6. **Absence de mobilité** : Les professionnels ne peuvent pas travailler à distance, en clientèle ou en déplacement.

7. **Pas d'intelligence** : Aucun outil n'offre de détection d'anomalies, de suggestions d'imputation, d'OCR sur factures ou de pré-remplissage intelligent.

### 3.2 Conséquences

| Problème | Impact |
|----------|--------|
| Ressaisie manuelle | Perte de temps (estimée à 30-40% du temps productif d'un collaborateur comptable) |
| Erreurs de saisie | Risques fiscaux, pénalités, contentieux |
| Retard réglementaire | Non-conformité, amendes |
| Outils fragmentés | Coût total de possession élevé (licences multiples, maintenance, formation) |
| Pas de collaboration | Goulots d'étranglement pendant les périodes fiscales |
| Pas de visibilité | Le dirigeant de cabinet ou de PME n'a pas de tableau de bord consolidé |

### 3.3 Opportunité

Le Maroc compte environ **12 000 cabinets comptables et fiduciaires** et plus de **300 000 PME formelles**. La transformation numérique est encouragée par l'État (Maroc Digital, dématérialisation fiscale, e-facture en préparation). Le marché est prêt pour une solution SaaS intégrée, à condition qu'elle respecte parfaitement le contexte réglementaire local.

---

## 4. Proposition de valeur

### Pour les cabinets comptables et fiduciaires

> **"Gérez tous vos dossiers clients — comptabilité, paie, fiscal — dans une seule plateforme cloud, avec une IA qui vous fait gagner des heures chaque semaine."**

- Un seul outil remplace 3 à 5 logiciels.
- Multi-dossiers natif : basculez d'un client à l'autre en un clic.
- Travaux récurrents industrialisés (clôtures mensuelles, déclarations TVA, bulletins de paie).
- Collaboration entre collaborateurs et avec les clients (portail).
- IA : OCR factures, suggestions d'imputation, détection d'anomalies, pré-remplissage déclarations.

### Pour les PME marocaines

> **"Votre comptabilité, votre paie et votre gestion commerciale dans un seul outil simple, conforme et accessible depuis n'importe où."**

- Pas besoin d'être expert-comptable : interfaces guidées, assistants, contrôles automatiques.
- Conformité garantie : TVA, IR, CNSS, liasse fiscale mis à jour automatiquement.
- Vision en temps réel : tableaux de bord financiers, suivi de trésorerie, marges.
- Facturation + stock + encaissements intégrés.

### Pour les groupes multi-entités

> **"Consolidez la gestion de toutes vos filiales dans une seule instance, avec des droits d'accès granulaires et un reporting consolidé."**

- Multi-sociétés natif avec plan de comptes groupe.
- Élimination des intercos manuelles.
- Reporting consolidé et analytique multi-axes.
- Audit trail complet.

---

## 5. Cibles utilisateurs

### 5.1 Segments prioritaires

| Segment | Taille estimée (Maroc) | Priorité | Version cible |
|---------|----------------------|----------|---------------|
| Cabinets comptables et fiduciaires | ~12 000 | P0 | V1 |
| PME (10-250 salariés) avec comptabilité internalisée | ~50 000 | P1 | V2 |
| TPE / Auto-entrepreneurs avec besoin de facturation + compta simplifiée | ~200 000 | P2 | V3 |
| Groupes multi-entités (5+ filiales) | ~2 000 | P1 | V2 |
| Experts-comptables indépendants | ~5 000 | P0 | V1 |

### 5.2 Utilisateurs finaux

| Rôle | Description | Module principal |
|------|-------------|-----------------|
| Expert-comptable / Gérant de cabinet | Supervision, validation, stratégie | Tous |
| Collaborateur comptable | Saisie, rapprochement, révision | Comptabilité, TVA, Immobilisations |
| Gestionnaire de paie | Calcul, édition bulletins, déclarations sociales | Paie |
| Responsable administratif et financier (RAF) | Reporting, budgets, trésorerie | Reporting, Budgets, Analytique |
| Commercial / Gestionnaire des ventes | Facturation, suivi commandes, encaissements | Gestion commerciale |
| Magasinier / Responsable stock | Entrées, sorties, inventaire | Stock |
| Dirigeant / CEO | Tableaux de bord, indicateurs clés | Dashboard |
| Client du cabinet (accès portail) | Dépôt de pièces, consultation | Portail client |
| Administrateur système | Configuration, droits, paramétrage | Administration |

---

## 6. Personas détaillés

### Persona 1 : Karim — Gérant de cabinet comptable à Casablanca

| Attribut | Détail |
|----------|--------|
| **Âge** | 48 ans |
| **Formation** | Expert-comptable DPLE |
| **Structure** | Cabinet de 12 collaborateurs, 180 dossiers clients |
| **Outils actuels** | AtlasCompta (desktop), AtlasPaie (desktop), Excel, Word, e-mail |
| **Frustrations** | Ressaisie entre compta et paie, pas de vue consolidée sur l'avancement des dossiers, collaborateurs bloqués en période fiscale car mono-poste, mises à jour réglementaires en retard |
| **Objectifs** | Industrialiser les travaux récurrents, réduire le temps de clôture de 50%, offrir un portail à ses clients, fidéliser ses collaborateurs avec des outils modernes |
| **Citation** | *"Je perds 2 jours par mois juste à consolider les états de mes 180 dossiers dans Excel."* |
| **Critère d'achat** | Conformité marocaine irréprochable, multi-dossiers performant, migration facile depuis Atlas |

### Persona 2 : Fatima — Gestionnaire de paie en fiduciaire

| Attribut | Détail |
|----------|--------|
| **Âge** | 34 ans |
| **Formation** | Licence en gestion, 8 ans d'expérience paie |
| **Structure** | Fiduciaire de 6 personnes, gère la paie de 45 entreprises clientes |
| **Outils actuels** | AtlasPaie, Excel pour les simulations, envoi DAMANCOM manuel |
| **Frustrations** | Calcul IR complexe et source d'erreurs, pas de lien automatique entre paie et comptabilité, DAMANCOM demande des manipulations manuelles, pas de simulation brut ↔ net rapide |
| **Objectifs** | Générer les bulletins en masse, automatiser les déclarations CNSS, avoir un lien direct paie → écritures comptables |
| **Citation** | *"Chaque mois je passe une demi-journée à ressaisir les écritures de paie en compta."* |
| **Critère d'achat** | Fiabilité du calcul de paie, conformité CNSS/IR/AMO, gain de temps |

### Persona 3 : Youssef — Dirigeant d'une PME industrielle à Tanger

| Attribut | Détail |
|----------|--------|
| **Âge** | 42 ans |
| **Formation** | Ingénieur, MBA |
| **Structure** | PME de 80 salariés, fabrication et distribution, 3 dépôts |
| **Outils actuels** | Sage Ligne 100 (comptabilité), Excel (stock, facturation), logiciel maison (commandes) |
| **Frustrations** | Pas de vision consolidée compta + commercial + stock, logiciels déconnectés, pas d'accès mobile, dépendance à un informaticien pour les états |
| **Objectifs** | Un seul outil pour tout, accessible depuis son téléphone, tableaux de bord en temps réel, réduction des coûts IT |
| **Citation** | *"Je veux voir mes marges, mon stock et ma tréso en temps réel, pas attendre la fin du mois."* |
| **Critère d'achat** | Intégration compta + commercial + stock, simplicité, mobilité |

### Persona 4 : Amina — Collaboratrice comptable junior

| Attribut | Détail |
|----------|--------|
| **Âge** | 26 ans |
| **Formation** | Master CCA, 2 ans d'expérience |
| **Structure** | Cabinet de Karim (Persona 1) |
| **Outils actuels** | AtlasCompta (desktop), navigue entre 15 dossiers par jour |
| **Frustrations** | Interface datée, pas d'aide à la saisie, erreurs fréquentes d'imputation, recherche laborieuse dans les journaux |
| **Objectifs** | Saisir plus vite, moins d'erreurs, apprendre les bonnes pratiques comptables |
| **Citation** | *"Si le logiciel pouvait me suggérer le compte en fonction du libellé, je gagnerais énormément de temps."* |
| **Critère d'achat** | UX moderne, aide intelligente, rapidité de saisie |

### Persona 5 : Hassan — Responsable administratif et financier d'un groupe

| Attribut | Détail |
|----------|--------|
| **Âge** | 52 ans |
| **Formation** | Expert-comptable, DAF depuis 15 ans |
| **Structure** | Holding de 8 filiales, secteurs immobilier et BTP |
| **Outils actuels** | JD Edwards (holding), Sage (certaines filiales), Excel (consolidation) |
| **Frustrations** | Consolidation manuelle mensuelle, pas d'analytique multi-axes, intercos sources d'erreurs |
| **Objectifs** | Consolider automatiquement les 8 filiales, analytique par projet/chantier/région, audit trail complet |
| **Citation** | *"La consolidation mensuelle me prend une semaine entière. C'est inacceptable."* |
| **Critère d'achat** | Multi-sociétés, consolidation, analytique avancée, performance |

---

## 7. Cas d'usage principaux

### CU-01 : Saisie comptable quotidienne avec assistance IA

**Acteur** : Collaborateur comptable
**Prérequis** : Dossier ouvert, exercice en cours, journal sélectionné
**Flux principal** :
1. L'utilisateur ouvre le module de saisie rapide.
2. Il scanne ou dépose une facture fournisseur (PDF/image).
3. L'IA OCRise le document, extrait : fournisseur, date, montant HT, TVA, montant TTC, numéro de facture.
4. L'IA suggère l'imputation comptable (compte de charge, compte fournisseur, compte de TVA) en se basant sur l'historique.
5. L'utilisateur valide ou ajuste les suggestions.
6. L'écriture est enregistrée dans le journal d'achat, en équilibre (débit = crédit).
7. La pièce justificative est attachée à l'écriture.
8. L'écriture apparaît dans le grand livre et la balance instantanément.

**Flux alternatif** :
- Si l'OCR échoue ou donne une confiance faible, l'utilisateur saisit manuellement.
- Si le fournisseur est inconnu, l'utilisateur peut le créer à la volée.
- L'utilisateur peut utiliser un modèle d'écriture récurrente pour accélérer la saisie.

---

### CU-02 : Déclaration TVA mensuelle

**Acteur** : Collaborateur comptable ou expert-comptable
**Prérequis** : Écritures du mois saisies et vérifiées
**Flux principal** :
1. L'utilisateur accède au module TVA et sélectionne la période.
2. Le système calcule automatiquement : TVA collectée, TVA déductible sur charges, TVA déductible sur immobilisations, crédit de TVA reporté.
3. L'utilisateur visualise le détail ligne par ligne avec les comptes et montants.
4. L'IA signale les anomalies (TVA sans contrepartie, montant suspect, prorata non appliqué).
5. L'utilisateur corrige si nécessaire.
6. L'utilisateur valide la déclaration.
7. Le système génère le formulaire TVA au format réglementaire.
8. Le système génère le fichier EDI XML si applicable.
9. L'écriture de liquidation TVA est générée automatiquement en comptabilité.

---

### CU-03 : Traitement de la paie mensuelle

**Acteur** : Gestionnaire de paie
**Prérequis** : Salariés paramétrés, rubriques configurées, absences/congés saisis
**Flux principal** :
1. Le gestionnaire ouvre le traitement de paie du mois.
2. Le système récupère automatiquement : les éléments fixes (salaire de base, primes fixes, cotisations), les éléments variables saisis (heures supplémentaires, primes exceptionnelles, absences).
3. Le système calcule pour chaque salarié : brut, cotisations salariales (CNSS, AMO, CIMR, mutuelle), IR après abattements et déductions, net à payer.
4. Le gestionnaire visualise le récapitulatif et peut simuler des modifications.
5. Le gestionnaire valide la paie.
6. Les bulletins de paie sont générés (PDF).
7. Les écritures comptables de paie sont générées automatiquement dans le journal de paie (OD paie).
8. Les fichiers DAMANCOM (déclaration CNSS) sont générés.
9. L'état 9421 (déclaration annuelle des salaires) est alimenté.

---

### CU-04 : Cycle commercial complet (devis → facture → encaissement → compta)

**Acteur** : Commercial, puis comptable
**Prérequis** : Client et produits paramétrés
**Flux principal** :
1. Le commercial crée un devis pour un client.
2. Le client accepte → le devis est converti en bon de commande.
3. La commande est livrée → un bon de livraison est généré, le stock est décrémenté.
4. La facture est émise automatiquement à partir du BL.
5. La facture est envoyée au client (PDF/e-mail).
6. Le client paie → l'encaissement est enregistré.
7. L'écriture comptable de vente est générée automatiquement (compte client, produit, TVA).
8. L'écriture d'encaissement est générée (banque, client).
9. Le lettrage client-facture-règlement est proposé par l'IA.

---

### CU-05 : Clôture annuelle d'un dossier comptable

**Acteur** : Expert-comptable
**Prérequis** : Toutes les écritures de l'exercice saisies et validées
**Flux principal** :
1. L'utilisateur lance l'assistant de clôture.
2. Le système exécute les contrôles de pré-clôture : équilibre de tous les journaux, rapprochement bancaire vérifié, TVA soldée, lettrage complet des tiers, immobilisations amorties, provisions constatées.
3. L'IA signale les anomalies détectées et propose des corrections.
4. L'utilisateur corrige les anomalies.
5. L'utilisateur génère les états financiers (bilan, CPC, ESG, tableau de financement).
6. L'utilisateur génère la liasse fiscale.
7. L'utilisateur valide la clôture (action irréversible, soumise à confirmation).
8. Le système génère les à-nouveaux pour l'exercice suivant.
9. L'exercice est verrouillé (aucune modification possible sauf réouverture exceptionnelle par un administrateur).

---

### CU-06 : Gestion des immobilisations et amortissements

**Acteur** : Collaborateur comptable
**Prérequis** : Immobilisation acquise et comptabilisée
**Flux principal** :
1. L'utilisateur enregistre une immobilisation (nature, date d'acquisition, valeur d'origine, durée de vie, méthode d'amortissement).
2. Le système calcule automatiquement le plan d'amortissement (linéaire, dégressif, selon les règles CGNC).
3. Chaque mois/trimestre/année, le système génère les dotations aux amortissements.
4. Les écritures d'amortissement sont générées dans le journal des OD.
5. En cas de cession, le système calcule la plus/moins-value et génère les écritures de sortie.
6. Le tableau des immobilisations est mis à jour en temps réel pour la liasse fiscale.

---

### CU-07 : Import massif d'écritures depuis Excel

**Acteur** : Collaborateur comptable
**Prérequis** : Fichier Excel au format attendu
**Flux principal** :
1. L'utilisateur télécharge le modèle Excel d'import.
2. Il remplit le fichier avec les écritures (date, journal, compte, libellé, débit, crédit, référence pièce).
3. Il uploade le fichier dans EasyAccounting.
4. Le système valide le fichier : format, comptes existants, équilibre par écriture, dates dans l'exercice.
5. Les erreurs sont listées avec le numéro de ligne et le motif.
6. L'utilisateur corrige et re-uploade, ou valide les écritures correctes.
7. Les écritures sont importées dans les journaux correspondants.

---

### CU-08 : Suivi analytique multi-axes

**Acteur** : RAF / Expert-comptable
**Prérequis** : Axes analytiques configurés, écritures imputées
**Flux principal** :
1. L'utilisateur configure les axes analytiques (exemples : centre de coût, projet, région, activité).
2. Lors de la saisie comptable, chaque écriture peut être ventilée sur un ou plusieurs axes.
3. L'utilisateur accède au reporting analytique.
4. Il peut croiser les axes (ex : charges par projet ET par centre de coût).
5. Les états analytiques sont exportables en PDF et Excel.
6. L'IA peut suggérer l'imputation analytique en se basant sur l'historique.

---

### CU-09 : Gestion des congés et absences des salariés

**Acteur** : Gestionnaire de paie / RH
**Prérequis** : Salariés paramétrés, droits à congés calculés
**Flux principal** :
1. Le salarié (ou le gestionnaire) saisit une demande de congé.
2. Le système vérifie le solde de congés disponible.
3. Le responsable valide ou refuse.
4. En cas de validation, le congé est enregistré et impacte automatiquement la paie du mois.
5. Les provisions pour congés payés sont mises à jour en comptabilité.

---

### CU-10 : Gestion des prêts salariés

**Acteur** : Gestionnaire de paie
**Prérequis** : Salarié actif
**Flux principal** :
1. Le gestionnaire enregistre un prêt (montant, taux éventuel, nombre de mensualités, date de début).
2. Le système génère l'échéancier de remboursement.
3. Chaque mois, la retenue est automatiquement appliquée sur le bulletin de paie.
4. L'écriture comptable (remboursement prêt) est générée dans le journal de paie.
5. Le solde restant dû est visible à tout moment.

---

## 8. Objectifs produit

### 8.1 Objectifs business

| ID | Objectif | Métrique | Cible à 18 mois |
|----|----------|----------|-----------------|
| OB-01 | Acquérir des cabinets comptables | Nombre de cabinets actifs | 200 cabinets |
| OB-02 | Acquérir des PME | Nombre de PME actives | 500 PME |
| OB-03 | ARR (Annual Recurring Revenue) | Revenu annuel récurrent | 5M MAD |
| OB-04 | Rétention | Taux de rétention nette | > 95% |
| OB-05 | NPS | Net Promoter Score | > 50 |
| OB-06 | Upsell inter-modules | % clients utilisant 2+ modules | > 40% |

### 8.2 Objectifs produit

| ID | Objectif | Métrique | Cible |
|----|----------|----------|-------|
| OP-01 | Réduction du temps de saisie | Temps moyen par écriture | -50% vs saisie manuelle |
| OP-02 | Réduction du temps de clôture mensuelle | Jours de clôture par dossier | -40% |
| OP-03 | Conformité réglementaire | Taux de déclarations TVA/IR/CNSS générées sans erreur | > 99% |
| OP-04 | Adoption IA | % écritures avec suggestion IA acceptée | > 60% à 6 mois |
| OP-05 | Satisfaction utilisateur | Score CSAT in-app | > 4.2/5 |
| OP-06 | Performance | Temps de chargement des pages | < 2s (P95) |
| OP-07 | Disponibilité | Uptime SLA | 99.9% |

### 8.3 Objectifs techniques

| ID | Objectif | Détail |
|----|----------|--------|
| OT-01 | Multi-tenant sécurisé | Isolation totale des données entre tenants |
| OT-02 | Scalabilité | Support de 1000+ tenants simultanés sans dégradation |
| OT-03 | Audit trail complet | Chaque action est tracée (qui, quoi, quand, avant, après) |
| OT-04 | API-first | 100% des fonctionnalités accessibles via API REST documentée |
| OT-05 | Sécurité | Conformité OWASP Top 10, chiffrement at-rest et in-transit |

---

## 9. Non-objectifs

Les éléments suivants sont explicitement **hors périmètre** pour les versions V1 à V3 :

| Non-objectif | Justification |
|-------------|---------------|
| **Comptabilité IFRS** | Le produit cible le CGNC marocain. L'IFRS pourra être ajouté ultérieurement. |
| **Paie multi-pays** | La paie est spécifique au droit social marocain. Pas de support Tunisie, Sénégal, France, etc. en V1-V3. |
| **E-commerce / Site web intégré** | EasyAccounting est un ERP back-office. L'intégration e-commerce se fera via API/connecteurs. |
| **CRM avancé** | Le module commercial gère la facturation et le stock, pas le pipeline commercial, le marketing automation ou le support client. |
| **Gestion de projet / Timesheet** | Hors périmètre. Des intégrations tierces pourront être envisagées. |
| **Gestion RH complète** | Le module paie gère les éléments nécessaires au calcul de la paie. La gestion des talents, la formation, l'évaluation sont hors périmètre. |
| **Application mobile native** | Le produit est responsive web. Une app native n'est pas prévue en V1-V3 (sauf impression Bluetooth/WiFi qui sera gérée via PWA). |
| **Hébergement on-premise** | Le produit est SaaS uniquement. Pas de version installable. |
| **Consolidation statutaire groupe** | La consolidation comptable au sens IFRS/groupe n'est pas en V1-V2. Un reporting consolidé multi-sociétés est prévu. |

---

## 10. Positionnement marché

### 10.1 Paysage concurrentiel au Maroc

| Concurrent | Type | Forces | Faiblesses |
|-----------|------|--------|------------|
| **AtlasCompta / AtlasPaie / AtlasCom** | Desktop, licences | Base installée significative, fonctionnellement riche pour le Maroc | Desktop, pas de cloud, modules séparés, UX datée, pas d'IA |
| **Sage Ligne 100 / Sage 50** | Desktop / Client-serveur | Marque connue, réseau revendeurs | Cher, pas cloud-native, localisation marocaine limitée, pas de paie marocaine intégrée |
| **JD Edwards / SAP** | ERP on-premise / cloud | Complet, groupes | Extrêmement cher, complexe, pas adapté aux PME/cabinets marocains |
| **Odoo** | Open-source / SaaS | Modulaire, communauté, prix agressif | Localisation marocaine incomplète (paie, TVA, liasse), communauté francophone limitée |
| **Logiciels locaux (Al Mohassibi, GESTIMUM, etc.)** | Desktop | Prix bas, localisation | Mono-fonctionnel, pas de SaaS, pas de maintenance long terme, UX obsolète |
| **Excel** | Tableur | Flexible, universel | Pas de contrôle, pas d'audit trail, pas de conformité, erreurs humaines |

### 10.2 Positionnement d'EasyAccounting

```
                    Intégration fonctionnelle
                           ▲
                           │
           SAP/JDE ●       │       ● EasyAccounting
                           │
                           │
    Sage ●                 │
                           │
         Odoo ●            │
                           │
    Atlas ●                │
                           │
    ───────────────────────┼────────────────────► Modernité / Cloud
                           │
    Logiciels locaux ●     │
                           │
    Excel ●                │
```

**Positionnement** : EasyAccounting se positionne comme la **seule solution SaaS marocaine nativement intégrée** (compta + paie + commercial + fiscal) avec une **localisation marocaine de naissance** et une **couche IA d'assistance**.

### 10.3 Avantages compétitifs durables

1. **Localisation marocaine native** : pas un "add-on" sur un produit international, mais un produit conçu pour le Maroc dès le jour 1.
2. **Intégration inter-modules** : un seul flux de données, pas de ressaisie.
3. **Cloud-natif multi-tenant** : déploiement instantané, mises à jour automatiques, collaboration.
4. **IA contextuelle** : entraînée sur des données comptables marocaines, comprend le CGNC.
5. **Prix SaaS accessible** : modèle d'abonnement adapté aux cabinets et PME marocaines.
6. **Migration facilitée** : outils d'import depuis Atlas, Sage, Excel.

---

## 11. Périmètre fonctionnel complet

### 11.1 Module Comptabilité (MOD-COMPTA)

#### 11.1.1 Paramétrage comptable

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Plan comptable marocain (CGNC)** | Plan comptable pré-chargé classes 1 à 9 (+ classe 0 hors bilan). Conforme au CGNC. Personnalisable par dossier. | P0 |
| **Modèle normal** | Plan comptable complet pour les entreprises dépassant les seuils (CA > 10M MAD ou bilan > 5M MAD). | P0 |
| **Modèle simplifié** | Plan comptable réduit pour les petites entreprises. | P0 |
| **Journaux comptables** | Création et paramétrage de journaux : achats, ventes, banque(s), caisse(s), OD, paie, à-nouveaux, etc. Numérotation automatique séquentielle sans rupture. | P0 |
| **Exercices comptables** | Création d'exercices (12 mois par défaut, extensible). Gestion des exercices ouverts, clôturés, en cours. | P0 |
| **Périodes comptables** | Découpage en mois, trimestres ou périodes personnalisées. Verrouillage par période. | P0 |
| **Multi-dossiers** | Un utilisateur peut accéder à N dossiers. Chaque dossier est une entité comptable indépendante avec son propre plan de comptes, ses journaux, ses exercices. | P0 |
| **Multi-sociétés** | Un tenant peut contenir plusieurs sociétés. Chaque société a ses propres paramètres (forme juridique, ICE, IF, RC, CNSS, adresse, etc.). | P0 |
| **Devises** | Gestion multi-devises avec taux de change configurable. Écarts de conversion automatiques. | P1 |

#### 11.1.2 Saisie comptable

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Saisie au journal** | Saisie classique dans un journal : date, numéro de pièce, compte, libellé, débit, crédit. | P0 |
| **Saisie rapide (guidée)** | Mode de saisie simplifié avec assistants : facture fournisseur, facture client, règlement, OD. | P0 |
| **Contrôle d'équilibre** | Impossible de valider une écriture déséquilibrée (total débit ≠ total crédit). | P0 |
| **Modèles d'écriture** | Création de modèles réutilisables (ex : loyer mensuel, abonnement télécom). Application en un clic avec possibilité d'ajuster les montants. | P0 |
| **Duplication d'écriture** | Copier une écriture existante pour créer une nouvelle écriture similaire. | P0 |
| **Écritures en brouillard** | Les écritures peuvent être en statut brouillard (modifiable) avant validation définitive. | P0 |
| **Validation d'écriture** | Action de validation qui rend l'écriture non modifiable (sauf extourne). | P0 |
| **Extourne** | Génération automatique de l'écriture inverse avec référence à l'écriture originale. | P0 |
| **Pièces jointes** | Attachement de fichiers (PDF, image, scan) à chaque écriture. Stockage cloud. | P0 |
| **Import Excel** | Import massif d'écritures depuis un fichier Excel selon un modèle prédéfini, avec validation, rapport d'erreurs, et import partiel possible. | P0 |
| **Saisie par lot** | Saisie de plusieurs écritures en un seul formulaire (batch). | P1 |
| **Écritures récurrentes** | Programmation d'écritures automatiques (ex : loyers mensuels) avec date de début, fin, et périodicité. | P1 |
| **Recherche avancée** | Recherche d'écritures par : date, compte, montant, libellé, journal, numéro de pièce, pièce jointe, statut. | P0 |

#### 11.1.3 Lettrage

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Lettrage manuel** | Sélection manuelle des écritures à lettrer sur un compte de tiers. | P0 |
| **Lettrage automatique** | Lettrage par correspondance : montant, référence pièce, libellé. | P0 |
| **Lettrage assisté par IA** | L'IA propose des rapprochements sur la base de patterns historiques. | P1 |
| **Délettrage** | Possibilité de défaire un lettrage. | P0 |
| **Lettrage partiel** | Gestion des règlements partiels (solde non lettré visible). | P0 |

#### 11.1.4 Rapprochement bancaire

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Import relevé bancaire** | Import de relevés au format CSV, OFX, MT940, CAMT.053. | P0 |
| **Rapprochement automatique** | Correspondance automatique entre écritures comptables et lignes de relevé (montant, date, libellé). | P0 |
| **Rapprochement manuel** | Interface de rapprochement drag-and-drop. | P0 |
| **Rapprochement assisté par IA** | L'IA apprend les patterns de rapprochement et suggère les correspondances. | P1 |
| **État de rapprochement** | Génération de l'état de rapprochement bancaire (solde comptable, opérations en suspens, solde banque). | P0 |

#### 11.1.5 À-nouveaux et clôture

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Génération des à-nouveaux** | Calcul automatique des à-nouveaux : soldes des comptes de bilan (classes 1-5), report du résultat, report des lettres non soldées sur les comptes de tiers. | P0 |
| **À-nouveaux provisoires** | Génération d'à-nouveaux provisoires en cours d'exercice (pour situations intermédiaires). | P1 |
| **Clôture d'exercice** | Processus guidé : pré-contrôles → corrections → génération états → validation → verrouillage → génération à-nouveaux N+1. | P0 |
| **Réouverture exceptionnelle** | Réouverture d'un exercice clôturé par un administrateur avec traçabilité complète. | P0 |
| **Clôture par période** | Verrouillage d'une période mensuelle/trimestrielle pour empêcher les modifications. | P0 |

#### 11.1.6 Éditions et reporting comptable

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Journal** | Édition du journal comptable avec filtres (période, journal, compte). | P0 |
| **Grand livre** | Édition du grand livre général et auxiliaire, avec soldes progressifs. | P0 |
| **Balance** | Balance générale et auxiliaire. Balance âgée (par ancienneté). | P0 |
| **Balance comparative** | Comparaison N / N-1 avec écarts en valeur et en pourcentage. | P0 |
| **Bilan** | Bilan comptable conforme au modèle normal ou simplifié du CGNC. | P0 |
| **Compte de Produits et Charges (CPC)** | CPC conforme au CGNC, modèle normal ou simplifié. | P0 |
| **État des Soldes de Gestion (ESG)** | Calcul des soldes intermédiaires de gestion : marge brute, valeur ajoutée, EBE, résultat courant, résultat net. | P0 |
| **Tableau de Financement** | Tableau de financement conforme au CGNC. | P1 |
| **Liasse fiscale** | Génération de la liasse fiscale complète (tableaux A à J + états annexes). | P0 |
| **EDI XML** | Génération du fichier XML pour dépôt électronique de la liasse fiscale auprès de la DGI. | P0 |
| **Export PDF / Excel** | Tous les états sont exportables en PDF et Excel. | P0 |
| **Personnalisation des états** | Possibilité de personnaliser les en-têtes, logos, filtres des états. | P1 |

---

### 11.2 Module TVA (MOD-TVA)

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Paramétrage TVA** | Configuration des taux de TVA marocains : 20%, 14%, 10%, 7%, 0% (exonéré). | P0 |
| **Régimes TVA** | Gestion des régimes : encaissement, débit, régime normal, régime forfaitaire. | P0 |
| **TVA collectée** | Calcul automatique de la TVA collectée à partir des écritures de vente. | P0 |
| **TVA déductible** | TVA déductible sur charges et sur immobilisations, avec règle du décalage d'un mois. | P0 |
| **Prorata de déduction** | Gestion du prorata de TVA pour les entreprises partiellement assujetties. | P1 |
| **Crédit de TVA** | Report automatique du crédit de TVA d'un mois sur l'autre. | P0 |
| **Déclaration mensuelle** | Génération de la déclaration de TVA mensuelle avec détail par taux. | P0 |
| **Déclaration trimestrielle** | Pour les entreprises au régime trimestriel. | P0 |
| **Écriture de liquidation** | Génération automatique de l'écriture de liquidation TVA en comptabilité. | P0 |
| **État TVA détaillé** | Détail de la TVA par compte, par taux, par fournisseur/client. | P0 |
| **Contrôle de cohérence** | Vérification automatique : chiffre d'affaires déclaré vs écritures, TVA comptabilisée vs déclarée. | P0 |
| **Historique des déclarations** | Archivage de toutes les déclarations TVA avec possibilité de réédition. | P0 |

---

### 11.3 Module Immobilisations (MOD-IMMO)

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Fiche immobilisation** | Création : nature, catégorie, date d'acquisition, date de mise en service, valeur d'origine, fournisseur, localisation, numéro d'inventaire. | P0 |
| **Catégories d'immobilisations** | Catégories prédéfinies selon le CGNC : terrains, constructions, matériel, mobilier, véhicules, etc. Durées d'amortissement standards. | P0 |
| **Amortissement linéaire** | Calcul prorata temporis. | P0 |
| **Amortissement dégressif** | Selon les coefficients fiscaux marocains. | P0 |
| **Amortissement exceptionnel** | Pour les immobilisations éligibles (ex : logiciels). | P1 |
| **Plan d'amortissement** | Tableau d'amortissement prévisionnel sur toute la durée de vie. | P0 |
| **Dotation automatique** | Génération des écritures de dotation aux amortissements en comptabilité. | P0 |
| **Cession d'immobilisation** | Calcul de la plus/moins-value de cession. Génération des écritures de sortie. | P0 |
| **Mise au rebut** | Sortie d'une immobilisation sans contrepartie financière. | P0 |
| **Réévaluation** | Réévaluation libre ou légale avec traitement comptable. | P2 |
| **Tableau des immobilisations** | État récapitulatif conforme à la liasse fiscale (valeurs brutes, amortissements, VNA). | P0 |
| **Import d'immobilisations** | Import massif depuis Excel pour migration. | P0 |

---

### 11.4 Module Analytique (MOD-ANA)

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Axes analytiques** | Création d'axes analytiques libres : centre de coût, projet, département, région, activité, etc. Jusqu'à 5 axes simultanés. | P1 |
| **Sections analytiques** | Chaque axe contient des sections (ex : axe "Département" → sections Marketing, Production, Admin). | P1 |
| **Ventilation analytique** | Ventilation des écritures comptables sur les sections analytiques. Ventilation en % ou en montant. | P1 |
| **Ventilation automatique** | Règles de ventilation automatique par compte (ex : compte 61 → 100% Marketing). | P1 |
| **Balance analytique** | Balance par axe, par section, par compte. | P1 |
| **Grand livre analytique** | Détail des mouvements analytiques. | P1 |
| **Reporting croisé** | Croisement de plusieurs axes (ex : charges par projet ET par département). | P2 |
| **Clés de répartition** | Répartition automatique des charges indirectes selon des clés configurables. | P2 |
| **Comparaison réel / budget** | Voir module Budgets. | P2 |

---

### 11.5 Module Budgets (MOD-BUDGET)

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Création de budgets** | Budgets par compte comptable, par section analytique, par période. | P2 |
| **Saisie budgétaire** | Saisie manuelle ou import Excel. Répartition linéaire ou saisonnière. | P2 |
| **Suivi budgétaire** | Comparaison réel vs budget avec écarts en valeur et en %. | P2 |
| **Alertes de dépassement** | Notification quand un poste budgétaire dépasse un seuil (ex : 80%, 100%). | P2 |
| **Révision budgétaire** | Possibilité de réviser un budget en cours d'exercice avec historique des versions. | P2 |
| **Reporting budgétaire** | États de suivi budgétaire exportables. | P2 |

---

### 11.6 Module Paie (MOD-PAIE)

#### 11.6.1 Gestion des salariés

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Fiche salarié** | Informations personnelles : nom, prénom, CIN, date de naissance, adresse, situation familiale, personnes à charge, coordonnées bancaires (RIB). | P0 |
| **Informations contractuelles** | Type de contrat (CDI, CDD, intérim, stage), date d'embauche, date de fin, période d'essai, poste, catégorie professionnelle, convention collective. | P0 |
| **Catégories professionnelles** | Cadre, employé, ouvrier, etc. Impact sur les cotisations et plafonds. | P0 |
| **Historique des salaires** | Traçabilité de toutes les modifications de salaire avec dates d'effet. | P0 |
| **Affiliation CNSS** | Numéro d'affiliation CNSS du salarié, numéro d'employeur CNSS de l'entreprise. | P0 |
| **Affiliation CIMR** | Numéro d'affiliation, taux salarial et patronal. | P0 |
| **Affiliation mutuelle** | Organisme, numéro d'adhérent, taux. | P1 |
| **Multi-établissements** | Un salarié peut être rattaché à un établissement spécifique. | P1 |
| **Import salariés** | Import massif depuis Excel/TXT. | P0 |

#### 11.6.2 Rubriques de paie

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Rubriques prédéfinies** | Rubriques standard marocaines : salaire de base, heures supplémentaires (25%, 50%, 100%), prime d'ancienneté, indemnités de transport, prime de panier, etc. | P0 |
| **Rubriques personnalisées** | Création de rubriques libres avec formule de calcul configurable. | P0 |
| **Primes** | Primes fixes (mensuelles) et primes variables (saisie au mois). | P0 |
| **Retenues** | Retenues fixes et variables : avances, prêts, absences, sanctions. | P0 |
| **Heures supplémentaires** | Calcul selon les taux légaux marocains : 25% (jour), 50% (nuit), 100% (repos/férié). | P0 |
| **Indemnités** | Indemnités de licenciement, de préavis, de congés non pris, calculées selon le Code du travail marocain. | P0 |
| **Avantages en nature** | Logement, voiture, etc. — valorisation et impact sur le brut imposable. | P1 |

#### 11.6.3 Calcul de la paie

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Calcul brut** | Salaire de base + primes + heures supplémentaires + indemnités + avantages en nature. | P0 |
| **Cotisations CNSS** | Calcul automatique : part salariale et part patronale. Respect des plafonds (plafond CNSS = 6 000 MAD). Taux applicables : allocations familiales, prestations sociales court terme, prestations long terme, AMO, taxe de formation professionnelle. | P0 |
| **Cotisations CIMR** | Calcul selon les taux choisis par l'entreprise (part salariale + part patronale). | P0 |
| **Cotisations mutuelle** | Calcul selon le contrat souscrit. | P1 |
| **IR (Impôt sur le Revenu)** | Calcul selon le barème progressif en vigueur. Déductions : frais professionnels (20% plafonné), cotisations CNSS, CIMR, mutuelle, personnes à charge (30 MAD/personne/mois, max 6). Application du barème par tranches. | P0 |
| **Net à payer** | Brut - cotisations salariales - IR - retenues + indemnités non imposables. | P0 |
| **Simulation brut → net** | Calculer le net à partir d'un brut donné. | P0 |
| **Simulation net → brut** | Calcul inverse : trouver le brut correspondant à un net cible. | P0 |
| **Régularisation annuelle IR** | Calcul de la régularisation annuelle de l'IR en décembre (comparaison cumul mensuel vs calcul annuel). | P0 |
| **Périodicité de paie** | Support des paies mensuelles, bimensuelles (quinzaine) et hebdomadaires. | P0 |
| **Calcul de masse** | Traitement de la paie pour l'ensemble des salariés en un clic. | P0 |

#### 11.6.4 Congés et absences

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Droits à congés** | Calcul automatique : 1,5 jour ouvrable par mois de travail effectif (18 jours/an). Majoration pour ancienneté. | P0 |
| **Types de congés** | Congé annuel, congé maladie, congé maternité (14 semaines), congé sans solde, congé spécial (mariage, naissance, décès). | P0 |
| **Saisie des absences** | Enregistrement des absences avec impact automatique sur la paie (retenue proportionnelle). | P0 |
| **Solde de congés** | Calcul en temps réel du solde de congés restant. | P0 |
| **Provision pour congés payés** | Calcul et comptabilisation automatique de la provision pour congés payés. | P1 |

#### 11.6.5 Prêts salariés

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Enregistrement de prêt** | Montant, date d'octroi, nombre de mensualités, taux (0% par défaut). | P0 |
| **Échéancier** | Génération automatique de l'échéancier. | P0 |
| **Retenue automatique** | Déduction automatique sur le bulletin de chaque mois. | P0 |
| **Suivi du solde** | Solde restant dû visible à tout moment. | P0 |

#### 11.6.6 Bulletins de paie

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Bulletin individuel** | Génération du bulletin de paie conforme : identité employeur/salarié, période, détail des rubriques (gains, retenues), cotisations, IR, net à payer. | P0 |
| **Bulletin de masse** | Génération de tous les bulletins d'une période en un clic. | P0 |
| **Export PDF** | Export individuel ou en masse. | P0 |
| **Personnalisation du bulletin** | Logo entreprise, mentions légales, mise en page configurable. | P1 |
| **Envoi par e-mail** | Envoi automatique du bulletin à chaque salarié par e-mail. | P1 |
| **Historique des bulletins** | Consultation de tous les bulletins passés par salarié. | P0 |

#### 11.6.7 Déclarations sociales et fiscales

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **DAMANCOM** | Génération du fichier de déclaration CNSS au format DAMANCOM (fichier TXT/XML). Déclaration des salaires, des jours travaillés, des congés. | P0 |
| **État 9421** | Génération de l'état annuel des traitements et salaires (état 9421) pour déclaration à la DGI. | P0 |
| **Attestation de salaire** | Génération d'attestations de salaire pour les salariés. | P0 |
| **Atlas BDS (Bordereau de Déclaration de Salaire)** | Génération du bordereau récapitulatif de la CNSS. | P0 |
| **Conversion XML** | Export des déclarations au format XML pour envoi électronique. | P0 |
| **Import Excel/TXT** | Import de données de paie depuis Excel ou fichier TXT pour migration ou intégration avec des systèmes tiers. | P0 |

#### 11.6.8 Intégration paie → comptabilité

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Génération des écritures de paie** | Création automatique des écritures comptables de paie dans le journal d'OD paie : charges de personnel (classe 6), cotisations patronales, dettes sociales (classe 4), net à payer (classe 4). | P0 |
| **Paramétrage des comptes** | Correspondance configurable entre rubriques de paie et comptes comptables. | P0 |
| **Écritures détaillées ou centralisées** | Choix entre une écriture par salarié ou une écriture centralisée par rubrique. | P1 |

---

### 11.7 Module Gestion Commerciale (MOD-COM)

#### 11.7.1 Référentiels

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Clients** | Fiche client : raison sociale, ICE, IF, RC, adresse, contacts, conditions de paiement, plafond de crédit. | P0 |
| **Fournisseurs** | Fiche fournisseur : mêmes informations + conditions d'achat. | P0 |
| **Produits** | Fiche produit : référence, désignation, famille, sous-famille, unité, prix d'achat, prix de vente HT, taux de TVA. | P0 |
| **Familles de produits** | Classification hiérarchique des produits. | P0 |
| **Codes-barres** | Attribution d'un ou plusieurs codes-barres par produit (EAN-13, EAN-8, Code 128, QR Code). | P0 |
| **Scan code-barres** | Saisie par scan (caméra ou douchette) pour recherche produit et ajout en document. | P1 |
| **Tarifs / Grilles de prix** | Tarifs par client, par quantité, par période. | P1 |
| **Recherche avancée** | Recherche clients et produits par nom, code, code-barres, famille, etc. | P0 |

#### 11.7.2 Cycle de vente

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Devis** | Création de devis avec lignes produits, remises, TVA. Conversion en commande/facture. | P0 |
| **Bon de commande client** | Enregistrement des commandes confirmées. Suivi d'état (en attente, en préparation, livrée, annulée). | P0 |
| **Bon de livraison** | Génération à partir de la commande. Impact sur le stock (sortie). | P0 |
| **Facture de vente** | Génération à partir du BL ou directement. Numérotation séquentielle conforme. TVA détaillée. | P0 |
| **Avoir** | Facture d'avoir avec référence à la facture d'origine. Impact stock (retour). | P0 |
| **Suivi des commandes** | Tableau de bord des commandes : en cours, livrées, facturées, en retard. | P0 |
| **Export PDF** | Tous les documents (devis, BC, BL, facture, avoir) exportables en PDF. | P0 |
| **Impression** | Impression directe, impression Bluetooth, impression WiFi. | P1 |
| **Envoi par e-mail** | Envoi direct des documents au client par e-mail. | P1 |

#### 11.7.3 Cycle d'achat

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Bon de commande fournisseur** | Création et suivi des commandes fournisseurs. | P1 |
| **Bon de réception** | Enregistrement des réceptions. Impact stock (entrée). | P1 |
| **Facture d'achat** | Saisie ou import des factures fournisseurs. | P0 |

#### 11.7.4 Règlements et encaissements

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Modes de règlement** | Espèces, chèque, virement, effet, carte bancaire, mobile money. | P0 |
| **Encaissement client** | Enregistrement des règlements clients. Affectation aux factures (lettrage commercial). | P0 |
| **Paiement fournisseur** | Enregistrement des règlements fournisseurs. | P0 |
| **Échéancier** | Gestion des échéances client et fournisseur. Alertes de retard. | P0 |
| **Relance client** | Génération de lettres/e-mails de relance par ancienneté. | P1 |
| **Intégration comptable** | Génération automatique des écritures comptables de vente, d'achat et de règlement. | P0 |

#### 11.7.5 Gestion du stock

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Multi-dépôts** | Gestion de plusieurs dépôts/magasins. | P1 |
| **Entrées de stock** | Entrées par réception, production, régularisation. | P0 |
| **Sorties de stock** | Sorties par livraison, consommation, régularisation. | P0 |
| **Transfert inter-dépôts** | Mouvement de stock entre dépôts. | P1 |
| **Inventaire physique** | Saisie d'inventaire, calcul des écarts, génération des écritures de régularisation. | P0 |
| **Valorisation du stock** | Méthodes : CMUP (Coût Moyen Unitaire Pondéré), FIFO. | P0 |
| **Seuils d'alerte** | Alerte quand le stock d'un produit passe sous un seuil minimum. | P1 |
| **État du stock** | Consultation du stock en temps réel par produit, par dépôt. | P0 |

---

### 11.8 Module Reporting et Tableaux de Bord (MOD-REPORT)

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Dashboard dirigeant** | Tableau de bord synthétique : CA, résultat, trésorerie, créances, dettes, indicateurs clés. | P0 |
| **Dashboard cabinet** | Vue multi-dossiers : avancement des clôtures, dossiers en retard, échéances fiscales, productivité par collaborateur. | P0 |
| **Ratios financiers** | Calcul automatique : rentabilité, liquidité, solvabilité, rotation des stocks, BFR, FRNG. | P1 |
| **Reporting personnalisé** | Constructeur de rapports avec filtres, regroupements, formules. | P2 |
| **Comparaison N / N-1** | Sur tous les états financiers. | P0 |
| **Export PDF / Excel** | Tous les rapports exportables. | P0 |
| **Planification de rapports** | Génération et envoi automatique de rapports à date fixe. | P2 |

---

### 11.9 Module Gestion Documentaire (MOD-GED)

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Stockage cloud** | Stockage des pièces justificatives, contrats, documents légaux. | P0 |
| **Classement automatique** | Classification par dossier, type de document, date, module. | P1 |
| **OCR** | Extraction automatique de texte depuis les scans et photos. | P1 |
| **Recherche plein texte** | Recherche dans le contenu des documents. | P1 |
| **Versioning** | Historique des versions d'un document. | P2 |
| **Portail client** | Espace de dépôt de documents par les clients du cabinet. | P2 |
| **Lien avec écritures** | Association document ↔ écriture comptable, document ↔ bulletin de paie, document ↔ facture. | P0 |

---

### 11.10 Module Administration (MOD-ADMIN)

| Fonctionnalité | Description | Priorité |
|---------------|-------------|----------|
| **Gestion des utilisateurs** | Création, modification, désactivation d'utilisateurs. | P0 |
| **Rôles et permissions** | Rôles prédéfinis (administrateur, expert-comptable, collaborateur, gestionnaire paie, commercial, lecture seule). Permissions granulaires par module, par action (lire, créer, modifier, supprimer, valider). | P0 |
| **Droits par dossier** | Restriction d'accès par dossier pour chaque utilisateur (un collaborateur ne voit que ses dossiers). | P0 |
| **Authentification** | E-mail + mot de passe. MFA (authentification multi-facteurs) obligatoire pour les administrateurs. | P0 |
| **SSO** | Single Sign-On via SAML/OIDC pour les entreprises. | P2 |
| **Audit trail** | Journal d'audit complet : chaque action (création, modification, suppression, validation, connexion) est enregistrée avec horodatage, utilisateur, adresse IP, valeurs avant/après. | P0 |
| **Paramétrage entreprise** | Raison sociale, forme juridique, ICE, IF, RC, patente, CNSS employeur, adresse, logo, cachet, signature numérique. | P0 |
| **Sauvegarde et restauration** | Sauvegardes automatiques quotidiennes. Restauration à la demande par l'administrateur. | P0 |
| **Import / Migration** | Outils d'import depuis AtlasCompta, AtlasPaie, Sage, Excel pour faciliter la migration. | P0 |

---

## 12. Contraintes métier marocaines

### 12.1 Plan Comptable Marocain (CGNC)

Le produit **doit** implémenter le Plan Comptable Général des Entreprises marocain tel que défini par le Code Général de Normalisation Comptable (CGNC) :

| Classe | Intitulé | Détail |
|--------|----------|--------|
| **Classe 1** | Comptes de financement permanent | Capitaux propres, emprunts, provisions durables |
| **Classe 2** | Comptes d'actif immobilisé | Immobilisations incorporelles, corporelles, financières |
| **Classe 3** | Comptes d'actif circulant hors trésorerie | Stocks, créances, TVA récupérable |
| **Classe 4** | Comptes de passif circulant hors trésorerie | Fournisseurs, dettes fiscales et sociales, TVA due |
| **Classe 5** | Comptes de trésorerie | Banques, caisse, virements internes |
| **Classe 6** | Comptes de charges | Charges d'exploitation, financières, non courantes |
| **Classe 7** | Comptes de produits | Produits d'exploitation, financiers, non courants |
| **Classe 8** | Comptes de résultat | Résultat d'exploitation, financier, non courant, net |
| **Classe 9** | Comptes analytiques | Comptes de la comptabilité analytique |
| **Classe 0** | Comptes spéciaux (hors bilan) | Engagements donnés et reçus |

**Règles impératives** :
- Le plan de comptes livré par défaut doit être conforme au modèle normal ou simplifié du CGNC.
- Les comptes de classe 0 à 9 doivent être gérés.
- La numérotation doit respecter la nomenclature CGNC (ex : 6111 = Achats de marchandises, 3421 = Clients, etc.).
- L'utilisateur peut ajouter des sous-comptes mais pas modifier la structure des comptes CGNC de base.
- Le plan de comptes doit être versionné pour permettre les mises à jour réglementaires.

### 12.2 Modèle normal vs modèle simplifié

| Critère | Modèle normal | Modèle simplifié |
|---------|--------------|-----------------|
| **Seuil** | CA > 10M MAD ou Total bilan > 5M MAD | En dessous des seuils |
| **Plan de comptes** | Complet (toutes les subdivisions) | Réduit (comptes principaux) |
| **Bilan** | Modèle normal (actif/passif détaillés) | Modèle simplifié |
| **CPC** | Modèle normal (exploitation, financier, non courant) | Modèle simplifié |
| **ESG** | Obligatoire | Non obligatoire |
| **Tableau de financement** | Obligatoire | Non obligatoire |
| **Liasse fiscale** | Complète (tous les tableaux) | Simplifiée |

Le produit doit permettre de choisir le modèle applicable à chaque dossier/société et adapter automatiquement les états financiers en conséquence.

### 12.3 Exercice comptable

- Durée standard : 12 mois (du 01/01 au 31/12 par défaut).
- Premier exercice : peut être inférieur ou supérieur à 12 mois.
- L'exercice est découpé en périodes (mois par défaut).
- Un exercice peut être : ouvert, en cours de clôture, clôturé.
- La clôture est irréversible (sauf réouverture exceptionnelle par administrateur avec audit trail).

### 12.4 Journaux comptables

Les journaux suivants doivent être gérés a minima :

| Code | Journal | Description |
|------|---------|-------------|
| AC | Achats | Factures fournisseurs |
| VT | Ventes | Factures clients |
| BQ | Banque | Opérations bancaires (un journal par compte bancaire) |
| CA | Caisse | Opérations en espèces |
| OD | Opérations Diverses | Écritures d'ajustement, provisions, amortissements |
| PA | Paie | Écritures de paie |
| AN | À-Nouveaux | Report des soldes d'ouverture |

- Chaque journal a une numérotation séquentielle propre, sans rupture.
- Les journaux sont paramétrables (code, libellé, type, compte de contrepartie par défaut).
- L'utilisateur peut créer des journaux supplémentaires.

### 12.5 TVA marocaine

| Taux | Application |
|------|-------------|
| 20% | Taux normal (biens et services courants) |
| 14% | Transport, énergie (certains cas), beurre |
| 10% | Hôtellerie, restauration, professions libérales |
| 7% | Eau, produits pharmaceutiques, fournitures scolaires |
| 0% | Exportations (exonération avec droit de déduction) |
| Exonéré sans droit de déduction | Certaines opérations (éducation, santé, agriculture) |

**Règles critiques** :
- Régime de droit commun : TVA sur encaissement (pour les prestations de services) vs TVA sur débit (pour les ventes de biens).
- Option pour le régime des débits possible.
- Règle du décalage d'un mois pour la TVA déductible (sauf immobilisations).
- Prorata de TVA pour les entreprises partiellement assujetties.
- Crédit de TVA reportable.
- Déclaration mensuelle (CA > 1M MAD) ou trimestrielle (CA ≤ 1M MAD).

---

## 13. Contraintes réglementaires

### 13.1 Fiscalité

| Obligation | Détail | Module concerné |
|-----------|--------|----------------|
| **Liasse fiscale** | Déclaration annuelle comprenant le bilan, le CPC, l'ESG, le tableau de financement, et les états annexes (A1 à J). | MOD-COMPTA |
| **EDI XML** | Dépôt électronique de la liasse fiscale auprès de la DGI. Format XML conforme aux spécifications de la DGI. | MOD-COMPTA |
| **IS (Impôt sur les Sociétés)** | Calcul du résultat fiscal, acomptes provisionnels. Le produit peut assister au calcul mais la déclaration reste manuelle (hors périmètre de dépôt automatique). | MOD-COMPTA |
| **IR professionnel** | Barème progressif annuel. Régularisation en fin d'année. Calcul mensuel avec cumul. | MOD-PAIE |
| **Cotisation minimale** | 0,5% du CA + produits accessoires. Plancher de l'IS/IR professionnel. | MOD-COMPTA |
| **Taxe professionnelle** | Hors périmètre V1 (calcul simple proposé en V3). | — |
| **Retenue à la source** | Gestion des retenues à la source sur honoraires, commissions, loyers (selon les cas). | MOD-COMPTA |

### 13.2 Social

| Obligation | Détail | Module concerné |
|-----------|--------|----------------|
| **CNSS** | Déclaration mensuelle des salaires et cotisations via DAMANCOM. | MOD-PAIE |
| **AMO** | Assurance Maladie Obligatoire (intégrée aux cotisations CNSS). | MOD-PAIE |
| **CIMR** | Retraite complémentaire (volontaire mais très répandue). | MOD-PAIE |
| **État 9421** | Déclaration annuelle des traitements et salaires à la DGI. | MOD-PAIE |
| **Bulletin de paie** | Mentions obligatoires selon le Code du travail marocain. | MOD-PAIE |
| **Livre de paie** | Registre des salaires obligatoire. | MOD-PAIE |

### 13.3 Barème IR salarial (en vigueur — à maintenir à jour)

| Tranche de revenu annuel imposable (MAD) | Taux | Somme à déduire |
|------------------------------------------|------|-----------------|
| 0 – 30 000 | 0% | 0 |
| 30 001 – 50 000 | 10% | 3 000 |
| 50 001 – 60 000 | 20% | 8 000 |
| 60 001 – 80 000 | 30% | 14 000 |
| 80 001 – 180 000 | 34% | 17 200 |
| > 180 000 | 38% | 24 400 |

**Note** : Ce barème est celui applicable à la date de rédaction. Le moteur de règles doit permettre de mettre à jour le barème sans modification du code source.

### 13.4 Taux CNSS (à maintenir à jour)

| Cotisation | Part salariale | Part patronale | Plafond |
|-----------|---------------|---------------|---------|
| Prestations sociales court terme | — | 1,05% | — |
| Prestations sociales long terme | 3,96% | 7,93% | 6 000 MAD/mois |
| Allocations familiales | — | 6,40% | — |
| AMO | 2,26% | 4,52% | — |
| Taxe de formation professionnelle | — | 1,6% | — |

### 13.5 Conservation des données

- Durée légale de conservation des documents comptables au Maroc : **10 ans**.
- Les données ne doivent jamais être supprimées physiquement pendant cette période.
- L'audit trail est non modifiable et non supprimable.

### 13.6 Conformité numérique

- Les factures doivent comporter l'ICE (Identifiant Commun de l'Entreprise) obligatoirement.
- Les numéros de facture doivent être séquentiels et sans rupture.
- Le produit doit être prêt pour la facturation électronique (e-facture) lorsque la réglementation sera promulguée.

---

## 14. Rôle de l'IA

### 14.1 Principes fondamentaux

L'IA dans EasyAccounting est une **couche transverse d'assistance** qui intervient dans tous les modules. Elle est conçue pour :
- **Accélérer** le travail des utilisateurs,
- **Réduire les erreurs** humaines,
- **Détecter les anomalies** avant qu'elles ne deviennent des problèmes,
- **Apprendre** des patterns de chaque dossier pour des suggestions de plus en plus pertinentes.

### 14.2 Ce que l'IA PEUT faire

| Capacité | Module | Description |
|----------|--------|-------------|
| **OCR et extraction** | GED, COMPTA | Extraire les informations d'une facture scannée (fournisseur, montant, TVA, date, numéro). |
| **Classification de documents** | GED | Classifier automatiquement un document déposé (facture achat, facture vente, relevé bancaire, bulletin, contrat). |
| **Suggestion d'imputation** | COMPTA | Proposer le compte comptable le plus probable en fonction du fournisseur, du libellé et de l'historique. |
| **Pré-remplissage** | COMPTA, TVA, PAIE | Pré-remplir les formulaires et déclarations en se basant sur les données existantes. |
| **Détection d'anomalies** | COMPTA, PAIE, COM | Signaler : écriture déséquilibrée, compte inhabituel, montant anormalement élevé, doublon potentiel, salarié sans bulletin, stock négatif. |
| **Assistance au lettrage** | COMPTA | Proposer des rapprochements entre factures et règlements. |
| **Assistance au rapprochement bancaire** | COMPTA | Proposer des correspondances entre écritures comptables et lignes de relevé. |
| **Assistance à la clôture** | COMPTA | Lister les contrôles de pré-clôture et signaler les points de blocage. |
| **Prédiction de trésorerie** | REPORT | Prévision de trésorerie basée sur l'historique et les échéances. |
| **Suggestions budgétaires** | BUDGET | Proposer un budget basé sur le réel N-1. |
| **Analyse des écarts** | ANA, BUDGET | Expliquer les écarts significatifs entre le budget et le réel. |

### 14.3 Ce que l'IA NE PEUT PAS faire seule

| Interdiction | Justification |
|-------------|---------------|
| **Valider une écriture comptable officielle** | Seul un utilisateur habilité peut valider une écriture. L'IA peut proposer, l'humain valide. |
| **Clôturer un exercice** | La clôture est un acte juridique et comptable qui engage la responsabilité du professionnel. |
| **Modifier une règle métier** | Les taux de TVA, barèmes IR, taux CNSS sont des paramètres réglementaires qui ne peuvent être modifiés que par un administrateur humain. |
| **Générer une paie définitive sans validation** | Le calcul de paie peut être proposé par le système, mais la validation (= génération du bulletin officiel) nécessite une action humaine explicite. |
| **Déposer une déclaration fiscale** | L'IA peut préparer le fichier, mais le dépôt auprès de la DGI ou de la CNSS doit être déclenché par l'utilisateur. |
| **Supprimer des données** | L'IA n'a aucun droit de suppression. |
| **Modifier les droits d'accès** | Réservé aux administrateurs humains. |

### 14.4 Architecture IA

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **Moteur OCR** | Service cloud (Azure Document Intelligence / Google Document AI / modèle open-source) | Extraction de texte et de champs structurés depuis les documents scannés. |
| **Modèle de classification** | ML supervisé (entraîné sur les données anonymisées du produit) | Classification des documents et suggestion de comptes. |
| **Modèle d'anomalie** | Règles + ML non supervisé (détection d'outliers) | Détection d'anomalies comptables et de paie. |
| **Modèle de prévision** | Séries temporelles (Prophet / ARIMA) | Prévision de trésorerie et de tendances. |
| **LLM (assistant contextuel)** | API Claude / GPT (pour les fonctions conversationnelles) | Réponse aux questions contextuelles ("Pourquoi mon bilan ne s'équilibre pas ?"). |

### 14.5 Score de confiance

Toutes les suggestions de l'IA sont accompagnées d'un **score de confiance** :
- **> 90%** : suggestion appliquée par défaut avec possibilité de correction (opt-out).
- **70-90%** : suggestion proposée, l'utilisateur doit explicitement accepter (opt-in).
- **< 70%** : suggestion affichée en grisé avec mention "confiance faible". L'utilisateur doit saisir manuellement.

---

## 15. Rôle du moteur de règles

### 15.1 Objectif

Le moteur de règles est le composant qui **encode les règles métier marocaines** de manière configurable, sans code, afin de :
- Permettre des mises à jour réglementaires rapides (nouveau barème IR, nouveau taux CNSS) sans déploiement logiciel.
- Permettre une personnalisation par dossier/société (conventions collectives, accords d'entreprise).
- Garantir que les calculs sont toujours conformes et auditable.

### 15.2 Périmètre du moteur de règles

| Domaine | Règles gérées |
|---------|---------------|
| **TVA** | Taux par nature d'opération, régime (encaissement/débit), prorata, décalage, exonérations. |
| **IR** | Barème progressif, abattements (frais professionnels 20%, personnes à charge), déductions (CNSS, CIMR, mutuelle), régularisation annuelle. |
| **CNSS** | Taux salariaux et patronaux, plafonds, assiettes. |
| **CIMR** | Taux configurables par entreprise. |
| **Amortissements** | Durées de vie standards par catégorie, méthodes autorisées, coefficients dégressifs. |
| **Paie** | Formules de calcul des rubriques, conditions d'application, ordres de calcul. |
| **Heures supplémentaires** | Taux légaux (25%, 50%, 100%), conditions (jour/nuit/repos). |
| **Congés** | Droits légaux (1,5j/mois), ancienneté, congés spéciaux. |
| **Indemnités de licenciement** | Barème légal par ancienneté. |
| **Cotisation minimale** | Taux (0,5%), assiette (CA + produits accessoires). |
| **Retenue à la source** | Taux par type de prestation. |

### 15.3 Architecture du moteur de règles

```
┌─────────────────────────────────────────────┐
│              Interface Admin                 │
│   (Configuration des règles sans code)       │
├─────────────────────────────────────────────┤
│              Moteur de règles                │
│  ┌─────────────┐  ┌──────────────────────┐  │
│  │ Règles      │  │ Règles               │  │
│  │ nationales  │  │ entreprise/dossier   │  │
│  │ (barème IR, │  │ (taux CIMR, primes   │  │
│  │  taux CNSS) │  │  conventionnelles)   │  │
│  └─────────────┘  └──────────────────────┘  │
│                    │                         │
│  ┌─────────────────▼──────────────────────┐  │
│  │  Résolveur de règles                   │  │
│  │  (priorité : entreprise > national)    │  │
│  └─────────────────┬──────────────────────┘  │
├────────────────────┼────────────────────────┤
│                    ▼                         │
│   API de calcul (consommée par les modules)  │
└─────────────────────────────────────────────┘
```

### 15.4 Versioning des règles

- Chaque modification de règle est versionnée (date d'effet, date de fin, valeur précédente, valeur nouvelle, auteur).
- Un calcul de paie d'un mois passé utilise les règles en vigueur **à la date du calcul**, pas les règles actuelles.
- L'historique des règles est non supprimable et auditable.

---

## 16. Principes d'architecture produit

### 16.1 Architecture générale

```
┌──────────────────────────────────────────────────────────────┐
│                     CLIENTS                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Web App  │  │ PWA      │  │ API      │  │ Portail  │    │
│  │ (SPA)    │  │ Mobile   │  │ Clients  │  │ Client   │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
└───────┼──────────────┼──────────────┼──────────────┼─────────┘
        │              │              │              │
┌───────▼──────────────▼──────────────▼──────────────▼─────────┐
│                   API GATEWAY                                 │
│         (Auth, Rate Limiting, Routing, Logging)               │
├──────────────────────────────────────────────────────────────┤
│                   SERVICES MÉTIER                              │
│  ┌─────────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ │
│  │ Compta  │ │ TVA  │ │ Immo │ │ Paie │ │ Com  │ │Report│ │
│  │ Service │ │ Svc  │ │ Svc  │ │ Svc  │ │ Svc  │ │ Svc  │ │
│  └────┬────┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ │
│       │         │        │        │        │        │       │
│  ┌────▼─────────▼────────▼────────▼────────▼────────▼────┐  │
│  │              SERVICES TRANSVERSES                      │  │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐       │  │
│  │  │ IA   │ │Règles│ │ GED  │ │Audit │ │Notif │       │  │
│  │  │Engine│ │Engine│ │ Svc  │ │Trail │ │ Svc  │       │  │
│  │  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘       │  │
│  └───────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────┤
│                   COUCHE DONNÉES                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │PostgreSQL│  │ Redis    │  │ Object   │  │ Search   │    │
│  │(données) │  │ (cache)  │  │ Storage  │  │ (Elastic)│    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└──────────────────────────────────────────────────────────────┘
```

### 16.2 Principes architecturaux

| Principe | Détail |
|----------|--------|
| **Multi-tenant** | Isolation par schéma PostgreSQL (un schéma par tenant). Données totalement isolées. Requêtes toujours filtrées par tenant_id. |
| **API-first** | Toute fonctionnalité est exposée via une API REST documentée (OpenAPI 3.0). L'interface web consomme la même API que les intégrations tierces. |
| **Services modulaires** | Chaque module métier est un service indépendant avec sa propre base de données logique. Communication inter-services par événements (event-driven) et API synchrones quand nécessaire. |
| **Event-driven** | Les événements métier (écriture validée, paie calculée, facture émise) sont publiés sur un bus d'événements (Kafka / RabbitMQ) pour découplage inter-modules. |
| **Idempotence** | Toutes les opérations d'écriture sont idempotentes pour éviter les doublons en cas de retry. |
| **Audit trail natif** | Chaque mutation est tracée dans une table d'audit immuable (append-only). |
| **Soft delete** | Aucune suppression physique. Les enregistrements sont marqués comme supprimés avec horodatage. |
| **Versioning des données critiques** | Les règles métier, les plans de comptes, les barèmes sont versionnés avec date d'effet. |

### 16.3 Stack technologique recommandée

| Couche | Technologie | Justification |
|--------|------------|---------------|
| **Frontend** | React / Next.js + TypeScript | Écosystème riche, SSR pour performance, TypeScript pour robustesse. |
| **UI Framework** | Shadcn/UI + Tailwind CSS | Composants modernes, personnalisables, accessibles. |
| **Backend** | Node.js (NestJS) ou Python (FastAPI) | Performance, écosystème, facilité de recrutement au Maroc. |
| **Base de données** | PostgreSQL | Robustesse, support JSON, extensions (partitioning, row-level security). |
| **Cache** | Redis | Sessions, cache de requêtes, cache de règles. |
| **Bus d'événements** | RabbitMQ (V1) / Kafka (V3+) | Découplage inter-services, fiabilité. |
| **Object Storage** | MinIO / S3-compatible | Stockage des pièces jointes et documents. |
| **Recherche** | Elasticsearch / Meilisearch | Recherche plein texte dans les écritures, documents, produits. |
| **IA / ML** | Python (scikit-learn, PyTorch) + API LLM | Modèles de classification, OCR, anomalies, assistant conversationnel. |
| **CI/CD** | GitHub Actions / GitLab CI | Déploiement continu, tests automatisés. |
| **Infrastructure** | Kubernetes (AWS EKS / Azure AKS / OVH) | Scalabilité, résilience, déploiement cloud. |
| **Monitoring** | Prometheus + Grafana + Sentry | Observabilité, alerting, tracking d'erreurs. |

### 16.4 Sécurité

| Mesure | Détail |
|--------|--------|
| **Chiffrement at-rest** | AES-256 pour les bases de données et le stockage objet. |
| **Chiffrement in-transit** | TLS 1.3 pour toutes les communications. |
| **Authentification** | JWT avec rotation, refresh tokens, MFA. |
| **Autorisation** | RBAC (Role-Based Access Control) avec permissions granulaires. Row-Level Security PostgreSQL pour l'isolation multi-tenant. |
| **OWASP Top 10** | Protection contre injection SQL, XSS, CSRF, etc. Audit de sécurité régulier. |
| **Données sensibles** | Hachage des mots de passe (bcrypt/argon2). Chiffrement des données sensibles (RIB, CIN) avec clés par tenant. |
| **Conformité RGPD/CNDP** | Conformité avec la loi 09-08 (protection des données personnelles au Maroc). Droit d'accès, de rectification, de suppression (soft delete). |
| **Backup** | Sauvegardes automatiques quotidiennes, rétention 30 jours, backup géo-répliqué. |
| **Disaster Recovery** | RTO < 4h, RPO < 1h. |

### 16.5 Performance

| Métrique | Cible |
|----------|-------|
| Temps de chargement des pages | < 2s (P95) |
| Temps de calcul d'un bulletin de paie | < 3s |
| Temps de génération du bilan | < 5s (pour un exercice de 50 000 écritures) |
| Temps d'import Excel (1 000 écritures) | < 10s |
| Temps de recherche | < 500ms |
| Disponibilité | 99,9% (hors maintenance planifiée) |
| Concurrence | 500 utilisateurs simultanés par tenant sans dégradation |

---

## 17. Workflows métier principaux

### 17.1 Workflow : Saisie → Validation → Clôture (Comptabilité)

```
┌──────────┐    ┌──────────────┐    ┌───────────┐    ┌──────────┐
│  Saisie  │───▶│  Brouillard  │───▶│ Validation│───▶│  Clôture │
│ (draft)  │    │  (review)    │    │ (locked)  │    │ (sealed) │
└──────────┘    └──────────────┘    └───────────┘    └──────────┘
     │                │                    │                │
     │   Modifiable   │    Modifiable      │  Non modif.    │  Irréversible
     │                │    (avec trace)    │  (extourne     │  (sauf réouv.
     │                │                    │   possible)    │   admin)
```

**États d'une écriture** :
1. **Brouillard** : écriture en cours de saisie, modifiable librement.
2. **Validée** : écriture confirmée, non modifiable (seule une extourne est possible).
3. **Clôturée** : écriture appartenant à un exercice clôturé, totalement verrouillée.

### 17.2 Workflow : Traitement mensuel de la paie

```
┌────────────┐    ┌─────────────┐    ┌───────────┐    ┌──────────┐
│ Saisie des │───▶│  Calcul     │───▶│ Vérif. &  │───▶│Validation│
│ variables  │    │  de masse   │    │ simulation│    │ définit. │
└────────────┘    └─────────────┘    └───────────┘    └──────────┘
                                                            │
                    ┌───────────────────────────────────────┘
                    ▼
        ┌──────────────────┐    ┌──────────────┐    ┌──────────────┐
        │ Génération       │───▶│ Génération   │───▶│ Intégration  │
        │ bulletins (PDF)  │    │ DAMANCOM     │    │ comptable    │
        └──────────────────┘    └──────────────┘    └──────────────┘
```

**Étapes détaillées** :
1. Saisie des éléments variables (absences, HS, primes exceptionnelles).
2. Lancement du calcul en masse pour tous les salariés de la période.
3. Vérification des résultats (tableaux récapitulatifs, alertes, anomalies).
4. Simulation et ajustement si nécessaire.
5. Validation définitive (verrouille les bulletins).
6. Génération des bulletins de paie (PDF).
7. Génération du fichier DAMANCOM (déclaration CNSS).
8. Génération des écritures comptables de paie.
9. Envoi optionnel des bulletins par e-mail.

### 17.3 Workflow : Cycle commercial (Vente)

```
┌───────┐    ┌──────┐    ┌──────┐    ┌─────────┐    ┌──────────┐
│ Devis │───▶│  BC  │───▶│  BL  │───▶│ Facture │───▶│Règlement │
└───────┘    └──────┘    └──────┘    └─────────┘    └──────────┘
                            │             │               │
                            ▼             ▼               ▼
                      ┌──────────┐  ┌──────────┐   ┌──────────┐
                      │ Mvt      │  │ Écriture │   │ Écriture │
                      │ Stock    │  │ Vente    │   │ Encaiss. │
                      │ (sortie) │  │ (compta) │   │ (compta) │
                      └──────────┘  └──────────┘   └──────────┘
```

### 17.4 Workflow : Déclaration TVA

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Écritures    │───▶│ Calcul auto  │───▶│ Contrôle     │
│ du mois      │    │ TVA coll/déd │    │ cohérence    │
└──────────────┘    └──────────────┘    └──────────────┘
                                              │
                    ┌─────────────────────────┘
                    ▼
        ┌──────────────────┐    ┌──────────────┐    ┌──────────────┐
        │ Validation       │───▶│ Génération   │───▶│ Écriture de  │
        │ utilisateur      │    │ formulaire   │    │ liquidation  │
        └──────────────────┘    │ + EDI XML    │    │ comptable    │
                                └──────────────┘    └──────────────┘
```

### 17.5 Workflow : Clôture annuelle

```
┌──────────────────────────────────────────────────────────────────┐
│                    ASSISTANT DE CLÔTURE                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ☐ 1. Vérifier l'équilibre de tous les journaux                 │
│  ☐ 2. Vérifier le rapprochement bancaire                        │
│  ☐ 3. Vérifier le lettrage des comptes de tiers                 │
│  ☐ 4. Constater les amortissements                              │
│  ☐ 5. Constater les provisions                                  │
│  ☐ 6. Régulariser les charges et produits                       │
│  ☐ 7. Solder les comptes de TVA                                 │
│  ☐ 8. Générer le bilan et le CPC                                │
│  ☐ 9. Générer la liasse fiscale                                 │
│  ☐ 10. Valider la clôture                                       │
│  ☐ 11. Générer les à-nouveaux N+1                               │
│                                                                   │
│  [IA] Anomalies détectées : 3                                    │
│  [IA] Suggestions de correction : 3                              │
│                                                                   │
│  [Valider la clôture] ← action irréversible                     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 18. Flux inter-modules

### 18.1 Matrice des flux

| Source | Destination | Flux | Mécanisme |
|--------|------------|------|-----------|
| **MOD-PAIE** | **MOD-COMPTA** | Écritures de paie (charges personnel, cotisations, dettes sociales) | Événement `paie.validée` → génération auto des écritures |
| **MOD-COM** (Vente) | **MOD-COMPTA** | Écritures de vente (client, produit, TVA) | Événement `facture.émise` → génération auto |
| **MOD-COM** (Achat) | **MOD-COMPTA** | Écritures d'achat (fournisseur, charge, TVA) | Événement `facture_achat.saisie` → génération auto |
| **MOD-COM** (Règlement) | **MOD-COMPTA** | Écritures de règlement (banque/caisse, tiers) | Événement `règlement.enregistré` → génération auto |
| **MOD-COM** (Stock) | **MOD-COMPTA** | Écritures de variation de stock | Événement `inventaire.validé` → génération auto |
| **MOD-IMMO** | **MOD-COMPTA** | Dotations aux amortissements, cessions | Événement `dotation.calculée` → génération auto |
| **MOD-TVA** | **MOD-COMPTA** | Écriture de liquidation TVA | Événement `tva.liquidée` → génération auto |
| **MOD-COMPTA** | **MOD-TVA** | Écritures avec TVA | Événement `écriture.validée` → alimentation du calcul TVA |
| **MOD-COMPTA** | **MOD-REPORT** | Soldes et mouvements comptables | Requête directe (lecture) |
| **MOD-PAIE** | **MOD-REPORT** | Masse salariale, effectifs | Requête directe (lecture) |
| **MOD-COM** | **MOD-REPORT** | CA, marges, stock | Requête directe (lecture) |
| **MOD-GED** | **Tous modules** | Documents associés aux écritures, bulletins, factures | Lien document ↔ entité métier |
| **MOD-IA** | **Tous modules** | Suggestions, anomalies, OCR, classification | API transverse consommée par chaque module |
| **Moteur de règles** | **Tous modules** | Taux, barèmes, formules de calcul | API transverse consommée par chaque module |

### 18.2 Schéma des flux inter-modules

```
                         ┌───────────┐
                         │  MOD-IA   │◄──────────────────────────┐
                         │(transverse│                            │
                         └─────┬─────┘                            │
                               │ suggestions/anomalies            │
          ┌────────────────────┼────────────────────┐             │
          ▼                    ▼                    ▼             │
    ┌───────────┐      ┌───────────┐      ┌───────────┐         │
    │ MOD-PAIE  │─────▶│MOD-COMPTA │◄─────│ MOD-COM   │         │
    │           │écrit.│           │écrit. │           │         │
    └─────┬─────┘paie  └─────┬─────┘vente/└─────┬─────┘         │
          │                  │  achat       │                     │
          │            ┌─────┼─────┐        │                     │
          │            ▼     │     ▼        │                     │
          │     ┌──────────┐ │ ┌──────────┐ │                     │
          │     │ MOD-TVA  │ │ │ MOD-IMMO │ │                     │
          │     │          │─┘ │          │─┘                     │
          │     └──────────┘   └──────────┘                       │
          │            │              │                            │
          ▼            ▼              ▼                            │
    ┌──────────────────────────────────────────┐                  │
    │             MOD-REPORT                    │──────────────────┘
    │   (Dashboards, États, Ratios, Export)     │
    └──────────────────────────────────────────┘
          ▲                    ▲
          │                    │
    ┌───────────┐      ┌───────────┐
    │ MOD-ANA   │      │MOD-BUDGET │
    │(Analytique│      │           │
    └───────────┘      └───────────┘
```

### 18.3 Règles d'intégration inter-modules

1. **Principe de la source unique** : chaque donnée a un seul module propriétaire. Les autres modules la consomment en lecture.
2. **Asynchronisme par défaut** : les flux inter-modules passent par des événements asynchrones pour éviter le couplage fort.
3. **Idempotence** : chaque événement peut être rejoué sans effet de bord.
4. **Traçabilité** : chaque écriture générée automatiquement porte la référence de l'événement source (ex : "Facture VT-2026-001234").
5. **Réversibilité** : si une facture est annulée (avoir), l'écriture comptable correspondante est extournée automatiquement.

---

## 19. Critères de succès

### 19.1 Critères de succès produit (lancement V1)

| Critère | Métrique | Seuil de succès |
|---------|----------|----------------|
| **Parité fonctionnelle comptabilité** | Couverture des fonctionnalités AtlasCompta | ≥ 95% |
| **Fiabilité des calculs** | Taux d'erreur sur les états financiers | 0% (erreur = bug bloquant) |
| **Conformité TVA** | Déclarations TVA générées conformes à la réglementation | 100% |
| **Conformité liasse fiscale** | Liasse fiscale générée conforme au format DGI | 100% |
| **Performance** | Temps de génération du bilan (50k écritures) | < 5 secondes |
| **Stabilité** | Uptime sur le premier mois en production | > 99,5% |
| **Adoption early adopters** | Nombre de cabinets en beta | ≥ 20 |
| **Satisfaction early adopters** | Score CSAT | ≥ 4.0 / 5 |

### 19.2 Critères de succès business (à 18 mois)

| Critère | Métrique | Seuil de succès |
|---------|----------|----------------|
| **Acquisition** | Cabinets actifs payants | ≥ 200 |
| **Acquisition** | PME actives payantes | ≥ 500 |
| **Revenus** | ARR | ≥ 5M MAD |
| **Rétention** | Taux de rétention nette mensuel | > 97% |
| **Engagement** | DAU/MAU ratio | > 60% |
| **Expansion** | % clients multi-modules | > 40% |
| **NPS** | Net Promoter Score | > 50 |
| **Coût d'acquisition** | CAC | < 5 000 MAD |
| **Valeur vie client** | LTV / CAC | > 3x |

### 19.3 Critères de succès technique

| Critère | Métrique | Seuil de succès |
|---------|----------|----------------|
| **Disponibilité** | Uptime annuel | > 99,9% |
| **Performance** | P95 temps de réponse API | < 500ms |
| **Scalabilité** | Nombre de tenants supportés | > 1 000 |
| **Sécurité** | Incidents de sécurité critiques | 0 |
| **Qualité** | Couverture de tests | > 80% |
| **Déploiement** | Fréquence de déploiement | ≥ 1x / semaine |
| **Régression** | Taux de rollback | < 5% |

---

## 20. Hypothèses

### 20.1 Hypothèses marché

| ID | Hypothèse | Risque si invalide | Validation prévue |
|----|-----------|-------------------|-------------------|
| HM-01 | Les cabinets comptables marocains sont prêts à migrer vers le cloud | Adoption lente, pivot vers un modèle hybride | Enquête terrain auprès de 50 cabinets avant le lancement |
| HM-02 | Le prix d'un abonnement SaaS (500-2000 MAD/mois) est acceptable pour un cabinet | Barrière à l'entrée trop élevée | Tests de prix avec early adopters |
| HM-03 | Les PME marocaines cherchent une solution intégrée (vs outils séparés) | Le besoin est surestimé, les PME préfèrent des outils simples mono-fonction | Interviews utilisateurs, analyse des demandes Atlasdes PME |
| HM-04 | La dématérialisation fiscale va s'accélérer au Maroc (e-facture, EDI) | L'urgence perçue diminue, adoption plus lente | Veille réglementaire active |
| HM-05 | Les utilisateurs d'Atlas sont des early adopters naturels pour EasyAccounting | La base Atlas est fidèle et résistante au changement | Programme de migration avec incentives |

### 20.2 Hypothèses produit

| ID | Hypothèse | Risque si invalide | Validation prévue |
|----|-----------|-------------------|-------------------|
| HP-01 | La parité fonctionnelle avec AtlasCompta est suffisante pour convaincre les cabinets | Il manque des fonctionnalités critiques non identifiées | Beta test intensif avec 20 cabinets |
| HP-02 | L'IA apporte une valeur perçue suffisante pour justifier un premium | L'IA est perçue comme un gadget | Mesure du taux d'adoption des suggestions IA |
| HP-03 | Le multi-dossiers est le principal facteur de productivité pour les cabinets | D'autres facteurs sont plus importants | Interviews et observation d'usage |
| HP-04 | L'intégration paie → compta est un différentiateur clé | Les utilisateurs préfèrent garder des outils séparés | Test de la feature avec 10 fiduciaires |
| HP-05 | Le moteur de règles permet de gérer les mises à jour réglementaires sans release logicielle | Certaines mises à jour nécessitent quand même du code | Simulation avec les 3 dernières mises à jour réglementaires |

### 20.3 Hypothèses techniques

| ID | Hypothèse | Risque si invalide | Validation prévue |
|----|-----------|-------------------|-------------------|
| HT-01 | PostgreSQL avec isolation par schéma supporte 1 000+ tenants | Problèmes de performance ou de maintenance à l'échelle | Benchmark de charge avant mise en production |
| HT-02 | L'architecture event-driven assure la cohérence inter-modules | Des cas de désynchronisation apparaissent | Tests d'intégration exhaustifs, mécanismes de réconciliation |
| HT-03 | L'OCR atteint une précision > 90% sur les factures marocaines | Factures marocaines hétérogènes, OCR insuffisant | Test sur un corpus de 500 factures marocaines réelles |
| HT-04 | L'infrastructure cloud (AWS/Azure/OVH) offre une latence acceptable depuis le Maroc | Latence trop élevée pour une utilisation fluide | Benchmark depuis Casablanca, Rabat, Tanger |
| HT-05 | Le recrutement de développeurs compétents au Maroc est faisable | Difficultés de recrutement, coûts plus élevés | Cartographie du marché de l'emploi tech au Maroc |

---

## 21. Risques métier et produit

### 21.1 Risques stratégiques

| ID | Risque | Probabilité | Impact | Mitigation |
|----|--------|-------------|--------|------------|
| RS-01 | **Réglementation changeante** : une réforme fiscale majeure (TVA, IR, CNSS) impose des changements profonds | Moyenne | Élevé | Moteur de règles configurable, veille réglementaire permanente, partenariat avec un cabinet juridique |
| RS-02 | **Concurrence internationale** : Odoo, Sage, QuickBooks investissent la localisation marocaine | Moyenne | Élevé | Avance sur la localisation native, vitesse d'exécution, connaissance terrain |
| RS-03 | **Concurrence locale** : un éditeur marocain lance un produit similaire | Faible | Moyen | First-mover advantage, qualité d'exécution, communauté |
| RS-04 | **Résistance au changement** : les cabinets refusent de quitter leurs outils actuels | Élevée | Élevé | Programme de migration gratuit, formation, accompagnement, période d'essai longue |
| RS-05 | **Souveraineté des données** : inquiétude des clients sur l'hébergement cloud | Moyenne | Moyen | Hébergement au Maroc ou en France (OVH), certifications de sécurité, transparence |

### 21.2 Risques produit

| ID | Risque | Probabilité | Impact | Mitigation |
|----|--------|-------------|--------|------------|
| RP-01 | **Périmètre trop large** : vouloir tout faire dès V1 retarde le lancement | Élevée | Élevé | Priorisation stricte P0/P1/P2, lancement V1 avec comptabilité + TVA uniquement |
| RP-02 | **Qualité des calculs** : une erreur dans le calcul de TVA ou d'IR détruit la confiance | Moyenne | Critique | Tests unitaires exhaustifs sur les calculs, double-vérification avec des cas réels, beta test |
| RP-03 | **UX insuffisante** : interface trop complexe pour les utilisateurs non-experts | Moyenne | Élevé | Tests utilisateurs itératifs, design system, onboarding guidé |
| RP-04 | **Migration douloureuse** : les clients n'arrivent pas à migrer leurs données depuis Atlas/Sage | Moyenne | Élevé | Outils d'import dédiés, service de migration assistée, documentation |
| RP-05 | **IA pas assez précise** : suggestions de faible qualité qui ralentissent au lieu d'accélérer | Moyenne | Moyen | Score de confiance, opt-in sur les suggestions < 90%, apprentissage continu |

### 21.3 Risques techniques

| ID | Risque | Probabilité | Impact | Mitigation |
|----|--------|-------------|--------|------------|
| RT-01 | **Performance** : lenteur avec de gros volumes de données (cabinet avec 200 dossiers × 50k écritures) | Moyenne | Élevé | Architecture scalable, indexation, pagination, cache, benchmarks réguliers |
| RT-02 | **Sécurité** : faille de sécurité exposant les données clients | Faible | Critique | Audit de sécurité externe, tests de pénétration, bug bounty, chiffrement bout en bout |
| RT-03 | **Disponibilité** : pannes impactant la production pendant les périodes fiscales | Faible | Critique | Infrastructure redondante, monitoring 24/7, plan de reprise, SLA contractuel |
| RT-04 | **Cohérence inter-modules** : désynchronisation des données entre compta et paie/commercial | Moyenne | Élevé | Mécanismes de réconciliation, alertes de désynchronisation, tests d'intégration |
| RT-05 | **Dette technique** : accumulation de dette technique sous pression de livraison | Élevée | Moyen | Sprint de refactoring régulier (20% du temps), revue de code systématique, métriques de qualité |

### 21.4 Risques opérationnels

| ID | Risque | Probabilité | Impact | Mitigation |
|----|--------|-------------|--------|------------|
| RO-01 | **Recrutement** : difficulté à recruter des développeurs avec expertise compta/paie marocaine | Élevée | Élevé | Formation interne, documentation métier exhaustive, partenariat avec des cabinets |
| RO-02 | **Support** : afflux de demandes de support pendant les périodes fiscales (janvier, mars, avril) | Élevée | Moyen | Base de connaissances, chatbot FAQ, scaling du support, préparation saisonnière |
| RO-03 | **Pricing** : modèle de prix inadapté au marché marocain | Moyenne | Élevé | Tests de prix, offres modulaires, pricing en MAD, facturation locale |

---

## 22. Conclusion stratégique

### 22.1 Pourquoi maintenant ?

Le marché marocain de la gestion d'entreprise est à un point d'inflexion :

1. **Dématérialisation accélérée** : la DGI pousse l'EDI XML, l'e-facture est en préparation, DAMANCOM est obligatoire. Les outils desktop ne suivent plus.

2. **Adoption du cloud** : la connectivité Internet au Maroc a considérablement progressé (fibre, 4G+, 5G en déploiement). Le frein infrastructurel n'existe plus.

3. **Nouvelle génération de professionnels** : les jeunes collaborateurs comptables refusent les interfaces des années 2000. Ils attendent des outils aussi modernes que ceux qu'ils utilisent dans leur vie personnelle.

4. **Pression sur la productivité** : la concurrence entre cabinets s'intensifie. La productivité est un avantage concurrentiel. L'intégration et l'IA sont des leviers majeurs.

5. **Vide du marché** : il n'existe aujourd'hui aucune solution SaaS marocaine nativement intégrée (compta + paie + commercial) avec une localisation complète. C'est une opportunité unique.

### 22.2 Vision à 5 ans

EasyAccounting a vocation à devenir la **plateforme de référence de gestion d'entreprise au Maroc**, puis dans la région MENA/Afrique francophone. La roadmap long terme inclut :

- **V1 (Mois 0-9)** : Comptabilité + TVA + Immobilisations + Reporting — MVP pour cabinets comptables.
- **V2 (Mois 9-15)** : Paie marocaine complète + Intégration paie-compta — Extension aux fiduciaires et PME.
- **V3 (Mois 15-21)** : Gestion commerciale + Stock + Facturation — Extension aux PME commerciales et industrielles.
- **V4 (Mois 21-27)** : IA avancée + Analytique + Budgets + Consolidation multi-sociétés — Extension aux groupes.
- **V5 (Mois 27+)** : Portail collaboratif, e-facture, APIs marketplace, extensions tierces, internationalisation (Tunisie, Côte d'Ivoire, Sénégal).

### 22.3 Facteurs clés de succès

1. **Exécution irréprochable sur la conformité** : la confiance se gagne par la fiabilité des calculs et la conformité réglementaire. Zéro tolérance sur les erreurs comptables et fiscales.

2. **Expérience utilisateur supérieure** : l'UX est un différentiateur décisif face aux logiciels legacy. Chaque interaction doit être plus rapide, plus claire et plus agréable que l'alternative.

3. **Migration sans douleur** : la plus grande barrière à l'adoption est le coût de migration. Les outils d'import, la formation et l'accompagnement doivent rendre la transition naturelle.

4. **Time-to-value court** : un cabinet doit pouvoir être productif en moins de 2 semaines après la souscription. Pas de projet d'implémentation de 6 mois.

5. **Communauté et écosystème** : construire une communauté de professionnels comptables marocains autour du produit (forum, webinars, meetups, certifications) pour créer un effet réseau.

6. **IA comme accélérateur, pas comme risque** : l'IA doit être utile dès le jour 1 (OCR, suggestions) sans jamais compromettre la fiabilité. La transparence du score de confiance est essentielle.

### 22.4 Appel à l'action

Ce PRD définit le cadre fonctionnel, technique et stratégique d'EasyAccounting. Les prochaines étapes sont :

1. **Validation du PRD** par les parties prenantes (direction, équipe produit, équipe technique, conseillers métier).
2. **Constitution de l'équipe fondatrice** : Product Manager, Lead Developer, UX Designer, Expert comptable consultant.
3. **Phase de discovery** : interviews terrain avec 30+ cabinets et PME pour valider les hypothèses clés.
4. **Design sprint V1** : wireframes et prototypes du module comptabilité.
5. **Kick-off développement V1** : sprint 0 (architecture, CI/CD, design system) puis sprints fonctionnels.
6. **Programme beta** : recrutement de 20 cabinets early adopters.

---

*Ce document est un document vivant. Il sera mis à jour au fil de l'avancement du projet, des retours terrain et de l'évolution réglementaire.*

---

**EasyAccounting** — *La comptabilité marocaine, enfin unifiée.*
