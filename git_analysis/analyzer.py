import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import subprocess
from collections import defaultdict

@dataclass
class CommitInfo:
    hash: str
    author: str
    date: datetime
    message: str
    files_changed: List[str]
    insertions: int
    deletions: int

def run_git_command(repo_path: str, command: List[str]) -> str:
    """Run a git command in the specified repository"""
    try:
        full_command = ['git'] + command
        print(f"🔄 Running git command: {' '.join(full_command)}")
        print(f"📂 In directory: {repo_path}")
        
        result = subprocess.run(
            full_command,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {' '.join(full_command)}")
        raise ValueError(f"Git command failed: {e.stderr}")

def parse_git_log(log_output: str) -> List[CommitInfo]:
    """Parse git log output into CommitInfo objects"""
    commits = []
    current_commit = None
    
    for line in log_output.split('\n'):
        # Strip quotes first
        clean_line = line.strip('"')
        if clean_line.startswith('commit '):
            if current_commit:
                commits.append(current_commit)
            # Get the hash from the cleaned line
            hash = clean_line.split()[1]
            current_commit = CommitInfo(
                hash=hash,
                author='',
                date=datetime.now(),  # Will be updated
                message='',
                files_changed=[],
                insertions=0,
                deletions=0
            )
        elif clean_line.startswith('Author: '):
            if current_commit:
                current_commit.author = clean_line[8:].strip()
        elif clean_line.startswith('Date: '):
            if current_commit:
                date_str = clean_line[6:].strip()
                # Format: Thu, 6 Mar 2025 17:58:12 +0000
                current_commit.date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
        elif clean_line and current_commit and not current_commit.message:
            current_commit.message = clean_line
    
    if current_commit:
        commits.append(current_commit)
    
    return commits

def analyze_git_repo(repo_path: str, days: int = 7) -> List[CommitInfo]:
    """Analyze git commits from the past N days"""
    # First, try to get the last commit to verify repository access
    try:
        test_output = run_git_command(repo_path, ['log', '-1', '--pretty=format:%H'])
        print(f"Repository is accessible. Last commit: {test_output}")
    except ValueError as e:
        print(f"Error accessing repository: {e}")
        raise
    
    # Get detailed commit information with date filtering
    since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    log_output = run_git_command(repo_path, [
        'log',
        f'--since={since_date}',
        '--pretty=format:"commit %H%nAuthor: %an%nDate: %aD%n%s%n"'
    ])
    
    commits = parse_git_log(log_output)
    
    # Get stat information for each commit
    for commit in commits:
        stat_output = run_git_command(repo_path, [
            'show',
            '--stat',
            commit.hash
        ])
        
        # Parse stat information
        for line in stat_output.split('\n'):
            if '|' in line:  # File change statistics
                file_name = line.split('|')[0].strip()
                commit.files_changed.append(file_name)
                
                changes = line.split('|')[1]
                if '+' in changes:
                    commit.insertions += int(changes.count('+'))
                if '-' in changes:
                    commit.deletions += int(changes.count('-'))
    
    return commits

def generate_weekly_update(commits: List[CommitInfo]) -> str:
    """Generate a weekly update summary from commit information"""
    if not commits:
        return "No commits found in the specified time period."
    
    # Sort commits by date
    commits.sort(key=lambda x: x.date, reverse=True)
    
    # Aggregate statistics
    total_commits = len(commits)
    total_files = len(set(file for commit in commits for file in commit.files_changed))
    total_insertions = sum(commit.insertions for commit in commits)
    total_deletions = sum(commit.deletions for commit in commits)
    authors = set(commit.author for commit in commits)
    
    # Group commits by day
    commits_by_day = defaultdict(list)
    for commit in commits:
        day = commit.date.strftime('%Y-%m-%d')
        commits_by_day[day].append(commit)
    
    # Generate summary
    summary = [
        "📊 Weekly Update Summary",
        "=" * 30,
        f"📅 Period: {commits[-1].date.strftime('%Y-%m-%d')} to {commits[0].date.strftime('%Y-%m-%d')}",
        f"👥 Contributors: {len(authors)}",
        f"📝 Total Commits: {total_commits}",
        f"📂 Files Changed: {total_files}",
        f"📈 Lines Added: {total_insertions}",
        f"📉 Lines Removed: {total_deletions}",
        "\n📋 Daily Breakdown:",
    ]
    
    for day, day_commits in sorted(commits_by_day.items(), reverse=True):
        summary.append(f"\n🗓️ {day}")
        for commit in day_commits:
            summary.append(f"  • {commit.message} ({commit.author})")
            if commit.files_changed:
                files_summary = ', '.join(commit.files_changed[:3])
                if len(commit.files_changed) > 3:
                    files_summary += f" and {len(commit.files_changed) - 3} more"
                summary.append(f"    Modified: {files_summary}")
    
    return '\n'.join(summary)
