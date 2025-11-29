#!/usr/bin/env python3
import sys
import trimesh
import numpy as np
import svgwrite
from PIL import Image, ImageDraw

# ----------------------
# RGB Color Macros
# ----------------------
BLUE       = (0, 0, 255)
RED        = (255, 0, 0)
ORANGE     = (255, 50, 19)
GREEN      = (0, 255, 0)
YELLOW     = (255, 255, 0)
CYAN       = (0, 255, 255)
MAGENTA    = (255, 0, 255)
WHITE      = (255, 255, 255)
BLACK      = (0, 0, 0)
GRAY       = (128, 128, 128)

# ----------------------
# Choose your gradient colors
# ----------------------
START_COLOR = CYAN
END_COLOR   = MAGENTA

# ----------------------
# Parameters
# ----------------------
SVG_MAX_SIZE = 4200
GRID_DIV     = 490

# ----------------------
# Command line arguments
# ----------------------
if len(sys.argv) < 3:
    print("Usage: python3 map.py <png|svg> <input_file.obj>")
    sys.exit(1)

OUTPUT_MODE = sys.argv[1].lower()
INPUT_FILE  = sys.argv[2]

if OUTPUT_MODE not in ["png", "svg"]:
    print("First argument must be 'png' or 'svg'")
    sys.exit(1)

try:
    mesh = trimesh.load(INPUT_FILE)
except Exception:
    print("Invalid OBJ file path")
    sys.exit(1)

if isinstance(mesh, trimesh.Scene):
    mesh = trimesh.util.concatenate(tuple(mesh.dump()))

points = np.array(mesh.vertices)

# ----------------------
# Use OBJ axes directly
# ----------------------
x = points[:,0]  # horizontal
y = points[:,2]  # horizontal
z = points[:,1]  # height

# ----------------------
# Build grid
# ----------------------
xmin, xmax = x.min(), x.max()
ymin, ymax = y.min(), y.max()
x_range = xmax - xmin
y_range = ymax - ymin
max_range = max(x_range, y_range)

GRID_SIZE = max_range / GRID_DIV
nx = int(np.ceil(x_range / GRID_SIZE))
ny = int(np.ceil(y_range / GRID_SIZE))

ix = ((x - xmin) / GRID_SIZE).astype(int)
iy = ((y - ymin) / GRID_SIZE).astype(int)
ix = np.clip(ix, 0, nx-1)
iy = np.clip(iy, 0, ny-1)

height_grid = np.full((nx, ny), np.nan)
count_grid = np.zeros((nx, ny))
sum_grid   = np.zeros((nx, ny))

for i,j,h in zip(ix, iy, z):
    sum_grid[i,j] += h
    count_grid[i,j] += 1

mask = count_grid > 0
height_grid[mask] = sum_grid[mask] / count_grid[mask]

z_min, z_max = np.nanmin(height_grid), np.nanmax(height_grid)

# ----------------------
# Gradient color function
# ----------------------
def height_to_color(height, start_rgb, end_rgb):
    t = (height - z_min) / (z_max - z_min) if z_max > z_min else 1.0
    r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * t)
    g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * t)
    b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * t)
    return (r, g, b)

# ----------------------
# SVG mode
# ----------------------
if OUTPUT_MODE == "svg":
    scale = SVG_MAX_SIZE / max(nx, ny)
    dwg = svgwrite.Drawing("topdown.svg", size=(nx*scale, ny*scale))

    sorted_indices = np.argsort(height_grid.flatten())
    for idx in sorted_indices:
        i = idx // ny
        j = idx % ny
        if np.isnan(height_grid[i,j]):
            continue
        color = height_to_color(height_grid[i,j], START_COLOR, END_COLOR)
        x0 = (nx - i - 1) * scale
        y0 = (ny - j - 1) * scale
        dwg.add(dwg.rect(
            insert=(x0, y0),
            size=(scale, scale),
            fill=svgwrite.rgb(*color),
            stroke='none'
        ))

    dwg.save()
    print("✔ SVG generated: topdown.svg")
    sys.exit(0)

# ----------------------
# PNG mode
# ----------------------
if OUTPUT_MODE == "png":
    img = Image.new("RGB", (nx, ny), (0,0,0))
    draw = ImageDraw.Draw(img)

    sorted_indices = np.argsort(height_grid.flatten())
    for idx in sorted_indices:
        i = idx // ny
        j = idx % ny
        if np.isnan(height_grid[i,j]):
            continue
        color = height_to_color(height_grid[i,j], START_COLOR, END_COLOR)
        px = nx - i - 1
        py = ny - j - 1
        draw.point((px, py), fill=color)

    big = img.resize((nx*6, ny*6), Image.NEAREST)
    big.save("topdown.png")
    print("✔ PNG generated: topdown.png")
    sys.exit(0)
