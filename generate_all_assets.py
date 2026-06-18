import os
import requests
import json
import base64
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = '0933c226-0065-4f9d-aca9-79d97716b72b'
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

ASSETS_DIR = os.path.join('web', 'assets')
os.makedirs(ASSETS_DIR, exist_ok=True)

# List of assets to generate
# Mode: "pixflux" or "pixen"
# Details: { "prompt": str, "size": (width, height), "no_bg": bool }
ASSETS = {
    # 1. Backgrounds (16:9 ratio)
    "bg_base_ruined.png": {
        "mode": "pixen",
        "prompt": "ruined dark castle fortress exterior, crumbling stone walls, eerie desolate polluted purple sky, dark fantasy, gothic pixel art background, 16:9 side view",
        "size": (512, 288),
        "no_bg": False
    },
    "bg_base_restored.png": {
        "mode": "pixen",
        "prompt": "restored strong stone castle fortress exterior, banners waving, hopeful clear blue sky with white clouds, dark fantasy, gothic pixel art background, 16:9 side view",
        "size": (512, 288),
        "no_bg": False
    },
    "bg_hall.png": {
        "mode": "pixen",
        "prompt": "lord chamber castle throne hall interior, massive war table with dusty empire map, iron candlesticks with burning candles, dark fantasy, gothic pixel art background, 16:9 view",
        "size": (512, 288),
        "no_bg": False
    },
    "bg_magic_array.png": {
        "mode": "pixen",
        "prompt": "magic portal chamber interior, glowing blue magical rune circle on stone floor, hovering crystals, glowing mist, dark fantasy, gothic pixel art background, 16:9 view",
        "size": (512, 288),
        "no_bg": False
    },
    "bg_tavern.png": {
        "mode": "pixen",
        "prompt": "cozy tavern inn interior, roaring warm stone fireplace, wooden tables and oak ale barrels, lively atmosphere, dark fantasy, gothic pixel art background, 16:9 view",
        "size": (512, 288),
        "no_bg": False
    },
    "bg_sanctum.png": {
        "mode": "pixen",
        "prompt": "holy cathedral sanctum temple interior, half-broken marble goddess statue, beams of golden divine light from stained glass ceiling, dark fantasy, gothic pixel art background, 16:9 view",
        "size": (512, 288),
        "no_bg": False
    },
    "bg_blacksmith.png": {
        "mode": "pixen",
        "prompt": "castle blacksmith forge interior, glowing hot coal furnace, steel anvil, weapons rack with blades, dark fantasy, gothic pixel art background, 16:9 view",
        "size": (512, 288),
        "no_bg": False
    },
    "bg_battle_forest.png": {
        "mode": "pixen",
        "prompt": "corrupted dark forest path, twisted gnarled trees with eyes, glowing poisonous purple mist on ground, 2d side-scroller battle stage, dark fantasy pixel art, 16:9 view",
        "size": (512, 288),
        "no_bg": False
    },
    "bg_battle_ruins.png": {
        "mode": "pixen",
        "prompt": "ruined fantasy city street, debris of stone pillars, smoldering fires in distance, cloudy ash sky, 2d side-scroller battle stage, dark fantasy pixel art, 16:9 view",
        "size": (512, 288),
        "no_bg": False
    },
    "bg_battle_dungeon.png": {
        "mode": "pixen",
        "prompt": "ancient crypt dungeon corridor, dark damp brick walls, lit wall torches, skulls on floor, iron gates, 2d side-scroller battle stage, dark fantasy pixel art, 16:9 view",
        "size": (512, 288),
        "no_bg": False
    },
    "bg_event_campfire.png": {
        "mode": "pixen",
        "prompt": "campsite in dark woods at night, burning bright campfire wood fire, tree stumps around, starry night sky, cozy safety, dark fantasy pixel art background, 16:9 view",
        "size": (512, 288),
        "no_bg": False
    },

    # 2. Player Characters (Sprite Sheets & Portraits)
    "char_vanguard_sheet.png": {
        "mode": "pixflux",
        "prompt": "heavy plate armored knight vanguard warrior, steel sword and shield. pixel art spritesheet containing horizontal animation frame sequences for idle, move, attack, hit, death. transparent background",
        "size": (256, 128),
        "no_bg": True
    },
    "portrait_vanguard.png": {
        "mode": "pixflux",
        "prompt": "heavy plate armored knight face portrait, glowing red eyes under visor, dark fantasy gothic style, game UI portrait icon, pixel art, transparent background",
        "size": (64, 64),
        "no_bg": True
    },
    "char_scout_sheet.png": {
        "mode": "pixflux",
        "prompt": "stealth scout rogue character wearing dark leather hood and cloak, dual daggers. pixel art spritesheet containing horizontal animation frame sequences for idle, move, attack, hit, death. transparent background",
        "size": (256, 128),
        "no_bg": True
    },
    "portrait_scout.png": {
        "mode": "pixflux",
        "prompt": "leather hooded scout assassin face portrait, dark shadows covering eyes, gothic style, game UI portrait icon, pixel art, transparent background",
        "size": (64, 64),
        "no_bg": True
    },
    "char_mage_sheet.png": {
        "mode": "pixflux",
        "prompt": "old wizard mage in purple robes holding a glowing magic staff. pixel art spritesheet containing horizontal animation frame sequences for idle, move, attack, hit, death. transparent background",
        "size": (256, 128),
        "no_bg": True
    },
    "portrait_mage.png": {
        "mode": "pixflux",
        "prompt": "hooded old wizard mage face portrait, white beard, glowing blue eyes, dark fantasy style, game UI portrait icon, pixel art, transparent background",
        "size": (64, 64),
        "no_bg": True
    },
    "char_priest_sheet.png": {
        "mode": "pixflux",
        "prompt": "church priest cleric in dark religious robes holding a golden relic. pixel art spritesheet containing horizontal animation frame sequences for idle, move, attack, hit, death. transparent background",
        "size": (256, 128),
        "no_bg": True
    },
    "portrait_priest.png": {
        "mode": "pixflux",
        "prompt": "clergy priest cleric face portrait, halo motif behind head, serene look, dark fantasy style, game UI portrait icon, pixel art, transparent background",
        "size": (64, 64),
        "no_bg": True
    },

    # 3. Enemies
    "mob_goblin_sheet.png": {
        "mode": "pixflux",
        "prompt": "small green goblin monster, holding a rusted bone dagger, wearing tattered brown rags. pixel art spritesheet containing horizontal animation frame sequences for idle, move, attack, hit, death. transparent background",
        "size": (256, 128),
        "no_bg": True
    },
    "mob_skeleton_sheet.png": {
        "mode": "pixflux",
        "prompt": "undead skeleton archer warrior, glowing red eye sockets, holding a decayed wooden bow. pixel art spritesheet containing horizontal animation frame sequences for idle, move, attack, hit, death. transparent background",
        "size": (256, 128),
        "no_bg": True
    },
    "mob_inquisitor_sheet.png": {
        "mode": "pixflux",
        "prompt": "corrupted dark inquisitor fanatical cultist in red robes holding a cursed spellbook. pixel art spritesheet containing horizontal animation frame sequences for idle, move, attack, hit, death. transparent background",
        "size": (256, 128),
        "no_bg": True
    },
    "mob_golem_sheet.png": {
        "mode": "pixflux",
        "prompt": "giant horrific stitch flesh golem monster, massive stone club. pixel art spritesheet containing horizontal animation frame sequences for idle, move, attack, hit, death. transparent background",
        "size": (256, 128),
        "no_bg": True
    },

    # 4. VFX & Props
    "vfx_slash.png": {
        "mode": "pixflux",
        "prompt": "sword slash impact swipe wave effect, sharp curved line arc, red and white energy trace, game VFX, pixel art, transparent background",
        "size": (64, 64),
        "no_bg": True
    },
    "vfx_arrow.png": {
        "mode": "pixflux",
        "prompt": "single flying arrow projectile, pointed steel tip and feather fletching, pixel art game projectile, transparent background",
        "size": (32, 32),
        "no_bg": True
    },
    "vfx_fireball.png": {
        "mode": "pixflux",
        "prompt": "flying red fireball projectile and flame explosion frames spritesheet, pixel art game VFX, transparent background",
        "size": (128, 64),
        "no_bg": True
    },
    "vfx_heal.png": {
        "mode": "pixflux",
        "prompt": "sacred divine golden light ray beams casting down, sparkly holy heal effect, game spell VFX, pixel art, transparent background",
        "size": (64, 64),
        "no_bg": True
    },
    "vfx_cp_buff.png": {
        "mode": "pixflux",
        "prompt": "rising gold aura light beam column from ground, sparkly holy power up buff effect, game skill VFX, pixel art, transparent background",
        "size": (64, 64),
        "no_bg": True
    },
    "vfx_cp_strike.png": {
        "mode": "pixflux",
        "prompt": "colossal magical explosion, purple and blue energy blast eruption, game tactical spell VFX, pixel art, transparent background",
        "size": (128, 128),
        "no_bg": True
    },
    "vfx_status_stun.png": {
        "mode": "pixflux",
        "prompt": "spinning yellow stars circle dizzy stun effect, game status icon, pixel art, transparent background",
        "size": (32, 32),
        "no_bg": True
    },
    "vfx_status_poison.png": {
        "mode": "pixflux",
        "prompt": "bubbling toxic purple venom poison status effect, game status icon, pixel art, transparent background",
        "size": (32, 32),
        "no_bg": True
    },
    "vfx_status_bleed.png": {
        "mode": "pixflux",
        "prompt": "dripping crimson blood drops bleed status effect, game status icon, pixel art, transparent background",
        "size": (32, 32),
        "no_bg": True
    },
    "prop_chest_closed.png": {
        "mode": "pixflux",
        "prompt": "closed old wooden treasure chest, iron locks and corners, game loot prop, pixel art, transparent background",
        "size": (64, 64),
        "no_bg": True
    },
    "prop_chest_open.png": {
        "mode": "pixflux",
        "prompt": "open wooden treasure chest, glittering piles of gold coins and jewel gems inside, game loot prop, pixel art, transparent background",
        "size": (64, 64),
        "no_bg": True
    },
    "prop_cover_rock.png": {
        "mode": "pixflux",
        "prompt": "mossy gray granite rock boulder, battlefield cover obstacle prop, pixel art, transparent background",
        "size": (64, 64),
        "no_bg": True
    },
    "prop_cover_wall.png": {
        "mode": "pixflux",
        "prompt": "broken ruined grey brick wall structure, battlefield cover prop, pixel art, transparent background",
        "size": (64, 64),
        "no_bg": True
    },
    "prop_trap.png": {
        "mode": "pixflux",
        "prompt": "sharp metal bear claw trap open on ground, rusted steel teeth, game hazard prop, pixel art, transparent background",
        "size": (64, 64),
        "no_bg": True
    },

    # 5. UI & Icons
    "icon_gold.png": {
        "mode": "pixflux",
        "prompt": "pile of shiny gold coins, money currency icon, game UI, pixel art, transparent background",
        "size": (32, 32),
        "no_bg": True
    },
    "icon_ration.png": {
        "mode": "pixflux",
        "prompt": "cooked meat shank on bone, food ration resource icon, game UI, pixel art, transparent background",
        "size": (32, 32),
        "no_bg": True
    },
    "icon_loot.png": {
        "mode": "pixflux",
        "prompt": "glowing purple demon bone and monster leather, craft material loot icon, game UI, pixel art, transparent background",
        "size": (32, 32),
        "no_bg": True
    },
    "icon_cp.png": {
        "mode": "pixflux",
        "prompt": "ornate golden crowns with ruby gems, command points skill icon, game UI, pixel art, transparent background",
        "size": (32, 32),
        "no_bg": True
    },
    "icon_hp.png": {
        "mode": "pixflux",
        "prompt": "glowing red heart crystal, health HP stat icon, game UI, pixel art, transparent background",
        "size": (32, 32),
        "no_bg": True
    },
    "icon_mp.png": {
        "mode": "pixflux",
        "prompt": "sparkling blue magic potion flask, mana MP stat icon, game UI, pixel art, transparent background",
        "size": (32, 32),
        "no_bg": True
    },
    "icon_atk.png": {
        "mode": "pixflux",
        "prompt": "two crossed sharp steel swords, attack damage stat icon, game UI, pixel art, transparent background",
        "size": (32, 32),
        "no_bg": True
    },
    "icon_def.png": {
        "mode": "pixflux",
        "prompt": "strong solid steel wall shield, defense armor stat icon, game UI, pixel art, transparent background",
        "size": (32, 32),
        "no_bg": True
    },
    "icon_morale.png": {
        "mode": "pixflux",
        "prompt": "roaring orange fire flame, unit morale mental stat icon, game UI, pixel art, transparent background",
        "size": (32, 32),
        "no_bg": True
    },
    "icon_corruption.png": {
        "mode": "pixflux",
        "prompt": "creepy glowing purple eye of doom, corruption terror stat icon, game UI, pixel art, transparent background",
        "size": (32, 32),
        "no_bg": True
    },
    "icon_trait_good.png": {
        "mode": "pixflux",
        "prompt": "glowing golden sun border frame container, positive passive trait frame, game UI, pixel art, transparent background",
        "size": (64, 64),
        "no_bg": True
    },
    "icon_trait_bad.png": {
        "mode": "pixflux",
        "prompt": "cracked bloody red thorny border frame container, negative trait frame, game UI, pixel art, transparent background",
        "size": (64, 64),
        "no_bg": True
    },
    "ui_panel_bg.png": {
        "mode": "pixflux",
        "prompt": "brown textured old weathered gothic parchment paper background, dark border, game UI menu card, pixel art, transparent background",
        "size": (128, 128),
        "no_bg": True
    },
    "ui_button_normal.png": {
        "mode": "pixflux",
        "prompt": "stone gray medieval rectangular button, chisel borders, normal state, game UI, pixel art, transparent background",
        "size": (64, 32),
        "no_bg": True
    },
    "ui_button_hover.png": {
        "mode": "pixflux",
        "prompt": "stone gray medieval rectangular button with glowing cyan border highlights, hover state, game UI, pixel art, transparent background",
        "size": (64, 32),
        "no_bg": True
    },
    "ui_button_click.png": {
        "mode": "pixflux",
        "prompt": "dark pressed recessed gray stone rectangular button, active clicked state, game UI, pixel art, transparent background",
        "size": (64, 32),
        "no_bg": True
    },
    "ui_cursor.png": {
        "mode": "pixflux",
        "prompt": "glowing red target selector hand cursor arrow pointing downwards, turn indicator, game UI, pixel art, transparent background",
        "size": (32, 32),
        "no_bg": True
    },
    "ui_hp_bar_fill.png": {
        "mode": "pixflux",
        "prompt": "solid vibrant red textured health bar bar, HP fill, game UI, pixel art, transparent background",
        "size": (64, 16),
        "no_bg": True
    },
    "ui_hp_bar_bg.png": {
        "mode": "pixflux",
        "prompt": "empty hollow dark grey stone status bar frame slots, bar background border, game UI, pixel art, transparent background",
        "size": (64, 16),
        "no_bg": True
    }
}

def generate_asset(filename, spec):
    print(f"[{filename}] Starting generation...")
    url = f"https://api.pixellab.ai/v2/create-image-{spec['mode']}"
    
    payload = {
        "description": spec["prompt"],
        "image_size": {"width": spec["size"][0], "height": spec["size"][1]},
        "no_background": spec["no_bg"]
    }
    
    # Optional parameters for Pixen
    if spec["mode"] == "pixen":
        payload["detail"] = "highly detailed"

    max_retries = 3
    for attempt in range(max_retries):
        try:
            res = requests.post(url, headers=HEADERS, json=payload, timeout=60)
            res.raise_for_status()
            data = res.json()
            
            img_b64 = data["image"]["base64"]
            if "," in img_b64:
                img_b64 = img_b64.split(",")[1]
                
            img_data = base64.b64decode(img_b64)
            output_path = os.path.join(ASSETS_DIR, filename)
            with open(output_path, "wb") as f:
                f.write(img_data)
                
            print(f"[{filename}] Successfully generated on attempt {attempt+1}.")
            return filename, True
        except Exception as e:
            print(f"[{filename}] Attempt {attempt+1} failed: {e}")
            time.sleep(2)
            
    print(f"[{filename}] FAILED to generate after {max_retries} attempts.")
    return filename, False

def main():
    print(f"Starting batch generation of {len(ASSETS)} assets...")
    start_time = time.time()
    
    # Use ThreadPoolExecutor to run requests in parallel (limit max_workers to avoid rate limiting)
    success_count = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(generate_asset, filename, spec): filename for filename, spec in ASSETS.items()}
        for future in as_completed(futures):
            filename = futures[future]
            try:
                fn, success = future.result()
                if success:
                    success_count += 1
            except Exception as exc:
                print(f"[{filename}] generated an exception: {exc}")
                
    elapsed = time.time() - start_time
    print(f"Batch generation completed in {elapsed:.1f} seconds. Success: {success_count}/{len(ASSETS)}.")

if __name__ == "__main__":
    main()
