# 🗺️ 3D-to-2D Mapper

This project provides a simple and efficient tool to **project a 3D mesh into a 2D top-down map**, suitable for **cartography, georeferencing and spatial analysis**.  
It takes a 3D model in OBJ format (from photogrammetry, LiDAR scanning, or mobile 3D apps) and converts it into a **2D colored raster or vector map** based on the vertical height.

---

## 🛠️ Usage

### Command (You can choose the output format)
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

### What is possible to change

- **Output format**: Choose between `PNG` or `SVG` as the output file type.
- **Grid density**: Adjust the `GRID_SIZE` parameter to make the 2D projection more or less pixelated. Smaller `GRID_SIZE` = finer cells.
- **Number of color bands**: Modify `N_BANDS` to control how many discrete color levels are used.
- **Color gradient**: Use any two RGB colors (`start_color` and `end_color`) to define the gradient for height mapping. The higher the height, the closer the color to `end_color`.


---


This approach is ideal for:

- terrain height maps  
- CAD/GIS integration  
- converting 3D scans into clean 2D drawings  

---
