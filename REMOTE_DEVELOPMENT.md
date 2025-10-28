# Remote Development Guide

**How to code directly on your Ubuntu server from your Mac**

---

## Why Remote Development?

**Benefits:**
- Code runs in the actual deployment environment
- No "works on my machine" problems
- Use server's CPU/RAM for heavy tasks
- Edit files directly on server (no git push/pull cycle)
- Access to server-only resources (databases, local services)

**Prerequisites:**
✅ Tailscale installed on both Mac and server
✅ SSH access working: `ssh homeserver`

---

## Option 1: VS Code Remote SSH (Recommended)

**Best for:** Full IDE experience on remote server

### Setup (One-time, 2 minutes)

**1. Install VS Code Remote SSH Extension:**
```bash
# On your Mac:
# Open VS Code
# Press Cmd+Shift+X (Extensions)
# Search: "Remote - SSH"
# Install the extension by Microsoft
```

**2. Connect to Server:**
```
# In VS Code:
# Press Cmd+Shift+P
# Type: "Remote-SSH: Connect to Host"
# Select: homeserver (or type: youruser@your-server-name)

# First time: VS Code installs server components (30 seconds)
# Window reloads - you're now editing files ON the server!
```

**3. Open Your Project:**
```
# File > Open Folder
# Navigate to: /home/youruser/budgeting_automator_2.0
# Click OK

# You're now coding directly on the server!
```

### Features That Work:

✅ **Terminal** - Opens bash on the server
```bash
# Terminal > New Terminal
cd backend
source venv/bin/activate
python -m app.main
```

✅ **File Explorer** - Browse server files

✅ **Git** - Commit/push from server

✅ **Python Extensions** - Install on server:
- Python (Microsoft)
- Pylance
- Python Debugger

✅ **Live Debugging** - Set breakpoints, inspect variables

✅ **Port Forwarding** - Access server:8000 as localhost:8000 on Mac
```
# When you run: python -m app.main
# VS Code auto-forwards port 8000
# Open Mac browser: http://localhost:8000
# It's actually hitting the server!
```

### Workflow:

```bash
# 1. Open VS Code
# 2. Cmd+Shift+P → "Remote-SSH: Connect to Host" → homeserver
# 3. Open folder: budgeting_automator_2.0
# 4. Terminal → New Terminal
# 5. cd backend && source venv/bin/activate
# 6. Make changes, test immediately
# 7. Git commit/push when ready
```

---

## Option 2: SSH + Local Editor (Simpler)

**Best for:** Quick edits, prefer local editor

### Method A: SSHFS (Mount remote folder locally)

**Install SSHFS:**
```bash
# On Mac:
brew install macfuse
brew install gromgit/fuse/sshfs-mac

# Restart Mac after install
```

**Mount server folder:**
```bash
# Create mount point
mkdir -p ~/remote-server

# Mount server's home directory
sshfs homeserver:/home/youruser ~/remote-server

# Now edit files with any Mac app:
code ~/remote-server/budgeting_automator_2.0
# or
open -a "Sublime Text" ~/remote-server/budgeting_automator_2.0
```

**Unmount when done:**
```bash
umount ~/remote-server
```

**Make it automatic (Optional):**
```bash
# Add to ~/.zshrc or ~/.bashrc:
alias mount-server='sshfs homeserver:/home/youruser ~/remote-server'
alias unmount-server='umount ~/remote-server'
```

### Method B: Rsync (Sync changes)

**Edit locally, sync to server:**
```bash
# Make changes on Mac
code /Users/s-singhal/budgeting_automator_2.0

# Sync to server (one command):
rsync -avz --exclude 'venv' --exclude '__pycache__' \
  /Users/s-singhal/budgeting_automator_2.0/ \
  homeserver:~/budgeting_automator_2.0/

# Run on server:
ssh homeserver "cd budgeting_automator_2.0/backend && sudo systemctl restart budget-api"
```

**Automate with a script:**
```bash
# Create: ~/deploy.sh
#!/bin/bash
echo "Syncing to server..."
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '.git' \
  /Users/s-singhal/budgeting_automator_2.0/ \
  homeserver:~/budgeting_automator_2.0/

echo "Restarting API..."
ssh homeserver "sudo systemctl restart budget-api"

echo "Done! Check status:"
ssh homeserver "sudo systemctl status budget-api --no-pager"
```

```bash
chmod +x ~/deploy.sh
# Now just:
~/deploy.sh
```

---

## Option 3: tmux + SSH (For Terminal Lovers)

**Best for:** Vim/Emacs users, persistent sessions

**Setup tmux on server:**
```bash
ssh homeserver
sudo apt install tmux -y
```

**Create development session:**
```bash
# SSH in
ssh homeserver

# Start tmux session
tmux new -s dev

# Split screen (Ctrl+B then %)
# Left: editor, Right: run server

# In left pane:
cd budgeting_automator_2.0/backend
vim app/main.py  # or nano, emacs, etc.

# In right pane:
source venv/bin/activate
python -m app.main

# Switch panes: Ctrl+B then arrow keys
# Detach: Ctrl+B then D (session keeps running!)

# Re-attach later:
ssh homeserver
tmux attach -t dev
```

**tmux Cheat Sheet:**
```
Ctrl+B %        Split vertically
Ctrl+B "        Split horizontally
Ctrl+B arrows   Switch panes
Ctrl+B D        Detach (session stays alive)
Ctrl+B [        Scroll mode (q to exit)
tmux attach     Reattach
tmux ls         List sessions
```

---

## Option 4: JupyterLab (For Python Experimentation)

**Best for:** Testing Python code, data analysis

**Install on server:**
```bash
ssh homeserver
cd budgeting_automator_2.0/backend
source venv/bin/activate
pip install jupyterlab
```

**Run JupyterLab:**
```bash
# On server:
jupyter lab --no-browser --port=8888

# Copy the token from output
```

**Access from Mac:**
```bash
# In new terminal on Mac:
ssh -L 8888:localhost:8888 homeserver

# Open browser: http://localhost:8888
# Paste token
# Now you have Jupyter running on server, accessible from Mac!
```

**Create notebook:**
```python
# Test your API code interactively:
import sys
sys.path.append('/home/youruser/budgeting_automator_2.0/backend')

from app import crud, models
from app.database import SessionLocal

db = SessionLocal()
transactions = crud.get_transactions(db, limit=10)
for tx in transactions:
    print(f"{tx.vendor}: ¥{tx.amount}")
```

---

## Git Workflow (Recommended)

**Best Practice: Use git for changes**

**On Server:**
```bash
# Make changes
git add .
git commit -m "feat: add new feature"
git push origin main
```

**On Mac:**
```bash
# Pull changes
cd /Users/s-singhal/budgeting_automator_2.0
git pull origin main
```

**Or vice versa:**
```bash
# Develop on Mac
git commit -am "fix: bug fix"
git push

# Deploy to server
ssh homeserver
cd budgeting_automator_2.0
git pull
sudo systemctl restart budget-api
```

---

## Comparison Table

| Method | Setup Time | Best For | Pros | Cons |
|--------|-----------|----------|------|------|
| **VS Code Remote SSH** | 2 min | Everything | Full IDE, debugging, port forwarding | Requires VS Code |
| **SSHFS** | 5 min | Quick edits | Use any editor | Can be slow over wifi |
| **Rsync** | 1 min | Deploy workflow | Fast, simple | Manual sync |
| **tmux** | 2 min | Terminal users | Lightweight, persistent | Terminal only |
| **JupyterLab** | 3 min | Python testing | Interactive, great for data | Not for app development |
| **Git only** | 0 min | Production deploys | Clean, version controlled | More steps |

---

## My Recommendation

**For this project, use:**

1. **VS Code Remote SSH** (primary development)
   - Edit code on server
   - Test immediately
   - Debug with breakpoints

2. **Git** (save work)
   - Commit frequently
   - Push to GitHub
   - Never lose work

3. **tmux** (long-running tasks)
   - Keep server running while disconnected
   - Monitor logs

**Example workflow:**
```bash
# Morning:
# 1. Open VS Code, connect to homeserver
# 2. Open budgeting_automator_2.0 folder
# 3. Start coding

# During development:
# - Edit files in VS Code
# - Run/test in integrated terminal
# - Git commit when feature works

# End of day:
# - Git push
# - Close VS Code
# - Server keeps running via systemd

# Tomorrow:
# - Reconnect, continue coding
# - Changes are already on server!
```

---

## Troubleshooting

### VS Code can't connect:
```bash
# Test SSH manually first:
ssh homeserver
# If this works, VS Code should work

# Clear VS Code cache:
# Cmd+Shift+P → "Remote-SSH: Kill VS Code Server on Host"
# Reconnect
```

### SSHFS mount fails:
```bash
# Ensure macFUSE is installed
brew reinstall macfuse
# Restart Mac

# Try manually:
sshfs -o debug homeserver:/home/youruser ~/remote-server
```

### Port forwarding not working:
```bash
# Manual port forward:
ssh -L 8000:localhost:8000 homeserver

# In another terminal:
ssh homeserver
cd budgeting_automator_2.0/backend
source venv/bin/activate
python -m app.main

# Open Mac browser: http://localhost:8000
```

### Git conflicts:
```bash
# Server has changes, Mac has changes:
# On server:
git stash
git pull
git stash pop

# Or:
git fetch origin
git rebase origin/main
```

---

## Security Note

**Never edit production .env file locally!**

**Why:** Contains server-specific secrets, IPs, passwords

**Safe workflow:**
```bash
# Server only:
ssh homeserver
nano budgeting_automator_2.0/backend/.env
# Edit secrets here, never commit

# Mac: Use .env.example
# Backend/.env is in .gitignore (safe)
```

---

## Next Steps

1. **Install Tailscale** (if not done)
2. **Install VS Code + Remote SSH extension**
3. **Connect to server**
4. **Start coding!**

You now have a professional remote development setup, completely free and secure! 🚀
