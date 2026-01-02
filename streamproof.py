import ctypes
from ctypes import windll, wintypes

# Constant for SetWindowDisplayAffinity
WDA_EXCLUDEFROMCAPTURE = 0x00000011

def enable_streamproof(hwnd):
    """
    Hides the window from capture software (OBS, Discord, etc.)
    using the undocumented WDA_EXCLUDEFROMCAPTURE flag.
    Returns True if successful.
    """
    try:
        user32 = windll.user32
        result = user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
        return result != 0
    except Exception as e:
        print(f"Failed to enable streamproof: {e}")
        return False
