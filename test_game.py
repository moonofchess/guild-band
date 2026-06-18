import unittest
from game.mercenary import Mercenary
from game.resources import ResourceManager
from game.camp import BaseCamp
from game.combat import CombatEngine, Monster

class TestDarkFantasyMercenary(unittest.TestCase):

    def test_mercenary_initialization(self):
        """Test that mercenaries initialize stats based on class and rank."""
        merc = Mercenary(name="테스트용병", m_class="전사", rank="D")
        self.assertEqual(merc.name, "테스트용병")
        self.assertEqual(merc.m_class, "전사")
        self.assertEqual(merc.rank, "D")
        self.assertEqual(merc.level, 1)
        self.assertEqual(merc.hp, merc.get_max_hp())
        self.assertGreater(merc.get_atk(), 0)
        self.assertGreater(merc.get_def(), 0)

    def test_mercenary_awakening(self):
        """Test that hidden traits awaken properly at level 3."""
        # Force a mercenary with a hidden trait
        merc = Mercenary(name="각성용병", m_class="전사", rank="F")
        merc.hidden_trait = "오라 발현의 씨앗"
        merc.level = 1
        merc.exp = 0
        
        # Level 1 -> 2: needs 100 exp. Level 2 -> 3: needs 130 exp.
        # Gaining 250 EXP should level up to 3 naturally.
        log = merc.gain_exp(250)
        
        self.assertTrue(merc.is_awakened)
        self.assertEqual(merc.rank, "S")
        self.assertTrue("오라의 지배자" in merc.display_status())

    def test_resource_upkeep_normal(self):
        """Test standard upkeep deduction when enough resources are present."""
        resources = ResourceManager()
        resources.gold = 100
        resources.rations = 20
        
        m1 = Mercenary(rank="D")  # Gold upkeep: weekly 20 // 5 = 4 gold, Rations: 1
        m2 = Mercenary(rank="F")  # Gold upkeep: weekly 5 // 5 = 1 gold, Rations: 1
        mercs = [m1, m2]
        
        logs, conflict = resources.check_upkeep(mercs)
        
        self.assertEqual(resources.gold, 95)  # 100 - 4 - 1
        self.assertEqual(resources.rations, 18)  # 20 - 1 - 1
        self.assertEqual(resources.day, 2)

    def test_resource_upkeep_starvation(self):
        """Test starvation affects morale and corruption."""
        resources = ResourceManager()
        resources.gold = 100
        resources.rations = 0  # Starving!
        
        merc = Mercenary(rank="D")
        merc.morale = 50
        merc.corruption = 10
        
        logs, conflict = resources.check_upkeep([merc])
        
        # Starvation penalty: Morale -15 + 2 (well-fed offset is not applied, so net -15 or similar)
        # Let's verify it decreased from 50 and corruption increased
        self.assertLess(merc.morale, 50)
        self.assertGreater(merc.corruption, 10)

    def test_base_camp_upgrades(self):
        """Test base camp upgrades require correct resources."""
        resources = ResourceManager()
        resources.gold = 50
        resources.monster_loot = 0
        resources.ore = 0
        
        camp = BaseCamp()
        # Level 1 upgrade to 2 costs 200 gold
        success, msg = camp.upgrade_lord_hall(resources)
        self.assertFalse(success)
        self.assertEqual(camp.lord_hall_level, 1)
        
        # Add enough resources
        resources.add_resources(gold=500, loot=50, ore=20)
        success, msg = camp.upgrade_lord_hall(resources)
        self.assertTrue(success)
        self.assertEqual(camp.lord_hall_level, 2)

    def test_combat_engine_win_lose_states(self):
        """Test combat engine correctly flags win and lose conditions."""
        resources = ResourceManager()
        m1 = Mercenary(rank="D")
        m2 = Mercenary(rank="E")
        
        enemies = [
            Monster("고블린 A", 30, 5, 2),
            Monster("고블린 B", 20, 4, 1)
        ]
        
        engine = CombatEngine([m1, m2], enemies, resources)
        
        # Initially, combat continues
        self.assertEqual(engine.check_battle_over(), "CONTINUE")
        
        # Kill enemies -> WIN
        enemies[0].hp = 0
        enemies[1].hp = 0
        self.assertEqual(engine.check_battle_over(), "WIN")
        
        # Revive enemies and bleed all allies -> LOSE
        enemies[0].hp = 30
        m1.states.append("출혈")
        m2.states.append("출혈")
        self.assertEqual(engine.check_battle_over(), "LOSE")

if __name__ == "__main__":
    unittest.main()
