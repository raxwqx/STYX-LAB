#!/usr/bin/env bash
set -euo pipefail

SOURCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-$HOME/projeler/STYX-LAB}"

if [[ ! -d "$TARGET/.git" ]]; then
  echo "ERROR: Target must be an existing Git repository containing .git: $TARGET" >&2
  echo "Usage: bash install-to-repo.sh /path/to/STYX-LAB" >&2
  exit 2
fi

TARGET="$(cd "$TARGET" && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="${TMPDIR:-/tmp}/STYX-LAB-backup-$STAMP"
mkdir -p "$BACKUP"

FILES=(
  .github/workflows/tests.yml .gitignore CITATION.cff CHANGELOG.md
  CONTRIBUTING.md LICENSE README.md ROADMAP.md SECURITY.md pyproject.toml
  docs/ARCHITECTURE.md docs/methodology/README.md docs/scenarios/TEMPLATE.md
  docs/scenarios/web-security-headers.md lab/__init__.py lab/report.py lab/tui.py
  lab/web/__init__.py lab/web/security_headers_lab.py
  tests/test_project_structure.py tests/test_report.py tests/test_security_headers_lab.py
  tests/test_tui.py
)

MANIFEST="$BACKUP/manifest.tsv"
: > "$MANIFEST"
for rel in "${FILES[@]}"; do
  if [[ ! -f "$SOURCE_ROOT/$rel" ]]; then
    echo "ERROR: Package file missing: $SOURCE_ROOT/$rel" >&2
    exit 3
  fi
  if [[ -f "$TARGET/$rel" ]]; then
    printf 'EXISTS\t%s\n' "$rel" >> "$MANIFEST"
    mkdir -p "$BACKUP/$(dirname "$rel")"
    cp -p "$TARGET/$rel" "$BACKUP/$rel"
  else
    printf 'NEW\t%s\n' "$rel" >> "$MANIFEST"
  fi
done

rollback() {
  echo "Validation failed; restoring previous files..." >&2
  while IFS=$'\t' read -r state rel; do
    if [[ "$state" == "EXISTS" ]]; then
      mkdir -p "$TARGET/$(dirname "$rel")"
      cp -p "$BACKUP/$rel" "$TARGET/$rel"
    else
      rm -f "$TARGET/$rel"
    fi
  done < "$MANIFEST"
  echo "Rollback complete. Backup: $BACKUP" >&2
}

for rel in "${FILES[@]}"; do
  mkdir -p "$TARGET/$(dirname "$rel")"
  cp "$SOURCE_ROOT/$rel" "$TARGET/$rel"
done

if ! (cd "$TARGET" && python3 -m unittest discover -s tests -v); then
  rollback
  exit 4
fi

if ! (cd "$TARGET" && python3 -m compileall -q lab tests); then
  rollback
  exit 5
fi

echo
echo "STYX-LAB v1.0.1 installed and tested successfully."
echo "Git history was preserved."
echo "Backup of replaced files: $BACKUP"
echo "Next: cd '$TARGET' && python3 lab/tui.py"
