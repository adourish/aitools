#!/usr/bin/env bash
# Claude Code status line — emoji edition 🎉
# Line 1: [vim] context% | 📥 in 📤 out tokens | rate limits | model | agent | branch + sync + dirty | folder | session
# Line 2: active process | output style
# Protanopia-safe: cyan/yellow/magenta + emoji severity (never color-only)
# Uses python3 for JSON parsing (jq not available on this system)

input=$(cat)

# Parse all JSON fields in a single python3 call for performance
eval "$(echo "$input" | python3 -c "
import sys, json

def get(d, path, default=''):
    keys = path.split('.')
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k)
        else:
            return default
        if d is None:
            return default
    return d

try:
    d = json.load(sys.stdin)
except:
    d = {}

pairs = {
    'model': get(d, 'model.display_name', 'Unknown Model'),
    'model_id': get(d, 'model.id', ''),
    'agent_name': get(d, 'agent.name'),
    'cwd': get(d, 'workspace.current_dir') or get(d, 'cwd'),
    'worktree_branch': get(d, 'worktree.branch'),
    'used_pct': get(d, 'context_window.used_percentage'),
    'total_input': get(d, 'context_window.total_input_tokens', '0'),
    'total_output': get(d, 'context_window.total_output_tokens', '0'),
    'cache_read': get(d, 'context_window.current_usage.cache_read_input_tokens', '0'),
    'cache_write': get(d, 'context_window.current_usage.cache_creation_input_tokens', '0'),
    'five_hr': get(d, 'rate_limits.five_hour.used_percentage'),
    'seven_day': get(d, 'rate_limits.seven_day.used_percentage'),
    'output_style': get(d, 'output_style.name'),
    'session_name': get(d, 'session_name'),
    'vim_mode': get(d, 'vim.mode'),
}

for k, v in pairs.items():
    # Shell-safe: single-quote the value
    safe = str(v).replace(\"'\", \"'\\\\''\" )
    print(f\"{k}='{safe}'\")
" 2>/dev/null)"

# --- Git branch ---
cwd="${cwd//\\//}"
if [ -z "$cwd" ]; then
  cwd=$(pwd)
fi
branch=""
if [ -n "$cwd" ]; then
  branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null)
  if [ -z "$branch" ]; then
    branch=$(git -C "$cwd" --no-optional-locks rev-parse --short HEAD 2>/dev/null)
  fi
fi

if [ -n "$worktree_branch" ]; then
  branch="$worktree_branch (worktree)"
fi

# --- Git dirty file count ---
dirty_count=""
if [ -n "$cwd" ]; then
  dirty_count=$(git -C "$cwd" --no-optional-locks status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  [ "$dirty_count" = "0" ] && dirty_count=""
fi

# --- Git ahead/behind ---
ahead=""
behind=""
if [ -n "$cwd" ] && git -C "$cwd" --no-optional-locks rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1; then
  read -r behind ahead <<< "$(git -C "$cwd" --no-optional-locks rev-list --left-right --count '@{u}...HEAD' 2>/dev/null)"
  [ "$ahead" = "0" ] && ahead=""
  [ "$behind" = "0" ] && behind=""
fi

# --- Short CWD (last 2 path segments) ---
short_cwd=$(echo "$cwd" | sed 's|.*[/\\]\([^/\\]*[/\\][^/\\]*\)$|\1|')
if [ "$short_cwd" = "$cwd" ]; then
  short_cwd=$(basename "$cwd")
fi

# --- Token abbreviation helper ---
abbrev_tokens() {
  echo "$1" | awk '{
    n = $1 + 0
    if (n >= 1000000) printf "%.1fM", n / 1000000
    else if (n >= 1000) printf "%.1fk", n / 1000
    else printf "%d", n
  }'
}

# Clean up output_style if default
if [ "$output_style" = "default" ]; then
  output_style=""
fi

# ============================================================
# Model emoji — robot/alien theme per model 👾🤖🛸
# ============================================================
model_lower=$(echo "$model" | tr '[:upper:]' '[:lower:]')
case "$model_lower" in
  *opus*)   model_emoji="👾" ;;   # space invader boss — big & powerful
  *sonnet*) model_emoji="🤖" ;;   # robot — smart & fast
  *haiku*)  model_emoji="🛸" ;;   # UFO — small & quick
  *)        model_emoji="🦾" ;;   # robot arm — unknown model
esac

# --- Model short name (keyed on model ID) ---
model_id_lower=$(echo "$model_id" | tr '[:upper:]' '[:lower:]')
case "$model_id_lower" in
  *8405ac40-89c6-4613-848c-3d89986fbc01*) model_short="S4.6" ;;   # ELSA (FDA) Claude Sonnet 4.6
  *claude-sonnet-4-6*) model_short="S4.6" ;;
  *claude-opus-4-6*)   model_short="O4.6" ;;
  *claude-haiku-4-5*)  model_short="H4.5" ;;
  *claude-sonnet-4-5*) model_short="S4.5" ;;
  *claude-opus-4-5*)   model_short="O4.5" ;;
  *claude-sonnet-3-7*) model_short="S3.7" ;;
  *claude-sonnet-3-5*) model_short="S3.5" ;;
  *claude-haiku-3-5*)  model_short="H3.5" ;;
  *)                   model_short="$model" ;;
esac

# ============================================================
# Process detection + animated status indicators
# Animation frame cycles based on current second
# ============================================================
frame=$(( $(date +%s) % 4 ))

# Sniff running processes (Windows-compatible via tasklist/ps)
procs=$(ps -eo args 2>/dev/null || tasklist /FO CSV /NH 2>/dev/null)

active_anim=""

detect_proc() {
  echo "$procs" | grep -qi "$1" 2>/dev/null
}

if detect_proc "sf.*deploy.*destructive\|sfdx.*destructive"; then
  # 🐉 Destructive deploy — dragon fire
  case $frame in
    0) active_anim="$(printf '\033[1;35m🐉 🔥 Destroying...\033[0m')" ;;
    1) active_anim="$(printf '\033[1;35m🐉 💀 Destroying...\033[0m')" ;;
    2) active_anim="$(printf '\033[1;35m🐉 🔥 Destroying...\033[0m')" ;;
    3) active_anim="$(printf '\033[1;35m🐉 💀 Destroying...\033[0m')" ;;
  esac
elif detect_proc "sf project deploy\|sf.*deploy.*start\|sfdx.*deploy"; then
  # 🚀 SF Deploy — rocket launch
  case $frame in
    0) active_anim="$(printf '\033[0;36m🚀 💨 · 🌍 Deploying...\033[0m')" ;;
    1) active_anim="$(printf '\033[0;36m· 🚀 ☁️ 🌍 Deploying...\033[0m')" ;;
    2) active_anim="$(printf '\033[0;36m· · 🚀 ⭐ Deploying...\033[0m')" ;;
    3) active_anim="$(printf '\033[0;36m· · · 🚀 🌙 Deploying...\033[0m')" ;;
  esac
elif detect_proc "sf project retrieve\|sf.*retrieve"; then
  # 🎣 SF Retrieve — fishing
  case $frame in
    0) active_anim="$(printf '\033[0;36m🎣 · · · Retrieving...\033[0m')" ;;
    1) active_anim="$(printf '\033[0;36m🎣 · · 🐠 Retrieving...\033[0m')" ;;
    2) active_anim="$(printf '\033[0;36m🎣 · 🐟 🐠 Retrieving...\033[0m')" ;;
    3) active_anim="$(printf '\033[0;36m🎣 🐡 🐟 🐠 Retrieving...\033[0m')" ;;
  esac
elif detect_proc "sf apex run test\|sf apex test"; then
  # 🐹 Apex tests — hamster wheel
  case $frame in
    0) active_anim="$(printf '\033[0;33m🐹 ◐ Testing Apex...\033[0m')" ;;
    1) active_anim="$(printf '\033[0;33m🐹 ◓ Testing Apex...\033[0m')" ;;
    2) active_anim="$(printf '\033[0;33m🐹 ◑ Testing Apex...\033[0m')" ;;
    3) active_anim="$(printf '\033[0;33m🐹 ◒ Testing Apex...\033[0m')" ;;
  esac
elif detect_proc "playwright"; then
  # 🦉 E2E Playwright — owl patrol
  case $frame in
    0) active_anim="$(printf '\033[0;35m🦉 👁️ · · E2E...\033[0m')" ;;
    1) active_anim="$(printf '\033[0;35m· 🦉 👁️ · E2E...\033[0m')" ;;
    2) active_anim="$(printf '\033[0;35m· · 🦉 👁️ E2E...\033[0m')" ;;
    3) active_anim="$(printf '\033[0;35m· · · 🦉 👁️ E2E...\033[0m')" ;;
  esac
elif detect_proc "jest\|npm test"; then
  # 🐁 Jest tests — mouse in maze
  case $frame in
    0) active_anim="$(printf '\033[0;33m🐁 · · 🧀 Testing...\033[0m')" ;;
    1) active_anim="$(printf '\033[0;33m· 🐁 · 🧀 Testing...\033[0m')" ;;
    2) active_anim="$(printf '\033[0;33m· · 🐁 🧀 Testing...\033[0m')" ;;
    3) active_anim="$(printf '\033[0;33m· · 🐁 🧀 ✅ Done!\033[0m')" ;;
  esac
elif detect_proc "eslint"; then
  # 🐱 ESLint — cat grooming
  case $frame in
    0) active_anim="$(printf '\033[0;90m🐱 ✨ Linting...\033[0m')" ;;
    1) active_anim="$(printf '\033[0;90m🐱 💅 Linting...\033[0m')" ;;
    2) active_anim="$(printf '\033[0;90m🐱 ✨ Linting...\033[0m')" ;;
    3) active_anim="$(printf '\033[0;90m🐱 💅 Linting...\033[0m')" ;;
  esac
elif detect_proc "prettier"; then
  # 🐱 Prettier — cat grooming (sparkle variant)
  case $frame in
    0) active_anim="$(printf '\033[0;90m🐱 🪮 Prettifying...\033[0m')" ;;
    1) active_anim="$(printf '\033[0;90m🐱 ✨ Prettifying...\033[0m')" ;;
    2) active_anim="$(printf '\033[0;90m🐱 🪮 Prettifying...\033[0m')" ;;
    3) active_anim="$(printf '\033[0;90m🐱 ✨ Prettifying...\033[0m')" ;;
  esac
elif detect_proc "git push"; then
  # 🕊️ Git push — carrier pigeon outbound
  case $frame in
    0) active_anim="$(printf '\033[0;36m🕊️ · · · Pushing...\033[0m')" ;;
    1) active_anim="$(printf '\033[0;36m· 🕊️ · · Pushing...\033[0m')" ;;
    2) active_anim="$(printf '\033[0;36m· · 🕊️ · Pushing...\033[0m')" ;;
    3) active_anim="$(printf '\033[0;36m· · · 📬 Pushed!\033[0m')" ;;
  esac
elif detect_proc "git pull\|git fetch"; then
  # 🕊️ Git pull/fetch — carrier pigeon inbound
  case $frame in
    0) active_anim="$(printf '\033[0;36m· · · 🕊️ Pulling...\033[0m')" ;;
    1) active_anim="$(printf '\033[0;36m· · 🕊️ · Pulling...\033[0m')" ;;
    2) active_anim="$(printf '\033[0;36m· 🕊️ · · Pulling...\033[0m')" ;;
    3) active_anim="$(printf '\033[0;36m📬 · · · Pulled!\033[0m')" ;;
  esac
elif detect_proc "npm install\|yarn install\|pnpm install"; then
  # 🐜 Package install — ant carrying packages
  case $frame in
    0) active_anim="$(printf '\033[0;33m🐜 📦 · · Installing...\033[0m')" ;;
    1) active_anim="$(printf '\033[0;33m· 🐜 📦 · Installing...\033[0m')" ;;
    2) active_anim="$(printf '\033[0;33m· · 🐜 📦 Installing...\033[0m')" ;;
    3) active_anim="$(printf '\033[0;33m· · · 🐜 📦 Installing...\033[0m')" ;;
  esac
elif detect_proc "webpack\|vite\|npm run build"; then
  # 🦫 Build — beaver at work
  case $frame in
    0) active_anim="$(printf '\033[0;33m🦫 🪵 Building...\033[0m')" ;;
    1) active_anim="$(printf '\033[0;33m🦫 🪓 Building...\033[0m')" ;;
    2) active_anim="$(printf '\033[0;33m🦫 🏗️ Building...\033[0m')" ;;
    3) active_anim="$(printf '\033[0;33m🦫 🏠 Building...\033[0m')" ;;
  esac
elif detect_proc "sleep"; then
  # 🧪 TEST — remove after smoke test
  case $frame in
    0) active_anim="$(printf '\033[0;36m🐸 · · · Test anim...\033[0m')" ;;
    1) active_anim="$(printf '\033[0;36m· 🐸 · · Test anim...\033[0m')" ;;
    2) active_anim="$(printf '\033[0;36m· · 🐸 · Test anim...\033[0m')" ;;
    3) active_anim="$(printf '\033[0;36m· · · 🐸 Test anim...\033[0m')" ;;
  esac
elif detect_proc "python3\|python "; then
  # 🐍 Python script
  case $frame in
    0) active_anim="$(printf '\033[0;33m🐍 · · ⚙️ Python...\033[0m')" ;;
    1) active_anim="$(printf '\033[0;33m· 🐍 · ⚙️ Python...\033[0m')" ;;
    2) active_anim="$(printf '\033[0;33m· · 🐍 ⚙️ Python...\033[0m')" ;;
    3) active_anim="$(printf '\033[0;33m· · · 🐍 ⚙️ Python...\033[0m')" ;;
  esac
fi

# ============================================================
# Build output — two lines
# ============================================================
SEP="$(printf '\033[0;90m|\033[0m')"

join_parts() {
  local result=""
  for part in "$@"; do
    if [ -z "$result" ]; then
      result="$part"
    else
      result="$result $SEP $part"
    fi
  done
  printf '%b' "$result"
}

# --- Line 1 parts ---
line1=()

# Vim mode badge
if [ -n "$vim_mode" ]; then
  if [ "$vim_mode" = "NORMAL" ]; then
    line1+=("$(printf '\033[1;33m⌨️ [N]\033[0m')")
  else
    line1+=("$(printf '\033[1;36m✏️ [I]\033[0m')")
  fi
fi

# Context remaining % with escalation (FIRST)
if [ -n "$used_pct" ]; then
  used_int=$(printf '%.0f' "$used_pct")
  remaining_int=$((100 - used_int))
  if [ "$used_int" -ge 80 ]; then
    ctx_part="$(printf '\033[1;35m🚨 💥 %d%%\033[0m' "$remaining_int")"       # alarm + explosion — critical
  elif [ "$used_int" -ge 60 ]; then
    ctx_part="$(printf '\033[1;35m⚙️ ⚠️ %d%%\033[0m' "$remaining_int")"       # gears warning — getting tight
  elif [ "$used_int" -ge 40 ]; then
    ctx_part="$(printf '\033[0;33m🦑 %d%%\033[0m' "$remaining_int")"           # squid — watchful (aquatic)
  else
    ctx_part="$(printf '\033[0;36m🫧 %d%%\033[0m' "$remaining_int")"           # bubbles — plenty of room (aquatic calm)
  fi
  line1+=("$ctx_part")
fi

# Token totals — combined with escalating robot/tech emoji (SECOND)
tok_total=$(( ${total_input:-0} + ${total_output:-0} ))
if [ "$tok_total" -gt 0 ]; then
  if   [ "$tok_total" -ge 1000000 ]; then tok_emoji="🏭"   # factory — industrial scale
  elif [ "$tok_total" -ge 500000  ]; then tok_emoji="🔌"   # plug — heavily powered
  elif [ "$tok_total" -ge 250000  ]; then tok_emoji="🔩"   # bolt — well-used
  elif [ "$tok_total" -ge 100000  ]; then tok_emoji="👽"   # alien — getting interesting
  elif [ "$tok_total" -ge 50000   ]; then tok_emoji="🛰️"   # satellite — in orbit
  elif [ "$tok_total" -ge 10000   ]; then tok_emoji="🔋"   # battery — charging up
  else                                    tok_emoji="✨"   # sparkle — fresh start
  fi
  tok_abbrev=$(abbrev_tokens "$tok_total")
  line1+=("$(printf '\033[0;35m%s %s\033[0m' "$tok_emoji" "$tok_abbrev")")
fi

# Rate limits with escalation (THIRD)
if [ -n "$five_hr" ] || [ -n "$seven_day" ]; then
  rate_str=""
  if [ -n "$five_hr" ]; then
    five_int=$(printf '%.0f' "$five_hr")
    if [ "$five_int" -ge 80 ]; then
      rate_str="$(printf '\033[1;35m📡 5h: %d%%!\033[0m' "$five_int")"         # satellite dish — signal maxed
    elif [ "$five_int" -ge 50 ]; then
      rate_str="$(printf '\033[0;33m🐌 5h: %d%%\033[0m' "$five_int")"          # snail — slowing down
    else
      rate_str="$(printf '\033[0;90m💧 5h: %d%%\033[0m' "$five_int")"          # droplet — flowing fine (aquatic calm)
    fi
  fi
  if [ -n "$seven_day" ]; then
    seven_int=$(printf '%.0f' "$seven_day")
    sep_inner=""
    [ -n "$rate_str" ] && sep_inner=" "
    if [ "$seven_int" -ge 80 ]; then
      rate_str="${rate_str}${sep_inner}$(printf '\033[1;35m📡 7d: %d%%!\033[0m' "$seven_int")"
    elif [ "$seven_int" -ge 50 ]; then
      rate_str="${rate_str}${sep_inner}$(printf '\033[0;33m🐌 7d: %d%%\033[0m' "$seven_int")"
    else
      rate_str="${rate_str}${sep_inner}$(printf '\033[0;90m💧 7d: %d%%\033[0m' "$seven_int")"
    fi
  fi
  line1+=("$rate_str")
fi

# Model with robot/alien emoji (FOURTH)
line1+=("$(printf '\033[0;36m%s %s\033[0m' "$model_emoji" "$model_short")")

# Agent (only when present)
if [ -n "$agent_name" ]; then
  line1+=("$(printf '\033[0;35m🧠 %s\033[0m' "$agent_name")")
fi

# Branch + git indicators
if [ -n "$branch" ]; then
  git_str="$(printf '\033[0;33m🌿 %s\033[0m' "$branch")"

  # Ahead/behind with animal escalation
  if [ -n "$ahead" ] || [ -n "$behind" ]; then
    sync_str=""
    if [ -n "$ahead" ]; then
      if [ "$ahead" -ge 10 ]; then
        sync_str="$(printf '\033[0;36m🐘 ⬆ %s\033[0m' "$ahead")"    # elephant — way ahead
      elif [ "$ahead" -ge 5 ]; then
        sync_str="$(printf '\033[0;36m🐕 ⬆ %s\033[0m' "$ahead")"    # dog — moderately ahead
      else
        sync_str="$(printf '\033[0;36m🐾 ⬆ %s\033[0m' "$ahead")"    # paw — a few ahead
      fi
    fi
    if [ -n "$behind" ]; then
      sep_ab=""
      [ -n "$sync_str" ] && sep_ab=" "
      if [ "$behind" -ge 10 ]; then
        sync_str="${sync_str}${sep_ab}$(printf '\033[1;35m🦈 ⬇ %s\033[0m' "$behind")"   # shark — danger, way behind
      elif [ "$behind" -ge 5 ]; then
        sync_str="${sync_str}${sep_ab}$(printf '\033[1;35m🐊 ⬇ %s\033[0m' "$behind")"   # croc — pull soon
      else
        sync_str="${sync_str}${sep_ab}$(printf '\033[0;33m🐢 ⬇ %s\033[0m' "$behind")"   # turtle — a bit behind
      fi
    fi
    git_str="${git_str} ${sync_str}"
  fi

  # Dirty files with escalation
  if [ -n "$dirty_count" ]; then
    dirty_int=$((dirty_count + 0))
    if [ "$dirty_int" -ge 20 ]; then
      git_str="${git_str} $(printf '\033[1;35m🦝 %s\033[0m' "$dirty_count")"    # raccoon — messy!
    elif [ "$dirty_int" -ge 10 ]; then
      git_str="${git_str} $(printf '\033[0;33m🐿️ %s\033[0m' "$dirty_count")"    # squirrel — hoarding changes
    else
      git_str="${git_str} $(printf '\033[0;90m📝 %s\033[0m' "$dirty_count")"     # notepad — normal
    fi
  fi
  line1+=("$git_str")
fi

# Short folder
if [ -n "$short_cwd" ]; then
  line1+=("$(printf '\033[0;90m📁 %s\033[0m' "$short_cwd")")
fi

# Session name
if [ -n "$session_name" ]; then
  line1+=("$(printf '\033[0;90m💬 \"%s\"\033[0m' "$session_name")")
fi

# --- Line 2 parts ---
line2=()

# Active process animation (leading position — most eye-catching)
if [ -n "$active_anim" ]; then
  line2+=("$active_anim")
fi

# Output style
if [ -n "$output_style" ]; then
  line2+=("$(printf '\033[0;90m🎨 %s\033[0m' "$output_style")")
fi

# ============================================================
# Print both lines
# ============================================================
join_parts "${line1[@]}"
echo
join_parts "${line2[@]}"
echo
