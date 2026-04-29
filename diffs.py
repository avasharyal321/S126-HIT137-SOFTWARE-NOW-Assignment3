class Difference:
    def __init__(self, rect):
        self.rect = rect

    def apply(self, img):
        raise NotImplementedError()


class ColorShiftDifference(Difference):
    def apply(self, img):
        return img


class InvertDifference(Difference):
    def apply(self, img):
        return img


class ShapeDifference(Difference):
    def apply(self, img):
        return img


DIFF_TYPES = [ColorShiftDifference, InvertDifference, ShapeDifference]