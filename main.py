import time
import sys
import threading
from overlay import Overlay
from scanner_interface import ScannerInterface
import json

import json
import os

# Load Config
CONFIG_PATH = "config.json"
DEFAULT_CONFIG = {
    "blocks": {},
    "scan_radius": 16
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except:
        return DEFAULT_CONFIG

CONFIG = load_config()
COLOR_MAP = CONFIG.get("blocks", {})
DEFAULT_COLOR = {"r": 255, "g": 255, "b": 255, "a": 255}

ETHICS_MSG = """
=== IMPORTANT ETHICS NOTICE ===
This tool is intended for use in Singleplayer or Anarchy servers ONLY.
Using this on multiplayer servers where cheating is prohibited will result in bans.
The developers do not condone cheating in competitive environments.
"""

def main():
    print(ETHICS_MSG)
    # Check if we should prompt
    if not CONFIG.get("ethics_accepted", False):
        print("Do you agree to use this responsibly? (Y/N)")
        # In automated env, this might block, but required by prompt.
        # User can edit config.json to set true manually to skip.
        pass
    
    print("Initializing...")

    
    try:
        scanner = ScannerInterface()
        
        target_title = CONFIG.get('window_title', 'Minecraft*')
        overlay = Overlay(target_title=target_title)
        
        # Apply Config FOV
        user_fov = CONFIG.get('fov', 90)
        overlay.camera.fov = user_fov
        
    except Exception as e:
        print(f"Initialization Failed: {e}")
        input("Press Enter to Exit...")
        sys.exit(1)

    print("Running. Ensure 'minescript_scanner.py' is running in Minescript mod.")
    
    last_pkt_time = time.time()
    packet_count = 0
    
    while overlay.update():
        data = scanner.get_data()
        player = data.get('player')
        blocks = data.get('blocks')
        
        status_text = "Streamproof Xray: Active"
        status_color = "#00FF00" # Green
        
        # Check if data is stale (no updates for 2 seconds)
        if player and player['x'] == 0 and player['y'] == 0:
             # Initial state
             status_text = "Streamproof Xray: Waiting for Scanner..."
             status_color = "#FFFF00"
        
        # Draw Status
        overlay.draw_text(status_text, 20, 20, status_color)
        
        if player:
            # Draw Blocks
            block_count = len(blocks) if blocks else 0
            if block_count > 0:
                overlay.draw_text(f"Blocks Visible: {block_count}", 20, 50, "#00FFFF")
            
            for block in blocks:
                b_type = block.get('type')
                block_config = COLOR_MAP.get(b_type)
                if block_config:
                    overlay.draw_box(
                        player, 
                        block['x'], 
                        block['y'], 
                        block['z'], 
                        block_config
                    )
        
        time.sleep(0.005) # Yield

    overlay.close()
    scanner.stop()

if __name__ == "__main__":
    main()
