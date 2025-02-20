from pyspades.common import (coordinates, to_coordinates)
from piqueserver.commands import (command, CommandError, get_player,
                                  PermissionDenied, player_only, target_player)


@command(admin_only=True)
@target_player
def unstick(connection, player):
    """
    Unstick yourself or another player and inform everyone on the server of it
    /unstick [player]
    """
    connection.protocol.broadcast_chat("%s unstuck %s" %
                                  (connection.name, player.name), irc=True)
    player.set_location_safe(player.get_location())


@command('moves', admin_only=True)
def move_silent(connection, *args):
    """
    Silently move yourself or a given player to the specified x/y/z coordinates or sector
    /moves [player] <sector> or /moves [player] <x> <y> <z>
    If the z coordinate makes the player appear underground, put them at ground level instead.
    If the x/y/z coordinate makes the player appear outside of the world bounds,
    take the bound instead

    You can only move other players if you are admin or have the move_others right
    """
    do_move(connection, args, True)


@command(admin_only=True)
@player_only
def move(connection, *args):
    """
    Move yourself or a given player to the specified x/y/z coordinates or sector
    /move [player] <sector> or /move [player] <x> <y> <z>
    If you're invisible, it will happen silently.
    If the z coordinate makes the player appear underground, put them at ground level instead.
    If the x/y/z coordinate makes the player appear outside of the world bounds,
    take the bound instead

    You can only move other players if you are admin or have the move_others right
    """
    do_move(connection, args)

def do_move(connection, args, silent=False, branch_coverage=None):

    position = None
    player = None
    arg_count = len(args)

    # 1a
    if arg_count == 2 or arg_count == 4:  
        initial_index = 1
        branch_coverage["init_index_1"] = True
    # 1b
    else:  
        initial_index = 0
        branch_coverage["init_index_0"] = True

    # 2a
    if arg_count == 1 or arg_count == 2:  
        branch_coverage["target_sector"] = True
        x, y = coordinates(args[initial_index])
        x += 32
        y += 32
        z = connection.protocol.map.get_height(x, y) - 2
        position = args[initial_index].upper()
    # 2b
    elif arg_count == 3 or arg_count == 4:  
        branch_coverage["target_coordinates"] = True
        x = min(max(0, int(args[initial_index])), 511)
        y = min(max(0, int(args[initial_index + 1])), 511)
        z = min(max(0, int(args[initial_index + 2])),
                connection.protocol.map.get_height(x, y) - 2)
        position = '%d %d %d' % (x, y, z)
    # 2c
    else:  
        branch_coverage["error_invalid_params"] = True
        raise ValueError('Wrong number of parameters!')

    # 3a
    if arg_count == 1 or arg_count == 3:  
        branch_coverage["move_self"] = True
        # 3b
        if connection not in connection.protocol.players.values():  
            branch_coverage["error_requires_player"] = True
            raise ValueError("Both player and target player are required")
        # 3e
        else:  
            branch_coverage["player_exists"] = True
        player = connection.name
    # 3c
    elif arg_count == 2 or arg_count == 4:  
        branch_coverage["move_other"] = True
        # 3d
        if not (connection.admin or connection.rights.move_others):  
            branch_coverage["error_permission_denied"] = True
            raise PermissionDenied(
                "moving other players requires the move_others right")
        # 3f
        else:  
            branch_coverage["permission_granted"] = True
        player = args[0]
    # 3g
    else:  
        branch_coverage["error_invalid_arg_count"] = True
        raise ValueError("Invalid argument count provided")

    player = get_player(connection.protocol, player)

    # 4a
    if connection.invisible:  
        branch_coverage["evaluate_silent_true"] = True
        silent = True
    # 4b
    else:  
        branch_coverage["evaluate_silent_false"] = True
        silent = silent

    player.set_location((x, y, z))

    # 5a
    if connection is player:  
        branch_coverage["set_location_self"] = True
        message = ('%s ' + ('silently ' if silent else '') + 'teleported to '
                   'location %s')
        message = message % (player.name, position)
    # 5b
    else:  
        branch_coverage["set_location_other"] = True
        message = ('%s ' + ('silently ' if silent else '') + 'teleported %s '
                   'to location %s')
        message = message % (connection.name, player.name, position)

    # 6a
    if silent:  
        branch_coverage["silent_message"] = True
        connection.protocol.irc_say('* ' + message)
    # 6b
    else:  
        branch_coverage["broadcast_message"] = True
        connection.protocol.broadcast_chat(message, irc=True)





@command(admin_only=True)
@target_player
def where(connection, player):
    """
    Tell you the coordinates of yourself or of a given player
    /where [player]
    """
    x, y, z = player.get_location()
    return '%s is in %s (%s, %s, %s)' % (
        player.name, to_coordinates(x, y), int(x), int(y), int(z))


@command('teleport', 'tp', admin_only=True)
def teleport(connection, player1, player2=None, silent=False):
    """
    Teleport yourself or a given player to another player
    /teleport [player] <target player>
    """
    # TODO: refactor this
    player1 = get_player(connection.protocol, player1)
    if player2 is not None:
        if connection.admin or connection.rights.teleport_other:
            player, target = player1, get_player(
                connection.protocol, player2)
            silent = silent or player.invisible
            message = ('%s ' + ('silently ' if silent else '') + 'teleported '
                       '%s to %s')
            message = message % (connection.name, player.name, target.name)
        else:
            return 'No administrator rights!'
    else:
        if connection not in connection.protocol.players.values():
            raise ValueError("Both player and target player are required")
        player, target = connection, player1
        silent = silent or player.invisible
        message = '%s ' + \
            ('silently ' if silent else '') + 'teleported to %s'
        message = message % (player.name, target.name)
    x, y, z = target.get_location()
    player.set_location(((x - 0.5), (y - 0.5), (z + 0.5)))
    if silent:
        connection.protocol.irc_say('* ' + message)
    else:
        connection.protocol.broadcast_chat(message, irc=True)


@command('tpsilent', 'tps', admin_only=True)
def tpsilent(connection, player1, player2=None):
    """
    Silently teleport a player to another player
    /tpsilent [player] <target player>
    """
    teleport(connection, player1, player2, silent=True)


@command(admin_only=True)
@target_player
def fly(connection, player):
    """
    Enable flight
    /fly [player]
    Hold control and press space ;)
    """
    protocol = connection.protocol
    player.fly = not player.fly

    message = 'now flying' if player.fly else 'no longer flying'
    player.send_chat("You're %s" % message)
    if connection is not player and connection in protocol.players.values():
        connection.send_chat('%s is %s' % (player.name, message))
    protocol.irc_say('* %s is %s' % (player.name, message))
