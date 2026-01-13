"""
Tema och stilkonfiguration för MinaKontakter.
"""

from config import THEME


class Theme:
    """Tema-konstanter och hjälpmetoder för UI."""
    
    # Färger från config
    BG_DARK = THEME["bg_dark"]
    BG_MEDIUM = THEME["bg_medium"]
    BG_LIGHT = THEME["bg_light"]
    BG_HOVER = THEME["bg_hover"]
    BG_SELECTED = THEME["bg_selected"]
    
    ACCENT_GOLD = THEME["accent_gold"]
    ACCENT_GOLD_HOVER = THEME["accent_gold_hover"]
    ACCENT_GOLD_DARK = THEME["accent_gold_dark"]
    
    TEXT_PRIMARY = THEME["text_primary"]
    TEXT_SECONDARY = THEME["text_secondary"]
    TEXT_MUTED = THEME["text_muted"]
    
    BORDER = THEME["border"]
    BORDER_LIGHT = THEME["border_light"]
    
    SUCCESS = THEME["success"]
    WARNING = THEME["warning"]
    ERROR = THEME["error"]
    
    @staticmethod
    def get_font(size: str = "normal", bold: bool = False) -> tuple:
        """Returnerar font-tuple för CustomTkinter."""
        sizes = {
            "small": 12,
            "normal": 14,
            "large": 16,
            "title": 20,
            "header": 24,
        }
        font_size = sizes.get(size, 14)
        weight = "bold" if bold else "normal"
        return ("Segoe UI", font_size, weight)
    
    @staticmethod
    def get_entry_colors() -> dict:
        """Returnerar färger för CTkEntry."""
        return {
            "fg_color": Theme.BG_MEDIUM,
            "border_color": Theme.BORDER,
            "text_color": Theme.TEXT_PRIMARY,
            "placeholder_text_color": Theme.TEXT_MUTED,
        }
    
    @staticmethod
    def get_button_colors() -> dict:
        """Returnerar färger för primär CTkButton."""
        return {
            "fg_color": Theme.ACCENT_GOLD,
            "hover_color": Theme.ACCENT_GOLD_HOVER,
            "text_color": Theme.BG_DARK,
        }
    
    @staticmethod
    def get_secondary_button_colors() -> dict:
        """Returnerar färger för sekundär CTkButton."""
        return {
            "fg_color": Theme.BG_HOVER,
            "hover_color": Theme.BG_SELECTED,
            "text_color": Theme.TEXT_PRIMARY,
        }
    
    @staticmethod
    def get_danger_button_colors() -> dict:
        """Returnerar färger för destruktiv CTkButton."""
        return {
            "fg_color": Theme.ERROR,
            "hover_color": "#e53e3e",
            "text_color": Theme.TEXT_PRIMARY,
        }
