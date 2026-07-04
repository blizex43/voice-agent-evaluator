from pathlib import Path
import re
from enums.strings import FILE_PREFIX_REPORT


def find_next_index(name: str, parent_dir: Path, pattern: re.Pattern[str]) -> int:
    """Return the next available integer index matching `pattern` in `parent_dir`."""
    numbers = []
    for path in parent_dir.glob(f"{name}*"):
        match = pattern.match(path.stem)
        if match:
            numbers.append(int(match.group(1)))
    return max(numbers, default=0) + 1


def get_incremented_filename(name: str, parent_dir: Path) -> Path:
    """Return a new zero-padded numbered folder under `parent_dir`."""
    pattern = re.compile(rf"^{name}(\d+)$")
    next_num = find_next_index(name, parent_dir, pattern)
    return append_index_to_path(parent_dir, name, next_num)


def append_index_to_path(dir: Path, name: str, index: int) -> Path:
    return dir / f"{name}{index:02d}"


def get_incremented_file_dirs(
    parent_dir: Path,
    extensions: dict[str, str],
    prefix: str = FILE_PREFIX_REPORT,
    index: int = -1,
) -> dict[str, Path]:
    """Return a mapping of abbreviation -> file path using `prefix` + `name` + numeric folder."""
    base = append_index_to_path(parent_dir, prefix, index) if index and index != -1 else get_incremented_filename(f"{prefix}", parent_dir)
    return {
        abbr: base.with_suffix(f".{ext}") for abbr, ext in extensions.items()
    }


def ensure_output_dir(dir: Path) -> None:
    """Create `dir` (and parents) if it does not exist."""
    dir.mkdir(parents=True, exist_ok=True)
