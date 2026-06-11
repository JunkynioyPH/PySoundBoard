# Generated and tweaked with CHATGPT, because i am NOT gonna go through all that
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

def get_slate_blue_dark_palette():
    palette = QPalette()
    bgDimOffset = 40
    txtDimOffset = 10
    # Colors sampled/approximated from your screenshot
    window_bg = QColor(58-bgDimOffset, 58-bgDimOffset, 60-bgDimOffset)        # main background
    base_bg = QColor(45-bgDimOffset, 45-bgDimOffset, 50-bgDimOffset)          # inputs / deeper panels
    alt_bg = QColor(63-bgDimOffset, 45-bgDimOffset, 70-bgDimOffset)           # slightly raised surfaces
    border_hint = QColor(90-bgDimOffset, 92-bgDimOffset, 100-bgDimOffset)     # subtle edge contrast

    text_color = QColor(210-txtDimOffset, 214-txtDimOffset, 220-txtDimOffset)    # soft light gray (not pure white)
    dim_text = QColor(150-txtDimOffset, 155-txtDimOffset, 160-txtDimOffset)      # secondary text
    accent = QColor(100-txtDimOffset, 140-txtDimOffset, 200-txtDimOffset)        # muted blue (matches slider highlight)

    # Base UI
    palette.setColor(QPalette.ColorRole.Window, window_bg)
    palette.setColor(QPalette.ColorRole.WindowText, text_color)
    palette.setColor(QPalette.ColorRole.Base, base_bg)
    palette.setColor(QPalette.ColorRole.AlternateBase, alt_bg)

    # Text + tooltips
    palette.setColor(QPalette.ColorRole.Text, text_color)
    palette.setColor(QPalette.ColorRole.ToolTipBase, base_bg)
    palette.setColor(QPalette.ColorRole.ToolTipText, text_color)

    # Buttons (very similar to background in your UI)
    palette.setColor(QPalette.ColorRole.Button, window_bg)
    palette.setColor(QPalette.ColorRole.ButtonText, text_color)

    # Highlights (slider + selection)
    palette.setColor(QPalette.ColorRole.Highlight, accent)
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)

    # Links / accents
    palette.setColor(QPalette.ColorRole.Link, accent)
    palette.setColor(QPalette.ColorRole.BrightText, accent)

    # Disabled state (matches your dimmed labels)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, dim_text)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, dim_text)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, dim_text)

    return palette