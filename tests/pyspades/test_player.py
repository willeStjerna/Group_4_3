"""
test pyspades/protocol.py
"""

from twisted.trial import unittest
from unittest.mock import MagicMock, patch
from pyspades import player, server, contained
from pyspades import contained as loaders
from pyspades import world
from pyspades.constants import *
from pyspades.common import Vertex3
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



class TestOnBlockLineRecieved(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize branch coverage before running tests."""
        cls.branch_coverage = {i: False for i in range(1, 19)}

    def setUp(self):
        # Set up a player-scenario that passes by itself

        # Create a mock protocol and associated mocks
        self.mock_protocol = MagicMock()
        self.mock_map = MagicMock()
        self.mock_protocol.map = self.mock_map
        self.mock_protocol.update_entities = MagicMock()
        self.mock_protocol.broadcast_contained = MagicMock()

        # Barebones player
        self.player = player.ServerConnection(self.mock_protocol, Mock())
        self.player.player_id = 10
        self.player.tool = BLOCK_TOOL
        self.player.blocks = 50
        self.player.hp = 100  # "alive"
        self.player.line_build_start_pos = Vertex3(10, 10, 10)

        # Mock the world_object so it passes
        self.player.world_object = MagicMock()
        self.player.world_object.position = Vertex3(12, 10, 10)

        # Make sure these pass
        self.mock_map.is_valid_position.return_value = True
        self.mock_map.has_neighbors.return_value = True
        self.mock_map.get_solid.return_value = 0
        self.mock_map.build_point.return_value = True

    # make this patch so that points in on_block_recieved gets good values
    @patch('pyspades.world.cube_line', return_value=[(10, 10, 10), (11, 10, 10), (12, 10, 10)])
    def test_on_block_line_recieved_good_inputs(self, mock_cube_line):
        # We'll simulate a BlockLine packet with start and end coordinates
        contained = loaders.BlockLine()
        contained.x1, contained.y1, contained.z1 = (10, 10, 10)
        contained.x2, contained.y2, contained.z2 = (12, 10, 10)

        # Execute the code under test
        self.player.on_block_line_recieved(contained)

        # Finally, verify we updated entities after building
        self.mock_protocol.update_entities.assert_called_once()

    # def test_on_block_line_recieved_good_inputs(self):
    #     """Test grenade explosion and track branch coverage."""
    #     contained = loaders.BlockLine()
    #     contained.x1, contained.y1, contained.z1 = (10, 10, 10)
    #     contained.x2, contained.y2, contained.z2 = (12, 10, 10)
    #
    #     # Execute the code under test
    #     TestOnBlockLineRecieved.branch_coverage = self.player.on_block_line_recieved(
    #         contained, TestOnBlockLineRecieved.branch_coverage
    #     )
    #
    #     self.assertTrue(any(TestOnBlockLineRecieved.branch_coverage.values()),
    #                     "No branches were covered.")


    @classmethod
    def tearDownClass(cls):
        """Print branch coverage at the end of the test suite."""
        print("\nBranch Coverage Report:")
        for branch, hit in cls.branch_coverage.items():
            print(f"Branch {branch}: {'Covered' if hit else 'Not Covered'}")

if __name__ == "__main__":
    unittest.main()
