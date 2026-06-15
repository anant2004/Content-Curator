import json
import threading
from pathlib import Path
from backend.app.config import settings
from backend.app.schemas.generation import GenerationResponse

PRESENTATIONS_FILE = Path(settings.temp_dir) / "presentations.json"
PRESENTATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
_lock = threading.Lock()


class PresentationStore:
    """File-backed store for generated presentations.

    Follows the same pattern as the ingestion SessionStore so that
    slides survive server restarts.
    """

    def get(self, session_id: str) -> GenerationResponse | None:
        data = self._read()
        entry = data.get(session_id)
        return GenerationResponse(**entry) if entry else None

    def set(self, session_id: str, response: GenerationResponse) -> None:
        with _lock:
            data = self._read()
            data[session_id] = response.model_dump()
            self._write(data)

    def delete(self, session_id: str) -> None:
        with _lock:
            data = self._read()
            data.pop(session_id, None)
            self._write(data)

    def _read(self) -> dict:
        if not PRESENTATIONS_FILE.exists():
            return {}
        try:
            with open(PRESENTATIONS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _write(self, data: dict) -> None:
        with open(PRESENTATIONS_FILE, "w") as f:
            json.dump(data, f, indent=2, default=str)


# Singleton
presentation_store = PresentationStore()
