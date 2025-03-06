import os
from typing import List
from typing_extensions import Annotated
from collections import defaultdict

import autogen
from autogen.cache import Cache

from .analyzer import analyze_git_repo, generate_weekly_update

def create_git_analysis_agents(llm_config: dict):
    """Create and return the git analysis agents"""
    assistant = autogen.AssistantAgent(
        name="git_analyst",
        system_message="""You are a Git Repository Analyst. You analyze git repositories and provide insights about:
        - Code changes and their impact
        - Development patterns and trends
        - Team collaboration metrics
        - Key features and bug fixes
        Reply TERMINATE when the analysis is complete.""",
        llm_config=llm_config,
    )

    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        llm_config=llm_config,
    )

    @user_proxy.register_for_execution()
    @assistant.register_for_llm(description="Analyze git repository and provide insights")
    def analyze_repository(
        repo_path: Annotated[str, "Path to the git repository"],
        days: Annotated[int, "Number of days to analyze"] = 7,
    ) -> str:
        """Analyze git repository and generate insights"""
        try:
            commits = analyze_git_repo(repo_path, days)
            if not commits:
                return f"No commits found in the repository at {repo_path} in the last {days} days."

            # Generate basic report
            report = generate_weekly_update(commits)

            # Additional analysis
            authors = set(commit.author for commit in commits)
            file_types = defaultdict(int)
            for commit in commits:
                for file in commit.files_changed:
                    ext = os.path.splitext(file)[1] or 'no_extension'
                    file_types[ext] += 1

            # Enhanced insights
            insights = [
                "\nAdditional Insights",
                "=" * 30,
                f"\nTeam Collaboration:",
                f"- {len(authors)} contributors were active",
                f"- Most active contributor: {max(authors, key=lambda a: sum(1 for c in commits if c.author == a))}",
                f"\nFile Type Distribution:",
            ]
            
            for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
                insights.append(f"- {ext}: {count} changes")

            # Identify potential patterns
            large_commits = [c for c in commits if len(c.files_changed) > 5]
            if large_commits:
                insights.extend([
                    "\nNotable Large Changes:",
                    *[f"- {c.message} ({len(c.files_changed)} files)" for c in large_commits[:3]]
                ])

            return report + "\n" + "\n".join(insights)
        except ValueError as e:
            return f"Error analyzing repository: {str(e)}"

    return assistant, user_proxy

def run_git_analysis(llm_config: dict, repo_path: str, days: int = 7):
    """Run git repository analysis with AI agents"""
    assistant, user_proxy = create_git_analysis_agents(llm_config)
    
    with Cache.disk() as cache:
        message = f"Please analyze the git repository at {repo_path} for the past {days} days and provide insights."
        user_proxy.initiate_chat(
            assistant,
            message=message,
            summary_method="reflection_with_llm",
            cache=cache
        )
