import colour
import message


class LedStrip:
    def __init__(self, num_pixels: int) -> None:
        self._num_pixels = num_pixels
        self.state = [message.MessageType.OFF] * num_pixels
        self.colour = [colour.RGBColour(0, 0, 0)] * num_pixels

    def set_state(self, pixel_id: int, state: message.MessageType) -> None:
        self.state[pixel_id] = state

    def set_colour(self, pixel_id: int, colour: colour.RGBColour) -> None:
        self.colour[pixel_id] = colour
