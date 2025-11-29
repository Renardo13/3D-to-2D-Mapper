#!/usr/bin/env python3
import sys
import trimesh
import numpy as np
import svgwrite
from PIL import Image, ImageDraw

# ----------------------
# Paramètres
# ----------------------
SVG_MAX_SIZE = 4000
N_BANDS = 10
ALPHA_MIN = 1.0
ALPHA_MAX = 1.0

# ----------------------
# Vérification arguments
# ----------------------
if len(sys.argv) < 3:
    print("Usage: python3 map.py <png|svg> <fichier.obj>")
    sys.exit(1)

OUTPUT_MODE = sys.argv[1].lower()
INPUT_FILE = sys.argv[2]

if OUTPUT_MODE not in ["png", "svg"]:
    print("Le premier argument doit être png ou svg")
    sys.exit(1)

try:
    mesh = trimesh.load(INPUT_FILE)
except Exception:
    print("Invalid OBJ file path")
    exit(1)

if isinstance(mesh, trimesh.Scene):
    mesh = trimesh.util.concatenate(tuple(mesh.dump()))

points = np.array(mesh.vertices)

# ----------------------
# Détection axe vertical
# ----------------------
mins = points.min(axis=0)
maxs = points.max(axis=0)
ranges = maxs - mins
vert_axis = int(np.argmax(ranges))

print("Min:", mins)
print("Max:", maxs)
print(f"→ Axe vertical détecté : {['X','Y','Z'][vert_axis]}")

# ----------------------
# Réarrangement axes
# ----------------------
if vert_axis != 2:
    other = [0,1,2]
    other.remove(vert_axis)
    new_order = [other[0], other[1], vert_axis]
    points = points[:, new_order]
    print("→ Réordonné en XYZ =", new_order)

x = points[:,0]
y = points[:,2]   # horizontal
z = points[:,1]   # hauteur

# ----------------------
# Grille moins dense
# ----------------------
xmin, xmax = x.min(), x.max()
ymin, ymax = y.min(), y.max()

x_range = xmax - xmin
y_range = ymax - ymin
max_range = max(x_range, y_range)

GRID_SIZE = max_range / 250     # cellules moins denses comme demandé
print(f"GRID_SIZE : {GRID_SIZE}")

nx = int(np.ceil(x_range / GRID_SIZE))
ny = int(np.ceil(y_range / GRID_SIZE))

ix = ((x - xmin) / GRID_SIZE).astype(int)
iy = ((y - ymin) / GRID_SIZE).astype(int)

ix = np.clip(ix, 0, nx-1)
iy = np.clip(iy, 0, ny-1)

height_grid = np.full((nx, ny), np.nan)
count_grid = np.zeros((nx, ny))
sum_grid = np.zeros((nx, ny))

for i,j,h in zip(ix, iy, z):
    sum_grid[i,j] += h
    count_grid[i,j] += 1

mask = count_grid > 0
height_grid[mask] = sum_grid[mask] / count_grid[mask]

# ----------------------
# Couleurs ORIGINALES (bleu → rouge)
# ----------------------
z_min, z_max = np.nanmin(height_grid), np.nanmax(height_grid)
band_edges = np.linspace(z_min, z_max, N_BANDS+1)

def height_to_color(h):
    band = np.searchsorted(band_edges, h, side='right') - 1
    t = band / (N_BANDS-1)

    r = int(255*t)
    g = 50
    b = int(255*(1-t))

    return (r, g, b), band


# ----------------------
# MODE SVG
# ----------------------
if OUTPUT_MODE == "svg":
    scale = SVG_MAX_SIZE / max(nx, ny)
    svg_width = nx * scale
    svg_height = ny * scale

    dwg = svgwrite.Drawing("topdown.svg", size=(svg_width, svg_height))

    # bas → haut
    for band in range(N_BANDS):
        for i in range(nx):
            for j in range(ny):
                if np.isnan(height_grid[i,j]):
                    continue
                color, b = height_to_color(height_grid[i,j])
                if b != band:
                    continue

                # MIRROIR → inversion axe X
                x0 = (nx - i - 1) * scale
                y0 = (ny - j - 1) * scale

                dwg.add(dwg.rect(
                    insert=(x0, y0),
                    size=(scale, scale),
                    fill=svgwrite.rgb(*color),
                    stroke='none'
                ))

    dwg.save()
    print("✔ SVG généré : topdown.svg")
    sys.exit(0)


# ----------------------
# MODE PNG
# ----------------------
if OUTPUT_MODE == "png":
    img = Image.new("RGB", (nx, ny), (0,0,0))
    draw = ImageDraw.Draw(img)

    # bas → haut
    for band in range(N_BANDS):
        for i in range(nx):
            for j in range(ny):
                if np.isnan(height_grid[i,j]):
                    continue
                color, b = height_to_color(height_grid[i,j])
                if b != band:
                    continue

                # MIRROIR → inversion X
                px = (nx - i - 1)
                py = (ny - j - 1)
                draw.point((px, py), fill=color)

    big = img.resize((nx*6, ny*6), Image.NEAREST)
    big.save("topdown.png")

    print("✔ PNG généré : topdown.png")
    sys.exit(0)
