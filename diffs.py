import random
import cv2
import numpy as np


class Difference:
    def __init__(self, rect):
        self.rect = rect
        self.found = False

    def apply(self, img):
        raise NotImplementedError()

    def contains_point(self, pt, tolerance=20):
        x, y = pt
        rx, ry, rw, rh = self.rect
        if (rx - tolerance) <= x <= (rx + rw + tolerance) and (ry - tolerance) <= y <= (ry + rh + tolerance):
            return True
        return False


class ColorShiftDifference(Difference):
    def apply(self, img):
        x, y, w, h = self.rect
        ih, iw = img.shape[:2]
        x = max(0, min(x, iw - 1))
        y = max(0, min(y, ih - 1))
        w = max(1, min(w, iw - x))
        h = max(1, min(h, ih - y))
        roi = img[y:y+h, x:x+w]
        if roi.size == 0:
            return img
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        hsv[:, :, 0] = (hsv[:, :, 0].astype(int) + random.randint(15, 45)) % 180
        hsv[:, :, 1] = np.clip(hsv[:, :, 1].astype(int) + random.randint(10, 50), 0, 255)
        img[y:y+h, x:x+w] = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        return img


class InvertDifference(Difference):
    def apply(self, img):
        x, y, w, h = self.rect
        ih, iw = img.shape[:2]
        x = max(0, min(x, iw - 1))
        y = max(0, min(y, ih - 1))
        w = max(1, min(w, iw - x))
        h = max(1, min(h, ih - y))
        roi = img[y:y+h, x:x+w]
        if roi.size == 0:
            return img
        img[y:y+h, x:x+w] = cv2.bitwise_not(roi)
        return img


class ShapeDifference(Difference):
    def apply(self, img):
        x, y, w, h = self.rect
        ih, iw = img.shape[:2]
        x = max(0, min(x, iw - 1))
        y = max(0, min(y, ih - 1))
        w = max(1, min(w, iw - x))
        h = max(1, min(h, ih - y))
        cx = x + w // 2
        cy = y + h // 2
        radius = max(8, min(w, h) // 3)
        color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        cv2.circle(img, (cx, cy), radius, color, -1)
        return img