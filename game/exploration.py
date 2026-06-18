import random
import time
from game.utils import colorize, RED, GREEN, YELLOW, CYAN, BLUE, MAGENTA, BOLD, GRAY, BRIGHT_RED, BRIGHT_GREEN
from game.combat import CombatEngine, Monster

class Mission:
    def __init__(self, name, desc, difficulty, reward_gold, reward_rations, reward_loot, reward_ore):
        self.name = name
        self.desc = desc
        self.difficulty = difficulty
        self.gold = reward_gold
        self.rations = reward_rations
        self.loot = reward_loot
        self.ore = reward_ore

class ExplorationManager:
    def __init__(self, resources):
        self.resources = resources
        self.missions = [
            Mission("오염된 숲 정화", "성채 외곽의 오염된 숲에서 가축을 물어가는 고블린 무리를 소탕합니다.", 1, 120, 15, 10, 2),
            Mission("고대 마탑 유물 회수", "오래전 파괴된 제국 마탑의 폐허에서 미지의 마력핵과 유물을 찾아옵니다.", 2, 280, 25, 20, 6),
            Mission("생존자 상단 호위", "마수들에게 쫓기며 성채를 향해 다가오는 피난민 상단을 안전하게 구출 및 호위합니다.", 2, 350, 40, 15, 4),
            Mission("타락한 영주의 성채 공성전", "심연의 기운에 타락해 마수로 변한 옛 영주 바스티안을 격퇴하고 영지를 정화합니다.", 3, 700, 50, 40, 20)
        ]

    def get_enemies_for_difficulty(self, difficulty, is_boss_step=False):
        if difficulty == 1:
            return [
                Monster("오염된 고블린", 45, 10, 2),
                Monster("고블린 투척병", 35, 12, 1)
            ]
        elif difficulty == 2:
            if is_boss_step:
                return [
                    Monster("스켈레톤 수호병", 75, 15, 6),
                    Monster("리치 견습생", 60, 22, 3),
                    Monster("골렘 파편", 110, 18, 12)
                ]
            else:
                return [
                    Monster("고대 스켈레톤", 65, 14, 4),
                    Monster("배고픈 들개 마수", 55, 16, 2)
                ]
        else:  # Difficulty 3 (Boss Mission)
            if is_boss_step:
                return [
                    Monster("타락한 제국 친위대장", 120, 22, 12),
                    Monster("타락한 영주 바스티안", 320, 32, 15, is_boss=True)
                ]
            else:
                return [
                    Monster("타락한 제국 기사", 95, 20, 10),
                    Monster("심연의 그림자 사냥개", 80, 24, 5)
                ]

    def run_mission(self, mission_idx, squad):
        """Run the selected mission with the dispatched squad."""
        if mission_idx < 0 or mission_idx >= len(self.missions):
            return False
            
        mission = self.missions[mission_idx]
        
        # Verify squad status
        if not squad:
            print(colorize("출전할 용병이 없습니다!", RED))
            return False
            
        for m in squad:
            if "출혈" in m.states:
                print(colorize(f"출혈 상태인 {m.name}은(는) 출전할 수 없습니다!", RED))
                return False
                
        print(colorize(f"\n🚀 {mission.name} (난이도: {'★' * mission.difficulty}) 탐색을 시작합니다!", BOLD + CYAN))
        print(colorize(f"의뢰 요약: {mission.desc}", GRAY))
        
        # Exploration variables
        progress = 0
        total_steps = 4
        
        # Temp loot gathered during this run (only given on success or partial evacuation)
        gathered_gold = 0
        gathered_loot = 0
        gathered_ore = 0
        
        # Scout presence checker
        has_scout = any(m.m_class == "척후병" for m in squad)
        
        for step in range(1, total_steps + 1):
            progress += 25
            print(colorize(f"\n[탐색 진행도: {progress}%]", BOLD + YELLOW))
            time.sleep(0.5)
            
            # Determine step event
            # Step 4 is always the final battle / boss
            if step == total_steps:
                print(colorize("☠️ [마지막 구역 진입] 마수의 본거지에 도달했습니다!", RED + BOLD))
                enemies = self.get_enemies_for_difficulty(mission.difficulty, is_boss_step=True)
                
                engine = CombatEngine(squad, enemies, self.resources)
                success = engine.run_combat()
                if not success:
                    # Wipeout/Retreat penalty already handled inside combat
                    return False
                break
                
            # Random events for step 1, 2, 3
            event_type = random.choices(
                ["combat", "dilemma", "trap", "shelter"], 
                weights=[40, 25, 20, 15]
            )[0]
            
            if event_type == "combat":
                print(colorize("⚔️ 마수 무리와 조우했습니다! 전투 태세를 취하십시오!", RED))
                enemies = self.get_enemies_for_difficulty(mission.difficulty, is_boss_step=False)
                engine = CombatEngine(squad, enemies, self.resources)
                success = engine.run_combat()
                if not success:
                    return False
                    
            elif event_type == "dilemma":
                print(colorize("\n💎 [전리품 상자 발견] 던전 모퉁이에서 고대 병기 상자를 발견했습니다!", BRIGHT_YELLOW + BOLD))
                print("하지만 상자를 열려면 소음이 발생하여 주변 마수의 습격을 받을 것입니다.")
                print("1. 상자를 강제로 열어 파밍한다 (전투 돌입, 승리 시 광석 +3, 부산물 +8, 금화 +80 보너스)")
                print("2. 위험을 피해 안전하게 우회한다 (아무 일도 일어나지 않음)")
                
                choice = input("선택하세요: ").strip()
                if choice == "1":
                    print(colorize("상자를 여는 도중 마수들이 들이닥쳤습니다!", RED))
                    enemies = self.get_enemies_for_difficulty(mission.difficulty, is_boss_step=False)
                    engine = CombatEngine(squad, enemies, self.resources)
                    success = engine.run_combat()
                    if not success:
                        return False
                    # Victory adds extra loot
                    gathered_gold += 80
                    gathered_loot += 8
                    gathered_ore += 3
                    print(colorize("상자를 열어 추가 전리품을 챙겼습니다! (금화 +80, 부산물 +8, 광석 +3)", BRIGHT_GREEN))
                else:
                    print(colorize("상자를 지나쳐 안전한 길로 전진했습니다.", GRAY))
                    
            elif event_type == "trap":
                print(colorize("\n⚠️ [함정 조우] 전방에 마력 폭발 함정 혹은 독가스 분출구가 매설되어 있습니다!", BRIGHT_RED))
                
                if has_scout:
                    # Find a scout
                    scout_merc = next(m for m in squad if m.m_class == "척후병")
                    # Easy bypass
                    print(colorize(f"🎯 [척후병 활약] 척후병 {scout_merc.name}이(가) 노련한 손길로 함정을 안전하게 해제했습니다! (경험치 획득)", GREEN))
                    scout_merc.gain_exp(25)
                else:
                    print("분대에 함정을 해제할 척후병이 없습니다!")
                    print("1. 전사(Vanguard)가 방패로 충격을 받아내며 전진한다 (전사 HP -30)")
                    print("2. 조심스럽게 돌파를 시도한다 (모든 대원 30% 확률로 [부상] 또는 [독] 상태이상이 부여됩니다)")
                    
                    choice = input("선택하세요: ").strip()
                    if choice == "1":
                        vanguards = [m for m in squad if m.m_class == "전사"]
                        if vanguards:
                            vg = random.choice(vanguards)
                            vg.hp = max(1, vg.hp - 30)
                            print(colorize(f"🛡️ 전사 {vg.name}이(가) 방패를 세워 폭발을 막았습니다. {vg.name}의 HP가 30 감소했습니다.", RED))
                        else:
                            print(colorize("분대에 전사가 없습니다! 돌파 시도를 강행합니다.", RED))
                            self._apply_trap_fail(squad)
                    else:
                        self._apply_trap_fail(squad)
                        
            elif event_type == "shelter":
                print(colorize("\n🏕️ [안전지대 발견] 오염도가 낮은 안전한 은신처를 발견했습니다.", BRIGHT_GREEN))
                print("1. 식량 8을 소모하여 전원의 체력을 30 회복하고 사기를 10 보충한다.")
                print("2. 마력 파장을 감지해 휴식 대신 장비를 다듬는다 (아무 일도 일어나지 않음)")
                
                choice = input("선택하세요: ").strip()
                if choice == "1":
                    if self.resources.rations >= 8:
                        self.resources.rations -= 8
                        for m in squad:
                            if "출혈" not in m.states:
                                m.hp = min(m.get_max_hp(), m.hp + 30)
                                m.morale = min(100, m.morale + 10)
                        print(colorize("모닥불을 피우고 식량을 배급받아 휴식을 취했습니다. (HP +30, 사기 +10, 식량 -8)", GREEN))
                    else:
                        print(colorize("식량이 부족하여 휴식을 취할 수 없었습니다!", RED))
                else:
                    print(colorize("경계를 늦추지 않고 즉시 나아갔습니다.", GRAY))

        # Mission completed successfully!
        print(colorize(f"\n🎉 축하합니다! {mission.name} 의뢰를 성공적으로 완료했습니다! 🎉", BOLD + GREEN))
        
        # Give rewards
        success_gold = mission.gold + gathered_gold
        success_loot = mission.loot + gathered_loot
        success_ore = mission.ore + gathered_ore
        
        self.resources.add_resources(
            gold=success_gold, 
            rations=mission.rations, 
            loot=success_loot, 
            ore=success_ore
        )
        
        print(colorize(f"클리어 보상 ➔ 금화: +{success_gold}, 식량: +{mission.rations}, 부산물: +{success_loot}, 광석: +{success_ore}", BRIGHT_GREEN))
        
        # Extra morale for clear
        for m in squad:
            if "출혈" not in m.states:
                m.morale = min(100, m.morale + 15)
                # Small daily cleanup: reduce corruption slightly on successful cleanses
                if mission.difficulty == 3:
                    m.corruption = max(0, m.corruption - 15)
                    
        return True

    def _apply_trap_fail(self, squad):
        print(colorize("함정이 격발되거나 독가스가 누출되었습니다!", RED))
        for m in squad:
            if "출혈" not in m.states:
                if random.random() < 0.5:
                    status = random.choice(["부상", "독"])
                    if status not in m.states:
                        m.states.append(status)
                        print(colorize(f"☠️ {m.name}이(가) 함정에 휘말려 [{status}] 상태에 걸렸습니다!", RED))
                else:
                    dmg = int(m.get_max_hp() * 0.15)
                    m.hp = max(1, m.hp - dmg)
                    print(colorize(f"💥 {m.name}이(가) 폭발 파편으로 {dmg}의 피해를 입었습니다.", RED))
