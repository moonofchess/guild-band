import random
import time
from game.utils import colorize, RED, GREEN, YELLOW, CYAN, BLUE, MAGENTA, BOLD, GRAY, BRIGHT_RED, BRIGHT_GREEN

class Monster:
    def __init__(self, name, hp, atk, defn, is_boss=False):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.defn = defn
        self.is_boss = is_boss
        self.stunned_turns = 0

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, amount):
        actual = max(1, amount - self.defn)
        self.hp = max(0, self.hp - actual)
        return actual

class CombatEngine:
    def __init__(self, mercenaries, enemies, player_resources):
        self.mercenaries = mercenaries  # List of Mercenary objects
        self.enemies = enemies          # List of Monster objects
        self.resources = player_resources
        
        self.cp = 5                     # Command Points (Starts at 5, max 10)
        self.max_cp = 10
        self.leader_action_used = False # 1 command skill per turn
        
        # Formations: frontline/backline dictionaries
        # Keys are mercenary objects, values are "전열" (Front) or "후열" (Back)
        self.formations = {}
        for merc in self.mercenaries:
            if merc.m_class in ["전사", "척후병"]:
                self.formations[merc] = "전열"
            else:
                self.formations[merc] = "후열"

    def print_battle_state(self):
        print(colorize("\n" + "=" * 25 + " 전투 상황 " + "=" * 25, BOLD + MAGENTA))
        
        # Display Enemy Party
        print(colorize("[적 파티]", BOLD + RED))
        for idx, enemy in enumerate(self.enemies):
            if enemy.is_alive():
                stun_indicator = colorize(" [기절]", YELLOW) if enemy.stunned_turns > 0 else ""
                boss_indicator = colorize(" [★보스]", BRIGHT_RED + BOLD) if enemy.is_boss else ""
                hp_bar = f"[{'#' * int(enemy.hp * 10 / enemy.max_hp)}{'-' * (10 - int(enemy.hp * 10 / enemy.max_hp))}]"
                print(f"  [{idx}] {enemy.name}{boss_indicator} - HP: {enemy.hp}/{enemy.max_hp} {hp_bar} ATK: {enemy.atk} DEF: {enemy.defn}{stun_indicator}")
            else:
                print(f"  [{idx}] {enemy.name} - " + colorize("[토벌 완료]", GRAY))
                
        print(colorize("-" * 60, GRAY))
        
        # Display Player Command Points
        cp_bar = f"CP: {self.cp}/{self.max_cp} [" + colorize("★" * self.cp, MAGENTA) + "☆" * (self.max_cp - self.cp) + "]"
        print(cp_bar)
        
        # Display Player Mercenaries
        print(colorize("[아군 파티]", BOLD + GREEN))
        for idx, merc in enumerate(self.mercenaries):
            pos = self.formations.get(merc, "후열")
            pos_disp = colorize(f"[{pos}]", CYAN if pos == "전열" else BLUE)
            
            status_desc = ""
            if "출혈" in merc.states:
                status_desc = colorize(" [출혈/행동불가]", RED + BOLD)
            elif merc.hp <= 1 and merc.hp == merc.get_max_hp():
                # safeguard
                pass
            
            # Action Points display
            ap_disp = colorize("●" * getattr(merc, "current_ap", 0), GREEN) + colorize("○" * (merc.get_max_ap() - getattr(merc, "current_ap", 0)), GRAY)
            
            print(f"  [{idx}] {pos_disp} {merc.display_status()} | AP: {ap_disp} MP: {merc.mp}/{merc.max_mp}{status_desc}")
            
        print(colorize("=" * 60, BOLD + MAGENTA))

    def check_battle_over(self):
        # Check if all enemies are dead
        if all(not e.is_alive() for e in self.enemies):
            return "WIN"
            
        # Check if all mercenaries are dead, bleeding (unable to fight), or empty
        alive_mercs = [m for m in self.mercenaries if m.hp > 1 and "출혈" not in m.states]
        if not alive_mercs:
            return "LOSE"
            
        return "CONTINUE"

    def run_combat(self):
        """Returns True if win, False if defeat/retreat."""
        # Initialize combat AP
        for m in self.mercenaries:
            m.current_ap = m.get_max_ap()
            
        turn = 1
        while True:
            state = self.check_battle_over()
            if state == "WIN":
                return self.handle_victory()
            elif state == "LOSE":
                return self.handle_defeat()

            print(colorize(f"\n◈ [턴 {turn}] 플레이어 행동 단계 ◈", BOLD + YELLOW))
            
            # Start of turn: restore CP
            self.cp = min(self.max_cp, self.cp + 2)
            self.leader_action_used = False
            
            # Initialize AP & decrement stun counters
            for m in self.mercenaries:
                if "출혈" not in m.states:
                    m.current_ap = m.get_max_ap()
                    # Tick poison / states if needed in combat, or just keep it daily. Let's keep it daily for simplicity.
            
            # Player actions loop
            while True:
                self.print_battle_state()
                print("1. 용병 행동 수행  2. 단장 지휘 스킬  3. 턴 종료  4. 도망치기")
                choice = input("명령을 선택하세요: ").strip()
                
                if choice == "1":
                    self.execute_mercenary_turn()
                elif choice == "2":
                    self.execute_leader_command()
                elif choice == "3":
                    break
                elif choice == "4":
                    # Escape chance: 50%
                    if random.random() < 0.5:
                        print(colorize("\n🏃 용병단이 연막탄을 터뜨리고 전투에서 도망쳤습니다!", YELLOW + BOLD))
                        # Lose some rations and morale
                        for m in self.mercenaries:
                            m.morale = max(0, m.morale - 15)
                        return False
                    else:
                        print(colorize("\n❌ 도망치는 데 실패했습니다! 적들이 길을 가로막습니다!", RED + BOLD))
                        break
                        
                # Check battle over after player action
                state = self.check_battle_over()
                if state != "CONTINUE":
                    break
            
            # If all enemies dead, check immediately before enemy turn
            state = self.check_battle_over()
            if state == "WIN":
                return self.handle_victory()
            elif state == "LOSE":
                return self.handle_defeat()

            # Enemy turn
            self.execute_enemy_turn()
            
            # Tick enemy stun turns
            for enemy in self.enemies:
                if enemy.stunned_turns > 0:
                    enemy.stunned_turns -= 1
                    
            turn += 1

    def execute_mercenary_turn(self):
        # Select active mercenary
        active_mercs = [m for m in self.mercenaries if "출혈" not in m.states and m.current_ap > 0]
        if not active_mercs:
            print(colorize("행동 가능한 용병이 없습니다. 턴을 종료하세요.", RED))
            return
            
        print("\n행동할 용병을 선택하세요:")
        for idx, m in enumerate(self.mercenaries):
            status = " (행동 불가)" if "출혈" in m.states else f" (AP: {m.current_ap}/{m.get_max_ap()})"
            print(f"[{idx}] {m.name} ({m.m_class}){status}")
            
        try:
            m_idx = int(input("용병 번호: ").strip())
            if m_idx < 0 or m_idx >= len(self.mercenaries):
                print(colorize("올바르지 않은 용병 번호입니다.", RED))
                return
            merc = self.mercenaries[m_idx]
            if "출혈" in merc.states:
                print(colorize("출혈 상태의 용병은 행동할 수 없습니다!", RED))
                return
            if merc.current_ap <= 0:
                print(colorize("행동력이 부족합니다.", RED))
                return
        except ValueError:
            print(colorize("숫자를 입력하세요.", RED))
            return

        # Select Skill
        print(f"\n[{merc.name}]의 행동을 선택하세요:")
        print(f"1. 일반 공격 (AP 1) - 단일 대상 공격")
        print(f"2. 직업 스킬: {merc.get_skill_name()} ({merc.get_skill_desc()})")
        print(f"3. 취소")
        
        act = input("행동 선택: ").strip()
        if act == "1":
            # Target selection
            alive_enemies = [e for e in self.enemies if e.is_alive()]
            print("\n공격할 대상을 선택하세요:")
            for idx, e in enumerate(self.enemies):
                if e.is_alive():
                    print(f"[{idx}] {e.name} (HP: {e.hp}/{e.max_hp})")
            try:
                e_idx = int(input("대상 번호: ").strip())
                if e_idx < 0 or e_idx >= len(self.enemies) or not self.enemies[e_idx].is_alive():
                    print(colorize("올바르지 않은 대상입니다.", RED))
                    return
                target = self.enemies[e_idx]
            except ValueError:
                return
                
            # Perform attack
            merc.current_ap -= 1
            # Check hit chance
            if random.random() * 100 > merc.get_hit_chance():
                print(colorize(f"💨 {merc.name}의 공격이 빗나갔습니다!", GRAY))
            else:
                # Normal damage formula
                dmg = merc.get_atk()
                # Apply high morale crit
                is_crit = False
                if merc.morale >= 70 and random.random() < 0.25:
                    dmg = int(dmg * 1.5)
                    is_crit = True
                
                # Check Hidden trait pierce
                if merc.is_awakened and merc.hidden_trait == "오라 발현의 씨앗":
                    # Ignore defense completely
                    dmg_dealt = target.take_damage(dmg + target.defn) 
                else:
                    dmg_dealt = target.take_damage(dmg)
                    
                crit_msg = colorize(" ★치명타!★", BRIGHT_YELLOW + BOLD) if is_crit else ""
                print(colorize(f"⚔️ {merc.name}이(가) {target.name}에게 {dmg_dealt}의 물리 피해를 입혔습니다!{crit_msg}", GREEN))
                
        elif act == "2":
            # Class specific skills
            if merc.m_class == "전사":
                # AP 2, 40% stun
                if merc.current_ap < 2:
                    print(colorize("AP가 부족합니다.", RED))
                    return
                alive_enemies = [e for e in self.enemies if e.is_alive()]
                print("\n공격할 대상을 선택하세요:")
                for idx, e in enumerate(self.enemies):
                    if e.is_alive():
                        print(f"[{idx}] {e.name} (HP: {e.hp}/{e.max_hp})")
                try:
                    e_idx = int(input("대상 번호: ").strip())
                    if e_idx < 0 or e_idx >= len(self.enemies) or not self.enemies[e_idx].is_alive():
                        return
                    target = self.enemies[e_idx]
                except ValueError:
                    return
                    
                merc.current_ap -= 2
                dmg = int(merc.get_atk() * 1.2)
                
                if merc.is_awakened and merc.hidden_trait == "오라 발현의 씨앗":
                    dmg_dealt = target.take_damage(dmg + target.defn)
                else:
                    dmg_dealt = target.take_damage(dmg)
                    
                print(colorize(f"🛡️ [방패 충격] {merc.name}이(가) 방패로 {target.name}을 후려쳐 {dmg_dealt}의 물리 피해를 입혔습니다!", BRIGHT_GREEN))
                
                # Stun check
                if random.random() < 0.40:
                    target.stunned_turns = max(target.stunned_turns, 1)
                    print(colorize(f"💫 {target.name}이(가) 1턴간 [기절] 상태에 빠졌습니다!", YELLOW))
                    
            elif merc.m_class == "척후병":
                # AP 2, ignore 50% defense
                if merc.current_ap < 2:
                    print(colorize("AP가 부족합니다.", RED))
                    return
                print("\n급소 찌르기 대상을 선택하세요:")
                for idx, e in enumerate(self.enemies):
                    if e.is_alive():
                        print(f"[{idx}] {e.name} (HP: {e.hp}/{e.max_hp})")
                try:
                    e_idx = int(input("대상 번호: ").strip())
                    if e_idx < 0 or e_idx >= len(self.enemies) or not self.enemies[e_idx].is_alive():
                        return
                    target = self.enemies[e_idx]
                except ValueError:
                    return
                    
                merc.current_ap -= 2
                
                # Calculate damage ignoring 50% defense
                orig_def = target.defn
                target.defn = int(orig_def * 0.5)
                dmg = int(merc.get_atk() * 1.4)
                
                # Shadow Raider ap chance check
                free_ap = False
                if merc.is_awakened and merc.hidden_trait == "바람의 인도자":
                    if random.random() < 0.3:
                        free_ap = True
                        merc.current_ap += 2
                        
                dmg_dealt = target.take_damage(dmg)
                target.defn = orig_def
                
                free_msg = colorize(" [바람의 가호로 AP를 소모하지 않았습니다!]", MAGENTA + BOLD) if free_ap else ""
                print(colorize(f"🗡️ [급소 찌르기] {merc.name}이(가) {target.name}의 급소를 꿰뚫어 {dmg_dealt}의 방어 무시 피해를 입혔습니다!{free_msg}", BRIGHT_GREEN))
                
            elif merc.m_class == "마법사":
                # AP 3, MP 15, AOE elemental damage
                if merc.current_ap < 3:
                    print(colorize("AP가 부족합니다. (필요 AP: 3)", RED))
                    return
                mp_cost = 15
                if merc.is_awakened and merc.hidden_trait == "마나 폭풍의 눈":
                    mp_cost = int(mp_cost * 0.7)
                if merc.mp < mp_cost:
                    print(colorize(f"MP가 부족합니다. (필요 MP: {mp_cost})", RED))
                    return
                    
                merc.current_ap -= 3
                merc.mp -= mp_cost
                
                # Deal damage to all alive enemies
                mult = 1.7 if (merc.is_awakened and merc.hidden_trait == "마나 폭풍의 눈") else 1.2
                dmg = int(merc.get_atk() * mult)
                
                print(colorize(f"🔥 [화염 폭발] {merc.name}이(가) 주문을 캐스팅하여 전장을 화염으로 뒤덮었습니다!", BRIGHT_GREEN))
                for enemy in self.enemies:
                    if enemy.is_alive():
                        if merc.is_awakened and merc.hidden_trait == "마나 폭풍의 눈":
                            # Ignores magic def
                            dmg_dealt = enemy.take_damage(dmg + enemy.defn)
                        else:
                            dmg_dealt = enemy.take_damage(dmg)
                        print(f"  └ {enemy.name}에게 {dmg_dealt}의 마법 피해를 입혔습니다!")
                        
            elif merc.m_class == "사제":
                # AP 2, MP 10, Heal + status cure
                if merc.current_ap < 2:
                    print(colorize("AP가 부족합니다. (필요 AP: 2)", RED))
                    return
                mp_cost = 10
                if merc.mp < mp_cost:
                    print(colorize(f"MP가 부족합니다. (필요 MP: {mp_cost})", RED))
                    return
                    
                print("\n치유할 대상을 선택하세요:")
                for idx, m in enumerate(self.mercenaries):
                    print(f"[{idx}] {m.name} (HP: {m.hp}/{m.get_max_hp()})")
                try:
                    m_idx = int(input("대상 번호: ").strip())
                    if m_idx < 0 or m_idx >= len(self.mercenaries):
                        return
                    target = self.mercenaries[m_idx]
                except ValueError:
                    return
                    
                merc.current_ap -= 2
                merc.mp -= mp_cost
                
                mult = 2.0
                if merc.is_awakened and merc.hidden_trait == "성흔의 인장":
                    mult = 3.0
                    
                heal_amt = int(merc.get_atk() * mult)
                
                # Check priest trait
                if merc.positive_trait == "성자":
                    heal_amt = int(heal_amt * 1.3)
                    
                target.hp = min(target.get_max_hp(), target.hp + heal_amt)
                
                # Remove poisons and curses in combat!
                cured = []
                if "독" in target.states:
                    target.states.remove("독")
                    cured.append("독")
                if "저주" in target.states:
                    target.states.remove("저주")
                    cured.append("저주")
                    
                cure_msg = f" ({', '.join(cured)} 정화 완료)" if cured else ""
                print(colorize(f"✨ [성스러운 치유] {merc.name}이(가) {target.name}의 상처를 치료해 체력을 {heal_amt} 회복시켰습니다!{cure_msg}", BRIGHT_GREEN))

    def execute_leader_command(self):
        if self.leader_action_used:
            print(colorize("⚠️ 지휘 스킬은 턴당 1회만 사용 가능합니다!", RED))
            return
            
        print("\n=== 단장 지휘 스킬 ===")
        print(f"1. [일제 사격 명령] (CP 3) - 아군 전체가 공격력 버프(+50%)를 받고 단일 적을 즉시 일제 사격합니다.")
        print(f"2. [사기 진작] (CP 2) - 아군 전체 사기 +20, 행동력(AP) +2를 즉시 획득합니다.")
        print(f"3. [마력 간섭] (CP 4) - 강력한 간섭으로 모든 적을 1턴 동안 [기절]시킵니다.")
        print(f"4. 취소")
        
        choice = input("사용할 지휘 스킬: ").strip()
        if choice == "1":
            if self.cp < 3:
                print(colorize("CP가 부족합니다.", RED))
                return
            # Target selection
            print("\n일제 사격을 가할 적을 선택하세요:")
            for idx, e in enumerate(self.enemies):
                if e.is_alive():
                    print(f"[{idx}] {e.name} (HP: {e.hp}/{e.max_hp})")
            try:
                e_idx = int(input("대상 번호: ").strip())
                if e_idx < 0 or e_idx >= len(self.enemies) or not self.enemies[e_idx].is_alive():
                    return
                target = self.enemies[e_idx]
            except ValueError:
                return
                
            self.cp -= 3
            self.leader_action_used = True
            
            print(colorize(f"\n📢 [단장의 일제 사격 명령!] 모든 아군이 {target.name}에게 즉시 화력을 쏟아붓습니다!", MAGENTA + BOLD))
            
            for merc in self.mercenaries:
                if "출혈" not in merc.states:
                    # Deal base damage
                    dmg = int(merc.get_atk() * 1.5)
                    # Defense ignore for Seed Vanguard
                    if merc.is_awakened and merc.hidden_trait == "오라 발현의 씨앗":
                        dmg_dealt = target.take_damage(dmg + target.defn)
                    else:
                        dmg_dealt = target.take_damage(dmg)
                    print(f"  └ {merc.name}의 일격! {target.name}에게 {dmg_dealt}의 물리 피해!")
                    
        elif choice == "2":
            if self.cp < 2:
                print(colorize("CP가 부족합니다.", RED))
                return
                
            self.cp -= 2
            self.leader_action_used = True
            
            print(colorize("\n📢 [단장의 사기 진작!] 단장의 외침이 절망에 싸인 용병단의 영혼을 깨웁니다!", MAGENTA + BOLD))
            for merc in self.mercenaries:
                if "출혈" not in merc.states:
                    merc.morale = min(100, merc.morale + 20)
                    merc.current_ap = min(merc.get_max_ap() + 2, merc.current_ap + 2)
                    print(f"  └ {merc.name}: 사기 +20, 행동력(AP) +2 획득!")
                    
        elif choice == "3":
            if self.cp < 4:
                print(colorize("CP가 부족합니다.", RED))
                return
                
            self.cp -= 4
            self.leader_action_used = True
            
            print(colorize("\n📢 [단장의 마력 간섭!] 전장의 대기를 뒤흔드는 마력 역류로 적의 중심을 강타합니다!", MAGENTA + BOLD))
            for enemy in self.enemies:
                if enemy.is_alive():
                    enemy.stunned_turns = max(enemy.stunned_turns, 1)
                    print(f"  └ {enemy.name}이(가) 1턴간 [기절]합니다.")
                    
        elif choice == "4":
            pass

    def execute_enemy_turn(self):
        print(colorize("\n☠️ 적들의 공격 단계 ☠️", BOLD + RED))
        time.sleep(0.3)
        
        # Check stun status of enemies
        for enemy in self.enemies:
            if not enemy.is_alive():
                continue
                
            if enemy.stunned_turns > 0:
                print(colorize(f"  └ {enemy.name}은(는) 기절 상태여서 행동하지 못합니다.", GRAY))
                continue
                
            # Target Selection logic (Frontline vs Backline)
            # Find alive mercenaries
            alive_mercs = [m for m in self.mercenaries if m.hp > 1 and "출혈" not in m.states]
            if not alive_mercs:
                break
                
            # Filter by positions
            frontline = [m for m in alive_mercs if self.formations.get(m, "후열") == "전열"]
            backline = [m for m in alive_mercs if self.formations.get(m, "후열") == "후열"]
            
            target = None
            exposed_bonus = False
            
            if frontline:
                # 80% to target frontline, 20% to target backline
                if random.random() < 0.8:
                    target = random.choice(frontline)
                else:
                    target = random.choice(backline) if backline else random.choice(frontline)
            else:
                # Frontline empty! Target backline directly with +30% damage
                if backline:
                    target = random.choice(backline)
                    exposed_bonus = True
                else:
                    target = random.choice(alive_mercs)
                    
            if not target:
                continue

            # Check evasion
            if random.random() * 100 < target.get_eva():
                print(colorize(f"💨 {enemy.name}의 돌격! {target.name}이(가) 날렵하게 회피했습니다!", GREEN))
                continue
                
            # Deal damage
            dmg = enemy.atk
            if exposed_bonus:
                dmg = int(dmg * 1.3)  # Exposed penalty
                
            # Apply defense reduce
            defn = target.get_def()
            
            # Apply visible trait damage reduction (iron wall)
            if target.positive_trait == "철벽":
                dmg = int(dmg * (1.0 - VISIBLE_POSITIVE_TRAITS["철벽"]["dmg_red"]))
                
            damage_dealt = max(1, dmg - defn)
            
            # Apply coward morale damage
            if target.negative_trait == "겁쟁이":
                target.morale = max(0, target.morale - 10)
                
            target.hp -= damage_dealt
            
            exposed_tag = colorize(" [후열 노출!]", BRIGHT_RED) if exposed_bonus else ""
            print(colorize(f"💥 {enemy.name}이(가) {target.name}에게 {damage_dealt}의 피해를 입혔습니다!{exposed_tag}", RED))
            
            # HP check
            if target.hp <= 0:
                target.hp = 1
                target.states.append("출혈")
                print(colorize(f"🩸 [치명상] {target.name}이(가) 치명상을 입고 과다출혈 상태가 되어 쓰러졌습니다!", RED + BOLD))

    def handle_victory(self):
        print(colorize("\n👑 승리했습니다! 마수 무리를 토벌하는 데 성공했습니다! 👑", BOLD + GREEN))
        
        # Calculate rewards based on enemies
        base_exp = 0
        base_loot = 0
        base_ore = 0
        base_gold = 0
        
        for e in self.enemies:
            if e.is_boss:
                base_exp += 150
                base_loot += 15
                base_ore += 8
                base_gold += 150
            else:
                base_exp += 30
                base_loot += 3
                base_ore += 1
                base_gold += 20
                
        # Distribute EXP and rewards
        self.resources.add_resources(gold=base_gold, loot=base_loot, ore=base_ore)
        print(colorize(f"획득 전리품 ➔ 금화: +{base_gold}, 마수 부산물: +{base_loot}, 광석: +{base_ore}", BRIGHT_GREEN))
        
        # All alive/surviving mercenaries gain EXP and Morale
        for merc in self.mercenaries:
            if "출혈" not in merc.states:
                merc.morale = min(100, merc.morale + 10)
                # Gain EXP
                log = merc.gain_exp(base_exp)
                if log:
                    print(log)
                    
        return True

    def handle_defeat(self):
        print(colorize("\n💀 패배했습니다... 용병단 전원이 치명상을 입거나 퇴각했습니다.", BOLD + RED))
        # Reduce morale heavily, add injuries, lose some gold/rations
        lost_gold = int(self.resources.gold * 0.25)
        self.resources.gold -= lost_gold
        self.resources.rations = max(0, self.resources.rations - 10)
        
        print(colorize(f"패주 손실 ➔ 금화: -{lost_gold}, 식량: -10", RED))
        
        for merc in self.mercenaries:
            merc.morale = max(0, merc.morale - 30)
            if "출혈" not in merc.states:
                # Add injury
                merc.states.append("부상")
                merc.hp = max(1, int(merc.get_max_hp() * 0.2))
                print(f"🩹 {merc.name}은(는) 퇴각 중 부상을 입었습니다.")
                
        return False
