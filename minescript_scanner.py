import sys
import socket
import json
import time
import math

# Add minescript to path if needed or assume it's available in context
# import minescript as ms 
# (Minescript is usually injected into the global namespace or available via import)

HOST = '127.0.0.1'
PORT = 65432

INTERESTING_BLOCKS = {
    "minecraft:diamond_ore",
    "minecraft:deepslate_diamond_ore",
    "minecraft:gold_ore",
    "minecraft:deepslate_gold_ore",
    "minecraft:ancient_debris",
    "minecraft:emerald_ore",
    "minecraft:deepslate_emerald_ore"
}

def load_config():
    # Try to find config.json in likely locations
    # 1. Same dir as script
    # 2. Hardcoded path (User might need to set if they move script)
    paths = [
        "config.json",
        "../config.json",
        "streamproof_xray/config.json" # If they keep folder structure
    ]
    
    for p in paths:
        try:
            with open(p, 'r') as f:
                data = json.load(f)
                return data
        except:
            continue
    return None

CONFIG = load_config()
if CONFIG and "blocks" in CONFIG:
    # Update interesting blocks from config keys
    INTERESTING_BLOCKS = set(CONFIG["blocks"].keys())
    # Update radius if present
    # RADIUS = CONFIG.get("scan_radius", 16) - need to pass to scan function or make global


def get_player_data():
    # Minescript API usage
    # Assuming minescript module is available as 'minescript'
    import minescript
    
    # Position
    pos = minescript.player_position() # Returns (x, y, z)
    if pos is None:
        return None
    
    # Rotation
    # We need to find how to get yaw/pitch.
    # Often exposed as player object properties.
    p = minescript.player()
    
    # Inspecting player object for rotation usually:
    # yaw = p.yaw
    # pitch = p.pitch
    # If not directly available, we might fallback or need documentation.
    # Assuming standard names.
    yaw = getattr(p, 'yaw', 0.0)
    pitch = getattr(p, 'pitch', 0.0)
    
    return {
        "x": pos[0],
        "y": pos[1],
        "z": pos[2],
        "yaw": yaw,
        "pitch": pitch,
        "dimension": "overworld" # Placeholder
    }


# Precompute offsets for optimization
SCAN_RADIUS = 5
SCAN_OFFSETS = []
for x in range(-SCAN_RADIUS, SCAN_RADIUS):
    for y in range(-SCAN_RADIUS, SCAN_RADIUS):
        for z in range(-SCAN_RADIUS, SCAN_RADIUS):
            SCAN_OFFSETS.append((x, y, z))

def scan_radius(radius=5): # Radius arg is ignored in favor of global precomputed for speed
    import minescript
    
    blocks = []
    ppos = minescript.player_position()
    if not ppos:
        return []

    px, py, pz = int(ppos[0]), int(ppos[1]), int(ppos[2])
    
    # Batch Scan using getblocklist (One API call instead of 1000)
    # 1. Build request list
    query_positions = []
    for dx, dy, dz in SCAN_OFFSETS:
        query_positions.append([px + dx, py + dy, pz + dz])
        
    # 2. Bulk get
    try:
        results = minescript.getblocklist(query_positions)
        
        # 3. Process results
        if results:
            for i, block_str in enumerate(results):
                if not block_str: continue
                
                # Check interesting
                # block_str usually "minecraft:diamond_ore"
                # optimization: explicit check before split?
                if "ore" in block_str or "chest" in block_str or "spawner" in block_str:
                     b_name = block_str.split('[')[0]
                     if b_name in INTERESTING_BLOCKS:
                         # Reconstruct pos from query_positions[i]
                         # query_positions[i] is [x, y, z]
                         pos = query_positions[i]
                         blocks.append({"x": pos[0], "y": pos[1], "z": pos[2], "type": b_name})
    except Exception as e:
        pass
                    
    return blocks

def main():
    import minescript
    minescript.echo("Scanner Script Output: Started (Batch Mode)")
    print("Minescript Scanner Started")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while True:
        try:
            p_data = get_player_data()
            if p_data:
                # Real-time scanning now enabled via Batch API
                found_blocks = scan_radius(SCAN_RADIUS)
                
                packet = {
                    "player": p_data,
                    "blocks": found_blocks
                }
                
                sock.sendto(json.dumps(packet).encode('utf-8'), (HOST, PORT))
            
            # 60 FPS target
            time.sleep(0.016) 
            
        except Exception as e:
            minescript.echo(f"Scanner Error: {e}")
            print(f"Error in scanner: {e}")
            time.sleep(1)

if __name__ == '__main__':
    main()
