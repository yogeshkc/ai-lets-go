# AI Lets Go

A Python project demonstrating the use of AutoGen for building conversational AI applications. Currently implements two use cases:
1. Currency Exchange Rate Calculator
2. Git Repository Analysis

## Setup

### Prerequisites
- Python 3.13+
- Git
- Virtual Environment

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-lets-go
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```bash
# Required: Your OpenAI API key
OPENAI_API_KEY="your-api-key-here"

# Optional: Path to git repository for analysis (defaults to current directory)
GIT_REPO_PATH="/path/to/your/git/repo"
```

## Usage

The project contains two main features that can be run independently or together:

### 1. Currency Exchange
Uses AutoGen to create a conversational interface for currency conversion using real-time exchange rates.

Example usage in `main.py`:
```python
messages = ["How much is 1 USD in INR?"]
run_currency_exchange(llm_config, messages)
```

### 2. Git Repository Analysis
Analyzes a git repository to provide insights about commit history, team collaboration, and code changes.

Example usage in `main.py`:
```python
run_git_analysis_example()
```

### Running the Application

Run the main script to execute both examples:
```bash
python main.py
```

## Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| OPENAI_API_KEY | Yes | Your OpenAI API key for AutoGen | sk-... |
| GIT_REPO_PATH | No | Path to git repository for analysis | /path/to/repo |

## Project Structure

```
ai-lets-go/
├── currency_exchange/     # Currency exchange functionality
│   ├── __init__.py
│   ├── agent.py          # AutoGen agents for currency exchange
│   └── exchange.py       # Exchange rate calculation
├── git_analysis/         # Git analysis functionality
│   ├── __init__.py
│   ├── agent.py         # AutoGen agents for git analysis
│   └── analyzer.py      # Git log parsing and analysis
├── main.py              # Main entry point
├── requirements.txt     # Project dependencies
└── .env                # Environment variables
```

## Notes
- The currency exchange feature uses a free API (ExchangeRate-API) which updates rates daily
- Git analysis works with any git repository specified in GIT_REPO_PATH
- All API keys and sensitive information should be stored in .env file
- The .env file is included in .gitignore for security
