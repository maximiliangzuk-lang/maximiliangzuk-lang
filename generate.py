import os
import cv2
import numpy as np
from PIL import Image
from rembg import remove

RAMP = " .`:-=+*cs#%@"
COLS = 90
CHAR_W = 7.74
CHAR_H = 12.9

def build_svg():
    # 1. Bild laden & Hintergrund entfernen
    input_img = Image.open("portrait.jpg")
    img_no_bg = remove(input_img)
    
    # 2. In Graustufen umwandeln
    img_np = np.array(img_no_bg)
    if img_np.shape[2] == 4:
        # Transparenter Hintergrund wird weiß
        alpha = img_np[:, :, 3]
        gray = cv2.cvtColor(img_np[:, :, :3], cv2.COLOR_RGB2GRAY)
        gray[alpha == 0] = 255
    else:
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

    # 3. Kontrast & Schärfe optimieren (Hell-Dunkel-Kurve)
    gray = cv2.bilateralFilter(gray, 5, 75, 75)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    
    # Abdunklungskurve anwenden (v/255)^1.7 für bessere Details
    gray_norm = gray / 255.0
    gray_curved = np.power(gray_norm, 1.7) * 255.0
    gray_curved = gray_curved.astype(np.uint8)

    # 4. Auf ASCII-Raster skalieren
    h, w = gray_curved.shape
    rows = int(COLS * (h / w) * (CHAR_W / CHAR_H))
    resized = cv2.resize(gray_curved, (COLS, rows))

    # 5. SVG mit Schreibmaschinen-Animation (SMIL) bauen
    svg_width = int(COLS * CHAR_W)
    svg_height = int(rows * CHAR_H)
    
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">',
        '  <style>',
        '    text { font-family: monospace; font-size: 12.9px; fill: #ffffff; white-space: pre; }',
        '  </style>',
        f'  <rect width="100%" height="100%" fill="#0d1117"/>'
    ]

    for y in range(rows):
        line_chars = ""
        for x in range(COLS):
            val = resized[y, x]
            idx = int((val / 255.0) * (len(RAMP) - 1))
            line_chars += RAMP[idx]
        
        # Jede Zeile tippt sich verzögert ein
        delay = y * 0.08
        svg_lines.append(f'  <g transform="translate(0, {(y + 1) * CHAR_H})">')
        svg_lines.append(f'    <text>{line_chars}</text>')
        svg_lines.append(f'    <rect x="0" y="-10" width="{svg_width}" height="{CHAR_H + 2}" fill="#0d1117">')
        svg_lines.append(f'      <animate attributeName="x" from="0" to="{svg_width}" dur="0.4s" begin="{delay}s" fill="freeze" />')
        svg_lines.append(f'      <animate attributeName="width" from="{svg_width}" to="0" dur="0.4s" begin="{delay}s" fill="freeze" />')
        svg_lines.append('    </rect>')
        svg_lines.append('  </g>')

    svg_lines.append('</svg>')
    
    with open("portrait.svg", "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))

if __name__ == "__main__":
    build_svg()
  
