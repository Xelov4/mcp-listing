# Statistiques du Crawling - Cursor Directory MCPs

## Résumé de l'opération

**Date de crawling :** 20 août 2025  
**Heure de début :** 19:22  
**Heure de fin :** 19:32  
**Durée totale :** ~10 minutes  

## Résultats du crawling

### Total des MCPs crawlé
**50 MCPs** au total

### Répartition par statut GitHub

| Statut | Nombre | Pourcentage |
|--------|--------|-------------|
| **Avec lien GitHub** | 2 | 4% |
| **Sans lien GitHub** | 48 | 96% |

### MCPs avec liens GitHub trouvés

1. **Blockchain Data by Tatum**
   - Repository: https://github.com/tatumio/blockchain-mcp
   - Description: Official Tatum blockchain MCP server giving you RPC and API read and write data access to 130+ blockchain protocols

2. **Caiyun Weather**
   - Repository: https://github.com/caiyunapp/mcp-caiyun-weather
   - Description: Weather data service providing real-time weather information, forecasts, and historical weather data through an API

### MCPs sans liens GitHub

Les 48 autres MCPs n'ont pas de liens GitHub directs sur leurs pages cursor.directory. Cela peut être dû à :
- Absence de repository public
- Repository privé
- Pas encore de repository créé
- Lien GitHub non référencé sur la page

## Fichiers générés

### Structure des fichiers
```
cursordirectory/
├── README.md (résumé général)
├── STATISTICS.md (ce fichier)
└── [nom-du-mcp].md (50 fichiers individuels)
```

### Types de contenu par fichier
Chaque fichier MCP contient :
- **Titre** du MCP
- **Description** complète
- **Lien GitHub** (si disponible)
- **Fonctionnalités** principales
- **Cas d'usage** (si applicable)
- **Source** et date de mise à jour

## Méthodologie utilisée

1. **Crawling du sitemap** : Analyse de https://cursor.directory/sitemap.xml
2. **Navigation vers la page MCPs** : https://cursor.directory/mcp
3. **Extraction des informations** : Description, fonctionnalités, liens
4. **Recherche de liens GitHub** : Analyse du HTML de chaque page
5. **Génération des fichiers** : Création automatique des fichiers Markdown

## Outils utilisés

- **Playwright** : Navigation et extraction de contenu web
- **Terminal** : Création de dossiers et fichiers
- **Éditeur de fichiers** : Génération des fichiers Markdown

## Observations

- **Taux de succès GitHub** : Seulement 4% des MCPs ont des liens GitHub publics
- **Qualité des descriptions** : Excellente, descriptions détaillées disponibles
- **Cohérence** : Tous les MCPs suivent le même format de présentation
- **Complétude** : 100% des MCPs listés ont été documentés

## Recommandations

1. **Recherche approfondie** : Certains MCPs peuvent avoir des repositories GitHub non référencés
2. **Mise à jour régulière** : Vérifier périodiquement les nouveaux liens GitHub
3. **Contact direct** : Contacter les développeurs des MCPs sans repository pour encourager l'open source
4. **Documentation** : Améliorer la documentation des MCPs existants

## Conclusion

Le crawling de cursor.directory a été un succès complet. Tous les 50 MCPs ont été documentés avec leurs informations complètes. Bien que seulement 2 aient des liens GitHub directs, cela fournit une base solide pour la découverte et l'utilisation de ces outils MCP dans l'écosystème Cursor.
