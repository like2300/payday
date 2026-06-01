---
name: googleaut
description: Configuration de l'authentification Google via django-allauth et application du style visuel "Haram" (Glassmorphism, variables CSS sémantiques). Utilisez cette skill pour automatiser le setup Google Auth et l'UI premium dans les projets Django.
---

# Haram Auth Branding

Cette skill automatise l'intégration de l'authentification Google et applique le style visuel "Haram" basé sur le Glassmorphism et les variables CSS modernes.

## Workflow d'Authentification

Pour configurer Google Auth :
1.  **Vérification .env** : Assurez-vous que `GOOGLE_CLIENT_ID` et `GOOGLE_CLIENT_SECRET` sont présents.
2.  **Configuration Django** : Suivez les instructions dans [auth_setup.md](references/auth_setup.md).
3.  **Vérification Admin** : Assurez-vous que le `Site` (django.contrib.sites) est configuré avec le bon domaine.

## Guide de Style "Haram" (Overload Style)

Le style Haram repose sur une surcharge visuelle premium :
-   **Couleurs** : Palette Twilight et French Blue (voir [ui_patterns.md](references/ui_patterns.md)).
-   **Effets** : Glassmorphism (blur 20px, bordures translucides).
-   **Typographie** : Inter (font-black pour les titres, uppercase tracking-tighter).
-   **Composants** : Boutons "Sapphire", Cartes immersives, Sidebars transformables.

Pour appliquer ce style :
1.  Utilisez les variables CSS définies dans `base.html`.
2.  Appliquez les classes Tailwind combinées avec les variables sémantiques (ex: `bg-[var(--bg-surface)]`).
3.  Consultez [ui_patterns.md](references/ui_patterns.md) pour les snippets de code spécifiques.

## Triggers
- "Ajoute l'authentification Google"
- "Applique le style Haram"
- "Configure le mode production avec mon style"
- "Crée une page avec mon style de surcharge"
