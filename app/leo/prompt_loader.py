from functools import lru_cache
from pathlib import Path


class PromptLoader:
    """Загружает системные промпты."""

    def __init__(
        self,
        prompts_path: Path,
    ) -> None:
        self._prompts_path = prompts_path

    @lru_cache(maxsize=32)
    def load(
        self,
        name: str,
    ) -> str:
        path = self._prompts_path / name

        return path.read_text(
            encoding="utf-8",
        )