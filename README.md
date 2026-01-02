# 💎 Streamproof X-Ray for Minescript

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Minescript](https://img.shields.io/badge/Minecraft-Minescript-blue.svg)](https://minescript.org/)

A high-performance, stream-safe overlay designed to visualize hidden blocks in Minecraft using the Minescript API.

> [!IMPORTANT]  
> **Project Status:** This project is currently a proof-of-concept exploring the real-time capabilities of Minescript. It is not considered "production-ready." If you find this useful, please **star the repository** or **contribute** via pull requests to support further development.

---

## ⚠️ Disclaimer

- **Ethical Use:** This tool is intended strictly for **Singleplayer** or **Anarchy** servers.
- **Fair Play:** Using this on multiplayer servers with anti-cheat policies will likely result in a permanent ban.
- **Responsibility:** The developers do not condone or support cheating in competitive environments. Use at your own risk.

---

## ✨ Features

- **Streamproof Overlay:** Rendered as a separate window layer, invisible to most screen-recording software (OBS, Discord, etc.).
- **Real-time Scanning:** Leverages the Minescript Scanner Interface for low-latency block detection.
- **Fully Customizable:**
  - Adjustable **Field of View (FOV)**.
  - Configurable **Scan Radius** to balance performance and visibility.
  - Custom **Block Filtering** (choose exactly which ores/blocks to highlight).
  - Dynamic **Color Mapping** for different block types.

---

## 🚀 Getting Started

### Prerequisites

1. **Minecraft:** An active instance running [Minescript](https://minescript.net/).
2. **Display Mode:** Minecraft must be running in **Windowed** or **Borderless Windowed** mode.
3. **Python:** Version 3.10+ installed (via [python.org](https://www.python.org/) or Microsoft Store).
4. **Script Setup:** Place `Minescript_scanner.py` into your `.minecraft/minescript` directory.

### Installation & Usage

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/streamproof-xray.git
   cd streamproof-xray
   ```
2. **Launch the Overlay:**
   ```bash
   python main.py
   ```
3. **Initialize in Minecraft:**
   Open the in-game chat and execute:
   ```text
   \minescript_scanner.py
   ```

---

## ⚙️ Configuration

All settings are managed via `config.json`. You can modify this file to tailor the overlay to your needs:

| Key | Description |
| :--- | :--- |
| `fov` | The horizontal/vertical field of view for the overlay. |
| `scan_radius` | How many blocks away the scanner should look. |
| `blocks` | A list of block IDs to target. |
| `colors` | Hex or RGB values assigned to specific block IDs. |

---

## 🤝 Contributing

Contributions are welcome! Whether it's bug fixes, performance improvements, or new features, feel free to open an issue or submit a pull request.