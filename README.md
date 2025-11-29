# 🗺️ 3D-to-2D Mapper

This project provides a simple and efficient tool to **project a 3D mesh into a 2D top-down map**, suitable for **cartography, georeferencing and spatial analysis**.  
It takes a 3D model in OBJ format (from photogrammetry, LiDAR scanning, or mobile 3D apps) and converts it into a **2D colored raster or vector map** based on the vertical height of the geometry.

---

## 🛠️ Usage

### Basic command (PNG output)
```bash
python3 map.py <png | svg> <path to the.obj file>           
```
---

###  ✨ Features

- 📁 Reads any OBJ mesh using `trimesh` python library
- 🎨 Height-based color shading (customizable color ramp)
- Exports **PNG** raster maps
- Exports **SVG** vector maps
- ⚙️ Adjustable grid resolution / cell density (Macro inside the code)
- 🚀 Efficient even with dense LiDAR or photogrammetry meshes

---


This approach is ideal for:

- terrain height maps  
- CAD/GIS integration  
- converting 3D scans into clean 2D drawings  

---
