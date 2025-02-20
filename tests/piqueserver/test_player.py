"""
test piqueserver/server.py
"""

from twisted.trial import unittest
from unittest.mock import Mock
import piqueserver.player
from pyspades.constants import DESTROY_BLOCK, SPADE_DESTROY, GRENADE_DESTROY

class TestPlayer(unittest.TestCase):
    def setUp(self):
        # Create protocol with proper attribute types
        self.protocol = Mock(spec=[])
        self.protocol.command_limit_size = int(5)
        self.protocol.command_limit_time = int(2)
        self.protocol.building = True
        self.protocol.respawn_time = 5
        self.protocol.fall_damage = True
        self.protocol.teamswitch_interval = 0
        self.protocol.teamswitch_allowed = True
        self.protocol.balanced_teams = 0
        self.protocol.god_blocks = None
        self.protocol.user_blocks = None
        self.protocol.killing = True
        self.protocol.global_chat = True
        self.protocol.everyone_is_admin = False
        self.protocol.is_indestructable = Mock(return_value=False)
        self.protocol.map_info = Mock()
        self.protocol.map_info.on_block_destroy = None
        
        # Create address object with host and port attributes
        class Address:
            def __init__(self, host, port):
                self.host = host
                self.port = port
                
        # Create peer mock with proper address object
        class MockPeer:
            @property
            def address(self):
                return Address('127.0.0.1', 32887)
                
        self.peer = MockPeer()
        self.player = piqueserver.player.FeatureConnection(peer=self.peer, protocol=self.protocol)
        self.player.building = True
        self.player.god = False
    
    def test_on_block_destroy(self): 
        # Test for map_info.on_block_destroy returning True
        self.protocol.map_info.on_block_destroy = Mock(return_value=True)
        self.player.god = True
        result = self.player.on_block_destroy(0, 0, 0, DESTROY_BLOCK)
        self.assertIsNone(result)
        
        # Reset default attribute values
        self.player.god = False
        self.protocol.map_info.on_block_destroy = None