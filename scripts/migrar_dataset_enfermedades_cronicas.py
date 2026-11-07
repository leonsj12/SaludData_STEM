"""Migrate legacy respiratory-labelled artifacts to chronic-disease naming.

The original source CSV is intentionally preserved under its published
filename. This migration changes only the local dataset identifier and
artifact filenames; it does not filter, deduplicate, or alter source rows.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = "respiratorio"
NEW = "enfermedades_cronicas"
FOLDERS = [
    ROOT / "data" / "raw",
    ROOT / "data" / "processed",
    ROOT / "data" / "analytics",
    ROOT / "data" / "metadata",
]


def migrate() -> list[tuple[str, str]]:
    moved = []
    for folder in FOLDERS:
        if not folder.exists():
            continue
        for source in sorted(folder.glob(f"{OLD}*")):
            target = source.with_name(source.name.replace(OLD, NEW, 1))
            if target.exists():
                raise FileExistsError(
                    f"Migration stopped: target already exists: {target}"
                )
            source.rename(target)
            moved.append((str(source), str(target)))
    return moved


if __name__ == "__main__":
    for source, target in migrate():
        print(f"RENAMED {source} -> {target}")
    print("Dataset identifier migration completed. Source CSV unchanged.")
