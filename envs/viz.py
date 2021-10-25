import seaborn as sns
from pygame import Surface, PixelArray, Color

WAVE_MAX_HEIGHT = 20
SEAFLOOR_MIN_HEIGHT = -20
SEA_COLOR_PALETTE = sns.color_palette('Blues', n_colors=80)[40:]
for ix, color in enumerate(SEA_COLOR_PALETTE):
    r, g, b = int(255 * color[0]), int(255 * color[1]), int(255 * color[2])
    SEA_COLOR_PALETTE[ix] = (r, g, b)
CRASH_COLOR = (255, 255, 255)
BEACH_COLOR = (230, 207, 138)
WAVE_BREAK_RATIO = 2


class SurfBreakViz:
    def __init__(self, surfbreak):
        self.surfbreak = surfbreak

        self.surface = Surface((surfbreak.width, surfbreak.height))
        self.init_image()

    def step(self):
        self.surfbreak.step()
        self.get_image()

    def init_image(self):
        """
        Transforms from a Surfbreak object to the rgb pixel color space
        :param surfbreak: the image that will be transformed
        :return: image - the image transformed into the rgb pixel space
        """
        # image = list(self.image)
        pixel_array = PixelArray(self.surface)
        for y in range(self.surfbreak.height):
            for x in range(self.surfbreak.width):
                if self.surfbreak.base_water_level <= self.surfbreak.sea_floor[y, x]:
                    rgb = BEACH_COLOR
                elif self.surfbreak.crashing[y, x] > WAVE_BREAK_RATIO:
                    rgb = CRASH_COLOR
                else:
                    rgb = SEA_COLOR_PALETTE[int(self.surfbreak.active_water_level[y, x])
                                            - SEAFLOOR_MIN_HEIGHT]

                pixel_array[x, y] = Color(rgb)

        self.surface = pixel_array.make_surface()
        pixel_array.close()

        return self.surface

    def get_image(self):
        # image = list(self.image)
        # We update where the wave was and where it is now
        pixel_array = PixelArray(self.surface)
        for wave in self.surfbreak.swell.waves:
            for (y, x) in wave.coordinates:
                rgb = self.map_to_rgb(y, x)
                pixel_array[x, y] = Color(rgb)
            for (y, x) in wave.last_coordinates:
                rgb = self.map_to_rgb(y, x)
                pixel_array[x, y] = Color(rgb)

        self.surface = pixel_array.make_surface()
        pixel_array.close()

        return self.surface

    def map_to_rgb(self, y, x):
        if self.surfbreak.base_water_level <= \
                self.surfbreak.sea_floor[y, x]:
            return BEACH_COLOR
        elif self.surfbreak.crashing[y, x] > WAVE_BREAK_RATIO:
            return CRASH_COLOR
        else:
            ix = int(self.surfbreak.active_water_level[y, x]) \
                 - SEAFLOOR_MIN_HEIGHT

            if ix >= len(SEA_COLOR_PALETTE):
                ix = len(SEA_COLOR_PALETTE) - 1
            elif ix < 0:
                ix = 0
            return SEA_COLOR_PALETTE[ix]