#!/usr/bin/env bash
# duo-install / duo-init 共用的备份与标记块更新逻辑。

duo_options() {
  UPDATE=0
  case "${1:-}" in
    '') [ "$#" -eq 0 ] || return 2 ;;
    --update) [ "$#" -eq 1 ] || return 2; UPDATE=1 ;;
    -h|--help) [ "$#" -eq 1 ] || return 2; echo "$USAGE"; exit 0 ;;
    *) echo "未知参数: $1。$USAGE" >&2; return 2 ;;
  esac
}

duo_backup() {
  local backup
  backup="$(mktemp "$1.duo-backup.XXXXXX")"
  cp -p "$1" "$backup"
  echo "已备份: $backup"
}

# 只接受零个或一个完整标记块，防止损坏的标记吞掉用户内容。
duo_validate() {
  [ -f "$1" ] || return 0
  if ! awk -v b='<!-- DUO-KIT:BEGIN -->' -v e='<!-- DUO-KIT:END -->' '
    $0==b { if (inside || seen) bad=1; inside=1; seen=1 }
    $0==e { if (!inside) bad=1; inside=0 }
    END { exit (bad || inside) ? 1 : 0 }
  ' "$1"; then
    echo "错误: $1 的 DUO-KIT 标记不完整或重复,请修复后重试。" >&2
    return 1
  fi
}

# source 是不含标记的规则正文；legacy 仅用于迁移旧版项目协作章节。
duo_upsert() {
  local target="$1" source="$2" legacy="${3:-}" tmp input
  duo_validate "$target"
  input="$target"
  if [ ! -e "$input" ]; then input=/dev/null; fi
  tmp="$(mktemp)"
  awk -v src="$source" -v legacy="$legacy" \
      -v b='<!-- DUO-KIT:BEGIN -->' -v e='<!-- DUO-KIT:END -->' '
    function block( line) {
      print b
      while ((getline line < src)>0) print line
      close(src)
      print e
      inserted=1
    }
    $0==b { block(); skip=1; next }
    $0==e { skip=0; next }
    legacy!="" && $0==legacy && !inserted { block(); old=1; next }
    old && /^##? / { old=0 }
    !skip && !old { print }
    END { if (!inserted) { if (NR) print ""; block() } }
  ' "$input" > "$tmp"
  if [ -f "$target" ] && cmp -s "$tmp" "$target"; then
    echo "已是最新: $target"
  else
    if [ -f "$target" ]; then duo_backup "$target"; fi
    cat "$tmp" > "$target"
    echo "已更新规则: $target"
  fi
  rm -f "$tmp"
}

duo_copy() {
  local source="$1" target="$2"
  if [ -f "$target" ] && cmp -s "$source" "$target"; then
    echo "已是最新: $target"
  else
    if [ -e "$target" ]; then duo_backup "$target"; fi
    cp "$source" "$target"
    echo "已更新: $target"
  fi
}
