
class ServerState:
    up_since = None  # Datetime since connection was 'up'
    local_ip = None  # Server local IP
    remote_ip = None  # Server remote IP TODO actually for clients only!
    mode = None  # Server mode, in OVPN it can be client|server but here should always be server!
    success = None  # TODO ??
