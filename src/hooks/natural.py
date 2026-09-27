#!/usr/bin/env python3
"""
natural.py - Backdated commits that look like real human activity:
active stretches of varying length, quiet stretches, fewer weekend commits,
varied intensity, and the occasional stray commit on a quiet day.
"""
import argparse, os, random, subprocess, sys
from datetime import datetime, timedelta

p = argparse.ArgumentParser()
p.add_argument("--start", required=True, help="YYYY-MM-DD")
p.add_argument("--end", required=True, help="YYYY-MM-DD (inclusive)")
p.add_argument("--level", type=float, default=0.4, help="Overall activity 0.1 (sparse) to 0.9 (busy)")
p.add_argument("--max", type=int, default=6, help="Max commits in one day")
p.add_argument("--file", default="activity.log")
p.add_argument("--seed", type=int)
p.add_argument("--push", action="store_true")
p.add_argument("--dry-run", action="store_true")
a = p.parse_args()
if a.seed is not None:
    random.seed(a.seed)

top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
if top.returncode != 0:
    sys.exit("Not inside a git repo. cd into your project first.")
repo = top.stdout.strip()

def git(*args, env=None):
    r = subprocess.run(["git", *args], cwd=repo, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed:\n{r.stderr}")

day = datetime.strptime(a.start, "%Y-%m-%d")
end = datetime.strptime(a.end, "%Y-%m-%d")
lvl = min(max(a.level, 0.05), 0.95)

active = random.random() < lvl
left = 0
intensity = 1.0
total = days = 0

while day <= end:
    # Switch between active and quiet stretches of random length
    if left <= 0:
        active = random.random() < lvl + 0.1
        if active:
            left = random.randint(3, 20)
            intensity = random.uniform(1, a.max * 0.7)  # some stretches light, some heavy
        else:
            left = random.randint(2, int(5 + 25 * (1 - lvl)))
    left -= 1

    weekend = day.weekday() >= 5
    if active:
        chance = 0.35 if weekend else 0.8
    else:
        chance = 0.06 * lvl * 2  # rare stray commit

    if random.random() < chance:
        base = intensity if active else 1
        n = max(1, min(a.max, round(random.gauss(base, 1.3))))
        times = sorted(day.replace(hour=random.randint(9, 23), minute=random.randint(0, 59),
                                   second=random.randint(0, 59)) for _ in range(n))
        for t in times:
            stamp = t.strftime("%Y-%m-%dT%H:%M:%S")
            if a.dry_run:
                print("[dry-run]", stamp)
            else:
                with open(os.path.join(repo, a.file), "a") as f:
                    f.write(stamp + "\n")
                env = dict(os.environ, GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
                git("add", a.file)
                git("commit", "-q", "-m", f"Update {t:%Y-%m-%d %H:%M}", env=env)
        total += n
        days += 1
    day += timedelta(days=1)

print(f"Done: {total} commits across {days} days ({a.start} -> {a.end})")
if a.push and not a.dry_run and total:
    git("push")
    print("Pushed.")
