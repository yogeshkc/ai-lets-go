import os
from dotenv import load_dotenv
from currency_exchange import run_currency_exchange
from git_analysis import run_git_analysis

# Load environment variables from .env file
load_dotenv()

llm_config = {
    "config_list": [{"model": "gpt-4", "api_key": os.getenv("OPENAI_API_KEY")}],
}

def run_currency_example():
    """Run currency exchange example"""
    print("\n=== Currency Exchange Example ===")
    messages = ["How much is 1 USD in INR?"]
    run_currency_exchange(llm_config, messages)

def run_git_analysis_example():
    """Run git repository analysis example with AI"""
    print("\n=== Git Analysis Example ===")
    
    # Get repository path from environment variable
    repo_path = os.getenv("GIT_REPO_PATH")
    if not repo_path:
        raise ValueError("GIT_REPO_PATH environment variable is not set")
    if not os.path.exists(repo_path):
        raise ValueError(f"Repository path does not exist: {repo_path}")
        
    run_git_analysis(llm_config, repo_path, days=7)

def main():
    # Run both examples
    # run_currency_example()
    run_git_analysis_example()

if __name__ == "__main__":
    main()