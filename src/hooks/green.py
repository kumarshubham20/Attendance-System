#!/usr/bin/env python3
"""
green.py - Create random backdated commits between two dates to fill a GitHub contribution graph.

Usage examples:
  python3 green.py --start 2025-01-01 --end 2025-12-31
  python3 green.py --start 2025-06-01 --end 2025-09-30 --min 1 --max 8 --freq 80 --no-weekends --push
  python3 green.py --start 2024-01-01 --end 2024-12-31 --repo ./my-repo --dry-run
"""
import argparse
import os
import random
import subprocess
import sys
from datetime import datetime, timedelta


def run(cmd, cwd, env=None):
    result = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running {' '.join(cmd)}:\n{result.stderr}")
        sys.exit(1)
    return result.stdout.strip()


def parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        sys.exit(f"Invalid date '{s}'. Use YYYY-MM-DD.")


def main():
    p = argparse.ArgumentParser(description="Random backdated commits to make your graph green.")
    p.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    p.add_argument("--end", required=True, help="End date YYYY-MM-DD (inclusive)")
    p.add_argument("--min", type=int, default=1, help="Min commits on an active day (default 1)")
    p.add_argument("--max", type=int, default=5, help="Max commits on an active day (default 5)")
    p.add_argument("--freq", type=int, default=70, help="Percent of days that get commits, 0-100 (default 70)")
    p.add_argument("--no-weekends", action="store_true", help="Skip Saturdays and Sundays")
    p.add_argument("--repo", default=".", help="Path to git repo (default: current dir)")
    p.add_argument("--file", default="activity.log", help="File to modify for each commit")
    p.add_argument("--seed", type=int, help="Random seed for reproducible patterns")
    p.add_argument("--push", action="store_true", help="git push when done")
    p.add_argument("--dry-run", action="store_true", help="Show plan without committing")
    a = p.parse_args()

    start, end = parse_date(a.start), parse_date(a.end)
    if start > end:
        sys.exit("--start must be before --end")
    if not (1 <= a.min <= a.max):
        sys.exit("Need 1 <= --min <= --max")
    if not (0 <= a.freq <= 100):
        sys.exit("--freq must be 0-100")
    if a.seed is not None:
        random.seed(a.seed)

    repo = os.path.abspath(a.repo)
    if not a.dry_run:
        if not os.path.isdir(os.path.join(repo, ".git")):
            os.makedirs(repo, exist_ok=True)
            run(["git", "init"], repo)
            print(f"Initialized new repo in {repo}")

    target = os.path.join(repo, a.file)
    total, days_active = 0, 0
    day = start

    while day <= end:
        if a.no_weekends and day.weekday() >= 5:
            day += timedelta(days=1)
            continue
        if random.randint(1, 100) > a.freq:
            day += timedelta(days=1)
            continue

        n = random.randint(a.min, a.max)
        # Random, sorted times during the day (09:00 - 23:59)
        times = sorted(
            day.replace(hour=random.randint(9, 23), minute=random.randint(0, 59), second=random.randint(0, 59))
            for _ in range(n)
        )
        days_active += 1

        for t in times:
            stamp = t.strftime("%Y-%m-%dT%H:%M:%S")
            if a.dry_run:
                print(f"[dry-run] commit at {stamp}")
            else:
                with open(target, "a") as f:
                    f.write(f"{stamp}\n")
                env = os.environ.copy()
                env["GIT_AUTHOR_DATE"] = stamp
                env["GIT_COMMITTER_DATE"] = stamp
                run(["git", "add", a.file], repo)
                run(["git", "commit", "-q", "-m", f"Update {t.strftime('%Y-%m-%d %H:%M')}"], repo, env)
            total += 1

        day += timedelta(days=1)

    print(f"\nDone: {total} commits across {days_active} days ({a.start} -> {a.end}).")

    if a.push and not a.dry_run and total:
        print("Pushing...")
        run(["git", "push"], repo)
        print("Pushed.")


if __name__ == "__main__":
    main()