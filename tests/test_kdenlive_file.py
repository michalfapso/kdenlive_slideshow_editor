import os
from pathlib import Path

from kdenlive_file import KdenliveFile

assets = Path(os.path.join(os.path.dirname(__file__), "assets/"))


class TestKdenliveFile:
    def test_load(self):
        k_file = KdenliveFile()
        k_file.Load(assets / "local_2.kdenlive")
