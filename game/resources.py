import random
from game.utils import colorize, RED, GREEN, YELLOW, CYAN, BLUE, MAGENTA, BOLD, GRAY

class ResourceManager:
    def __init__(self):
        self.gold = 500
        self.rations = 60
        self.monster_loot = 0
        self.ore = 0
        self.day = 1
        
    def add_resources(self, gold=0, rations=0, loot=0, ore=0):
        self.gold += gold
        self.rations += rations
        self.monster_loot += loot
        self.ore += ore
        
    def check_upkeep(self, mercenaries):
        """
        Process daily upkeep and state updates for mercenaries.
        Returns a list of log messages and potentially a conflict event.
        """
        logs = []
        
        # Calculate daily costs
        total_gold_upkeep = 0
        total_ration_upkeep = 0
        
        for merc in mercenaries:
            # Gold upkeep is weekly salary divided by 5 (daily cost)
            total_gold_upkeep += max(1, merc.get_weekly_salary() // 5)
            total_ration_upkeep += merc.get_daily_ration_cost()
            
        logs.append(colorize(f"\n[일일 결산 - 1일 경과] (현재 {self.day}일째)", BOLD + CYAN))
        logs.append(f"용병단 유지비 청구: 금화 -{total_gold_upkeep}, 식량 -{total_ration_upkeep}")

        # Consume rations
        rations_starvation = False
        if self.rations >= total_ration_upkeep:
            self.rations -= total_ration_upkeep
            logs.append(f"식량을 정상 배급했습니다. (남은 식량: {self.rations})")
        else:
            lack = total_ration_upkeep - self.rations
            self.rations = 0
            rations_starvation = True
            logs.append(colorize(f"⚠️ 식량이 부족하여 {lack}명 분의 배급에 실패했습니다! 용병단이 굶주립니다!", RED + BOLD))

        # Consume gold (pay upkeep)
        gold_unpaid = False
        if self.gold >= total_gold_upkeep:
            self.gold -= total_gold_upkeep
            logs.append(f"용병 주급을 지불했습니다. (남은 금화: {self.gold})")
        else:
            lack_gold = total_gold_upkeep - self.gold
            self.gold = 0
            gold_unpaid = True
            logs.append(colorize(f"⚠️ 금화가 부족하여 주급 {lack_gold} 골드가 미지급되었습니다! 용병들의 원망이 커집니다!", RED + BOLD))

        # Update each mercenary's morale, corruption, and state
        mercenaries_to_remove = []
        
        for merc in mercenaries:
            # 1. Regenerate/drain morale and corruption based on food & money
            morale_change = 0
            corruption_change = 0
            
            # Trait effects
            if merc.positive_trait == "낙천적":
                morale_change += 2
            if merc.negative_trait == "탈영병":
                morale_change -= 2
                
            if rations_starvation:
                morale_change -= 15
                corruption_change += 10
            else:
                morale_change += 2  # Well-fed bonus
                
            if gold_unpaid:
                morale_change -= 20
                corruption_change += 5
                
            merc.morale = max(0, min(100, merc.morale + morale_change))
            merc.corruption = max(0, min(100, merc.corruption + corruption_change))
            
            # 2. Check states (Poison, Bleeding, etc.)
            if "독" in merc.states:
                poison_dmg = int(merc.get_max_hp() * 0.15)
                merc.hp = max(1, merc.hp - poison_dmg)
                logs.append(colorize(f"💀 {merc.name}은(는) 맹독 중독으로 인해 HP가 {poison_dmg} 감소했습니다.", RED))
                
            if "출혈" in merc.states:
                # 30% chance of death
                if random.random() < 0.3:
                    logs.append(colorize(f"🩸 [사망] {merc.name}은(는) 치료받지 못한 과다출혈로 인해 숨을 거두었습니다...", RED + BOLD))
                    mercenaries_to_remove.append(merc)
                    continue
                else:
                    logs.append(colorize(f"🩸 {merc.name}은(는) 심각한 출혈 상태입니다! 성소에서의 정화가 필요합니다.", RED))

            # 3. Check low morale desertion
            if merc.morale <= 0:
                desert_chance = 0.40 if merc.negative_trait == "겁쟁이" else 0.25
                if random.random() < desert_chance:
                    logs.append(colorize(f"🏃 [이탈] 사기가 바닥난 {merc.name}({merc.m_class})이(가) 야반도주했습니다!", RED + BOLD))
                    mercenaries_to_remove.append(merc)
                    continue

            # 4. Check high corruption (>= 100) madness/monster transformation
            if merc.corruption >= 100:
                logs.append(colorize(f"👹 [타락] {merc.name}({merc.m_class})의 정신이 오염되어 마수로 돌변하여 폭주했습니다! 아군에게 부상을 입히고 어둠 속으로 도망쳤습니다.", RED + BOLD))
                mercenaries_to_remove.append(merc)
                # Inflict injury on another random mercenary if possible
                other_mercs = [m for m in mercenaries if m != merc and m not in mercenaries_to_remove]
                if other_mercs:
                    victim = random.choice(other_mercs)
                    if "부상" not in victim.states:
                        victim.states.append("부상")
                        logs.append(colorize(f"⚡ 폭주한 {merc.name}의 습격으로 {victim.name}이(가) [부상]을 입었습니다!", RED))
                continue

        # Clean up deceased/deserted mercenaries
        for merc in mercenaries_to_remove:
            if merc in mercenaries:
                mercenaries.remove(merc)

        self.day += 1
        
        # Trigger Alignment Conflict Event (성향 갈등)
        conflict_event = None
        if len(mercenaries) >= 2 and random.random() < 0.25:
            conflict_event = self._generate_conflict(mercenaries)
            
        return logs, conflict_event

    def _generate_conflict(self, mercenaries):
        # Choose two random mercenaries
        m1, m2 = random.sample(mercenaries, 2)
        
        # Determine a conflict background
        conflicts = [
            {
                "title": "야영지 갈등: 귀족의 오만 vs 빈민의 분노",
                "desc": f"제국 귀족 출신 행세를 하는 {m1.name}와(과) 빈민가 출신 도둑이었던 {m2.name}이(가) 배급 식량의 청결도를 두고 주먹다짐을 벌였습니다!",
                "options": [
                    {"text": "양쪽 모두 징계한다 (둘 다 사기 -15)", "type": "discipline"},
                    {"text": "금화를 써서 술자리를 주선한다 (금화 -30, 둘 다 사기 +10, 타락 -5)", "type": "reconcile"},
                    {"text": f"{m1.name}을(를) 편들고 {m2.name}을(를) 추방한다 (단원 영구 이탈)", "type": "banish_m2"},
                    {"text": "상관하지 않고 방치한다 (둘 다 타락 +20, 사기 -10)", "type": "ignore"}
                ]
            },
            {
                "title": "야영지 갈등: 신념의 대립",
                "desc": f"독선적인 신앙을 가진 {m1.name}이(가) 이단 성향이 있는 {m2.name}의 소지품에서 마수 뼈로 만든 호신부를 발견하고 사교도라며 칼을 빼 들었습니다!",
                "options": [
                    {"text": "공평하게 벌금과 자성을 명한다 (금화 -10, 둘 다 사기 -10)", "type": "discipline"},
                    {"text": "종교 분쟁을 막기 위해 신전 기부금을 내어 중재한다 (금화 -50, 둘 다 사기 +15)", "type": "reconcile"},
                    {"text": f"{m1.name}의 정화 주장을 받아들여 {m2.name}을(를) 추방한다", "type": "banish_m2"},
                    {"text": "아포칼립스 세상에선 힘이 법이다. 방관한다 (둘 다 타락 +25, 사기 -10)", "type": "ignore"}
                ]
            }
        ]
        
        chosen = random.choice(conflicts)
        chosen["m1"] = m1
        chosen["m2"] = m2
        return chosen

    def resolve_conflict(self, event, choice_idx, mercenaries):
        m1 = event["m1"]
        m2 = event["m2"]
        option = event["options"][choice_idx]
        op_type = option["type"]
        
        log = ""
        if op_type == "discipline":
            m1.morale = max(0, m1.morale - 15)
            m2.morale = max(0, m2.morale - 15)
            log = colorize(f"엄격한 규율로 두 용병을 처벌했습니다. {m1.name}와 {m2.name}의 사기가 15씩 감소했습니다.", YELLOW)
        elif op_type == "reconcile":
            self.gold = max(0, self.gold - 30)
            m1.morale = min(100, m1.morale + 10)
            m2.morale = min(100, m2.morale + 10)
            m1.corruption = max(0, m1.corruption - 5)
            m2.corruption = max(0, m2.corruption - 5)
            log = colorize(f"금화 30을 소모해 고기 극주와 안주를 풀었습니다. 두 용병이 화해하고 사기가 올랐습니다.", GREEN)
        elif op_type == "banish_m2":
            if m2 in mercenaries:
                mercenaries.remove(m2)
            m1.morale = min(100, m1.morale + 15)
            log = colorize(f"편애와 독단으로 {m2.name}을(를) 용병단에서 추방했습니다. {m1.name}의 사기가 15 증가했습니다.", RED)
        elif op_type == "ignore":
            m1.corruption = min(100, m1.corruption + 20)
            m2.corruption = min(100, m2.corruption + 20)
            m1.morale = max(0, m1.morale - 10)
            m2.morale = max(0, m2.morale - 10)
            log = colorize(f"방임했습니다. 용병단 규율이 땅에 떨어지며 두 용병의 타락이 20씩 상승하고 사기가 10 감소했습니다.", RED + BOLD)
            
        return log
