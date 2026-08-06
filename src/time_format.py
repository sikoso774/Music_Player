# src/time_format.py
# Convertit une durée en millisecondes en chaîne MM:SS.

def format_time(ms):
    """Convertit les millisecondes en format MM:SS."""
    seconds = ms // 1000
    minutes = seconds // 60
    seconds %= 60
    return f"{minutes:02d}:{seconds:02d}"
