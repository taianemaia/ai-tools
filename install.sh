#!/usr/bin/env bash
# install.sh — symlink agents/skills into ~/.claude/ and copy agents into VS Code Copilot
#
# Usage:
#   ./install.sh
#   ./install.sh --dry-run     # preview without creating anything

set -euo pipefail

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

# VS Code user prompts dir — where .agent.md files live (user-level, all workspaces)
VSCODE_PROMPTS_DIR="$HOME/Library/Application Support/Code/User/prompts"

# ── helpers ──────────────────────────────────────────────────────────────────

run()  { $DRY_RUN || "$@"; }
info() { echo "  $1  $2"; }

# ── Claude Code: symlink each agents/ and skills/ subdirectory ────────────────

link_subdirs() {
    local src_root="$1"
    local dst_root="$2"

    [[ -d "$src_root" ]] || return 0
    run mkdir -p "$dst_root"

    for src in "$src_root"/*/; do
        [[ -d "$src" ]] || continue
        local name dst current_target
        name="$(basename "$src")"
        dst="$dst_root/$name"

        if [[ -L "$dst" ]]; then
            current_target="$(readlink "$dst")"
            if [[ "$current_target" == "$src" ]]; then
                info "=" "Already linked (Claude): $name"
                continue
            fi
            run ln -sfn "$src" "$dst"
            info "~" "Updated stale link (Claude): $name"
        elif [[ -e "$dst" ]]; then
            info "!" "Skipped — real directory exists, remove manually: $dst"
        else
            if $DRY_RUN; then
                info "?" "Would link (Claude): $dst -> $src"
            else
                ln -s "$src" "$dst"
                info "+" "Linked (Claude): $name"
            fi
        fi
    done
}

# ── VS Code Copilot: copy main .md as <name>.agent.md ────────────────────────

sync_vscode_agents() {
    local src_root="$1"
    local dst_dir="$2"

    [[ -d "$src_root" ]] || return 0

    if [[ ! -d "$dst_dir" ]]; then
        if $DRY_RUN; then
            info "?" "Would create: $dst_dir"
        else
            mkdir -p "$dst_dir"
        fi
    fi

    for src in "$src_root"/*/; do
        [[ -d "$src" ]] || continue
        local name src_md dst
        name="$(basename "$src")"
        src_md="$src/$name.md"
        dst="$dst_dir/$name.agent.md"

        [[ -f "$src_md" ]] || continue   # skip agents with no matching .md file

        if $DRY_RUN; then
            info "?" "Would write (VS Code): $name.agent.md"
        else
            cp "$src_md" "$dst"
            info "+" "Copied (VS Code): $name.agent.md"
        fi
    done
}

# ── run ──────────────────────────────────────────────────────────────────────

echo "Claude Code"
link_subdirs "$REPO_ROOT/agents" "$CLAUDE_DIR/agents"
link_subdirs "$REPO_ROOT/skills" "$CLAUDE_DIR/skills"

echo ""
echo "VS Code Copilot"
sync_vscode_agents "$REPO_ROOT/agents" "$VSCODE_PROMPTS_DIR"

if $DRY_RUN; then
    echo -e "\nDry run complete — nothing was changed."
else
    echo -e "\nDone. Restart VS Code for agent changes to take effect."
fi
