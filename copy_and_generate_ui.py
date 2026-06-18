import os
import shutil
import base64
from PIL import Image, ImageDraw

# Paths
ART_DIR = r"C:\Users\Admin\.gemini\antigravity\brain\29d3c65f-d037-4dba-b34c-8193a27dc0cc"
ASSETS_DIR = r"c:\gem\web\assets"

# 1. Copy generated images from artifacts folder
COPY_MAP = {
    "scout_spritesheet_1781763132669.png": "char_scout_sheet.png",
    "magic_array_bg_1781763145490.png": "bg_magic_array.png",
    "tavern_bg_1781763158735.png": "bg_tavern.png",
    "sanctum_bg_1781763170807.png": "bg_sanctum.png",
    "blacksmith_bg_1781763186114.png": "bg_blacksmith.png",
    "battle_ruins_bg_1781763197984.png": "bg_battle_ruins.png",
    "battle_dungeon_bg_1781763210904.png": "bg_battle_dungeon.png",
    "campfire_bg_1781763224481.png": "bg_event_campfire.png",
    
    # Copy from previous session's artifacts
    "bg_castle_ruined_1781760260588.png": "bg_base_ruined.png",
    "bg_corrupted_forest_1781760281595.png": "bg_battle_forest.png",
    "vanguard_attack_spritesheet_1781760850760.png": "char_vanguard_sheet.png"
}

for src_name, dest_name in COPY_MAP.items():
    src_path = os.path.join(ART_DIR, src_name)
    dest_path = os.path.join(ASSETS_DIR, dest_name)
    if os.path.exists(src_path):
        shutil.copy(src_path, dest_path)
        print(f"Copied {src_name} to {dest_name}")
    else:
        print(f"WARNING: Source {src_name} not found!")

# 2. Programmatically generate UI components and simple icons
print("Generating UI components...")

def make_icon_mp():
    # Blue potion bottle (32x32)
    img = Image.new("RGBA", (32, 32), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # Draw glass neck
    draw.rectangle([13, 4, 18, 9], fill=(200, 200, 200, 255), outline=(50, 50, 50, 255))
    # Draw bottle body
    draw.ellipse([8, 10, 23, 27], fill=(0, 0, 220, 255), outline=(50, 50, 50, 255))
    # Liquid surface shine
    draw.ellipse([11, 13, 20, 16], fill=(100, 150, 255, 255))
    img.save(os.path.join(ASSETS_DIR, "icon_mp.png"))

def make_icon_atk():
    # Crossed swords (32x32)
    img = Image.new("RGBA", (32, 32), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # Sword 1 (top-left to bottom-right)
    draw.line([4, 4, 27, 27], fill=(180, 180, 180, 255), width=2)
    draw.rectangle([25, 25, 28, 28], fill=(139, 69, 19, 255)) # Hilt
    # Sword 2 (top-right to bottom-left)
    draw.line([27, 4, 4, 27], fill=(180, 180, 180, 255), width=2)
    draw.rectangle([3, 25, 6, 28], fill=(139, 69, 19, 255)) # Hilt
    img.save(os.path.join(ASSETS_DIR, "icon_atk.png"))

def make_icon_def():
    # Iron shield (32x32)
    img = Image.new("RGBA", (32, 32), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # Shield shape
    draw.polygon([(6,6), (25,6), (25,16), (16,27), (6,16)], fill=(120, 120, 120, 255), outline=(40, 40, 40, 255))
    # Gold trim inner
    draw.polygon([(9,8), (22,8), (22,15), (16,23), (9,15)], fill=(80, 80, 80, 255))
    img.save(os.path.join(ASSETS_DIR, "icon_def.png"))

def make_icon_morale():
    # Flame (32x32)
    img = Image.new("RGBA", (32, 32), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # Draw fire layers
    draw.ellipse([8, 10, 23, 27], fill=(255, 69, 0, 255)) # Red outer
    draw.ellipse([11, 14, 20, 25], fill=(255, 140, 0, 255)) # Orange mid
    draw.ellipse([13, 18, 18, 23], fill=(255, 215, 0, 255)) # Yellow inner
    img.save(os.path.join(ASSETS_DIR, "icon_morale.png"))

def make_icon_corruption():
    # Glowing purple eye (32x32)
    img = Image.new("RGBA", (32, 32), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # Eye white (but purple)
    draw.ellipse([4, 8, 27, 23], fill=(75, 0, 130, 255), outline=(20, 0, 40, 255))
    # Pupil
    draw.ellipse([12, 10, 19, 21], fill=(186, 85, 211, 255))
    # Slit pupil center
    draw.line([16, 12, 16, 19], fill=(0, 0, 0, 255), width=2)
    img.save(os.path.join(ASSETS_DIR, "icon_corruption.png"))

def make_icon_trait_good():
    # Golden border (64x64)
    img = Image.new("RGBA", (64, 64), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([2, 2, 61, 61], outline=(255, 215, 0, 255), width=3)
    draw.rectangle([5, 5, 58, 58], outline=(218, 165, 32, 255), width=1)
    img.save(os.path.join(ASSETS_DIR, "icon_trait_good.png"))

def make_icon_trait_bad():
    # Red cracked border (64x64)
    img = Image.new("RGBA", (64, 64), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([2, 2, 61, 61], outline=(220, 20, 60, 255), width=3)
    # Draw cracks
    draw.line([2, 10, 12, 15], fill=(220, 20, 60, 255), width=2)
    draw.line([61, 45, 50, 40], fill=(220, 20, 60, 255), width=2)
    img.save(os.path.join(ASSETS_DIR, "icon_trait_bad.png"))

def make_ui_panel_bg():
    # Parchment box (128x128)
    img = Image.new("RGBA", (128, 128), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # Background fill
    draw.rectangle([0, 0, 127, 127], fill=(245, 222, 179, 255), outline=(101, 67, 33, 255), width=4)
    # Corner rivets
    for cx, cy in [(8, 8), (119, 8), (8, 119), (119, 119)]:
        draw.ellipse([cx-3, cy-3, cx+3, cy+3], fill=(80, 80, 80, 255), outline=(40, 40, 40, 255))
    img.save(os.path.join(ASSETS_DIR, "ui_panel_bg.png"))

def make_ui_buttons():
    # Normal state button
    img_normal = Image.new("RGBA", (64, 32), (0,0,0,0))
    draw_n = ImageDraw.Draw(img_normal)
    draw_n.rectangle([0, 0, 63, 31], fill=(128, 128, 128, 255), outline=(64, 64, 64, 255), width=2)
    img_normal.save(os.path.join(ASSETS_DIR, "ui_button_normal.png"))
    
    # Hover state button
    img_hover = Image.new("RGBA", (64, 32), (0,0,0,0))
    draw_h = ImageDraw.Draw(img_hover)
    draw_h.rectangle([0, 0, 63, 31], fill=(160, 160, 160, 255), outline=(0, 255, 255, 255), width=2)
    img_hover.save(os.path.join(ASSETS_DIR, "ui_button_hover.png"))
    
    # Click state button
    img_click = Image.new("RGBA", (64, 32), (0,0,0,0))
    draw_c = ImageDraw.Draw(img_click)
    draw_c.rectangle([0, 0, 63, 31], fill=(96, 96, 96, 255), outline=(32, 32, 32, 255), width=2)
    img_click.save(os.path.join(ASSETS_DIR, "ui_button_click.png"))

def make_ui_cursor():
    # Arrow cursor (32x32) pointing down
    img = Image.new("RGBA", (32, 32), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # Draw triangle head pointing down
    draw.polygon([(16, 28), (4, 12), (28, 12)], fill=(255, 0, 0, 255), outline=(0,0,0,255))
    # Draw arrow body stem
    draw.rectangle([13, 2, 19, 12], fill=(255, 0, 0, 255), outline=(0,0,0,255))
    img.save(os.path.join(ASSETS_DIR, "ui_cursor.png"))

def make_ui_hp_bars():
    # HP Bar Fill
    img_fill = Image.new("RGBA", (64, 16), (0,0,0,0))
    draw_f = ImageDraw.Draw(img_fill)
    draw_f.rectangle([0, 0, 63, 15], fill=(220, 20, 60, 255))
    img_fill.save(os.path.join(ASSETS_DIR, "ui_hp_bar_fill.png"))
    
    # HP Bar BG
    img_bg = Image.new("RGBA", (64, 16), (0,0,0,0))
    draw_b = ImageDraw.Draw(img_bg)
    draw_b.rectangle([0, 0, 63, 15], fill=(64, 64, 64, 255), outline=(0, 0, 0, 255), width=1)
    img_bg.save(os.path.join(ASSETS_DIR, "ui_hp_bar_bg.png"))

def make_vfx_slash():
    # Slash VFX arc (64x64)
    img = Image.new("RGBA", (64, 64), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # Red slash curve
    draw.arc([10, 10, 54, 54], start=45, end=225, fill=(255, 50, 50, 255), width=4)
    # White center curve
    draw.arc([10, 10, 54, 54], start=60, end=210, fill=(255, 255, 255, 255), width=2)
    img.save(os.path.join(ASSETS_DIR, "vfx_slash.png"))

make_icon_mp()
make_icon_atk()
make_icon_def()
make_icon_morale()
make_icon_corruption()
make_icon_trait_good()
make_icon_trait_bad()
make_ui_panel_bg()
make_ui_buttons()
make_ui_cursor()
make_ui_hp_bars()
make_vfx_slash()

print("All missing assets created successfully!")
