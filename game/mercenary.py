import random
from game.utils import colorize, GREEN, RED, YELLOW, CYAN, BLUE, MAGENTA, BOLD, GRAY, WHITE

CLASSES = ["전사", "척후병", "마법사", "사제"]

# Trait definitions
VISIBLE_POSITIVE_TRAITS = {
    "신속함": {"desc": "행동력(AP) +1, 회피율 +10%", "ap_bonus": 1, "eva_bonus": 10},
    "강인함": {"desc": "최대 체력(HP) +20%, 방어력 +5", "hp_mult": 1.2, "def_bonus": 5},
    "강타자": {"desc": "공격력 +20%", "atk_mult": 1.2},
    "철벽": {"desc": "받는 피해 -15%, 방어력 +8", "dmg_red": 0.15, "def_bonus": 8},
    "낙천적": {"desc": "매일 사기 회복 +1, 스트레스 저항", "morale_regen": 1}
}

VISIBLE_NEGATIVE_TRAITS = {
    "겁쟁이": {"desc": "전투 피격 시 사기 추가 감소, 도망칠 확률 증가", "coward": True},
    "탈영병": {"desc": "매일 사기 소모 +2", "daily_morale_drain": 2},
    "애꾸눈": {"desc": "명중률 -15%", "hit_penalty": 15},
    "피의 굶주림": {"desc": "사기가 낮을 때 아군을 공격할 수 있음", "bloodlust": True},
    "이단자": {"desc": "성소 정화/치유 효율 -30%", "sanctum_penalty": 0.3}
}

HIDDEN_TRAITS = {
    "오라 발현의 씨앗": {
        "class_req": "전사",
        "desc": "오라의 싹이 보입니다. 각성 시 제국 제일의 검사로 성장합니다.",
        "awoken_name": "오라의 지배자",
        "awoken_desc": "공격력 +60%, 최대 체력 +30%, 모든 공격에 방어 무시 오라 부여.",
        "atk_mult": 1.6,
        "hp_mult": 1.3,
        "pierce": True
    },
    "바람의 인도자": {
        "class_req": "척후병",
        "desc": "바람이 발걸음을 돕습니다. 각성 시 누구도 쫓을 수 없는 그림자가 됩니다.",
        "awoken_name": "그림자 습격자",
        "awoken_desc": "회피율 +30%, 행동력(AP) +2, 행동 시 30% 확률로 AP를 소모하지 않음.",
        "eva_bonus": 30,
        "ap_bonus": 2,
        "free_ap_chance": 0.3
    },
    "마나 폭풍의 눈": {
        "class_req": "마법사",
        "desc": "잠재된 마력이 폭풍처럼 요동칩니다. 각성 시 대재앙의 대마법사가 됩니다.",
        "awoken_name": "마나의 군주",
        "awoken_desc": "스킬 공격력 +70%, MP 소모량 -30%, 모든 주문이 적의 마법 저항을 관통.",
        "skill_mult": 1.7,
        "mp_cost_red": 0.3,
        "m_pierce": True
    },
    "성흔의 인장": {
        "class_req": "사제",
        "desc": "신의 각인이 영혼에 새겨져 있습니다. 각성 시 죽음마저 거스르는 대사제가 됩니다.",
        "awoken_name": "성흔의 대사제",
        "awoken_desc": "힐량 +50%, 아군 전체의 타락 축적률 -25%, 아군 부상 치료 비용 무료.",
        "heal_mult": 1.5,
        "corruption_resist": 0.25,
        "free_treatment": True
    }
}

NAMES = [
    "카엘", "로건", "발렌", "시릴", "일리아", "에스더", "브란", "다미안", "레이나", "휴고", 
    "아리아", "제드", "오스왈드", "에블린", "가레스", "아이리스", "테론", "유나", "로익", "실비아"
]

class Mercenary:
    def __init__(self, name=None, m_class=None, rank=None):
        self.name = name if name else random.choice(NAMES)
        self.m_class = m_class if m_class else random.choice(CLASSES)
        
        # Rank determine baseline stats (F, E, D, C, B, A, S)
        self.rank = rank if rank else random.choices(
            ["F", "E", "D", "C", "B", "A"], 
            weights=[35, 30, 20, 10, 4, 1]
        )[0]
        
        self.level = 1
        self.exp = 0
        self.exp_to_next = 100
        
        # Stat multiplier by rank
        rank_mults = {"F": 0.8, "E": 0.9, "D": 1.0, "C": 1.1, "B": 1.2, "A": 1.4, "S": 1.8}
        mult = rank_mults[self.rank]
        
        # Base Stats by Class
        if self.m_class == "전사":
            self.max_hp = int(120 * mult)
            self.max_mp = int(30 * mult)
            self.atk = int(15 * mult)
            self.defn = int(10 * mult)
            self.eva = int(5 * mult)
            self.max_ap = 3
        elif self.m_class == "척후병":
            self.max_hp = int(90 * mult)
            self.max_mp = int(40 * mult)
            self.atk = int(18 * mult)
            self.defn = int(4 * mult)
            self.eva = int(20 * mult)
            self.max_ap = 4
        elif self.m_class == "마법사":
            self.max_hp = int(70 * mult)
            self.max_mp = int(80 * mult)
            self.atk = int(22 * mult)  # Magic power is mapped to atk
            self.defn = int(2 * mult)
            self.eva = int(8 * mult)
            self.max_ap = 3
        else:  # 사제
            self.max_hp = int(85 * mult)
            self.max_mp = int(60 * mult)
            self.atk = int(12 * mult)
            self.defn = int(5 * mult)
            self.eva = int(10 * mult)
            self.max_ap = 3

        self.hp = self.max_hp
        self.mp = self.max_mp
        
        self.morale = 50       # 0 ~ 100
        self.corruption = 0    # 0 ~ 100
        
        # State: "정상", "부상" (HP max -20%), "독" (매 턴 HP -10%), "저주" (공격력 -30%), "출혈" (매일 30% 확률로 사망)
        self.states = [] 
        
        # Generate traits
        self.positive_trait = random.choice(list(VISIBLE_POSITIVE_TRAITS.keys()))
        self.negative_trait = random.choice(list(VISIBLE_NEGATIVE_TRAITS.keys()))
        
        # Hidden talent (Seed) - F or E rank has higher chance to have hidden talent (Leader's Insight gimmick)
        self.hidden_trait = None
        self.is_identified = False
        self.is_awakened = False
        
        # 15% chance for F/E rank to have hidden trait matching their class. Other ranks 5%.
        talent_chance = 0.25 if self.rank in ["F", "E"] else 0.05
        if random.random() < talent_chance:
            # Find hidden traits matching class
            matching_talents = [k for k, v in HIDDEN_TRAITS.items() if v["class_req"] == self.m_class]
            if matching_talents:
                self.hidden_trait = matching_talents[0]

        # Equips (Weapon / Armor level)
        self.weapon_level = 0
        self.armor_level = 0

    def get_max_hp(self):
        val = self.max_hp
        # Apply traits
        if self.positive_trait == "강인함":
            val = int(val * VISIBLE_POSITIVE_TRAITS["강인함"]["hp_mult"])
        if self.is_awakened and self.hidden_trait:
            ht = HIDDEN_TRAITS[self.hidden_trait]
            if "hp_mult" in ht:
                val = int(val * ht["hp_mult"])
        # Apply state
        if "부상" in self.states:
            val = int(val * 0.8)
        return val

    def get_max_mp(self):
        return self.max_mp

    def get_atk(self):
        val = self.atk + (self.weapon_level * 3)
        if self.positive_trait == "강타자":
            val = int(val * VISIBLE_POSITIVE_TRAITS["강타자"]["atk_mult"])
        if self.is_awakened and self.hidden_trait:
            ht = HIDDEN_TRAITS[self.hidden_trait]
            if "atk_mult" in ht:
                val = int(val * ht["atk_mult"])
        if "저주" in self.states:
            val = int(val * 0.7)
        return max(1, val)

    def get_def(self):
        val = self.defn + (self.armor_level * 2)
        if self.positive_trait == "강인함":
            val += VISIBLE_POSITIVE_TRAITS["강인함"]["def_bonus"]
        if self.positive_trait == "철벽":
            val += VISIBLE_POSITIVE_TRAITS["철벽"]["def_bonus"]
        return max(0, val)

    def get_eva(self):
        val = self.eva
        if self.positive_trait == "신속함":
            val += VISIBLE_POSITIVE_TRAITS["신속함"]["eva_bonus"]
        if self.is_awakened and self.hidden_trait:
            ht = HIDDEN_TRAITS[self.hidden_trait]
            if "eva_bonus" in ht:
                val += ht["eva_bonus"]
        return val

    def get_max_ap(self):
        val = self.max_ap
        if self.positive_trait == "신속함":
            val += VISIBLE_POSITIVE_TRAITS["신속함"]["ap_bonus"]
        if self.is_awakened and self.hidden_trait:
            ht = HIDDEN_TRAITS[self.hidden_trait]
            if "ap_bonus" in ht:
                val += ht["ap_bonus"]
        return val

    def get_hit_chance(self):
        chance = 90
        if self.negative_trait == "애꾸눈":
            chance -= VISIBLE_NEGATIVE_TRAITS["애꾸눈"]["hit_penalty"]
        return max(30, chance)

    def gain_exp(self, amount):
        if self.rank == "S" and self.level >= 10:
            return ""  # Max S-rank Level 10
            
        self.exp += amount
        log_lines = [f"{self.name}({self.m_class})이(가) {amount} EXP를 획득했습니다."]
        
        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level += 1
            self.exp_to_next = int(self.exp_to_next * 1.3)
            # Boost stats on level up
            self.max_hp = int(self.max_hp * 1.1)
            self.max_mp = int(self.max_mp * 1.1)
            self.atk = int(self.atk * 1.1)
            self.defn += 1
            self.hp = self.get_max_hp()
            self.mp = self.max_mp
            log_lines.append(colorize(f"\n★ 레벨 업! [{self.name}] {self.level}레벨이 되었습니다!", YELLOW + BOLD))
            
            # Check awakening of hidden trait at level 3 or higher
            if self.hidden_trait and not self.is_awakened and self.level >= 3:
                self.awaken()
                log_lines.append(colorize(f"\n⚡⚡ [각성] {self.name}의 숨겨진 재능 '{self.hidden_trait}'이(가) '{HIDDEN_TRAITS[self.hidden_trait]['awoken_name']}'(으)로 각성했습니다! 등급이 S로 상향됩니다! ⚡⚡", MAGENTA + BOLD))
        return "".join(log_lines)

    def awaken(self):
        self.is_awakened = True
        self.is_identified = True
        self.rank = "S"
        self.hp = self.get_max_hp()

    def identify(self):
        """Leader's Insight reveals the hidden trait."""
        self.is_identified = True
        return self.hidden_trait is not None

    def get_weekly_salary(self):
        rank_salaries = {"F": 5, "E": 10, "D": 20, "C": 35, "B": 60, "A": 100, "S": 200}
        return rank_salaries[self.rank]

    def get_daily_ration_cost(self):
        # High rank eating slightly more clean rations
        rank_rations = {"F": 1, "E": 1, "D": 1, "C": 2, "B": 2, "A": 3, "S": 3}
        return rank_rations[self.rank]

    def display_status(self, index=None):
        idx_str = f"[{index}] " if index is not None else ""
        
        # Rank color coding
        rank_colors = {
            "F": GRAY, "E": WHITE, "D": GREEN, "C": BLUE, 
            "B": CYAN, "A": YELLOW, "S": MAGENTA
        }
        rank_disp = colorize(f"[{self.rank}급]", rank_colors.get(self.rank, WHITE) + BOLD)
        
        state_str = f" ({','.join(self.states)})" if self.states else ""
        state_disp = colorize(state_str, RED) if self.states else ""

        # Hidden trait display depending on insight identification
        if self.hidden_trait:
            if self.is_awakened:
                ht_name = HIDDEN_TRAITS[self.hidden_trait]["awoken_name"]
                ht_disp = colorize(f" [각성: {ht_name}]", MAGENTA + BOLD)
            elif self.is_identified:
                ht_disp = colorize(f" [잠재력: {self.hidden_trait}]", BRIGHT_YELLOW + BOLD)
            else:
                ht_disp = colorize(" [잠재력: ???]", GRAY)
        else:
            ht_disp = ""

        # Status text
        hp_max = self.get_max_hp()
        status_line = (
            f"{idx_str}{rank_disp} {colorize(self.name, BOLD)} ({self.m_class} Lvl {self.level}) "
            f"HP: {self.hp}/{hp_max} MP: {self.mp}/{self.max_mp} ATK: {self.get_atk()} DEF: {self.get_def()} "
            f"사기: {colorize(str(self.morale), GREEN if self.morale > 40 else RED)} "
            f"타락: {colorize(str(self.corruption), RED if self.corruption > 50 else YELLOW)}"
            f"{state_disp}{ht_disp}"
        )
        return status_line

    def get_skill_name(self):
        if self.m_class == "전사":
            return "방패 충격 (Shield Bash)"
        elif self.m_class == "척후병":
            return "급소 찌르기 (Vitals Strike)"
        elif self.m_class == "마법사":
            return "화염 폭발 (Fire Blast)"
        else:  # 사제
            return "성스러운 치유 (Holy Heal)"

    def get_skill_desc(self):
        if self.m_class == "전사":
            return "AP 2 소모: 적에게 물리 피해를 주고 40% 확률로 1턴 기절시킵니다."
        elif self.m_class == "척후병":
            return "AP 2 소모: 적의 방어력을 50% 무시하고 큰 피해를 줍니다."
        elif self.m_class == "마법사":
            return "AP 3, MP 15 소모: 적 전체에게 강력한 원소 피해를 입힙니다."
        else:  # 사제
            return "AP 2, MP 10 소모: 아군 한 명의 HP를 회복시키고 해로운 상태이상을 해제합니다."
