# ai-tools

Personal agents and skills for Claude Code and Codex, stored as a versioned git repository.

## Structure

```
ai-tools/
├── agents/           # Claude Code agent definitions (.md with YAML frontmatter)
├── skills/           # Claude Code / Codex skill definitions (<name>/SKILL.md)
├── hooks/            # Lifecycle hooks (hooks.json)
├── .claude/          # Pre-granted permissions for skills
└── .claude-plugin/   # Plugin manifest (plugin.json)
```

## Symlink setup

Both AI providers read from symlinks that point here:

| Symlink | → Points to |
|---------|-------------|
| `~/.claude/agents` | `~/Documents/Projects/ai-tools/agents` |
| `~/.agents/skills` | `~/Documents/Projects/ai-tools/skills` |

Edit anything in this repo and changes are instantly available in Claude Code and Codex — no copy step needed.

## Setup on a new machine

```bash
git clone <remote-url> ~/Documents/Projects/ai-tools

# Replace provider paths with symlinks
rm -rf ~/.claude/agents
ln -s ~/Documents/Projects/ai-tools/agents ~/.claude/agents

rm -rf ~/.agents/skills
mkdir -p ~/.agents
ln -s ~/Documents/Projects/ai-tools/skills ~/.agents/skills
```

## Adding a skill

1. Create `skills/<name>/SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: skill-name
   description: What this skill does and when to trigger it.
   ---
   ```
2. Add the skill body (instructions, references, etc.)
3. Commit and push.

## Adding an agent

1. Create `agents/<name>.md` with YAML frontmatter:
   ```yaml
   ---
   name: agent-name
   description: What this agent does and when to delegate to it.
   tools: Read, Edit, Bash
   model: sonnet
   ---
   ```
2. Add the agent system prompt as the body.
3. Commit and push.
