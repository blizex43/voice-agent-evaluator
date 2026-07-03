from pathlib import Path
import re
def get_incremented_filename(name: str, parent_dir: Path) -> Path:
	pattern = re.compile(rf"^{name}(\d+)$")

	numbers = []

	for path in parent_dir.iterdir():
		if path.is_dir():
			match = pattern.match(path.name)
			if match:
				numbers.append(int(match.group(1)))
				
	next_num = max(numbers, default=0) + 1
	new_folder = parent_dir / f"{name}{next_num:02d}"
	return new_folder

def get_incremented_file_dirs(name: str, parent_dir: Path, extensions: dict[str, str]) -> dict[str, Path]:
	base = get_incremented_filename(name, parent_dir)
	return {
    abbr: base.with_suffix(f".{ext}") for abbr, ext in extensions.items()
}


def ensure_output_dir(dir: Path) -> None:
    dir.mkdir(parents=True, exist_ok=True)