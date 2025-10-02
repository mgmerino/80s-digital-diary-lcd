# CardKB Input Functions

CARDKB_ADDR = 0x5F


def read_key(ctx):
    try:
        b = ctx.i2c.readfrom(CARDKB_ADDR, 1)
        if not b:
            return None
        v = b[0]
        return None if v == 0 else v
    except OSError:
        return None

