#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


RELEASE_SCRIPT = "<script src='https://unpkg.com/maplibre-gl@5.24.0/dist/maplibre-gl.js'></script>"
RELEASE_TITLE = "<title>Terrain in Maplibre - Release</title>"


def run(command: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return result.stdout.strip()


def create_commit_html(script_dir: Path, commit_id: str) -> Path:
    release_path = script_dir / "release.html"
    target_path = script_dir / f"{commit_id}.html"

    html = release_path.read_text()
    if RELEASE_TITLE not in html:
        raise RuntimeError(f"Could not find release title in {release_path}")
    if RELEASE_SCRIPT not in html:
        raise RuntimeError(f"Could not find release MapLibre script tag in {release_path}")

    html = html.replace(
        RELEASE_TITLE,
        f"<title>Terrain in Maplibre - {commit_id}</title>",
    )
    html = html.replace(RELEASE_SCRIPT, f"<script src='{commit_id}.js'></script>")
    target_path.write_text(html)
    return target_path


def update_index(script_dir: Path, commit_id: str) -> None:
    index_path = script_dir / "index.html"
    index = index_path.read_text()
    href = f"{commit_id}.html"

    if f'href="{href}"' in index or f"href='{href}'" in index:
        return

    link = f'\t\t<li><a href="{href}">Commit {commit_id}</a></li>\n'
    if "\t</ul>" in index:
        index = index.replace("\t</ul>", link + "\t</ul>", 1)
    else:
        raise RuntimeError(f"Could not find link insertion point in {index_path}")

    index_path.write_text(index)


def ensure_clean_worktree(maplibre_dir: Path) -> bool:
    status = run(["git", "status", "--porcelain"], cwd=maplibre_dir)
    if not status:
        return True

    print(f"MapLibre checkout has uncommitted changes at {maplibre_dir}:", file=sys.stderr)
    print(status, file=sys.stderr)
    return False


def main() -> int:
    script_dir = Path(__file__).resolve().parent

    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} MAPLIBRE_DIR", file=sys.stderr)
        return 2

    maplibre_dir = Path(sys.argv[1]).expanduser().resolve()

    if not (maplibre_dir / ".git").is_dir():
        print(f"MapLibre checkout not found at {maplibre_dir}", file=sys.stderr)
        return 1

    if not ensure_clean_worktree(maplibre_dir):
        return 1

    commit_id = run(["git", "rev-parse", "--short", "HEAD"], cwd=maplibre_dir)

    dist_dir = maplibre_dir / "dist"
    subprocess.run(["npm", "run", "build-prod"], cwd=maplibre_dir, check=True)

    bundle_src = dist_dir / "maplibre-gl.js"
    if not bundle_src.is_file():
        print(f"Expected bundle was not created: {bundle_src}", file=sys.stderr)
        return 1

    bundle_dst = script_dir / f"{commit_id}.js"
    shutil.copy2(bundle_src, bundle_dst)

    target_html = create_commit_html(script_dir, commit_id)
    update_index(script_dir, commit_id)

    print(f"Created {bundle_dst} and {target_html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
