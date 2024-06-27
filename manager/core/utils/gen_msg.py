from enum import Enum

class MsgType(Enum):
    INFO    = "Info"
    CAUTION = "Caution"
    ERROR = "Error"
    CRITICAL   = "Critical"

@staticmethod
def gen_msg(sender: object, type: MsgType, msg: str) -> str: return f'{sender.__name__}: {type}: {msg}' # type: ignore
