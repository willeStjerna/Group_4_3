"""
test pyspades/protocol.py
"""

from twisted.trial import unittest
from pyspades import player, server, contained
from pyspades import world  
from pyspades.team import Team
from unittest.mock import Mock


class BaseConnectionTest(unittest.TestCase):
    def test_repr(self):
        ply = player.ServerConnection(Mock(), Mock())
        repr(ply)

    def test_team_join(self):
        prot = Mock()
        prot.team_class = Team
        server.ServerProtocol._create_teams(prot)
        # Some places still use the old name
        prot.players = {}

        for team in (prot.team_1, prot.team_2, prot.team_spectator):
            ply = player.ServerConnection(prot, Mock())
            ply.spawn = Mock()
            ex_ply = contained.ExistingPlayer()
            ex_ply.team = team.id
            ply.on_new_player_recieved(ex_ply)

            self.assertEqual(ply.team, team)

class GrenadeExplosionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize branch coverage before running tests."""
        cls.branch_coverage = {i: False for i in range(1, 19)}

    def setUp(self):
        """
        Common setup for each test:
         - Create a mock protocol and map
         - Create our player
         - Create a default grenade
         - Ensure 'player' won't exit early by default
        """
        self.mock_protocol = Mock()
        # Provide a mock .map with .destroy_point returning 0 by default
        self.mock_protocol.map = Mock()
        self.mock_protocol.map.destroy_point = Mock(return_value=0)

        # Our "ServerConnection" instance with a real or mock Team
        self.player = player.ServerConnection(self.mock_protocol, Mock())
        self.player.name = "TestPlayer"         # So we do NOT trigger branch 1 (spectator/name) by default
        self.player.team = Mock(spec=Team)      
        self.player.team.spectator = False      # Not a spectator, so won't exit early
        # Provide a "team.other" that returns a list of players; by default let's say it's empty
        # so the loop won't blow up.
        self.player.team.other = Mock()
        self.player.team.other.get_players = Mock(return_value=[])
        self.player.player_id = 1
        # Default grenade: same team as the player => won't trigger "enemy grenade" check
        self.mock_grenade = Mock(spec=world.Grenade)
        self.mock_grenade.team = self.player.team
        # Mock position safely in-bounds
        self.mock_grenade.position.x = 100
        self.mock_grenade.position.y = 100
        self.mock_grenade.position.z = 10
        self.mock_grenade.get_damage.return_value = 25  # default damage

    def test_grenade_explosion(self):
        """Test grenade explosion and track branch coverage."""
        GrenadeExplosionTest.branch_coverage = self.player.grenade_exploded(
            self.mock_grenade, GrenadeExplosionTest.branch_coverage
        )  # FIX: Store branch coverage at the class level

        # Verify that at least one branch was executed
        self.assertTrue(any(GrenadeExplosionTest.branch_coverage.values()), "No branches were covered.")

    @classmethod
    def tearDownClass(cls):
        """Print branch coverage at the end of the test suite."""
        print("\nBranch Coverage Report:")
        for branch, hit in cls.branch_coverage.items():
            print(f"Branch {branch}: {'Covered' if hit else 'Not Covered'}")

if __name__ == "__main__":
    unittest.main()

