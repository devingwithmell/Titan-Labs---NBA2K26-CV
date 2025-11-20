# 🧬 TitanLabs – NBA2K Computer Vision Engine (Public Release)

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
git clone https://github.com/yourusername/TitanLabs-NBA2K-CVEngine.git
cd TitanLabs-NBA2K-CVEngine
