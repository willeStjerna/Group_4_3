"""
test pyspades/test_grenade_explosion.py
"""
from twisted.trial import unittest
from unittest.mock import Mock
from pyspades import player, server, contained, world
from pyspades.team import Team
from pyspades.constants import GRENADE_KILL, GRENADE_DESTROY


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

