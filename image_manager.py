class ImageManager:
    def __init__(self):
        self.diffs = []

    def load_and_generate(self, path, num_diffs=5):
        raise NotImplementedError()