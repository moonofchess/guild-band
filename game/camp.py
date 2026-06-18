from game.mercenary import Mercenary, VISIBLE_POSITIVE_TRAITS, VISIBLE_NEGATIVE_TRAITS, HIDDEN_TRAITS
from game.utils import colorize, GREEN, RED, YELLOW, CYAN, BLUE, MAGENTA, BOLD, GRAY

class BaseCamp:
    def __init__(self):
        # Building Levels (starts at 1)
        self.lord_hall_level = 1
        self.magic_array_level = 1
        self.tavern_level = 1
        self.sanctum_level = 1
        self.blacksmith_level = 1
        
        # Temp storage for recruited mercenaries waiting in the Tavern/Magic Array
        self.recruits_pool = []

    def get_max_mercenaries(self):
        # Level 1: 4, Level 2: 6, Level 3: 8
        return 4 + (self.lord_hall_level - 1) * 2

    def get_max_squad_size(self):
        # Level 1: 3, Level 2: 4, Level 3: 4 (with stat bonus)
        return 3 if self.lord_hall_level == 1 else 4

    # --- UPGRADES ---
    def upgrade_lord_hall(self, resources):
        level = self.lord_hall_level
        if level >= 3:
            return False, "영주실은 이미 최고 레벨(3)입니다."
            
        costs = {
            1: {"gold": 200, "loot": 10, "ore": 5},
            2: {"gold": 500, "loot": 30, "ore": 15}
        }
        cost = costs[level]
        if resources.gold < cost["gold"] or resources.monster_loot < cost["loot"] or resources.ore < cost["ore"]:
            return False, f"자원이 부족합니다. (필요 자원 - 금화: {cost['gold']}, 부산물: {cost['loot']}, 광석: {cost['ore']})"
            
        resources.gold -= cost["gold"]
        resources.monster_loot -= cost["loot"]
        resources.ore -= cost["ore"]
        self.lord_hall_level += 1
        return True, f"영주실이 레벨 {self.lord_hall_level}(으)로 업그레이드되었습니다! (최대 고용 용병: {self.get_max_mercenaries()}명, 전투 분대 크기: {self.get_max_squad_size()}명)"

    def upgrade_magic_array(self, resources):
        level = self.magic_array_level
        if level >= 3:
            return False, "마법 통신진은 이미 최고 레벨(3)입니다."
            
        costs = {
            1: {"gold": 150, "loot": 10, "ore": 5},
            2: {"gold": 350, "loot": 25, "ore": 10}
        }
        cost = costs[level]
        if resources.gold < cost["gold"] or resources.monster_loot < cost["loot"] or resources.ore < cost["ore"]:
            return False, f"자원이 부족합니다. (필요 자원 - 금화: {cost['gold']}, 부산물: {cost['loot']}, 광석: {cost['ore']})"
            
        resources.gold -= cost["gold"]
        resources.monster_loot -= cost["loot"]
        resources.ore -= cost["ore"]
        self.magic_array_level += 1
        return True, f"마법 통신진이 레벨 {self.magic_array_level}(으)로 업그레이드되었습니다! (더 유능한 용병의 신호가 포착됩니다.)"

    def upgrade_tavern(self, resources):
        level = self.tavern_level
        if level >= 3:
            return False, "주점은 이미 최고 레벨(3)입니다."
            
        costs = {
            1: {"gold": 100, "loot": 8, "ore": 3},
            2: {"gold": 250, "loot": 20, "ore": 8}
        }
        cost = costs[level]
        if resources.gold < cost["gold"] or resources.monster_loot < cost["loot"] or resources.ore < cost["ore"]:
            return False, f"자원이 부족합니다. (필요 자원 - 금화: {cost['gold']}, 부산물: {cost['loot']}, 광석: {cost['ore']})"
            
        resources.gold -= cost["gold"]
        resources.monster_loot -= cost["loot"]
        resources.ore -= cost["ore"]
        self.tavern_level += 1
        return True, f"주점이 레벨 {self.tavern_level}(으)로 업그레이드되었습니다! (사기 회복 효율이 25% 상승합니다.)"

    def upgrade_sanctum(self, resources):
        level = self.sanctum_level
        if level >= 3:
            return False, "치유의 성소는 이미 최고 레벨(3)입니다."
            
        costs = {
            1: {"gold": 150, "loot": 15, "ore": 5},
            2: {"gold": 400, "loot": 30, "ore": 12}
        }
        cost = costs[level]
        if resources.gold < cost["gold"] or resources.monster_loot < cost["loot"] or resources.ore < cost["ore"]:
            return False, f"자원이 부족합니다. (필요 자원 - 금화: {cost['gold']}, 부산물: {cost['loot']}, 광석: {cost['ore']})"
            
        resources.gold -= cost["gold"]
        resources.monster_loot -= cost["loot"]
        resources.ore -= cost["ore"]
        self.sanctum_level += 1
        return True, f"치유의 성소인 레벨 {self.sanctum_level}(으)로 업그레이드되었습니다! (정화 및 정비 비용이 30% 감소합니다.)"

    def upgrade_blacksmith(self, resources):
        level = self.blacksmith_level
        if level >= 3:
            return False, "대장간은 이미 최고 레벨(3)입니다."
            
        costs = {
            1: {"gold": 150, "loot": 15, "ore": 8},
            2: {"gold": 350, "loot": 30, "ore": 15}
        }
        cost = costs[level]
        if resources.gold < cost["gold"] or resources.monster_loot < cost["loot"] or resources.ore < cost["ore"]:
            return False, f"자원이 부족합니다. (필요 자원 - 금화: {cost['gold']}, 부산물: {cost['loot']}, 광석: {cost['ore']})"
            
        resources.gold -= cost["gold"]
        resources.monster_loot -= cost["loot"]
        resources.ore -= cost["ore"]
        self.blacksmith_level += 1
        return True, f"대장간이 레벨 {self.blacksmith_level}(으)로 업그레이드되었습니다! (장비 담금질 한계가 {self.blacksmith_level * 2}단계로 확장됩니다.)"

    # --- MAGIC array: RECRUITMENT ---
    def roll_recruits(self, resources):
        """Generate 3 potential recruits based on Magic Array Level. Costs 40 Gold."""
        cost = 40
        if resources.gold < cost:
            return False, "통신진을 가동할 골드가 부족합니다. (필요: 40 골드)"
            
        resources.gold -= cost
        self.recruits_pool = []
        
        # Decide ranks based on level
        if self.magic_array_level == 1:
            ranks = ["F", "E", "D"]
            weights = [50, 35, 15]
        elif self.magic_array_level == 2:
            ranks = ["E", "D", "C"]
            weights = [40, 40, 20]
        else:
            ranks = ["D", "C", "B", "A"]
            weights = [30, 40, 20, 10]
            
        for _ in range(3):
            rank = self.recruits_pool_weighted_choice(ranks, weights)
            self.recruits_pool.append(Mercenary(rank=rank))
            
        return True, f"마법 통신진을 가동해 제국 변방 생존자 신호 3개를 감지했습니다! (금화 -{cost})"

    def recruits_pool_weighted_choice(self, choices, weights):
        import random
        return random.choices(choices, weights=weights)[0]

    def use_insight(self, resources):
        """Use Leader's Insight to identify all recruits in the pool. Costs 15 Gold."""
        cost = 15
        if not self.recruits_pool:
            return False, "감지된 영입 대상이 없습니다. 먼저 마법 통신을 가동하세요."
        if resources.gold < cost:
            return False, "단장의 통찰안을 가동할 골드가 부족합니다. (필요: 15 골드)"
            
        resources.gold -= cost
        found_talent = False
        for merc in self.recruits_pool:
            if merc.identify():
                found_talent = True
                
        if found_talent:
            msg = colorize("⚡ [단장의 통찰안] 눈이 부시게 빛나는 잠재력을 가진 숨겨진 인재의 재능을 감지했습니다! ⚡", MAGENTA + BOLD)
        else:
            msg = colorize("[단장의 통찰안] 이번 무리 중에는 특출난 은폐 재능을 지닌 자가 없는 듯합니다.", GRAY)
            
        return True, msg

    def hire_recruit(self, index, resources, current_mercenaries):
        if not self.recruits_pool or index < 0 or index >= len(self.recruits_pool):
            return False, "올바르지 않은 선택입니다."
            
        if len(current_mercenaries) >= self.get_max_mercenaries():
            return False, f"용병단 정원이 가득 찼습니다. (영주실 레벨 {self.lord_hall_level} 기준 최대 {self.get_max_mercenaries()}명)"
            
        merc = self.recruits_pool[index]
        cost = merc.get_weekly_salary()  # Hiring fee is baseline weekly salary
        
        if resources.gold < cost:
            return False, f"금화가 부족하여 고용할 수 없습니다. (필요: {cost} 골드)"
            
        resources.gold -= cost
        current_mercenaries.append(merc)
        self.recruits_pool.pop(index)
        
        # Welcoming message
        welcome = f"🤝 [{merc.name}]({merc.m_class})을(를) {cost} 골드에 영입했습니다!"
        if merc.hidden_trait and merc.is_identified:
            welcome += colorize(f"\n💡 (비밀을 간직한 인재가 용병단에 들어왔습니다: '{merc.hidden_trait}')", BRIGHT_YELLOW)
        return True, welcome

    # --- TAVERN: MORALE MANAGEMENT ---
    def rest_cheap(self, resources, mercenaries):
        """Cheap barley bread and soup. Costs 3 Gold per mercenary. Morale +8, Corruption -2."""
        if not mercenaries:
            return False, "휴식할 용병이 없습니다."
        cost = len(mercenaries) * 3
        if resources.gold < cost:
            return False, f"금화가 부족합니다. (필요: {cost} 골드)"
            
        resources.gold -= cost
        mult = 1.25 if self.tavern_level >= 2 else 1.0
        
        for m in mercenaries:
            m.morale = min(100, m.morale + int(8 * mult))
            m.corruption = max(0, m.corruption - 2)
            
        return True, f"거친 보리빵과 따뜻한 쥐고기 스프로 배를 채웠습니다. 전원 사기 회복 (+{int(8*mult)}), 타락 감소 (-2). (금화 -{cost})"

    def rest_luxury(self, resources, mercenaries):
        """Spiced liquor and roast meat. Costs 10 Gold per mercenary. Morale +25, Corruption -6."""
        if not mercenaries:
            return False, "휴식할 용병이 없습니다."
        cost = len(mercenaries) * 10
        if resources.gold < cost:
            return False, f"금화가 부족합니다. (필요: {cost} 골드)"
            
        resources.gold -= cost
        mult = 1.25 if self.tavern_level >= 2 else 1.0
        
        for m in mercenaries:
            m.morale = min(100, m.morale + int(25 * mult))
            m.corruption = max(0, m.corruption - 6)
            
        return True, f"독주와 귀한 오염되지 않은 구운 고기로 성대한 만찬을 가졌습니다! 전원 사기 대폭 회복 (+{int(25*mult)}), 타락 감소 (-6). (금화 -{cost})"

    # --- SANCTUM: PURIFICATION & HEALING ---
    def treat_injury(self, merc, resources):
        """Remove '부상' and restore HP. Cost: 30 Gold, 2 Loot. Sanctum Lvl 2 reduces by 30%."""
        if "부상" not in merc.states:
            return False, "치료할 부상이 없습니다."
            
        cost_g = 30
        cost_l = 2
        if self.sanctum_level >= 2:
            cost_g = int(cost_g * 0.7)
            cost_l = int(cost_l * 0.7)
            
        # Saint trait on priest gives discount
        if merc.is_awakened and merc.hidden_trait == "성흔의 인장":
            cost_g, cost_l = 0, 0
            
        if resources.gold < cost_g or resources.monster_loot < cost_l:
            return False, f"자원이 부족합니다. (필요 - 골드: {cost_g}, 부산물: {cost_l})"
            
        resources.gold -= cost_g
        resources.monster_loot -= cost_l
        merc.states.remove("부상")
        merc.hp = merc.get_max_hp()
        return True, f"🏥 {merc.name}의 깊은 부상이 말끔히 아물고 체력이 회복되었습니다. (골드 -{cost_g}, 부산물 -{cost_l})"

    def treat_poison_curse(self, merc, resources):
        """Remove '독' and '저주'. Cost: 20 Gold. Sanctum Lvl 2 reduces by 30%."""
        has_status = "독" in merc.states or "저주" in merc.states
        if not has_status:
            return False, "해독하거나 정화할 저주가 없습니다."
            
        cost_g = 20
        if self.sanctum_level >= 2:
            cost_g = int(cost_g * 0.7)
            
        if merc.is_awakened and merc.hidden_trait == "성흔의 인장":
            cost_g = 0
            
        if resources.gold < cost_g:
            return False, f"금화가 부족합니다. (필요: {cost_g} 골드)"
            
        resources.gold -= cost_g
        if "독" in merc.states:
            merc.states.remove("독")
        if "저주" in merc.states:
            merc.states.remove("저주")
            
        return True, f"✨ 성스러운 성수로 {merc.name}의 영혼을 정화하여 독과 저주를 정화했습니다. (골드 -{cost_g})"

    def treat_bleeding(self, merc, resources):
        """Remove '출혈'. Cost: 40 Gold, 5 Loot. Sanctum Lvl 2 reduces by 30%."""
        if "출혈" not in merc.states:
            return False, "지혈할 상처가 없습니다."
            
        cost_g = 40
        cost_l = 5
        if self.sanctum_level >= 2:
            cost_g = int(cost_g * 0.7)
            cost_l = int(cost_l * 0.7)
            
        if merc.is_awakened and merc.hidden_trait == "성흔의 인장":
            cost_g, cost_l = 0, 0
            
        if resources.gold < cost_g or resources.monster_loot < cost_l:
            return False, f"자원이 부족합니다. (필요 - 골드: {cost_g}, 부산물: {cost_l})"
            
        resources.gold -= cost_g
        resources.monster_loot -= cost_l
        merc.states.remove("출혈")
        return True, f"🩸 붕대와 응급 마법으로 {merc.name}의 동맥 출혈을 멈추고 생기를 불어넣었습니다. (골드 -{cost_g}, 부산물 -{cost_l})"

    def treat_corruption(self, merc, resources):
        """Purify Corruption (-30). Cost: 30 Gold, 4 Loot. Sanctum Lvl 2 reduces by 30%."""
        if merc.corruption <= 0:
            return False, "정화할 타락도가 없습니다."
            
        cost_g = 30
        cost_l = 4
        if self.sanctum_level >= 2:
            cost_g = int(cost_g * 0.7)
            cost_l = int(cost_l * 0.7)
            
        if merc.is_awakened and merc.hidden_trait == "성흔의 인장":
            cost_g, cost_l = 0, 0
            
        if resources.gold < cost_g or resources.monster_loot < cost_l:
            return False, f"자원이 부족합니다. (필요 - 골드: {cost_g}, 부산물: {cost_l})"
            
        resources.gold -= cost_g
        resources.monster_loot -= cost_l
        merc.corruption = max(0, merc.corruption - 30)
        return True, f"🕯️ {merc.name}의 영혼을 갉아먹던 심연의 마기를 기도로 정화했습니다. 타락도 30 감소. (골드 -{cost_g}, 부산물 -{cost_l})"

    # --- BLACKSMITH: GEAR UPGRADES ---
    def upgrade_weapon(self, merc, resources):
        max_level = self.blacksmith_level * 2
        if merc.weapon_level >= max_level:
            return False, f"현재 대장간 레벨({self.blacksmith_level})에서는 무기를 더 이상 강화할 수 없습니다. (최대 {max_level}강)"
            
        next_lvl = merc.weapon_level + 1
        cost_l = next_lvl * 8
        cost_o = next_lvl * 3
        
        if resources.monster_loot < cost_l or resources.ore < cost_o:
            return False, f"강화 재료가 부족합니다. (필요 - 부산물: {cost_l}, 광석: {cost_o})"
            
        resources.monster_loot -= cost_l
        resources.ore -= cost_o
        merc.weapon_level += 1
        return True, f"🔨 담금질 성공! {merc.name}의 무기가 {merc.weapon_level}단계로 강화되어 공격력이 증가했습니다! (부산물 -{cost_l}, 광석 -{cost_o})"

    def upgrade_armor(self, merc, resources):
        max_level = self.blacksmith_level * 2
        if merc.armor_level >= max_level:
            return False, f"현재 대장간 레벨({self.blacksmith_level})에서는 갑옷을 더 이상 강화할 수 없습니다. (최대 {max_level}강)"
            
        next_lvl = merc.armor_level + 1
        cost_l = next_lvl * 8
        cost_o = next_lvl * 3
        
        if resources.monster_loot < cost_l or resources.ore < cost_o:
            return False, f"강화 재료가 부족합니다. (필요 - 부산물: {cost_l}, 광석: {cost_o})"
            
        resources.monster_loot -= cost_l
        resources.ore -= cost_o
        merc.armor_level += 1
        return True, f"🛡️ 무구 개조 성공! {merc.name}의 갑옷이 {merc.armor_level}단계로 개조되어 방어력이 증가했습니다! (부산물 -{cost_l}, 광석 -{cost_o})"
