def scale_colour(colour, scale):
    r = (colour & 0xff0000) >> 16
    g = (colour & 0x00ff00) >> 8
    b = colour & 0x0000ff

    r *= scale
    g *= scale 
    b *= scale 

    r = int(r)<<16
    g = int(g)<<8
    b = int(b)

    colour = r | g | b
    return colour


if __name__ == "__main__":
    scale_colour(0xfe48ff, 0.5)