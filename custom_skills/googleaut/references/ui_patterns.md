# Haram UI Patterns (Overload Style)

## CSS Variables Core
```css
:root {
    --bg-app: #fafafa;
    --bg-surface: #ffffff;
    --bg-surface-alt: #f3f4f6;
    --text-main: #111827;
    --text-muted: #6b7280;
    --accent-primary: #046ffb;
    --accent-soft: rgba(4, 111, 251, 0.05);
    --border-subtle: #e5e7eb;
}

.dark {
    --bg-app: #010223;
    --bg-surface: #020231;
    --bg-surface-alt: #030563;
    --text-main: #f9fafb;
    --text-muted: #9ca3af;
    --accent-primary: #368cfc;
    --border-subtle: rgba(255, 255, 255, 0.08);
}
```

## Glassmorphism Pattern
```css
.glass-card {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(20px) saturate(150%);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}
```

## Typography Style
- **Titres** : `font-black uppercase tracking-tighter text-[var(--text-main)]`
- **Badges** : `text-[10px] font-black uppercase tracking-widest bg-[var(--accent-soft)] text-[var(--accent-primary)] px-3 py-1 rounded-full`

## Interactive Components
- **Bouton Sapphire** :
  ```html
  <button class="bg-[var(--accent-primary)] text-white font-black uppercase tracking-widest py-4 px-8 rounded-2xl hover:scale-105 transition-all shadow-xl shadow-[var(--accent-primary)]/20">
      Texte
  </button>
  ```
