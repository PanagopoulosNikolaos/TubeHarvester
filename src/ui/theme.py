"""
Theme injection and styling definitions for the TubeHarvester web application.

Implements the Orange and Dark Soft design system using CSS custom properties,
glassmorphic surface styling, Google Fonts, and custom NiceGUI component overrides.
"""

from nicegui import ui

THEME_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Roboto:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-base: #121214;
    --bg-surface: rgba(28, 28, 32, 0.82);
    --bg-surface-elevated: rgba(36, 36, 42, 0.92);
    --bg-input: rgba(20, 20, 24, 0.85);
    
    --border-subtle: rgba(255, 255, 255, 0.12);
    --border-hover: rgba(255, 255, 255, 0.22);
    --border-focus: #FF7A3D;
    
    --accent: #FF7A3D;
    --accent-hover: #FF955F;
    --accent-active: #E86A2F;
    --accent-glow: rgba(255, 122, 61, 0.28);
    
    --brown-selected: #5D4037;
    --brown-border: rgba(141, 110, 99, 0.65);
    
    --danger: #EF4444;
    --danger-hover: #F87171;
    --danger-bg: rgba(239, 68, 68, 0.15);
    
    --green-ok: #22C55E;
    --red-err: #F87171;
    --yellow-warn: #FBBF24;
    
    --font-brand: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-body: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
    
    --text-1: #EDEDEF;
    --text-2: #D1D1D6;
    --text-muted: #8E8E93;
    
    --shadow-card: 0 16px 36px rgba(0, 0, 0, 0.55), 0 4px 12px rgba(0, 0, 0, 0.35);
    --shadow-glow: 0 0 24px rgba(255, 122, 61, 0.3);
    
    --radius-sm: 8px;
    --radius-md: 14px;
    --radius-lg: 20px;
    --radius-full: 9999px;
}

html, body {
    background-color: var(--bg-base) !important;
    color: var(--text-1) !important;
    font-family: var(--font-body) !important;
    min-height: 100vh;
    width: 100%;
    margin: 0;
    padding: 0;
    overflow-x: hidden;
}

body::before {
    content: '';
    position: fixed;
    top: -20%;
    left: 50%;
    transform: translateX(-50%);
    width: min(100vw, 850px);
    height: 560px;
    background: radial-gradient(circle, rgba(255, 122, 61, 0.14) 0%, rgba(93, 64, 55, 0.08) 50%, transparent 70%);
    pointer-events: none;
    z-index: 0;
    filter: blur(50px);
}

#app, .q-layout, .q-page-container {
    min-height: 100vh !important;
    width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
}

.nicegui-content {
    min-height: 100vh !important;
    width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    padding: clamp(16px, 3vh, 48px) clamp(16px, 3vw, 32px) !important;
    box-sizing: border-box !important;
}

.app-wrapper {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    z-index: 1;
}

.app-container {
    max-width: clamp(340px, 92vw, 680px);
    width: 100%;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: clamp(14px, 2vh, 20px);
}

/* Icon image filters & sizing */
.app-icon {
    width: 20px;
    height: 20px;
    object-fit: contain;
    filter: invert(1);
    pointer-events: none;
}

.app-icon-hero {
    width: 32px;
    height: 32px;
    object-fit: contain;
    filter: invert(1);
    pointer-events: none;
}

/* Quasar button icon image filter overrides */
.q-btn .q-icon img,
.nav-tab-btn .q-icon img,
.btn-primary .q-icon img,
.btn-secondary .q-icon img {
    filter: invert(1);
    width: 20px;
    height: 20px;
    object-fit: contain;
    vertical-align: middle;
    pointer-events: none;
}

.nav-tab-btn .q-icon {
    font-size: 20px !important;
    margin-right: 6px !important;
}

/* Prevent any child element from blocking button clicks */
.q-btn *, .nav-tab-btn *, .btn-primary *, .btn-secondary * {
    pointer-events: none !important;
}

.q-btn {
    pointer-events: auto !important;
    cursor: pointer !important;
}

.hero-banner {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 4px 0;
    gap: 8px;
}

.hero-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.hero-logo-box {
    width: 48px;
    height: 48px;
    border-radius: var(--radius-md);
    background: linear-gradient(135deg, #FF7A3D 0%, #5D4037 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 16px rgba(255, 122, 61, 0.35);
    color: #FFFFFF;
}

.hero-app-title {
    font-family: var(--font-brand);
    font-size: clamp(24px, 4vw, 32px);
    font-weight: 800;
    letter-spacing: -0.5px;
    margin: 0;
    background: linear-gradient(180deg, #FFFFFF 0%, #EDEDEF 60%, #D1D1D6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-app-tagline {
    font-size: clamp(12px, 1.8vw, 14px);
    color: var(--text-2);
    margin: 0;
    font-weight: 400;
}

/* Glass Card with uniform styling across views */
.glass-card {
    background: var(--bg-surface) !important;
    backdrop-filter: blur(20px) saturate(1.4) !important;
    -webkit-backdrop-filter: blur(20px) saturate(1.4) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--shadow-card) !important;
    padding: clamp(16px, 3vw, 24px) !important;
    transition: border-color 260ms ease, box-shadow 260ms ease;
    box-sizing: border-box;
    min-height: 460px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}

.glass-card:hover {
    border-color: var(--border-hover) !important;
    box-shadow: 0 20px 42px rgba(0, 0, 0, 0.65), 0 0 24px rgba(255, 122, 61, 0.1) !important;
}

/* Nav Tabs: transparent default, brown-8 when selected */
.glass-tabs {
    background: transparent !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-full) !important;
    padding: 3px !important;
}

.nav-tab-btn {
    border-radius: var(--radius-full) !important;
    font-family: var(--font-brand) !important;
    font-weight: 600 !important;
    font-size: clamp(12px, 1.8vw, 14px) !important;
    transition: all 220ms ease !important;
    min-height: 40px !important;
    padding: 0 16px !important;
}

.tab-inactive {
    background: transparent !important;
    color: var(--text-2) !important;
    border: 1px solid transparent !important;
}

.tab-inactive:hover {
    color: #FFFFFF !important;
    background: rgba(255, 255, 255, 0.06) !important;
}

.tab-active {
    background: var(--brown-selected) !important;
    color: #FFFFFF !important;
    border: 1px solid var(--brown-border) !important;
    box-shadow: 0 2px 10px rgba(93, 64, 55, 0.45) !important;
}

/* Primary Action button: transparent resting, brown-8 active/hover */
.btn-primary {
    background: transparent !important;
    color: #FFFFFF !important;
    font-family: var(--font-brand) !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    border-radius: var(--radius-md) !important;
    border: 1px solid rgba(255, 122, 61, 0.65) !important;
    box-shadow: 0 0 14px rgba(255, 122, 61, 0.2) !important;
    transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1) !important;
    height: 46px !important;
    min-width: 140px;
    letter-spacing: 0.2px;
}

.btn-primary:hover, .btn-primary:focus, .btn-primary:active {
    background: var(--brown-selected) !important;
    border-color: var(--brown-border) !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(93, 64, 55, 0.5) !important;
}

/* Secondary Button: subtle ghost button with low visual weight */
.btn-secondary {
    background: transparent !important;
    color: var(--text-2) !important;
    font-family: var(--font-brand) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    font-weight: 500 !important;
    font-size: 13.5px !important;
    transition: all 200ms ease !important;
    height: 44px !important;
}

.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    color: #FFFFFF !important;
    border-color: var(--border-hover) !important;
}

.btn-secondary:active, .btn-secondary:focus {
    background: var(--brown-selected) !important;
    color: #FFFFFF !important;
    border-color: var(--brown-border) !important;
}

.btn-danger {
    background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important;
    color: #FFFFFF !important;
    font-family: var(--font-brand) !important;
    font-weight: 600 !important;
    border-radius: var(--radius-md) !important;
    border: none !important;
    box-shadow: 0 4px 16px rgba(239, 68, 68, 0.4) !important;
    animation: pulse-danger 2s infinite;
    height: 46px !important;
}

.glass-input .q-field__control {
    background: var(--bg-input) !important;
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border-subtle) !important;
    color: var(--text-1) !important;
    transition: border-color 200ms ease, box-shadow 200ms ease;
    height: 46px !important;
}

.glass-input.q-field--focused .q-field__control {
    border-color: var(--border-focus) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}

.glass-input .q-field__native, .glass-input input {
    color: var(--text-1) !important;
    font-family: var(--font-body) !important;
    font-size: 14px !important;
}

.field-label {
    font-family: var(--font-brand);
    font-size: 12.5px;
    font-weight: 600;
    color: var(--text-2);
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 4px;
}

.field-helper {
    font-size: 11.5px;
    color: var(--text-muted);
    margin-top: 2px;
}

.input-error-msg {
    font-size: 12px;
    color: var(--red-err);
    margin-top: 4px;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Metadata Preview Card */
.metadata-preview-card {
    background: rgba(18, 18, 22, 0.75) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    padding: 10px 12px !important;
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 12px;
    animation: fadeIn 250ms ease-out;
}

.preview-thumb-box {
    width: 80px;
    height: 52px;
    border-radius: var(--radius-sm);
    overflow: hidden;
    background: #0E0E12;
    flex-shrink: 0;
}

.preview-thumb-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.preview-title {
    font-family: var(--font-brand);
    font-size: 13.5px;
    font-weight: 600;
    color: #FFFFFF;
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.preview-meta {
    font-size: 11.5px;
    color: var(--text-2);
    display: flex;
    gap: 8px;
    margin-top: 2px;
}

/* Skeleton Loading Shimmer */
.skeleton-shimmer {
    background: linear-gradient(90deg, rgba(255,255,255,0.04) 25%, rgba(255,255,255,0.11) 50%, rgba(255,255,255,0.04) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: var(--radius-sm);
    height: 44px;
    width: 100%;
}

.log-console {
    background: #0E0E12 !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    font-family: var(--font-mono) !important;
    font-size: 12.5px !important;
    padding: 12px 14px !important;
    max-height: 180px;
    min-height: 80px;
    overflow-y: auto;
    color: var(--text-1);
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.log-entry {
    line-height: 1.5;
    animation: fadeIn 200ms ease-out;
    word-break: break-word;
}

.log-info {
    color: var(--text-1);
}

.log-success {
    color: var(--green-ok);
    font-weight: 500;
}

.log-error {
    color: var(--red-err);
    font-weight: 500;
}

.q-linear-progress {
    border-radius: var(--radius-full) !important;
    height: 8px !important;
    background: rgba(255, 255, 255, 0.08) !important;
}

.q-linear-progress__model {
    background: linear-gradient(90deg, #FF7A3D 0%, #5D4037 100%) !important;
    transition: width 300ms ease-out !important;
}

/* Modal Dialog and Scrim */
.q-dialog__backdrop {
    background: rgba(8, 8, 10, 0.88) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
}

.preset-row {
    background: rgba(24, 24, 30, 0.7);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 10px 14px;
    cursor: pointer;
    transition: all 180ms ease;
    width: 100%;
}

.preset-row:hover {
    background: rgba(93, 64, 55, 0.3);
    border-color: var(--brown-border);
    transform: translateX(3px);
}

.q-menu {
    background: var(--bg-surface-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    backdrop-filter: blur(16px) !important;
    color: var(--text-1) !important;
}

.q-item {
    color: var(--text-1) !important;
    font-family: var(--font-body) !important;
    transition: background 150ms ease;
}

.q-item:hover {
    background: rgba(93, 64, 55, 0.3) !important;
    color: #FFFFFF !important;
}

::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.18);
    border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 122, 61, 0.4);
}

@keyframes pulse-danger {
    0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.45); }
    50% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
}

@keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 640px) {
    .glass-card {
        padding: 16px !important;
        min-height: auto;
    }
    .hero-app-title {
        font-size: 24px;
    }
    .log-console {
        max-height: 130px;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, ::before, ::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
"""


def injectTheme() -> None:
    """
    Injects the complete Orange and Dark Soft design CSS stylesheet into the head.
    """
    # Injects the application stylesheet into the document head for global styling.
    ui.add_head_html(f"<style>{THEME_CSS}</style>")


def glassCard() -> str:
    """
    Returns the CSS class string for glassmorphism card surfaces.

    Returns:
        str: Class string for styling cards.
    """
    return "glass-card"


def btnPrimary() -> str:
    """
    Returns the CSS class string for primary call-to-action buttons.

    Returns:
        str: Class string for primary buttons.
    """
    return "btn-primary"


def btnSecondary() -> str:
    """
    Returns the CSS class string for secondary neutral buttons.

    Returns:
        str: Class string for secondary buttons.
    """
    return "btn-secondary"


def btnDanger() -> str:
    """
    Returns the CSS class string for dangerous cancellation buttons.

    Returns:
        str: Class string for danger action buttons.
    """
    return "btn-danger"
