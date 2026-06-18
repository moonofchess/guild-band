import { GameEngine } from './engine.js';
import { Mercenary, BaseCamp, ResourceManager, CLASSES, POSITIVE_TRAITS, NEGATIVE_TRAITS } from './game_state.js';

// Global Game State
const camp = new BaseCamp();
const resources = new ResourceManager();
const mercenaries = [
    new Mercenary("카엘", "전사", "D"),
    new Mercenary("로익", "척후병", "E"),
    new Mercenary("실비아", "사제", "F")
];

// Class emoji mapping (portrait fallback)
const CLASS_EMOJI = {
    '전사': '⚔️', '척후병': '🗡️', '마법사': '🔥', '사제': '✨',
};
function setPortraitFallback(el, mClass, portraitFile) {
    if (!portraitFile) { el.textContent = CLASS_EMOJI[mClass] || '👤'; return; }
    const img = new Image();
    img.onload = () => {
        el.style.backgroundImage = `url('assets/${portraitFile}')`;
        el.textContent = '';
    };
    img.onerror = () => { el.textContent = CLASS_EMOJI[mClass] || '👤'; };
    img.src = `assets/${portraitFile}`;
}

// Active expedition configurations
let selectedStage = 'forest';
let selectedSquad = []; // list of mercenary indexes
let activeBattle = null;

// Initialize Render Canvas Engine
const engine = new GameEngine('game-canvas');
engine.loop();

// Initial UI bindings (ES module is deferred — DOM is ready at this point)
updateTopBar();
renderGuildList();
updateCampBackground();

// ─── In-game Toast Notification (replaces alert()) ───
let _toastTimer = null;
function showToast(msg, type = 'normal') {
    const el = document.getElementById('game-toast');
    el.innerHTML = msg;
    el.className = type === 'error' ? 'toast-error' : type === 'success' ? 'toast-success' : '';
    el.classList.remove('hidden');
    if (_toastTimer) clearTimeout(_toastTimer);
    _toastTimer = setTimeout(() => el.classList.add('hidden'), 2800);
}

// UI helpers
function updateTopBar() {
    document.getElementById("res-day").innerText = resources.day;
    document.getElementById("res-gold").innerText = resources.gold;
    document.getElementById("res-rations").innerText = resources.rations;
    document.getElementById("res-loot").innerText = resources.monsterLoot;
}

const BG_GRADIENTS = {
    lordhall:   'linear-gradient(160deg, #0e0c1a 0%, #1a1530 50%, #0a0810 100%)',
    magicarray: 'linear-gradient(160deg, #070a1a 0%, #0d1535 50%, #1a0a2a 100%)',
    blacksmith: 'linear-gradient(160deg, #140c05 0%, #2a1a08 50%, #0f0a04 100%)',
    tavern:     'linear-gradient(160deg, #140a05 0%, #2a1808 50%, #1a1005 100%)',
    sanctum:    'linear-gradient(160deg, #0a0e14 0%, #101828 50%, #0a1418 100%)',
    expedition: 'linear-gradient(160deg, #0a0d05 0%, #1a1e08 50%, #0a0d05 100%)',
    camp_ruined:   'linear-gradient(160deg, #0d0a18 0%, #13101f 40%, #0a0a10 100%)',
    camp_restored: 'linear-gradient(160deg, #0d1018 0%, #131820 40%, #0a0e10 100%)',
};

function updateCampBackground() {
    const key = camp.lordHallLevel === 1 ? 'camp_ruined' : 'camp_restored';
    const bgFile = camp.lordHallLevel === 1 ? 'bg_base_ruined.png' : 'bg_base_restored.png';
    const container = document.getElementById("game-container");
    const img = new Image();
    img.onload = () => { container.style.background = `url('assets/${bgFile}') center/cover no-repeat`; };
    img.onerror = () => { container.style.background = BG_GRADIENTS[key]; };
    img.src = `assets/${bgFile}`;
}

function renderGuildList() {
    const listDiv = document.getElementById("guild-merc-list");
    listDiv.innerHTML = "";
    
    document.getElementById("merc-count").innerText = mercenaries.length;
    document.getElementById("merc-max").innerText = camp.getMaxMercenaries();

    mercenaries.forEach((m, idx) => {
        const hpPct = (m.hp / m.maxHp) * 100;
        const mpPct = m.maxMp > 0 ? (m.mp / m.maxMp) * 100 : 0;
        
        let stateBadges = "";
        m.states.forEach(s => {
            stateBadges += `<span class="state-badge">${s}</span>`;
        });

        const card = document.createElement("div");
        card.className = "merc-card";
        card.innerHTML = `
            <div class="merc-portrait" data-portrait="${m.portrait}" data-class="${m.mClass}"></div>
            <div class="merc-info">
                <div class="merc-name-row">
                    <span class="merc-name">${m.name} (${m.mClass})</span>
                    <span class="merc-rank">${m.rank}</span>
                </div>
                <div class="merc-stats">
                    HP: ${m.hp}/${m.maxHp}
                    <div class="stat-bar"><div class="bar-fill-hp" style="width: ${hpPct}%"></div></div>
                    ${m.maxMp > 0 ? `MP: ${m.mp}/${m.maxMp}<div class="stat-bar"><div class="bar-fill-mp" style="width: ${mpPct}%"></div></div>` : ''}
                    사기: ${m.morale}/100 | 타락: ${m.corruption}/100
                </div>
                <div class="merc-states-row">${stateBadges}</div>
            </div>
        `;
        listDiv.appendChild(card);
        // Apply portrait with fallback after DOM insertion
        setPortraitFallback(card.querySelector('.merc-portrait'), m.mClass, m.portrait);
    });
}

// Tab switcher & dynamic UI renderers
window.switchTab = (tab) => {
    // Show overlay
    document.getElementById("tab-overlay").classList.remove("hidden");
    
    // Hide all tab panes
    const panes = document.querySelectorAll(".tab-pane");
    panes.forEach(p => p.classList.add("hidden"));
    
    // Show active pane
    const activePane = document.getElementById(`tab-${tab}`);
    if (activePane) activePane.classList.remove("hidden");

    // Dynamic background changes when entering tabs
    const TAB_BG = {
        lordhall:  { file: 'bg_hall.png',         key: 'lordhall' },
        magicarray:{ file: 'bg_magic_array.png',   key: 'magicarray' },
        blacksmith:{ file: 'bg_blacksmith.png',    key: 'blacksmith' },
        tavern:    { file: 'bg_tavern.png',         key: 'tavern' },
        sanctum:   { file: 'bg_sanctum.png',        key: 'sanctum' },
        expedition:{ file: 'bg_event_campfire.png', key: 'expedition' },
    };
    const container = document.getElementById("game-container");
    if (TAB_BG[tab]) {
        const { file, key } = TAB_BG[tab];
        const img = new Image();
        img.onload = () => { container.style.background = `url('assets/${file}') center/cover no-repeat`; };
        img.onerror = () => { container.style.background = BG_GRADIENTS[key] || BG_GRADIENTS['camp_ruined']; };
        img.src = `assets/${file}`;
    }
    if (tab === 'magicarray') renderRecruitTab();
    if (tab === 'blacksmith') renderBlacksmithTab();
    if (tab === 'tavern')     renderTavernTab();
    if (tab === 'sanctum')    renderSanctumTab();
    if (tab === 'expedition') renderExpeditionTab();
};

window.closeOverlay = () => {
    document.getElementById("tab-overlay").classList.add("hidden");
    // Restore default background
    updateCampBackground();
    renderGuildList();
};

// Facility upgrades
window.upgradeFacility = (facility) => {
    let cost = { gold: 0, loot: 0 };
    let lvl = 0;
    
    if (facility === 'lordhall') {
        lvl = camp.lordHallLevel;
        if (lvl === 1) cost = { gold: 200, loot: 10 };
        else if (lvl === 2) cost = { gold: 500, loot: 30 };
    } else if (facility === 'magicarray') {
        lvl = camp.magicArrayLevel;
        if (lvl === 1) cost = { gold: 150, loot: 10 };
        else if (lvl === 2) cost = { gold: 350, loot: 25 };
    } else if (facility === 'blacksmith') {
        lvl = camp.blacksmithLevel;
        if (lvl === 1) cost = { gold: 150, loot: 15 };
        else if (lvl === 2) cost = { gold: 350, loot: 30 };
    } else if (facility === 'tavern') {
        lvl = camp.tavernLevel;
        if (lvl === 1) cost = { gold: 100, loot: 8 };
        else if (lvl === 2) cost = { gold: 250, loot: 20 };
    } else if (facility === 'sanctum') {
        lvl = camp.sanctumLevel;
        if (lvl === 1) cost = { gold: 150, loot: 15 };
        else if (lvl === 2) cost = { gold: 400, loot: 30 };
    }

    if (lvl >= 3) {
        showToast("이미 최고 레벨(3)입니다!", 'error');
        return;
    }

    if (resources.gold < cost.gold || resources.monsterLoot < cost.loot) {
        showToast("업그레이드 비용이 부족합니다! (골드 또는 마수 부산물 부족)", 'error');
        return;
    }

    resources.gold -= cost.gold;
    resources.monsterLoot -= cost.loot;
    
    if (facility === 'lordhall') camp.lordHallLevel++;
    if (facility === 'magicarray') camp.magicArrayLevel++;
    if (facility === 'blacksmith') camp.blacksmithLevel++;
    if (facility === 'tavern') camp.tavernLevel++;
    if (facility === 'sanctum') camp.sanctumLevel++;

    updateTopBar();
    showToast("시설이 성공적으로 업그레이드되었습니다!", 'success');
    
    // Update upgrade pane
    document.getElementById("lvl-lordhall").innerText = camp.lordHallLevel;
    document.getElementById("lvl-magicarray").innerText = camp.magicArrayLevel;
    document.getElementById("lvl-blacksmith").innerText = camp.blacksmithLevel;
    document.getElementById("lvl-tavern").innerText = camp.tavernLevel;
    document.getElementById("lvl-sanctum").innerText = camp.sanctumLevel;
};

// 1. RECRUITMENT LOGIC
window.rollRecruits = () => {
    const res = camp.rollRecruits(resources);
    updateTopBar();
    if (res.success) {
        renderRecruitTab();
        showToast(res.msg, 'success');
    } else {
        showToast(res.msg, 'error');
    }
};

function renderRecruitTab() {
    const list = document.getElementById("recruits-pool-list");
    list.innerHTML = "";
    
    if (camp.recruitsPool.length === 0) {
        list.innerHTML = `<p style="grid-column: 1/4; text-align: center; color: var(--text-gray); padding: 40px;">마법 신호를 감지하려면 [신호 탐색 가동] 버튼을 누르세요.</p>`;
        return;
    }

    camp.recruitsPool.forEach((rec, idx) => {
        const hireCost = rec.getWeeklySalary() * 2;
        const posTrait = POSITIVE_TRAITS[rec.positiveTrait];
        const negTrait = NEGATIVE_TRAITS[rec.negativeTrait];

        const card = document.createElement("div");
        card.className = "recruit-card";
        card.innerHTML = `
            <div>
                <h3>${rec.name} (${rec.mClass})</h3>
                <div class="recruit-details">
                    <div class="recruit-stat-row"><span>등급:</span> <span class="merc-rank">${rec.rank}</span></div>
                    <div class="recruit-stat-row"><span>주급:</span> <span>💰 ${rec.getWeeklySalary()}</span></div>
                    <div class="recruit-stat-row"><span>최대 HP:</span> <span>${rec.maxHp}</span></div>
                    <div class="recruit-stat-row"><span>공격력:</span> <span>${rec.atk}</span></div>
                    <div class="trait-desc trait-good"><b>[${rec.positiveTrait}]</b> ${posTrait.desc}</div>
                    <div class="trait-desc trait-bad"><b>[${rec.negativeTrait}]</b> ${negTrait.desc}</div>
                </div>
            </div>
            <button class="action-btn" onclick="hireRecruit(${idx})" style="width: 100%; margin-top: 15px;">고용 (💰 ${hireCost}골드)</button>
        `;
        list.appendChild(card);
    });
}

window.hireRecruit = (idx) => {
    if (mercenaries.length >= camp.getMaxMercenaries()) {
        showToast("용병단 인원이 꽉 찼습니다! (영주실을 업그레이드하세요)", 'error');
        return;
    }

    const recruit = camp.recruitsPool[idx];
    const cost = recruit.getWeeklySalary() * 2;

    if (resources.gold < cost) {
        showToast(`고용 골드가 부족합니다! (필요: ${cost}골드)`, 'error');
        return;
    }

    resources.gold -= cost;
    mercenaries.push(recruit);
    camp.recruitsPool.splice(idx, 1);
    
    updateTopBar();
    renderRecruitTab();
    showToast(`${recruit.name}을(를) 용병단으로 영입했습니다!`, 'success');
};

// 2. BLACKSMITH LOGIC
function renderBlacksmithTab() {
    const list = document.getElementById("blacksmith-merc-list");
    list.innerHTML = "";

    mercenaries.forEach((m, idx) => {
        const wCost = (m.weaponLevel + 1) * 30;
        const wLootCost = (m.weaponLevel + 1) * 2;
        const aCost = (m.armorLevel + 1) * 30;
        const aLootCost = (m.armorLevel + 1) * 2;
        const maxLevel = camp.blacksmithLevel * 2;

        const card = document.createElement("div");
        card.className = "facility-card";
        card.innerHTML = `
            <div class="merc-portrait" data-portrait="${m.portrait}" data-class="${m.mClass}"></div>
            <div class="facility-card-info">
                <div>
                    <h4>${m.name} (${m.mClass})</h4>
                    <p>공격력: ${m.atk} (무기 +${m.weaponLevel})</p>
                    <p>방어력: ${m.def} (방어구 +${m.armorLevel})</p>
                </div>
                <div class="facility-card-actions">
                    <button class="action-btn" onclick="upgradeGear(${idx}, 'weapon')" ${m.weaponLevel >= maxLevel ? 'disabled' : ''}>
                        무기강화 ${m.weaponLevel >= maxLevel ? '(최대)' : `(💰${wCost}, 🦴${wLootCost})`}
                    </button>
                    <button class="action-btn" onclick="upgradeGear(${idx}, 'armor')" ${m.armorLevel >= maxLevel ? 'disabled' : ''}>
                        갑옷강화 ${m.armorLevel >= maxLevel ? '(최대)' : `(💰${aCost}, 🦴${aLootCost})`}
                    </button>
                </div>
            </div>
        `;
        list.appendChild(card);
        setPortraitFallback(card.querySelector('.merc-portrait'), m.mClass, m.portrait);
    });
}

window.upgradeGear = (idx, type) => {
    const m = mercenaries[idx];
    const maxLevel = camp.blacksmithLevel * 2;

    if (type === 'weapon') {
        const cost = (m.weaponLevel + 1) * 30;
        const lootCost = (m.weaponLevel + 1) * 2;
        if (m.weaponLevel >= maxLevel) return;
        if (resources.gold < cost || resources.monsterLoot < lootCost) {
            showToast(`강화 자원이 부족합니다! (필요: 💰${cost}, 🦴${lootCost})`, 'error');
            return;
        }
        resources.gold -= cost;
        resources.monsterLoot -= lootCost;
        m.weaponLevel++;
        m.atk += 3;
        showToast(`${m.name}의 무기를 강화했습니다! (+${m.weaponLevel})`, 'success');
    } else {
        const cost = (m.armorLevel + 1) * 30;
        const lootCost = (m.armorLevel + 1) * 2;
        if (m.armorLevel >= maxLevel) return;
        if (resources.gold < cost || resources.monsterLoot < lootCost) {
            showToast(`강화 자원이 부족합니다! (필요: 💰${cost}, 🦴${lootCost})`, 'error');
            return;
        }
        resources.gold -= cost;
        resources.monsterLoot -= lootCost;
        m.armorLevel++;
        m.def += 2;
        m.maxHp += 10;
        m.hp += 10;
        showToast(`${m.name}의 갑옷을 강화했습니다! (+${m.armorLevel})`, 'success');
    }

    updateTopBar();
    renderBlacksmithTab();
};

// 3. TAVERN LOGIC
function renderTavernTab() {
    const list = document.getElementById("tavern-merc-list");
    list.innerHTML = "";

    // Add Party Drink option at top
    const drinkCard = document.createElement("div");
    drinkCard.className = "facility-card";
    drinkCard.style.gridColumn = "1/3";
    drinkCard.innerHTML = `
        <div class="facility-card-info">
            <div>
                <h4>🍻 전체 술자리 주선</h4>
                <p>용병단 전체의 사기를 진작시킵니다. (모든 용병 사기 +30)</p>
            </div>
            <div class="facility-card-actions">
                <button class="action-btn" onclick="tavernRest(-1)">술지불 (💰 20골드)</button>
            </div>
        </div>
    `;
    list.appendChild(drinkCard);

    mercenaries.forEach((m, idx) => {
        const card = document.createElement("div");
        card.className = "facility-card";
        card.innerHTML = `
            <div class="merc-portrait" data-portrait="${m.portrait}" data-class="${m.mClass}"></div>
            <div class="facility-card-info">
                <div>
                    <h4>${m.name} (${m.mClass})</h4>
                    <p>사기: ${m.morale} / 100</p>
                </div>
                <div class="facility-card-actions">
                    <button class="action-btn" onclick="tavernRest(${idx})" ${m.morale >= 100 ? 'disabled' : ''}>
                        휴식 정비 (💰 10골드, 사기+50)
                    </button>
                </div>
            </div>
        `;
        list.appendChild(card);
        setPortraitFallback(card.querySelector('.merc-portrait'), m.mClass, m.portrait);
    });
}

window.tavernRest = (idx) => {
    if (idx === -1) {
        if (resources.gold < 20) {
            showToast("골드가 부족합니다! (필요: 💰20)", 'error');
            return;
        }
        resources.gold -= 20;
        mercenaries.forEach(m => m.morale = Math.min(100, m.morale + 30));
        showToast("전체 술자리! 모든 용병 사기 +30", 'success');
    } else {
        if (resources.gold < 10) {
            showToast("골드가 부족합니다! (필요: 💰10)", 'error');
            return;
        }
        const m = mercenaries[idx];
        if (m.morale >= 100) return;
        resources.gold -= 10;
        m.morale = Math.min(100, m.morale + 50);
        showToast(`${m.name} 사기 +50 회복`, 'success');
    }
    
    updateTopBar();
    renderTavernTab();
};

// 4. SANCTUM LOGIC
function renderSanctumTab() {
    const list = document.getElementById("sanctum-merc-list");
    list.innerHTML = "";

    mercenaries.forEach((m, idx) => {
        const isInjured = m.states.includes("부상");
        const isPoisoned = m.states.includes("독") || m.states.includes("출혈") || m.states.includes("저주");

        const card = document.createElement("div");
        card.className = "facility-card";
        card.innerHTML = `
            <div class="merc-portrait" data-portrait="${m.portrait}" data-class="${m.mClass}"></div>
            <div class="facility-card-info">
                <div>
                    <h4>${m.name} (${m.mClass})</h4>
                    <p>상태: ${m.states.length > 0 ? m.states.join(", ") : '정상'}</p>
                    <p>타락도: ${m.corruption} / 100</p>
                </div>
                <div class="facility-card-actions">
                    <button class="action-btn" onclick="sanctumAction(${idx}, 'injury')" ${!isInjured ? 'disabled' : ''}>
                        부상 치료 (💰 50골드)
                    </button>
                    <button class="action-btn" onclick="sanctumAction(${idx}, 'poison')" ${!isPoisoned ? 'disabled' : ''}>
                        상태 치료 (💰 30골드)
                    </button>
                    <button class="action-btn" onclick="sanctumAction(${idx}, 'purify')" ${m.corruption === 0 ? 'disabled' : ''}>
                        타락 정화 (💰 50골드, 타락 -40)
                    </button>
                </div>
            </div>
        `;
        list.appendChild(card);
        setPortraitFallback(card.querySelector('.merc-portrait'), m.mClass, m.portrait);
    });
}

window.sanctumAction = (idx, action) => {
    const m = mercenaries[idx];
    let cost = 50;
    if (action === 'poison') cost = 30;

    if (resources.gold < cost) {
        showToast(`골드가 부족합니다! (필요: 💰${cost})`, 'error');
        return;
    }

    if (action === 'injury') {
        const i = m.states.indexOf("부상");
        if (i > -1) m.states.splice(i, 1);
        m.hp = m.maxHp;
    } else if (action === 'poison') {
        m.states = m.states.filter(s => s !== "독" && s !== "출혈" && s !== "저주");
    } else if (action === 'purify') {
        m.corruption = Math.max(0, m.corruption - 40);
    }

    resources.gold -= cost;
    const msgs = { injury: '부상 치료 완료!', poison: '상태이상 치료 완료!', purify: `${m.name} 타락 정화 완료! (-40)` };
    showToast(msgs[action], 'success');
    updateTopBar();
    renderSanctumTab();
};

// 5. EXPEDITION TAB AND SQUAD BUILDING
function renderExpeditionTab() {
    const squadLimit = camp.getSquadSizeLimit();
    document.getElementById("squad-limit").innerText = squadLimit;

    // Reset squad setup if invalid sizes
    selectedSquad = selectedSquad.filter(idx => idx < mercenaries.length);

    const setupList = document.getElementById("squad-setup-list");
    setupList.innerHTML = "";

    mercenaries.forEach((m, idx) => {
        const inSquad = selectedSquad.includes(idx);
        const isBleeding = m.states.includes("출혈");

        const slot = document.createElement("div");
        slot.className = `squad-slot ${inSquad ? 'filled' : ''}`;
        slot.innerHTML = `
            <div>
                <strong>${m.name} (${m.mClass})</strong> - Rank ${m.rank}
                <br><small>HP: ${m.hp}/${m.maxHp} | 사기: ${m.morale}</small>
            </div>
            <button class="action-btn" onclick="toggleSquadSlot(${idx})" ${isBleeding ? 'disabled' : ''}>
                ${inSquad ? '해제' : '편성'}
            </button>
        `;
        setupList.appendChild(slot);
    });
}

window.selectStage = (el, stage) => {
    selectedStage = stage;
    document.querySelectorAll(".stage-card").forEach(c => c.classList.remove("active"));
    el.classList.add("active");
};

window.toggleSquadSlot = (idx) => {
    const limit = camp.getSquadSizeLimit();
    const pos = selectedSquad.indexOf(idx);

    if (pos > -1) {
        selectedSquad.splice(pos, 1);
    } else {
        if (selectedSquad.length >= limit) {
            showToast(`분대 편성 한계입니다! (최대 ${limit}명)`, 'error');
            return;
        }
        selectedSquad.push(idx);
    }
    renderExpeditionTab();
};

// 6. TURN UPKEEP PROGRESSION
window.nextDay = () => {
    const logs = resources.advanceDay(mercenaries);
    updateTopBar();
    renderGuildList();
    closeOverlay();

    // Show result logs in a popup dialog
    showEventPopup("하루 경과 결산 보고", logs.join("<br>"), [
        { text: "확인", action: () => closeEventPopup() }
    ]);
};

// Global Event Popup helper
function showEventPopup(title, content, options) {
    const ev = document.getElementById("event-overlay");
    document.getElementById("event-title").innerHTML = title;
    document.getElementById("event-content").innerHTML = content;
    
    const act = document.getElementById("event-actions");
    act.innerHTML = "";
    
    options.forEach(opt => {
        const btn = document.createElement("button");
        btn.className = "action-btn";
        btn.innerText = opt.text;
        btn.onclick = () => {
            opt.action();
        };
        act.appendChild(btn);
    });
    ev.classList.remove("hidden");
}

window.closeEventPopup = () => {
    document.getElementById("event-overlay").classList.add("hidden");
};


// 7. BATTLE CODE (COMBAT SYSTEM INTEGRATION)
class WebMonster {
    constructor(name, hp, atk, def, sheet, scale = 1.2) {
        this.name = name;
        this.maxHp = hp;
        this.hp = hp;
        this.atk = atk;
        this.def = def;
        this.sheet = sheet;
        this.scale = scale;
        this.stunned_turns = 0;
        this.states = [];
    }
    isAlive() { return this.hp > 0; }
    takeDamage(amount) {
        const actual = Math.max(1, amount - this.def);
        this.hp = Math.max(0, this.hp - actual);
        return actual;
    }
}

window.beginBattle = () => {
    if (selectedSquad.length === 0) {
        showToast("전투에 출전할 용병을 최소 1명 이상 선택하세요!", 'error');
        return;
    }

    // Close overlays
    closeOverlay();

    // Setup Enemies based on stage
    let enemiesData = [];
    let bgAsset = 'bg_battle_forest.png';
    
    if (selectedStage === 'forest') {
        bgAsset = 'bg_battle_forest.png';
        enemiesData = [
            new WebMonster("고블린 A", 50, 12, 3, "mob_goblin_sheet.png", 1.2),
            new WebMonster("고블린 B", 50, 12, 3, "mob_goblin_sheet.png", 1.2)
        ];
    } else if (selectedStage === 'ruins') {
        bgAsset = 'bg_battle_ruins.png';
        enemiesData = [
            new WebMonster("고블린 대장", 70, 15, 5, "mob_goblin_sheet.png", 1.3),
            new WebMonster("스켈레톤 궁수 A", 60, 16, 3, "mob_skeleton_sheet.png", 1.2),
            new WebMonster("스켈레톤 궁수 B", 60, 16, 3, "mob_skeleton_sheet.png", 1.2)
        ];
    } else if (selectedStage === 'dungeon') {
        bgAsset = 'bg_battle_dungeon.png';
        enemiesData = [
            new WebMonster("스켈레톤 초병", 60, 16, 3, "mob_skeleton_sheet.png", 1.2),
            new WebMonster("이단심문관 (보스)", 140, 22, 8, "mob_inquisitor_sheet.png", 1.3),
            new WebMonster("살점 골렘 (보스)", 260, 32, 12, "mob_golem_sheet.png", 1.5)
        ];
    }

    // Hide base UI screen elements
    document.getElementById("camp-screen").classList.add("hidden");
    document.getElementById("combat-overlay").classList.remove("hidden");

    // Enable canvas pointer events for target selection
    document.getElementById("game-canvas").style.pointerEvents = "auto";

    // Start engine combat mode
    engine.clear();
    engine.isCombat = true;
    engine.setBattleBackground(`assets/${bgAsset}`);

    // Map squad mercenaries to combat logic
    const squadAllies = selectedSquad.map(idx => mercenaries[idx]);
    
    activeBattle = {
        allies: squadAllies,
        enemies: enemiesData,
        cp: 5,
        maxCp: 10,
        turn: 1,
        activeAllyIdx: 0,
        leaderUsed: false,
        formation: {} // Map ally to '전열' or '후열'
    };

    // Initialize formations
    activeBattle.allies.forEach(m => {
        m.currentAp = m.maxAp;
        activeBattle.formation[m.name] = (m.mClass === "전사" || m.mClass === "척후병") ? "전열" : "후열";
    });

    // Spawn Sprites on Canvas
    // Ally positions (Left side)
    activeBattle.allySprites = activeBattle.allies.map((m, i) => {
        const x = 200 + (activeBattle.formation[m.name] === "전열" ? 100 : 0);
        const y = 320 + i * 110;
        return engine.spawnSprite(`assets/${m.assetName}`, x, y, 1.2, false, m);
    });

    // Enemy positions (Right side — kept clear of log panel on far right)
    activeBattle.enemySprites = activeBattle.enemies.map((e, i) => {
        const x = 820 - (i % 2 === 0 ? 0 : 70);
        const y = 300 + i * 110;
        return engine.spawnSprite(`assets/${e.sheet}`, x, y, -e.scale, true, e);
    });

    addCombatLog("⚔️ 토벌 구역 침투 성공! 전투가 시작되었습니다.", "system");
    selectActiveMercenary(0);
    updateCombatUI();
};

function updateCombatUI() {
    if (!activeBattle) return;
    document.getElementById("combat-cp").innerText = activeBattle.cp;
    document.getElementById("combat-turn-text").innerText = `TURN ${activeBattle.turn}`;

    const activeMerc = activeBattle.allies[activeBattle.activeAllyIdx];
    if (activeMerc) {
        document.getElementById("active-merc-name").innerText = activeMerc.name;
        document.getElementById("active-merc-class").innerText = `${activeMerc.mClass} (${activeBattle.formation[activeMerc.name]})`;
        document.getElementById("active-merc-ap").innerText = `${activeMerc.currentAp} / ${activeMerc.maxAp}`;
        document.getElementById("active-merc-mp").innerText = `${activeMerc.mp} / ${activeMerc.maxMp}`;
        
        setPortraitFallback(document.getElementById("active-merc-p-img"), activeMerc.mClass, activeMerc.portrait);

        const skillBtn = document.getElementById("btn-class-skill");
        if (activeMerc.mClass === '전사') skillBtn.innerText = "🛡️ 방패 충격 (AP 2)";
        if (activeMerc.mClass === '척후병') skillBtn.innerText = "🗡️ 급소 찌르기 (AP 2)";
        if (activeMerc.mClass === '마법사') skillBtn.innerText = "🔥 화염 폭발 (AP 3, MP 15)";
        if (activeMerc.mClass === '사제') skillBtn.innerText = "✨ 성스러운 치유 (AP 2, MP 10)";
    }

    // Update ally switch panel
    const switchPanel = document.getElementById("ally-switch-panel");
    switchPanel.innerHTML = "";
    activeBattle.allies.forEach((m, idx) => {
        const isDead = m.states.includes("출혈");
        const btn = document.createElement("button");
        btn.className = `ally-switch-btn${idx === activeBattle.activeAllyIdx ? ' active-ally' : ''}`;
        btn.disabled = isDead;
        btn.innerText = `${m.name} AP:${m.currentAp}/${m.maxAp}`;
        if (!isDead) btn.onclick = () => selectActiveMercenary(idx);
        switchPanel.appendChild(btn);
    });
}

function selectActiveMercenary(idx) {
    if (!activeBattle) return;
    activeBattle.activeAllyIdx = idx;
    
    // Clear selection outlines
    activeBattle.allySprites.forEach(s => s.isSelected = false);
    
    if (activeBattle.allySprites[idx]) {
        activeBattle.allySprites[idx].isSelected = true;
    }
    updateCombatUI();
}

function addCombatLog(msg, type = "normal") {
    const list = document.getElementById("battle-log-entries");
    const entry = document.createElement("div");
    entry.className = `log-entry log-${type}`;
    entry.innerHTML = msg;
    list.appendChild(entry);
    list.scrollTop = list.scrollHeight;
}

// 8. COMBAT ACTION COMMAND HANDLERS
window.combatAction = (action) => {
    if (!activeBattle) return;
    const activeMerc = activeBattle.allies[activeBattle.activeAllyIdx];

    if (action === "end-turn") {
        addCombatLog("🔔 턴을 종료했습니다. 적들의 반격이 시작됩니다.", "system");
        executeEnemyTurn();
        return;
    }

    if (action === "retreat") {
        if (Math.random() < 0.5) {
            addCombatLog("🏃 연막탄 투하! 전투에서 긴급 탈출했습니다.", "system");
            handleBattleFinish(false, true); // Retreat
        } else {
            addCombatLog("❌ 도망칠 수 없습니다! 마수가 경로를 밀폐 차단했습니다!", "enemy");
            // End player actions and execute enemy turn directly as a penalty
            executeEnemyTurn();
        }
        return;
    }

    if (activeMerc.currentAp <= 0) {
        showToast("행동력(AP)이 부족합니다! 턴을 종료하거나 다른 용병을 선택하세요.", 'error');
        return;
    }

    // Trigger targets select mode
    if (action === "attack") {
        // Target selection
        promptTargetSelect("적을 공격하세요.", (enemyIdx) => {
            executePlayerAttack(activeMerc, enemyIdx);
        });
    }

    if (action === "skill") {
        if (activeMerc.mClass === '전사') {
            if (activeMerc.currentAp < 2) { showToast("AP 부족! (필요 AP: 2)", 'error'); return; }
            promptTargetSelect("방패로 기절시킬 적을 선택하세요.", (enemyIdx) => {
                executeWarriorSkill(activeMerc, enemyIdx);
            });
        }
        if (activeMerc.mClass === '척후병') {
            if (activeMerc.currentAp < 2) { showToast("AP 부족! (필요 AP: 2)", 'error'); return; }
            promptTargetSelect("급소 찌르기 대상을 선택하세요.", (enemyIdx) => {
                executeScoutSkill(activeMerc, enemyIdx);
            });
        }
        if (activeMerc.mClass === '마법사') {
            if (activeMerc.currentAp < 3) { showToast("AP 부족! (필요 AP: 3)", 'error'); return; }
            if (activeMerc.mp < 15) { showToast("MP 부족! (필요 MP: 15)", 'error'); return; }
            executeMageSkill(activeMerc);
        }
        if (activeMerc.mClass === '사제') {
            if (activeMerc.currentAp < 2) { showToast("AP 부족! (필요 AP: 2)", 'error'); return; }
            if (activeMerc.mp < 10) { showToast("MP 부족! (필요 MP: 10)", 'error'); return; }
            promptAllySelect("치유 성광을 부여할 아군을 선택하세요.", (allyIdx) => {
                executePriestSkill(activeMerc, allyIdx);
            });
        }
    }
};

function promptTargetSelect(promptText, onSelect) {
    addCombatLog(`🎯 [지정 요망] ${promptText}`, "system");

    const targets = [];
    activeBattle.enemySprites.forEach((s, idx) => {
        if (s.data.isAlive()) {
            s.isSelected = true;
            targets.push({ sprite: s, idx });
        }
    });

    registerCanvasClick(targets, onSelect);
}

function promptAllySelect(promptText, onSelect) {
    addCombatLog(`🎯 [아군 지정 요망] ${promptText}`, "system");

    const targets = [];
    activeBattle.allySprites.forEach((s, idx) => {
        if (s.data.hp > 0) {
            s.isSelected = true;
            targets.push({ sprite: s, idx });
        }
    });

    registerCanvasClick(targets, onSelect);
}

let canvasClickHandler = null;

// Attach to combat-overlay (z-index 10) not the canvas (z-index 2)
// — the overlay sits on top and intercepts all clicks in the battle area.
function registerCanvasClick(targets, onSelect) {
    const canvas = document.getElementById("game-canvas");
    // combat-overlay covers the whole screen at z-index 10 and receives all clicks
    const hitArea = document.getElementById("combat-overlay");

    if (canvasClickHandler) {
        hitArea.removeEventListener("mousedown", canvasClickHandler);
        canvasClickHandler = null;
    }

    canvasClickHandler = (e) => {
        // Ignore clicks on UI panels (controls, log) — only handle canvas-area clicks
        if (e.target.closest("#combat-controls-panel") ||
            e.target.closest("#battle-log-console")) return;

        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width  / rect.width;
        const scaleY = canvas.height / rect.height;
        const x = (e.clientX - rect.left) * scaleX;
        const y = (e.clientY - rect.top)  * scaleY;

        for (const { sprite, idx } of targets) {
            const dx = x - sprite.x;
            const dy = y - sprite.y;
            // Generous hitbox: 90×100 pixels
            if (Math.abs(dx) < 90 && Math.abs(dy) < 100) {
                hitArea.removeEventListener("mousedown", canvasClickHandler);
                canvasClickHandler = null;
                clearSelectors();
                onSelect(idx);
                return;
            }
        }
    };

    hitArea.addEventListener("mousedown", canvasClickHandler);
}

function clearSelectors() {
    activeBattle.enemySprites.forEach(s => s.isSelected = false);
    activeBattle.allySprites.forEach(s => s.isSelected = false);
    
    // Reselect active merc cursor
    if (activeBattle.allySprites[activeBattle.activeAllyIdx]) {
        activeBattle.allySprites[activeBattle.activeAllyIdx].isSelected = true;
    }
}

// 9. DAMAGE / ACTION EXECUTION DETAILS
function executePlayerAttack(merc, enemyIdx) {
    const targetSprite = activeBattle.enemySprites[enemyIdx];
    const target = targetSprite.data;
    const attackerSprite = activeBattle.allySprites[activeBattle.activeAllyIdx];

    merc.currentAp -= 1;
    attackerSprite.setAnimation("attack");

    // Hit check (Evasion)
    const hitRate = merc.negativeTrait === "애꾸눈" ? 0.70 : 0.85;
    if (Math.random() > hitRate) {
        addCombatLog(`💨 ${merc.name}의 일반 일격이 허공을 갈랐습니다! (빗나감)`, "normal");
        updateCombatUI();
        return;
    }

    // Slash VFX
    engine.spawnVfx("assets/vfx_slash.png", targetSprite.x, targetSprite.y, 100, 4);

    setTimeout(() => {
        targetSprite.shakeTimer = 200;
        targetSprite.setAnimation("hit");
        
        let dmg = merc.atk;
        // Crit check
        let isCrit = false;
        if (merc.morale >= 70 && Math.random() < 0.25) {
            dmg = Math.round(dmg * 1.5);
            isCrit = true;
        }
        
        const damageDealt = target.takeDamage(dmg);
        engine.spawnFloatingText(damageDealt + (isCrit ? " Crit!" : ""), targetSprite.x, targetSprite.y - 30, isCrit ? '#f1c40f' : '#ff5252');
        addCombatLog(`⚔️ ${merc.name}이(가) ${target.name}에게 ${damageDealt} 물리 피해를 줬습니다.`, "player");

        checkBattleStatus();
        updateCombatUI();
    }, 200);
}

function executeWarriorSkill(merc, enemyIdx) {
    const targetSprite = activeBattle.enemySprites[enemyIdx];
    const target = targetSprite.data;
    const attackerSprite = activeBattle.allySprites[activeBattle.activeAllyIdx];

    merc.currentAp -= 2;
    attackerSprite.setAnimation("attack");
    
    // Slash VFX
    engine.spawnVfx("assets/vfx_slash.png", targetSprite.x, targetSprite.y, 110, 4);

    setTimeout(() => {
        targetSprite.shakeTimer = 300;
        targetSprite.setAnimation("hit");
        
        let dmg = Math.round(merc.atk * 1.25);
        const damageDealt = target.takeDamage(dmg);
        engine.spawnFloatingText(damageDealt.toString(), targetSprite.x, targetSprite.y - 30, '#ff5252');
        addCombatLog(`🛡️ [방패 충격] ${merc.name}이(가) 방패로 ${target.name}을 강타하여 ${damageDealt} 피해를 입혔습니다!`, "player");

        // Stun roll
        if (Math.random() < 0.40) {
            target.stunned_turns = Math.max(target.stunned_turns, 1);
            engine.spawnVfx("assets/vfx_status_stun.png", targetSprite.x, targetSprite.y - 60, 48, 1, 800);
            addCombatLog(`💫 ${target.name}이(가) 1턴간 [기절]했습니다!`, "system");
        }

        checkBattleStatus();
        updateCombatUI();
    }, 200);
}

function executeScoutSkill(merc, enemyIdx) {
    const targetSprite = activeBattle.enemySprites[enemyIdx];
    const target = targetSprite.data;
    const attackerSprite = activeBattle.allySprites[activeBattle.activeAllyIdx];

    merc.currentAp -= 2;
    attackerSprite.setAnimation("attack");
    engine.spawnVfx("assets/vfx_slash.png", targetSprite.x, targetSprite.y, 90, 4);

    setTimeout(() => {
        targetSprite.shakeTimer = 250;
        targetSprite.setAnimation("hit");
        
        // Pierce defense
        const origDef = target.def;
        target.def = Math.round(origDef * 0.5); // ignore 50%
        let dmg = Math.round(merc.atk * 1.4);
        
        const damageDealt = target.takeDamage(dmg);
        target.def = origDef; // restore
        
        engine.spawnFloatingText(damageDealt.toString(), targetSprite.x, targetSprite.y - 30, '#ff3333');
        addCombatLog(`🗡️ [급소 찌르기] ${merc.name}이(가) ${target.name}에게 방어구 관통 급소 찔러 ${damageDealt} 피해!`, "player");

        checkBattleStatus();
        updateCombatUI();
    }, 200);
}

function executeMageSkill(merc) {
    merc.currentAp -= 3;
    merc.mp -= 15;
    
    const attackerSprite = activeBattle.allySprites[activeBattle.activeAllyIdx];
    attackerSprite.setAnimation("attack");
    
    addCombatLog(`🔥 [화염 폭발] ${merc.name}이(가) 광역 주문 화염 폭사를 캐스팅합니다!`, "player");

    // Spawn fireball projectile flying to center
    const mainTargetSprite = activeBattle.enemySprites.find(s => s.data.isAlive());
    if (!mainTargetSprite) return;

    engine.spawnProjectile("assets/vfx_fireball.png", attackerSprite.x, attackerSprite.y, mainTargetSprite.x, mainTargetSprite.y, 60, 4, 0.6, () => {
        // Impact
        activeBattle.enemySprites.forEach(es => {
            if (es.data.isAlive()) {
                es.shakeTimer = 400;
                es.setAnimation("hit");
                
                const dmg = Math.round(merc.atk * 1.3);
                const damageDealt = es.data.takeDamage(dmg);
                engine.spawnFloatingText(damageDealt.toString(), es.x, es.y - 30, '#e67e22');
                engine.spawnVfx("assets/vfx_fireball.png", es.x, es.y, 120, 4, 500); // Explode vfx
            }
        });
        addCombatLog("🔥 대폭발로 적군 전체가 화마의 격통에 휩싸입니다!", "player");
        
        checkBattleStatus();
        updateCombatUI();
    });
}

function executePriestSkill(merc, allyIdx) {
    const targetSprite = activeBattle.allySprites[allyIdx];
    const target = targetSprite.data;
    const attackerSprite = activeBattle.allySprites[activeBattle.activeAllyIdx];

    merc.currentAp -= 2;
    merc.mp -= 10;

    attackerSprite.setAnimation("attack");

    // Heal light beam VFX
    engine.spawnVfx("assets/vfx_heal.png", targetSprite.x, targetSprite.y, 120, 4, 600);

    setTimeout(() => {
        const healAmt = merc.atk * 2.0;
        target.heal(healAmt);
        
        // Remove toxic states
        target.states = target.states.filter(s => s !== "독" && s !== "출혈" && s !== "저주");
        
        engine.spawnFloatingText("+" + healAmt, targetSprite.x, targetSprite.y - 30, '#2ecc71');
        addCombatLog(`✨ [성스러운 치유] ${merc.name}이(가) ${target.name}에게 성광을 내뿜어 HP +${healAmt} 치유 및 해독!`, "player");
        
        updateCombatUI();
    }, 200);
}

// 10. LEADER CP COMMAND SKILLS
window.toggleLeaderSkills = () => {
    if (!activeBattle) return;
    const overlay = document.getElementById("leader-skills-overlay");
    overlay.classList.toggle("hidden");
};

window.useLeaderSkill = (skill) => {
    toggleLeaderSkills();
    if (activeBattle.leaderUsed) {
        showToast("지휘 스킬은 턴당 1회만 기동할 수 있습니다!", 'error');
        return;
    }

    if (skill === 'strike') {
        if (activeBattle.cp < 3) { showToast("CP 부족! (필요 CP: 3)", 'error'); return; }
        promptTargetSelect("지휘 집중 포화를 가할 표적 마수를 지정하세요.", (enemyIdx) => {
            activeBattle.cp -= 3;
            activeBattle.leaderUsed = true;
            
            const targetSprite = activeBattle.enemySprites[enemyIdx];
            const target = targetSprite.data;
            
            addCombatLog(`📢 [단장의 일제 사격 명령!] 전체 아군이 무기를 들고 {${target.name}}을(를) 조준 정렬 사격합니다!`, "system");
            
            // Spawn CP Strike VFX overlay
            engine.spawnVfx("assets/vfx_cp_strike.png", targetSprite.x, targetSprite.y, 160, 4, 600);

            setTimeout(() => {
                targetSprite.shakeTimer = 500;
                targetSprite.setAnimation("hit");
                
                let totalDmg = 0;
                activeBattle.allies.forEach((m, idx) => {
                    if (m.hp > 0 && !m.states.includes("출혈")) {
                        const dmg = Math.round(m.atk * 1.5);
                        totalDmg += target.takeDamage(dmg);
                        activeBattle.allySprites[idx].setAnimation("attack");
                    }
                });
                
                engine.spawnFloatingText(totalDmg.toString(), targetSprite.x, targetSprite.y - 30, '#ff99ff');
                addCombatLog(`💥 집중 공습으로 ${target.name}에게 총 ${totalDmg} 피해를 쏟았습니다!`, "player");
                
                checkBattleStatus();
                updateCombatUI();
            }, 300);
        });
    }

    if (skill === 'buff') {
        if (activeBattle.cp < 2) { showToast("CP 부족! (필요 CP: 2)", 'error'); return; }
        activeBattle.cp -= 2;
        activeBattle.leaderUsed = true;
        
        addCombatLog(`📢 [단장의 사기 진작!] 단장의 사자후가 병사들의 심장을 요동치게 만듭니다!`, "system");
        
        activeBattle.allies.forEach((m, idx) => {
            if (m.hp > 0 && !m.states.includes("출혈")) {
                m.morale = Math.min(100, m.morale + 20);
                m.currentAp = Math.min(m.maxAp + 2, m.currentAp + 2);
                
                const sprite = activeBattle.allySprites[idx];
                engine.spawnVfx("assets/vfx_cp_buff.png", sprite.x, sprite.y, 90, 4, 500);
            }
        });
        addCombatLog("✨ 모든 아군이 사기 +20, 행동력(AP) +2를 보충 받았습니다!", "player");
        updateCombatUI();
    }

    if (skill === 'stun') {
        if (activeBattle.cp < 4) { showToast("CP 부족! (필요 CP: 4)", 'error'); return; }
        activeBattle.cp -= 4;
        activeBattle.leaderUsed = true;
        
        addCombatLog(`📢 [단장의 마력 간섭!] 자기장 과부하로 적군 기동력을 통제 봉쇄합니다!`, "system");
        
        // Screen blast VFX
        engine.spawnVfx("assets/vfx_cp_strike.png", 640, 360, 500, 4, 700);

        activeBattle.enemies.forEach((e, idx) => {
            if (e.isAlive()) {
                e.stunned_turns = Math.max(e.stunned_turns, 1);
                
                const sprite = activeBattle.enemySprites[idx];
                engine.spawnVfx("assets/vfx_status_stun.png", sprite.x, sprite.y - 65, 48, 1, 800);
            }
        });
        addCombatLog("💫 마력 왜곡 폭발! 모든 적군이 1턴 동안 기절하여 행동 불능이 되었습니다!", "player");
        updateCombatUI();
    }
};

// 11. ENEMY AI ACTIONS LOOP
function executeEnemyTurn() {
    // Disable controls overlay during enemy turn
    document.getElementById("combat-controls-panel").style.pointerEvents = "none";
    
    // Play enemy actions sequentially
    let p = Promise.resolve();
    
    activeBattle.enemies.forEach((enemy, idx) => {
        if (enemy.isAlive()) {
            p = p.then(() => {
                return new Promise((resolve) => {
                    const sprite = activeBattle.enemySprites[idx];
                    
                    if (enemy.stunned_turns > 0) {
                        enemy.stunned_turns--;
                        addCombatLog(`💫 {${enemy.name}}은(는) 기절해 있습니다.`, "normal");
                        resolve();
                        return;
                    }

                    // Target Select
                    const aliveAllies = activeBattle.allies.filter(m => m.hp > 0 && !m.states.includes("출혈"));
                    if (aliveAllies.length === 0) {
                        resolve();
                        return;
                    }

                    // Position weight selectors
                    const front = aliveAllies.filter(m => activeBattle.formation[m.name] === "전열");
                    const back = aliveAllies.filter(m => activeBattle.formation[m.name] === "후열");
                    
                    let target = null;
                    let backExposed = false;
                    
                    if (front.length > 0) {
                        if (Math.random() < 0.8) {
                            target = front[Math.floor(Math.random() * front.length)];
                        } else {
                            target = back.length > 0 ? back[Math.floor(Math.random() * back.length)] : front[Math.floor(Math.random() * front.length)];
                        }
                    } else {
                        // frontline collapsed! Target backline directly with +30% penalty
                        target = back.length > 0 ? back[Math.floor(Math.random() * back.length)] : aliveAllies[Math.floor(Math.random() * aliveAllies.length)];
                        backExposed = true;
                    }

                    const allyIdx = activeBattle.allies.indexOf(target);
                    const allySprite = activeBattle.allySprites[allyIdx];

                    // Play enemy animations
                    sprite.setAnimation("attack");
                    
                    // VFX type
                    const isSkeleton = enemy.sheet.includes("skeleton");
                    if (isSkeleton) {
                        // Projectile arrow VFX
                        engine.spawnProjectile("assets/vfx_arrow.png", sprite.x, sprite.y, allySprite.x, allySprite.y, 40, 1, 0.5, () => {
                            applyEnemyDamage(enemy, target, allySprite, backExposed);
                            resolve();
                        });
                    } else {
                        // Normal melee swipe
                        setTimeout(() => {
                            engine.spawnVfx("assets/vfx_slash.png", allySprite.x, allySprite.y, 90, 4);
                            applyEnemyDamage(enemy, target, allySprite, backExposed);
                            resolve();
                        }, 250);
                    }
                });
            }).then(() => {
                // Pause between attacks
                return new Promise(r => setTimeout(r, 600));
            });
        }
    });

    p.then(() => {
        // End of enemy turn, start player next turn
        if (activeBattle) {
            activeBattle.turn++;
            activeBattle.cp = Math.min(activeBattle.maxCp, activeBattle.cp + 2);
            activeBattle.leaderUsed = false;
            
            // Restore AP
            activeBattle.allies.forEach(m => {
                if (!m.states.includes("출혈")) {
                    m.currentAp = m.maxAp;
                }
            });

            addCombatLog(`◈ [턴 ${activeBattle.turn}] 당신의 명령 단계 ◈`, "system");
            
            // Enable controls
            document.getElementById("combat-controls-panel").style.pointerEvents = "auto";
            
            // Auto select first alive mercenary
            const firstAlive = activeBattle.allies.findIndex(m => m.hp > 0 && !m.states.includes("출혈"));
            if (firstAlive > -1) selectActiveMercenary(firstAlive);
            
            updateCombatUI();
        }
    });
}

function applyEnemyDamage(enemy, target, allySprite, backExposed) {
    allySprite.shakeTimer = 250;
    allySprite.setAnimation("hit");
    
    // Evasion check
    if (Math.random() < target.eva) {
        addCombatLog(`💨 {${enemy.name}}의 돌진 공격을 ${target.name}이(가) 회피했습니다!`, "green");
        return;
    }

    let dmg = enemy.atk;
    if (backExposed) dmg = Math.round(dmg * 1.3); // backline collapse penalty

    // Defense reduction
    let defn = target.def;
    if (target.positiveTrait === "철벽") {
        dmg = Math.round(dmg * (1.0 - POSITIVE_TRAITS["철벽"].dmg_red));
    }

    const damageDealt = Math.max(1, dmg - defn);
    
    // Apply Coward penalty
    if (target.negativeTrait === "겁쟁이") {
        target.morale = Math.max(0, target.morale - 8);
    }

    target.hp -= damageDealt;
    engine.spawnFloatingText(damageDealt.toString(), allySprite.x, allySprite.y - 30, '#ff5252');
    
    const exposedMsg = backExposed ? `<span class="text-red"> [후열 방어선 붕괴!]</span>` : '';
    addCombatLog(`💥 {${enemy.name}}이(가) ${target.name}에게 ${damageDealt}의 타격을 줬습니다.${exposedMsg}`, "enemy");

    // HP collapse check
    if (target.hp <= 0) {
        target.hp = 1;
        target.states.push("출혈");
        allySprite.setAnimation("death");
        addCombatLog(`🩸 <span class="text-red"><b>[치명상]</b> ${target.name}이(가) 과다출혈 부상으로 쓰러졌습니다! (전투 불능)</span>`, "system");
    }

    checkBattleStatus();
}

function checkBattleStatus() {
    if (!activeBattle) return;
    
    // All enemies dead check
    const enemiesAlive = activeBattle.enemies.some(e => e.isAlive());
    if (!enemiesAlive) {
        handleBattleFinish(true);
        return;
    }

    // All allies dead/bleeding check
    const alliesAlive = activeBattle.allies.some(m => m.hp > 1 && !m.states.includes("출혈"));
    if (!alliesAlive) {
        handleBattleFinish(false);
    }
}

// 12. BATTLE END RESOLUTIONS
function handleBattleFinish(isWin, isRetreat = false) {
    const battle = activeBattle;
    activeBattle = null;
    engine.isCombat = false;
    
    // Clear canvas events
    const canvas = document.getElementById("game-canvas");
    if (canvasClickHandler) {
        canvas.removeEventListener("mousedown", canvasClickHandler);
        canvasClickHandler = null;
    }

    // Restore base camp UI overlay
    document.getElementById("combat-overlay").classList.add("hidden");
    document.getElementById("camp-screen").classList.remove("hidden");
    document.getElementById("battle-log-entries").innerHTML = "";
    document.getElementById("game-canvas").style.pointerEvents = "none";

    let titleText = "";
    let logBody = "";

    if (isRetreat) {
        titleText = "전장 긴급 퇴각";
        logBody = "피비린내 나는 전장에서 생사의 갈림길을 피해 전술적 후퇴를 단행했습니다.<br>";
        
        battle.allies.forEach(m => {
            m.morale = Math.max(0, m.morale - 15);
            logBody += `└ ${m.name}: 사기 -15 감소<br>`;
        });
    } else if (isWin) {
        titleText = "👑 토벌 작전 승리! 👑";
        logBody = `마수 무리를 깨끗하게 박멸하고 전리품을 수거했습니다!<br><br>`;
        
        let gainGold = 0;
        let gainLoot = 0;
        let gainExp = 0;

        if (selectedStage === 'forest') {
            gainGold = 60; gainLoot = 5; gainExp = 30;
        } else if (selectedStage === 'ruins') {
            gainGold = 130; gainLoot = 10; gainExp = 55;
        } else if (selectedStage === 'dungeon') {
            gainGold = 320; gainLoot = 25; gainExp = 120;
        }

        resources.gold += gainGold;
        resources.monsterLoot += gainLoot;
        
        logBody += `<b>획득 전리품</b>: 💰 +${gainGold} 골드, 🦴 +${gainLoot} 마수 부산물<br><br>`;

        battle.allies.forEach(m => {
            if (!m.states.includes("출혈")) {
                m.morale = Math.min(100, m.morale + 10);
                
                // Gain EXP
                m.exp += gainExp;
                let lvlUpMsg = "";
                if (m.exp >= m.expToNext) {
                    m.level++;
                    m.exp -= m.expToNext;
                    m.expToNext = Math.round(m.expToNext * 1.3);
                    m.maxHp = Math.round(m.maxHp * 1.15);
                    m.atk = Math.round(m.atk * 1.12);
                    m.hp = m.maxHp;
                    lvlUpMsg = ` <span class="text-green">★LEVEL UP (Lv.${m.level})★</span>`;
                }
                logBody += `└ ${m.name}: 경험치 +${gainExp} 획득, 사기 +10 회복${lvlUpMsg}<br>`;
            } else {
                logBody += `└ ${m.name}: 출혈 부상 상태로 귀환 (경험치 보너스 제외)<br>`;
            }
        });
    } else {
        // Lose
        titleText = "💀 작전 실패 (패배) 💀";
        logBody = `용병단 전원이 전투 불능에 빠져 치명상을 입은 채 패주했습니다.<br><br>`;
        
        const lostGold = Math.floor(resources.gold * 0.25);
        resources.gold -= lostGold;
        resources.rations = Math.max(0, resources.rations - 12);
        
        logBody += `<b>패주 손실</b>: 💰 -${lostGold} 골드, 🍖 -12 식량<br><br>`;

        battle.allies.forEach(m => {
            m.morale = Math.max(0, m.morale - 30);
            if (!m.states.includes("부상")) {
                m.states.push("부상");
            }
            m.hp = Math.max(1, Math.round(m.maxHp * 0.2));
            logBody += `└ ${m.name}: 사기 -30 폭락, [부상] 피해 획득 (HP 20%로 급감)<br>`;
        });
    }

    updateTopBar();
    renderGuildList();
    updateCampBackground();

    // Show Battle Summary event popup
    showEventPopup(titleText, logBody, [
        { text: "거처로 복귀", action: () => closeEventPopup() }
    ]);
}
