from app.const import RatingColor

class ColorUtils:
    def get_rating_color(index: int, value: float):
        color_map = RatingColor.RATING_COLOR_MAP
        index_list = [
            [70, 60, 55, 52.5, 51, 49, 45],
            [1.7, 1.4, 1.2, 1.1, 1.0, 0.95, 0.8],
            [2, 1.5, 1.3, 1.0, 0.6, 0.3, 0.2],
            [2450, 2100, 1750, 1550, 1350, 1100, 750]
        ]
        data = index_list[index]
        if value == -1:
            return (128, 128, 128)
        elif value == -2:
            return (0, 0, 0)
        for i in range(len(data) - 1):
            if value >= data[i + 1] and value < data[i]:
                return color_map[i+1]
        if value >= data[0]:
            return color_map[0]
        if value < data[-1]:
            return color_map[-1]