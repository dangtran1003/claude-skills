#!/usr/bin/env bash
# Cài skill vào ~/.claude/skills/ — mặc định symlink để `git pull` là có bản mới ngay.
#   ./install.sh                 cài tất cả
#   ./install.sh bss-flow watcher   cài vài cái
#   COPY=1 ./install.sh          copy thay vì symlink
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$DEST"

targets=("$@")
if [ ${#targets[@]} -eq 0 ]; then
  targets=()
  for d in "$SRC"/*/; do targets+=("$(basename "$d")"); done
fi

for name in "${targets[@]}"; do
  if [ ! -d "$SRC/$name" ]; then
    echo "  bỏ qua $name (không có trong repo)" >&2
    continue
  fi

  if [ -e "$DEST/$name" ] && [ ! -L "$DEST/$name" ]; then
    backup="$DEST/$name.bak.$(date +%Y%m%d%H%M%S)"
    mv "$DEST/$name" "$backup"
    echo "  $name: đã có sẵn, backup sang $(basename "$backup")"
  else
    rm -f "$DEST/$name"
  fi

  if [ "${COPY:-0}" = "1" ]; then
    cp -r "$SRC/$name" "$DEST/$name"
  else
    ln -s "$SRC/$name" "$DEST/$name"
  fi

  if [ -f "$SRC/$name/.env.example" ] && [ ! -f "$DEST/$name/.env" ]; then
    echo "  $name: cần điền credential → cp $SRC/$name/.env.example $SRC/$name/.env"
  else
    echo "  $name: xong"
  fi
done

echo
echo "Mở lại Claude Code để nạp skill mới."
