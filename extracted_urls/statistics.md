# Statistiques détaillées de l'extraction des URLs

## Vue d'ensemble

**Date d'extraction**: $(date)
**Fichier source**: seed.md
**Total des URLs extraites**: 13,146

## Répartition par répertoire

### 1. Server (12,912 URLs - 98.2%)
Le répertoire le plus important avec la majorité des URLs. Contient tous les serveurs MCP disponibles sur la plateforme.

### 2. News (101 URLs - 0.8%)
Articles et actualités du site MCP Market.

### 3. Businesses (80 URLs - 0.6%)
Entreprises et organisations référencées sur la plateforme.

### 4. Categories (24 URLs - 0.2%)
Catégories de serveurs MCP organisées par domaine d'application.

### 5. Client (20 URLs - 0.2%)
Clients et applications clientes MCP.

### 6. Search (5 URLs - 0.04%)
Pages de recherche et résultats.

### 7. Autres répertoires (4 URLs - 0.03%)
- leaderboards: 1 URL
- submit: 1 URL
- waitlist: 1 URL
- what-is-an-mcp-server: 1 URL

## Analyse des données

### Répartition par priorité
- **daily**: URLs mises à jour quotidiennement
- **weekly**: URLs mises à jour hebdomadairement

### Répartition par score
- **Score 1.0**: URLs de plus haute priorité
- **Score 0.9**: URLs de haute priorité
- **Score 0.8**: URLs de priorité moyenne
- **Score 0.7**: URLs de priorité standard
- **Score 0.6**: URLs de priorité inférieure
- **Score 0.5**: URLs de priorité minimale

## Structure des URLs

### Format général
```
https://mcpmarket.com/{répertoire}/{identifiant}
```

### Exemples par répertoire
- **Server**: `https://mcpmarket.com/server/{nom-du-serveur}`
- **Categories**: `https://mcpmarket.com/categories/{nom-catégorie}`
- **Businesses**: `https://mcpmarket.com/businesses/{nom-entreprise}`
- **News**: `https://mcpmarket.com/news/{uuid-article}`
- **Search**: `https://mcpmarket.com/search/{terme-recherche}`

## Métadonnées associées

Chaque URL dans le fichier original contient :
- **URL**: L'adresse complète
- **Timestamp**: Date et heure de dernière mise à jour
- **Fréquence**: Fréquence de mise à jour (daily/weekly)
- **Score**: Score de priorité (0.5 à 1.0)

## Utilisation des fichiers générés

### Fichiers principaux
- `server.md` - Liste complète des serveurs MCP
- `categories.md` - Catégories de serveurs
- `businesses.md` - Entreprises référencées
- `news.md` - Articles et actualités

### Fichiers de support
- `README.md` - Résumé général
- `statistics.md` - Ce fichier de statistiques

## Notes techniques

- **Encodage**: UTF-8
- **Format**: Markdown
- **Organisation**: Par répertoire URL
- **Tri**: Alphabétique par URL
- **Validation**: URLs extraites et nettoyées automatiquement
