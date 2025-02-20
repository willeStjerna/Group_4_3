"""
test pyspades/test_grenade_explosion.py
"""
from twisted.trial import unittest
from twisted.internet import reactor
from unittest.mock import Mock, MagicMock, patch
from pyspades import player, server, contained, world
from pyspades.team import Team
from pyspades.constants import GRENADE_KILL, GRENADE_DESTROY
from pyspades import contained as loaders
from pyspades.constants import *
from pyspades.common import Vertex3


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
    def setUp(self):
        """
        Common setup for each test:
        - Create a mock protocol and map
        - Create our player
        - Create a default grenade
        - Ensure 'player' won't exit early by default
        """
        self.mock_protocol = Mock()
        self.mock_protocol.map = Mock()
        # by default, destroy_point returns 0 => no blocks destroyed
        self.mock_protocol.map.destroy_point = Mock(return_value=0)

        # Create the "player" with a name and a non-spectator team
        self.player = player.ServerConnection(self.mock_protocol, Mock())
        self.player.name = "TestPlayer"
        self.player.team = Mock(spec=Team)
        self.player.team.spectator = False
        self.player.team.other = Mock()
        # By default, no other players are returned
        self.player.team.other.get_players = Mock(return_value=[])
        self.player.player_id = 1
        self.player.world_object = Mock()  # needed if e.g. on_hit references it

        # Create a default "grenade"
        self.mock_grenade = Mock(spec=world.Grenade)
        self.mock_grenade.team = self.player.team
        self.mock_grenade.position = Mock()
        self.mock_grenade.position.x = 100
        self.mock_grenade.position.y = 100
        self.mock_grenade.position.z = 10
        self.mock_grenade.get_damage.return_value = 25  # default damage

        # For on_hit / on_unvalidated_hit / on_block_destroy, etc.
        self.player.on_unvalidated_hit = Mock(return_value=None)
        self.player.on_hit = Mock(return_value=None)
        self.player.on_block_destroy = Mock(return_value=True)
        self.player.on_block_removed = Mock()
        self.player.protocol.broadcast_contained = Mock()
        self.player.protocol.update_entities = Mock()

        # Make sure the "player" has some HP
        self.player.hp = 100

        # Define hit_indicator as a tuple (x, y, z)
        self.mock_grenade.position.get = Mock(return_value=(100, 100, 10))

    def test_ignore_spectator(self):
        """
        Requirement 1: If the player is a spectator, immediately return.
        """
        self.player.team.spectator = True
        self.player.grenade_exploded(self.mock_grenade)
        # If this function "returns" early, no calls to 'on_hit' or block destruction happen.
        self.player.on_hit.assert_not_called()
        self.player.protocol.map.destroy_point.assert_not_called()

    def test_ignore_no_name(self):
        """
        Requirement 1: If the player has no name, immediately return.
        """
        self.player.name = None
        self.player.grenade_exploded(self.mock_grenade)
        self.player.on_hit.assert_not_called()
        self.player.protocol.map.destroy_point.assert_not_called()

    def test_ignore_enemy_grenade(self):
        """
        Requirement 2: If grenade team is not same as player team then return. Ex: player switches team.
        """
        enemy_team = Mock(spec=Team)
        enemy_team.spectator = False
        self.mock_grenade.team = enemy_team

        self.player.grenade_exploded(self.mock_grenade)
        self.player.on_hit.assert_not_called()
        self.player.protocol.map.destroy_point.assert_not_called()

    def test_ignore_out_of_bounds(self):
        """
        Requirement 3: Grenade must be within (0<=x<=512, 0<=y<=512, 0<=z<=63).
        Otherwise, ignore.
        """
        # place the grenade out of bounds
        self.mock_grenade.position.x = 999
        self.player.grenade_exploded(self.mock_grenade)
        self.player.on_hit.assert_not_called()
        self.player.protocol.map.destroy_point.assert_not_called()

    def test_dead_player_skips_damage(self):
        """
        Requirement 4: Dead players (hp=0) take no damage.
        """
        # Suppose we have one "other" player who is dead
        dead_player = Mock()
        dead_player.hp = 0
        self.player.team.other.get_players.return_value = [dead_player]

        self.player.grenade_exploded(self.mock_grenade)
        # dead player => skip => no calls to set_hp
        dead_player.set_hp.assert_not_called()

    def test_zero_damage_skips(self):
        """
        Requirement 5: If grenade.get_damage(...) == 0, skip damage.
        """
        zero_damage_player = Mock()
        zero_damage_player.hp = 100
        self.player.team.other.get_players.return_value = [zero_damage_player]

        # force get_damage to return 0
        self.mock_grenade.get_damage.return_value = 0

        self.player.grenade_exploded(self.mock_grenade)
        zero_damage_player.set_hp.assert_not_called()


    def test_normal_path_block_destroy(self):
        """
        A scenario where everything is normal:
        - The player is valid (not spectator, has a name)
        - The grenade team is the same
        - The grenade is in-bounds
        - There's a living player in the 'other' team
        - The block destroy is allowed => we do block destruction
        """
        living_player = Mock()
        living_player.hp = 100
        self.player.team.other.get_players.return_value = [living_player]

        # Provide 27 return values for destroy_point (3x3x3 grid)
        self.mock_protocol.map.destroy_point.side_effect = [1] * 27  # All blocks are destroyed

        self.player.grenade_exploded(self.mock_grenade)

        # We should have destroyed some blocks
        self.assertEqual(self.player.total_blocks_removed, 27)  # All 27 blocks destroyed
        self.player.protocol.broadcast_contained.assert_called()
        self.player.protocol.update_entities.assert_called()

        # living_player should have taken damage
        living_player.set_hp.assert_called_once()



class TestOnBlockLineRecieved(unittest.TestCase):
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
    def test_dead_player_returns_immediately(self, mock_cube_line):
        """
        # Requirement 1. If the player is dead (self.hp < 0) it should return.
        Checks that it does not call update_entities
        """
        contained = loaders.BlockLine()
        contained.x1, contained.y1, contained.z1 = (10, 10, 10)
        contained.x2, contained.y2, contained.z2 = (12, 10, 10)

        self.player.hp = 0  # "dead"

        self.player.on_block_line_recieved(contained)
        self.mock_protocol.update_entities.assert_not_called()

    # make this patch so that points in on_block_recieved gets good values
    @patch('pyspades.world.cube_line', return_value=[(10, 10, 10), (11, 10, 10), (12, 10, 10)])
    def test_no_start_position_returns_immediately(self, mock_cube_line):
        """
        # Requirement 2. If the line build start position is not set (self.line_build_start_pos is None) it should return.
        Checks that it does not call update_entities
        """
        contained = loaders.BlockLine()
        contained.x1, contained.y1, contained.z1 = (10, 10, 10)
        contained.x2, contained.y2, contained.z2 = (12, 10, 10)

        self.player.line_build_start_pos = None

        self.player.on_block_line_recieved(contained)
        self.mock_protocol.update_entities.assert_not_called()


    @patch('twisted.internet.reactor.seconds', return_value=10)
    def test_rapid_hack_detection(self, mock_seconds):
        """
        Requirement 3. If a rapid hack is detected it should return.
        We simulate a call that came in just after the last one and check if 'record_event' is invoked
        and that it does not call update_entities.
        """
        contained = loaders.BlockLine()
        contained.x1, contained.y1, contained.z1 = (10, 10, 10)
        contained.x2, contained.y2, contained.z2 = (12, 10, 10)

        self.player.last_block = 10
        self.player.rapid_hack_detect = True
        self.player.rapids = MagicMock()
        self.player.rapids.above_limit.return_value = False

        # Two calls in rapid succession should trigger it.
        self.player.on_block_line_recieved(contained)

        self.player.rapids.record_event.assert_called_once()
        self.mock_protocol.update_entities.assert_not_called()

    # make this patch so that points in on_block_recieved gets good values
    @patch('pyspades.world.cube_line', return_value=[(10, 10, 10), (11, 10, 10), (12, 10, 10)])
    def test_not_in_range_of_start_or_end_returns_immediately(self, mock_cube_line):
        """
        # Requirement 5. If the player is not in range of start or end pos of the block it should return.
        Checks that it does not call update_entities
        """
        contained = loaders.BlockLine()
        contained.x1, contained.y1, contained.z1 = (10, 10, 10)
        contained.x2, contained.y2, contained.z2 = (12, 10, 10)

        self.player.world_object.position.x = 1000

        self.player.on_block_line_recieved(contained)
        self.mock_protocol.update_entities.assert_not_called()

    # make this patch so that points in on_block_recieved gets good values
    @patch('pyspades.world.cube_line', return_value=[(10, 10, 10), (11, 10, 10), (12, 10, 10)])
    def test_on_block_line_recieved_good_inputs(self, mock_cube_line):
        """
        # Requirement 12. It should update the entities.
        Checks that it calls update_entities when given good inputs
        """
        contained = loaders.BlockLine()
        contained.x1, contained.y1, contained.z1 = (10, 10, 10)
        contained.x2, contained.y2, contained.z2 = (12, 10, 10)

        self.player.on_block_line_recieved(contained)
        self.mock_protocol.update_entities.assert_called_once()
