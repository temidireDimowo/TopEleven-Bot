"""Color tokens and font helpers for the TopEleven Bot UI."""

# ── Palette ──────────────────────────────────────────────────────────
BG_PRIMARY   = "#1a1a2e"
BG_SECONDARY = "#16213e"
BG_CARD      = "#2a2a3e"
BG_SIDEBAR   = "#12122a"

ACCENT_BLUE   = "#4a9eff"
ACCENT_GREEN  = "#4ec9b0"
ACCENT_ORANGE = "#f0a500"
ACCENT_RED    = "#f14c4c"
ACCENT_PURPLE = "#9b59b6"

TEXT_PRIMARY   = "#e8e8f0"
TEXT_SECONDARY = "#9090a8"
TEXT_MUTED     = "#606078"

LOG_INFO    = "#9cdcfe"
LOG_WARNING = "#ffd700"
LOG_ERROR   = "#f14c4c"
LOG_SUCCESS = "#4ec9b0"
LOG_DEBUG   = "#c5c5c5"

STATUS_RUNNING = "#4ec9b0"
STATUS_PAUSED  = "#f0a500"
STATUS_IDLE    = "#606078"
STATUS_ERROR   = "#f14c4c"

NAV_ACTIVE   = "#3a3a6e"
NAV_HOVER    = "#252545"
NAV_INACTIVE = "transparent"

BORDER_COLOR = "#3a3a5a"

# ── Typography ───────────────────────────────────────────────────────
FONT_FAMILY = "Segoe UI" if __import__("sys").platform == "win32" else "SF Pro Display"

FONT_H1 = (FONT_FAMILY, 22, "bold")
FONT_H2 = (FONT_FAMILY, 16, "bold")
FONT_H3 = (FONT_FAMILY, 13, "bold")
FONT_BODY = (FONT_FAMILY, 12)
FONT_SMALL = (FONT_FAMILY, 10)
FONT_MONO = ("Consolas" if __import__("sys").platform == "win32" else "Monaco", 11)
FONT_STAT_VALUE = (FONT_FAMILY, 28, "bold")
FONT_STAT_LABEL = (FONT_FAMILY, 11)

# ── Status helpers ────────────────────────────────────────────────────

STATUS_COLORS = {
    "running": STATUS_RUNNING,
    "paused":  STATUS_PAUSED,
    "idle":    STATUS_IDLE,
    "error":   STATUS_ERROR,
}

STATUS_LABELS = {
    "running": "● Running",
    "paused":  "⏸ Paused",
    "idle":    "◌ Idle",
    "error":   "✕ Error",
}

LOG_COLORS = {
    "info":    LOG_INFO,
    "warning": LOG_WARNING,
    "error":   LOG_ERROR,
    "success": LOG_SUCCESS,
    "debug":   LOG_DEBUG,
}
