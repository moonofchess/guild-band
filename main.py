import sys
from game.utils import (
    colorize, RED, GREEN, YELLOW, CYAN, BLUE, MAGENTA, BOLD, GRAY, 
    BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW, BRIGHT_CYAN, 
    clear_screen, print_header, print_divider, get_input
)
from game.mercenary import Mercenary
from game.resources import ResourceManager
from game.camp import BaseCamp
from game.exploration import ExplorationManager

def display_top_bar(resources, camp, mercenaries):
    print_divider()
    res_str = (
        f"📅 [생존 {resources.day}일째]  "
        f"🪙 골드: {colorize(str(resources.gold), YELLOW)}g  "
        f"🍞 식량: {colorize(str(resources.rations), GREEN)}개  "
        f"🦴 부산물: {colorize(str(resources.monster_loot), CYAN)}개  "
        f"🪨 광석: {colorize(str(resources.ore), GRAY)}개  "
        f"👥 용병단: {len(mercenaries)}/{camp.get_max_mercenaries()}명"
    )
    print(res_str)
    print_divider()

def initialize_game():
    resources = ResourceManager()
    camp = BaseCamp()
    
    # Starting mercenaries
    # 1. Vanguard (Logan): Rank F, Cowardly, Aura seed!
    logan = Mercenary(name="로건", m_class="전사", rank="F")
    logan.positive_trait = "강인함"
    logan.negative_trait = "겁쟁이"
    logan.hidden_trait = "오라 발현의 씨앗"
    logan.is_identified = False
    
    # 2. Priest (Esther): Rank E, Optimistic
    esther = Mercenary(name="에스더", m_class="사제", rank="E")
    esther.positive_trait = "낙천적"
    esther.negative_trait = "탈영병"
    
    # 3. Scout (Kael): Rank D, Fleet-footed
    kael = Mercenary(name="카엘", m_class="척후병", rank="D")
    kael.positive_trait = "신속함"
    kael.negative_trait = "애꾸눈"
    
    mercenaries = [logan, esther, kael]
    return resources, camp, mercenaries

def show_roster_menu(resources, camp, mercenaries):
    while True:
        clear_screen()
        print_header("영주실 (Lord's Hall) - 용병단 관리")
        print(f"현재 영주실 레벨: {camp.lord_hall_level}")
        print(f"최대 고용 인원: {camp.get_max_mercenaries()}명")
        print(f"전투 분대 크기: 최대 {camp.get_max_squad_size()}명\n")
        
        print(colorize("=== [용병단 명단] ===", BOLD))
        if not mercenaries:
            print(colorize("용병이 아무도 없습니다! 즉시 용병을 고용하세요.", RED))
        else:
            for idx, merc in enumerate(mercenaries):
                print(merc.display_status(idx))
                
        print("\n1. 용병 해고하기")
        print("2. 영주실 건물 업그레이드")
        print("3. 뒤로 가기")
        
        choice = get_input("명령을 선택하세요: ", ["1", "2", "3"])
        
        if choice == "1":
            if not mercenaries:
                continue
            try:
                idx = int(input("해고할 용병 번호를 입력하세요: ").strip())
                if 0 <= idx < len(mercenaries):
                    merc = mercenaries[idx]
                    confirm = input(f"정말로 {merc.name}을(를) 해고하시겠습니까? (y/n): ").strip().lower()
                    if confirm == 'y':
                        mercenaries.pop(idx)
                        print(colorize(f"[{merc.name}]을(를) 방출했습니다.", RED))
                        input("계속하려면 엔터를 누르세요...")
                else:
                    print(colorize("올바르지 않은 번호입니다.", RED))
                    input("계속하려면 엔터를 누르세요...")
            except ValueError:
                pass
        elif choice == "2":
            success, msg = camp.upgrade_lord_hall(resources)
            print(msg)
            input("계속하려면 엔터를 누르세요...")
        elif choice == "3":
            break

def show_magic_array_menu(resources, camp, mercenaries):
    while True:
        clear_screen()
        print_header("마법 통신진 (Magic Communication Array)")
        print(f"현재 통신진 레벨: {camp.magic_array_level}\n")
        
        # Display current recruits waiting in pool
        print(colorize("=== [감지된 생존자/패잔병 신호] ===", BOLD))
        if not camp.recruits_pool:
            print(colorize("통신진 신호가 꺼져 있습니다. 신호 탐색을 먼저 실행하세요.", GRAY))
        else:
            for idx, merc in enumerate(camp.recruits_pool):
                print(merc.display_status(idx))
                print(f"   ㄴ 영입 비용: {merc.get_weekly_salary()} 골드")
                
        print("\n1. 생존자 신호 탐색 (비용: 40 골드)")
        print("2. 단장의 통찰안 발동 (비용: 15 골드 - 숨겨진 특성 스캔)")
        print("3. 용병 고용하기")
        print("4. 마법 통신진 업그레이드")
        print("5. 뒤로 가기")
        
        choice = get_input("명령을 선택하세요: ", ["1", "2", "3", "4", "5"])
        
        if choice == "1":
            success, msg = camp.roll_recruits(resources)
            print(msg)
            input("계속하려면 엔터를 누르세요...")
        elif choice == "2":
            success, msg = camp.use_insight(resources)
            print(msg)
            input("계속하려면 엔터를 누르세요...")
        elif choice == "3":
            if not camp.recruits_pool:
                print(colorize("영입할 대상이 없습니다. 먼저 탐색을 가동하세요.", RED))
                input("계속하려면 엔터를 누르세요...")
                continue
            try:
                idx = int(input("고용할 용병 번호를 입력하세요: ").strip())
                success, msg = camp.hire_recruit(idx, resources, mercenaries)
                print(msg)
                input("계속하려면 엔터를 누르세요...")
            except ValueError:
                pass
        elif choice == "4":
            success, msg = camp.upgrade_magic_array(resources)
            print(msg)
            input("계속하려면 엔터를 누르세요...")
        elif choice == "5":
            break

def show_tavern_menu(resources, camp, mercenaries):
    while True:
        clear_screen()
        print_header("주점 / 여관 (Tavern)")
        print(f"현재 주점 레벨: {camp.magic_array_level}")
        print("독주와 거친 배급식으로 용병들의 사기를 충전하고 타락 수치를 정화합니다.\n")
        
        print("1. 보리빵과 쥐고기 스프로 간소한 배급 (비용: 용병 인당 3골드, 사기 +8, 타락 -2)")
        print("2. 독주와 구운 고기 성찬 대접 (비용: 용병 인당 10골드, 사기 +25, 타락 -6)")
        print("3. 주점 건물 업그레이드")
        print("4. 뒤로 가기")
        
        choice = get_input("명령을 선택하세요: ", ["1", "2", "3", "4"])
        
        if choice == "1":
            success, msg = camp.rest_cheap(resources, mercenaries)
            print(msg)
            input("계속하려면 엔터를 누르세요...")
        elif choice == "2":
            success, msg = camp.rest_luxury(resources, mercenaries)
            print(msg)
            input("계속하려면 엔터를 누르세요...")
        elif choice == "3":
            success, msg = camp.upgrade_tavern(resources)
            print(msg)
            input("계속하려면 엔터를 누르세요...")
        elif choice == "4":
            break

def show_sanctum_menu(resources, camp, mercenaries):
    while True:
        clear_screen()
        print_header("치유의 성소 (Sanctum)")
        print(f"현재 성소 레벨: {camp.sanctum_level}\n")
        
        print(colorize("=== [치료 대상 용병 목록] ===", BOLD))
        if not mercenaries:
            print("성소에 들어갈 용병단이 비어 있습니다.")
        else:
            for idx, merc in enumerate(mercenaries):
                print(merc.display_status(idx))
                
        print("\n1. 부상 치료 (HP 만개, 부상 디버프 제거 | 비용: 30 골드, 2 부산물)")
        print("2. 독/저주 정화 (해독 및 공격력 디버프 제거 | 비용: 20 골드)")
        print("3. 출혈 긴급 지혈 (출혈 치료, 사망 방지 | 비용: 40 골드, 5 부산물)")
        print("4. 성스러운 세례 (타락 수치 30 감소 | 비용: 30 골드, 4 부산물)")
        print("5. 성소 건물 업그레이드")
        print("6. 뒤로 가기")
        
        choice = get_input("명령을 선택하세요: ", ["1", "2", "3", "4", "5", "6"])
        
        if choice in ["1", "2", "3", "4"]:
            if not mercenaries:
                continue
            try:
                m_idx = int(input("대상 용병 번호를 입력하세요: ").strip())
                if m_idx < 0 or m_idx >= len(mercenaries):
                    print(colorize("올바르지 않은 번호입니다.", RED))
                    input("계속하려면 엔터를 누르세요...")
                    continue
                merc = mercenaries[m_idx]
            except ValueError:
                continue
                
            success, msg = False, ""
            if choice == "1":
                success, msg = camp.treat_injury(merc, resources)
            elif choice == "2":
                success, msg = camp.treat_poison_curse(merc, resources)
            elif choice == "3":
                success, msg = camp.treat_bleeding(merc, resources)
            elif choice == "4":
                success, msg = camp.treat_corruption(merc, resources)
                
            print(msg)
            input("계속하려면 엔터를 누르세요...")
            
        elif choice == "5":
            success, msg = camp.upgrade_sanctum(resources)
            print(msg)
            input("계속하려면 엔터를 누르세요...")
        elif choice == "6":
            break

def show_blacksmith_menu(resources, camp, mercenaries):
    while True:
        clear_screen()
        print_header("대장간 (Blacksmith)")
        print(f"현재 대장간 레벨: {camp.blacksmith_level} (강화 한계: {camp.blacksmith_level * 2}단계)\n")
        
        print(colorize("=== [장비 강화 대상 목록] ===", BOLD))
        if not mercenaries:
            print("강화할 용병이 없습니다.")
        else:
            for idx, merc in enumerate(mercenaries):
                print(
                    f"[{idx}] {merc.name}({merc.m_class}) "
                    f"⚔️ 무기 강: {merc.weapon_level}강 (공격력+{merc.weapon_level*3}) | "
                    f"🛡️ 갑옷 강: {merc.armor_level}강 (방어력+{merc.armor_level*2})"
                )
                
        print("\n1. 무기 담금질 (공격력 강화 | 비용: [다음강화수]*8 부산물, [다음강화수]*3 광석)")
        print("2. 갑옷 덧대기 (방어력 강화 | 비용: [다음강화수]*8 부산물, [다음강화수]*3 광석)")
        print("3. 대장간 건물 업그레이드")
        print("4. 뒤로 가기")
        
        choice = get_input("명령을 선택하세요: ", ["1", "2", "3", "4"])
        
        if choice in ["1", "2"]:
            if not mercenaries:
                continue
            try:
                m_idx = int(input("대상 용병 번호를 입력하세요: ").strip())
                if m_idx < 0 or m_idx >= len(mercenaries):
                    print(colorize("올바르지 않은 번호입니다.", RED))
                    input("계속하려면 엔터를 누르세요...")
                    continue
                merc = mercenaries[m_idx]
            except ValueError:
                continue
                
            success, msg = False, ""
            if choice == "1":
                success, msg = camp.upgrade_weapon(merc, resources)
            elif choice == "2":
                success, msg = camp.upgrade_armor(merc, resources)
                
            print(msg)
            input("계속하려면 엔터를 누르세요...")
            
        elif choice == "3":
            success, msg = camp.upgrade_blacksmith(resources)
            print(msg)
            input("계속하려면 엔터를 누르세요...")
        elif choice == "4":
            break

def setup_squad_and_run(resources, camp, mercenaries):
    clear_screen()
    print_header("의뢰 수주 및 탐색 파견")
    
    # Roster check
    alive_mercs = [m for m in mercenaries if "출혈" not in m.states]
    if not alive_mercs:
        print(colorize("현재 출전할 수 있는 건강한 용병이 없습니다!", RED))
        input("계속하려면 엔터를 누르세요...")
        return
        
    # Mission selection
    manager = ExplorationManager(resources)
    print("=== [수주 가능한 의뢰] ===")
    for idx, mission in enumerate(manager.missions):
        difficulty_stars = "★" * mission.difficulty
        print(
            f"[{idx}] {colorize(mission.name, BOLD)} (난이도: {colorize(difficulty_stars, RED)})"
            f"\n    ㄴ 요약: {mission.desc}"
            f"\n    ㄴ 완료 보상: 금화 +{mission.gold}, 식량 +{mission.rations}, 부산물 +{mission.loot}, 광석 +{mission.ore}"
        )
        print_divider()
        
    try:
        m_idx = int(input("수주할 의뢰 번호를 입력하세요 (취소는 -1): ").strip())
        if m_idx == -1:
            return
        if m_idx < 0 or m_idx >= len(manager.missions):
            print(colorize("올바르지 않은 의뢰입니다.", RED))
            input("계속하려면 엔터를 누르세요...")
            return
        mission = manager.missions[m_idx]
    except ValueError:
        return

    # Choose active squad
    squad = []
    max_size = camp.get_max_squad_size()
    
    while len(squad) < max_size:
        clear_screen()
        print_header(f"분대 편성 ({len(squad)}/{max_size}명)")
        print(f"선택한 의뢰: {mission.name}\n")
        
        print("=== [분대 목록] ===")
        for idx, m in enumerate(squad):
            print(f"  [{idx}] {m.name} ({m.m_class})")
        print_divider()
        
        print("=== [대기실 용병 명단] ===")
        available = [m for m in alive_mercs if m not in squad]
        if not available:
            print("편성 가능한 대원이 더 이상 없습니다.")
        else:
            for idx, m in enumerate(available):
                print(f"  [{idx}] {m.name} ({m.m_class}) | HP: {m.hp}/{m.get_max_hp()}")
                
        print("\n1. 용병 추가하기")
        print("2. 편성 완료 및 출발")
        print("3. 취소")
        
        ch = get_input("명령을 선택하세요: ", ["1", "2", "3"])
        
        if ch == "1":
            if not available:
                continue
            try:
                sel = int(input("추가할 용병 대기실 번호: ").strip())
                if 0 <= sel < len(available):
                    squad.append(available[sel])
                else:
                    print(colorize("올바르지 않은 번호입니다.", RED))
                    input("계속하려면 엔터를 누르세요...")
            except ValueError:
                pass
        elif ch == "2":
            if not squad:
                print(colorize("최소 한 명 이상의 용병을 배치해야 출발할 수 있습니다!", RED))
                input("계속하려면 엔터를 누르세요...")
                continue
            break
        elif ch == "3":
            return
            
    # Run exploration
    success = manager.run_mission(m_idx, squad)
    if success:
        # Check if boss mission (difficulty 3) was cleared
        if mission.difficulty == 3:
            print(colorize("\n🏆🏆🏆 [게임 승리!] 멸망한 세계의 거대 마수 영주 바스티안을 격퇴했습니다! 용병단은 이 세계의 전설이 됩니다! 🏆🏆🏆", BRIGHT_YELLOW + BOLD))
            input("엔터를 누르면 메인 메뉴로 돌아가 엔딩을 축하합니다.")
    else:
        print(colorize("\n💀 탐색 실패. 생존자들은 간신히 성채로 퇴각했습니다...", RED))
    input("계속하려면 엔터를 누르세요...")

def display_ending_ascii():
    logo = """
    ██████╗  █████╗ ██████╗ ██╗  ██╗    ███████╗ █████╗ ███╗   ██╗████████╗ █████╗ ███████╗██╗   ██╗
    ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝    ██╔════╝██╔══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔════╝╚██╗ ██╔╝
    ██║  ██║███████║██████╔╝█████╔╝     █████╗  ███████║██╔██╗ ██║   ██║   ███████║███████╗ ╚████╔╝ 
    ██║  ██║██╔══██║██╔══██╗██╔═██╗     ██╔══╝  ██╔══██║██║╚██╗██║   ██║   ██╔══██║╚════██║  ╚██╔╝  
    ██████╔╝██║  ██║██║  ██║██║  ██╗    ██║     ██║  ██║██║ ╚████║   ██║   ██║  ██║███████║   ██║   
    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚══════╝   ╚═╝   
    """
    print(colorize(logo, BRIGHT_RED + BOLD))

def main():
    resources, camp, mercenaries = initialize_game()
    
    # Title Screen
    clear_screen()
    display_ending_ascii()
    print(colorize("=" * 60, GRAY))
    print(colorize("     멸망한 세계에서 용병단으로 살아남기 (다크 판타지 에디션)", BOLD + BRIGHT_YELLOW))
    print(colorize("=" * 60, GRAY))
    print("목표: 30일 이내에 영주의 성채를 공략하여 타락한 영주 바스티안을 토벌하세요.")
    print("용병들을 먹여 살리고, 성채를 보수하여 기적을 창조하십시오.")
    input("\n시작하려면 엔터를 누르세요...")
    
    while True:
        # Check Lose Condition
        if not mercenaries and resources.gold < 40 and resources.rations <= 0:
            clear_screen()
            print_header("용병단 몰락 (GAME OVER)")
            print(colorize("성채는 텅 비었고, 금화는 바닥났으며, 생존자 식량조차 없습니다.", RED))
            print(colorize("용병단은 어둠 속에 삼켜져 멸망했습니다...", RED + BOLD))
            break
            
        if resources.day > 35:
            clear_screen()
            print_header("시간 초과 (GAME OVER)")
            print(colorize("35일 안에 심연의 지배자 바스티안을 격퇴하지 못했습니다.", RED))
            print(colorize("성채마저 마수 무리에 함락되어 파멸했습니다...", RED + BOLD))
            break
            
        clear_screen()
        display_top_bar(resources, camp, mercenaries)
        
        print("1. 영주실 (용병단 roster & 거처 업그레이드)")
        print("2. 마법 통신진 (인재 영입 및 단장의 통찰안)")
        print("3. Tavern / 주점 (사기 충전 및 피로 완화)")
        print("4. 치유의 성소 (부상 정화 및 타락 치료)")
        print("5. 대장간 (무기 담금질 및 갑옷 강화)")
        print("6. 의뢰 수주 및 탐색 출발 (전투 및 자원 획득)")
        print("7. 하루 종료 (식량/주급 지불 및 일차 경과)")
        print("8. 게임 종료")
        
        choice = get_input("\n행동을 선택하세요: ", ["1", "2", "3", "4", "5", "6", "7", "8"])
        
        if choice == "1":
            show_roster_menu(resources, camp, mercenaries)
        elif choice == "2":
            show_magic_array_menu(resources, camp, mercenaries)
        elif choice == "3":
            show_tavern_menu(resources, camp, mercenaries)
        elif choice == "4":
            show_sanctum_menu(resources, camp, mercenaries)
        elif choice == "5":
            show_blacksmith_menu(resources, camp, mercenaries)
        elif choice == "6":
            setup_squad_and_run(resources, camp, mercenaries)
        elif choice == "7":
            # Process day transition
            logs, conflict = resources.check_upkeep(mercenaries)
            
            # Print logs
            clear_screen()
            print_header("하루 일과 정산")
            for log in logs:
                print(log)
            print_divider()
            
            # Resolve conflict if triggered
            if conflict:
                m1 = conflict["m1"]
                m2 = conflict["m2"]
                print(colorize(f"\n⚡ [사건 발생] {conflict['title']} ⚡", BRIGHT_RED + BOLD))
                print(conflict["desc"])
                for i, opt in enumerate(conflict["options"]):
                    print(f"{i + 1}. {opt['text']}")
                    
                c_choice = get_input("선택하세요: ", ["1", "2", "3", "4"])
                c_idx = int(c_choice) - 1
                res_log = resources.resolve_conflict(conflict, c_idx, mercenaries)
                print(res_log)
                print_divider()
                
            input("\n정산을 마치려면 엔터를 누르세요...")
        elif choice == "8":
            confirm = input(colorize("정말로 게임을 종료하시겠습니까? (y/n): ", YELLOW)).strip().lower()
            if confirm == "y":
                print(colorize("게임을 안전하게 종료합니다. 플레이해 주셔서 감사합니다!", GREEN))
                sys.exit(0)

if __name__ == "__main__":
    main()
