# CardKB Input Functions (HAL-aware)

CARDKB_ADDR = 0x5F


def read_key(ctx):
    """
    Read key using HAL input interface
    
    Args:
        ctx: Context object with hal_input attribute
    
    Returns:
        Key code or None
    """
    return ctx.hal_input.read_key()
