import cv2
import random
from diffs import DIFF_TYPES


class ImageManager:
    def __init__(self):
        self.diffs = []

    def load_and_generate(self, path, num_diffs=5):
        img = cv2.imdecode(np_from_file(path), cv2.IMREAD_COLOR)
        if img is None:
            img = cv2.imread(path, cv2.IMREAD_COLOR)
        h, w = img.shape[:2]
        modified = img.copy()

        rects = self._generate_nonoverlapping_rects(w, h, num_diffs)

        diffs = []
        for rect in rects:
            DiffCls = random.choice(DIFF_TYPES)
            d = DiffCls(rect)
            d.apply(modified)
            diffs.append(d)

        self.diffs = diffs
        return img, modified, diffs

    def _generate_nonoverlapping_rects(self, w, h, count):
        rects = []
        attempts = 0
        while len(rects) < count and attempts < 5000:
            attempts += 1
            min_rw = max(20, w // 40)
            min_rh = max(20, h // 40)
            max_rw = max(min_rw, w // 6)
            max_rh = max(min_rh, h // 6)
            rw = random.randint(min_rw, max_rw)
            rh = random.randint(min_rh, max_rh)
            rw = min(rw, w - 1)
            rh = min(rh, h - 1)
            if w - rw > 0:
                rx = random.randint(0, w - rw)
            else:
                rx = 0
            if h - rh > 0:
                ry = random.randint(0, h - rh)
            else:
                ry = 0
            new = (rx, ry, rw, rh)
            if not any(self._overlap(new, r) for r in rects):
                rects.append(new)
        if len(rects) < count:
            rects = self._grid_pack(w, h, count)
        return rects

    def _overlap(self, a, b):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return not (ax + aw < bx or bx + bw < ax or ay + ah < by or by + bh < ay)

    def _grid_pack(self, w, h, count):
        rects = []
        cols = int(count**0.5) + 1
        rows = (count + cols - 1) // cols
        rw = max(40, w // (cols * 2))
        rh = max(40, h // (rows * 2))
        for r in range(rows):
            for c in range(cols):
                if len(rects) >= count:
                    break
                rx = int((c + 0.5) * w / cols - rw // 2)
                ry = int((r + 0.5) * h / rows - rh // 2)
                rects.append((max(0, rx), max(0, ry), rw, rh))
        return rects


def np_from_file(path):
    import numpy as np
    with open(path, 'rb') as f:
        data = f.read()
    arr = np.frombuffer(data, dtype='uint8')
    return arr