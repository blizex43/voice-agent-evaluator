from pathlib import Path
import re
from enums.strings import FILE_PREFIX_REPORT


def find_next_index(parent_dir: Path, pattern: re.Pattern[str]) -> int:
    """Return the next available integer index matching `pattern` in `parent_dir`."""
    numbers = [
        int(match.group(1))
        for path in parent_dir.iterdir()
        if path.is_dir() and (match := pattern.match(path.name))
    ]
    return max(numbers, default=0) + 1


def get_incremented_filename(name: str, parent_dir: Path) -> Path:
    """Return a new zero-padded numbered folder under `parent_dir`."""
    pattern = re.compile(rf"^{name}(\d+)$")
    next_num = find_next_index(parent_dir, pattern)
    return parent_dir / f"{name}{next_num:02d}"


def get_incremented_file_dirs(
    name: str = "",
    parent_dir: Path,
    extensions: dict[str, str],
    prefix: str = FILE_PREFIX_REPORT,
) -> dict[str, Path]:
    """Return a mapping of abbreviation -> file path using `prefix` + `name` + numeric folder."""
    base = get_incremented_filename(f"{prefix}{name}", parent_dir)
    return {
        abbr: base.with_suffix(f".{ext}") for abbr, ext in extensions.items()
    }


def ensure_output_dir(dir: Path) -> None:
    """Create `dir` (and parents) if it does not exist."""
    dir.mkdir(parents=True, exist_ok=True)
