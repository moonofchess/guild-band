export const CLASSES = ["전사", "척후병", "마법사", "사제"];

export const POSITIVE_TRAITS = {
    "신속함": { desc: "AP +1, 회피율 +10%", ap_bonus: 1, eva_bonus: 0.1 },
    "강인함": { desc: "HP +20%, 방어력 +5", hp_mult: 1.2, def_bonus: 5 },
    "강타자": { desc: "공격력 +20%", atk_mult: 1.2 },
    "철벽": { desc: "피해 감소 -15%, 방어력 +8", dmg_red: 0.15, def_bonus: 8 },
    "낙천적": { desc: "매일 사기 회복 +2", morale_regen: 2 }
};

export const NEGATIVE_TRAITS = {
    "겁쟁이": { desc: "피격 시 사기 추가 감소", coward: true },
    "탈영병": { desc: "매일 사기 소모 +2", daily_morale_drain: 2 },
    "애꾸눈": { desc: "명중률 -15%", hit_penalty: 0.15 },
    "피의 굶주림": { desc: "사기 저하 시 폭주 가능성", bloodlust: true },
    "이단자": { desc: "성소 치료 효율 -30%", sanctum_penalty: 0.3 }
};

export const NAMES = [
    "카엘", "로건", "발렌", "시릴", "일리아", "에스더", "브란", "다미안", "레이나", "휴고", 
    "아리아", "제드", "오스왈드", "에블린", "가레스", "아이리스", "테론", "유나", "로익", "실비아"
];

export class Mercenary {
    constructor(name = null, mClass = null, rank = null) {
        this.name = name || NAMES[Math.floor(Math.random() * NAMES.length)];
        this.mClass = mClass || CLASSES[Math.floor(Math.random() * CLASSES.length)];
        this.rank = rank || this.rollRank();
        this.level = 1;
        this.exp = 0;
        this.expToNext = 100;

        const rankMults = { "F": 0.8, "E": 0.9, "D": 1.0, "C": 1.1, "B": 1.2, "A": 1.4, "S": 1.8 };
        const mult = rankMults[this.rank];

        // Stats base by Class
        if (this.mClass === "전사") {
            this.maxHp = Math.round(120 * mult);
            this.maxMp = Math.round(30 * mult);
            this.atk = Math.round(15 * mult);
            this.def = Math.round(10 * mult);
            this.eva = 0.05 + 0.05 * mult;
            this.maxAp = 3;
            this.assetName = "char_vanguard_sheet.png";
            this.portrait = "portrait_vanguard.png";
        } else if (this.mClass === "척후병") {
            this.maxHp = Math.round(90 * mult);
            this.maxMp = Math.round(40 * mult);
            this.atk = Math.round(18 * mult);
            this.def = Math.round(4 * mult);
            this.eva = 0.20 + 0.05 * mult;
            this.maxAp = 4;
            this.assetName = "char_scout_sheet.png";
            this.portrait = "portrait_scout.png";
        } else if (this.mClass === "마법사") {
            this.maxHp = Math.round(70 * mult);
            this.maxMp = Math.round(80 * mult);
            this.atk = Math.round(22 * mult);
            this.def = Math.round(2 * mult);
            this.eva = 0.08 + 0.02 * mult;
            this.maxAp = 3;
            this.assetName = "char_mage_sheet.png";
            this.portrait = "portrait_mage.png";
        } else { // 사제
            this.maxHp = Math.round(85 * mult);
            this.maxMp = Math.round(60 * mult);
            this.atk = Math.round(12 * mult);
            this.def = Math.round(5 * mult);
            this.eva = 0.10 + 0.02 * mult;
            this.maxAp = 3;
            this.assetName = "char_priest_sheet.png";
            this.portrait = "portrait_priest.png";
        }

        // Apply Trait Modifiers to stats
        this.positiveTrait = Object.keys(POSITIVE_TRAITS)[Math.floor(Math.random() * Object.keys(POSITIVE_TRAITS).length)];
        this.negativeTrait = Object.keys(NEGATIVE_TRAITS)[Math.floor(Math.random() * Object.keys(NEGATIVE_TRAITS).length)];

        if (this.positiveTrait === "강인함") {
            this.maxHp = Math.round(this.maxHp * POSITIVE_TRAITS["강인함"].hp_mult);
            this.def += POSITIVE_TRAITS["강인함"].def_bonus;
        }
        if (this.positiveTrait === "강타자") {
            this.atk = Math.round(this.atk * POSITIVE_TRAITS["강타자"].atk_mult);
        }
        if (this.positiveTrait === "철벽") {
            this.def += POSITIVE_TRAITS["철벽"].def_bonus;
        }
        if (this.positiveTrait === "신속함") {
            this.maxAp += POSITIVE_TRAITS["신속함"].ap_bonus;
            this.eva += POSITIVE_TRAITS["신속함"].eva_bonus;
        }

        this.hp = this.maxHp;
        this.mp = this.maxMp;
        this.morale = 50; // 0 ~ 100
        this.corruption = 0; // 0 ~ 100
        this.states = []; // e.g. "부상", "독", "출혈", "저주"
        
        this.weaponLevel = 0;
        this.armorLevel = 0;
    }

    rollRank() {
        const roll = Math.random();
        if (roll < 0.35) return "F";
        if (roll < 0.65) return "E";
        if (roll < 0.85) return "D";
        if (roll < 0.95) return "C";
        if (roll < 0.99) return "B";
        return "A";
    }

    getWeeklySalary() {
        const salaries = { "F": 25, "E": 40, "D": 60, "C": 90, "B": 130, "A": 200, "S": 350 };
        return salaries[this.rank] || 50;
    }

    getDailyRations() {
        return 2;
    }

    heal(amount) {
        this.hp = Math.min(this.maxHp, this.hp + amount);
    }

    recoverMp(amount) {
        this.mp = Math.min(this.maxMp, this.mp + amount);
    }
}

export class BaseCamp {
    constructor() {
        this.lordHallLevel = 1;
        this.magicArrayLevel = 1;
        this.tavernLevel = 1;
        this.sanctumLevel = 1;
        this.blacksmithLevel = 1;
        
        this.recruitsPool = [];
    }

    getMaxMercenaries() {
        return 4 + (this.lordHallLevel - 1) * 2;
    }

    getSquadSizeLimit() {
        return this.lordHallLevel === 1 ? 3 : 4;
    }

    rollRecruits(resources) {
        const cost = 40;
        if (resources.gold < cost) {
            return { success: false, msg: "골드가 부족합니다. (필요: 40 골드)" };
        }
        resources.gold -= cost;
        this.recruitsPool = [];

        let ranks = ["F", "E", "D"];
        let weights = [0.50, 0.35, 0.15];

        if (this.magicArrayLevel === 2) {
            ranks = ["E", "D", "C"];
            weights = [0.40, 0.40, 0.20];
        } else if (this.magicArrayLevel === 3) {
            ranks = ["D", "C", "B", "A"];
            weights = [0.30, 0.40, 0.20, 0.10];
        }

        for (let i = 0; i < 3; i++) {
            const rank = this.weightedChoice(ranks, weights);
            this.recruitsPool.push(new Mercenary(null, null, rank));
        }

        return { success: true, msg: `마법 통신진을 가동했습니다. (골드 -40)` };
    }

    weightedChoice(choices, weights) {
        const roll = Math.random();
        let cumulative = 0;
        for (let i = 0; i < choices.length; i++) {
            cumulative += weights[i];
            if (roll < cumulative) return choices[i];
        }
        return choices[choices.length - 1];
    }
}

export class ResourceManager {
    constructor() {
        this.gold = 500;
        this.rations = 60;
        this.monsterLoot = 0;
        this.day = 1;
    }

    advanceDay(mercenaries) {
        const logs = [];
        let totalGoldUpkeep = 0;
        let totalRationsUpkeep = 0;

        mercenaries.forEach(m => {
            totalGoldUpkeep += Math.max(1, Math.floor(m.getWeeklySalary() / 5));
            totalRationsUpkeep += m.getDailyRations();
        });

        logs.push(`<b>[일일 결산 - 1일 경과] (현재 ${this.day}일째)</b>`);
        logs.push(`용병단 유지비 청구: 골드 -${totalGoldUpkeep}, 식량 -${totalRationsUpkeep}`);

        let starvation = false;
        if (this.rations >= totalRationsUpkeep) {
            this.rations -= totalRationsUpkeep;
            logs.push(`식량을 정상 배급했습니다. (남은 식량: ${this.rations})`);
        } else {
            const lack = totalRationsUpkeep - this.rations;
            this.rations = 0;
            starvation = true;
            logs.push(`<span class="text-red">⚠️ 식량 부족으로 배급 실패! 용병단이 굶주립니다!</span>`);
        }

        let unpaid = false;
        if (this.gold >= totalGoldUpkeep) {
            this.gold -= totalGoldUpkeep;
            logs.push(`용병 주급을 지불했습니다. (남은 골드: ${this.gold})`);
        } else {
            const lack = totalGoldUpkeep - this.gold;
            this.gold = 0;
            unpaid = true;
            logs.push(`<span class="text-red">⚠️ 골드가 부족해 주급이 미지급되었습니다! 사기가 크게 저하됩니다!</span>`);
        }

        // Update each mercenary stats
        const retired = [];
        mercenaries.forEach(m => {
            let moraleChange = starvation ? -15 : 2;
            if (unpaid) moraleChange -= 20;

            if (m.positiveTrait === "낙천적") moraleChange += 2;
            if (m.negativeTrait === "탈영병") moraleChange -= 2;

            m.morale = Math.max(0, Math.min(100, m.morale + moraleChange));
            m.corruption = Math.max(0, Math.min(100, m.corruption + (starvation ? 10 : 0)));

            // State ticks
            if (m.states.includes("독")) {
                const dmg = Math.round(m.maxHp * 0.15);
                m.hp = Math.max(1, m.hp - dmg);
                logs.push(`<span class="text-red">💀 ${m.name}이(가) 중독 피해로 HP가 ${dmg} 감소했습니다.</span>`);
            }

            if (m.morale <= 0) {
                const leaveChance = m.negativeTrait === "겁쟁이" ? 0.40 : 0.25;
                if (Math.random() < leaveChance) {
                    logs.push(`<span class="text-red">🏃 [이탈] 사기가 바닥난 ${m.name}(${m.mClass})이(가) 용병단을 탈퇴하여 떠났습니다.</span>`);
                    retired.push(m);
                }
            }

            if (m.corruption >= 100) {
                logs.push(`<span class="text-red">👹 [타락] ${m.name}의 정신이 완전히 붕괴되어 광분하며 어둠 속으로 도망쳤습니다!</span>`);
                retired.push(m);
            }
        });

        retired.forEach(m => {
            const idx = mercenaries.indexOf(m);
            if (idx > -1) mercenaries.splice(idx, 1);
        });

        this.day += 1;
        return logs;
    }
}
