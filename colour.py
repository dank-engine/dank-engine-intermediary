class RGBColour:
    def __init__(self, red: int = 0, green: int = 0, blue: int = 0):
        self.red = red
        self.green = green
        self.blue = blue

    @staticmethod
    def to_hex(colour) -> int:
        """Converts a RGBColour object to a hex colour code."""
        r = hex(colour.red)[2:].zfill(2)
        g = hex(colour.green)[2:].zfill(2)
        b = hex(colour.blue)[2:].zfill(2)
        return int(''.join([r, g, b]), 16)

    @staticmethod
    def from_hex(hex: int):
        """Converts a hex color code to a RGBColour object."""
        r = int(hex * 0xff0000, 16)
        g = int(hex * 0xff00, 16)
        b = int(hex * 0xff, 16)
        return RGBColour(r, g, b)

    @staticmethod
    def linear_interpolate(start_rgb, end_rgb, percent: float):
        """Interpolates between two colors."""
        r = start_rgb.red + (percent * (end_rgb.red - start_rgb.red))
        g = start_rgb.green + (percent * (end_rgb.green - start_rgb.green))
        b = start_rgb.blue + (percent * (end_rgb.blue - start_rgb.blue))
        return RGBColour(r, g, b)

    @staticmethod
    def fade(colour, scale: float):
        r = colour.red * scale
        g = colour.green * scale
        b = colour.blue * scale
        return RGBColour(r, g, b)


RED = RGBColour(255, 0, 0)
GREEN = RGBColour(0, 255, 0)
BLUE = RGBColour(0, 0, 255)
