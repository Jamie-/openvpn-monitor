
class MonitorError(Exception):
    """Base exception for all other project exceptions.
    """
    pass


class InvalidConfigError(MonitorError):
    """Invalid config provided.
    """
    pass
