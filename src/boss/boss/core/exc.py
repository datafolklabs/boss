"""Boss core exceptions module."""

class BossError(Exception):
    """Generic errors."""
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg
    
    def __str__(self):
        return self.msg

            
class BossConfigError(BossError):
    pass

class BossRuntimeError(BossError):
    pass
        
class BossArgumentError(BossError):
    pass

class BossTemplateError(BossError):
    pass