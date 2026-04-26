# RepoShield CLI 🛡️

**Zero-Trust Git Clone Wrapper**

RepoShield is a developer-first CLI tool that protects your local machine from malicious open-source repositories. 

Before allowing untrusted code onto your host operating system, RepoShield safely clones the repository inside an ephemeral Docker container and scans it using industry-standard tools (Semgrep, Bandit, Gitleaks) to detect zero-day Git vulnerabilities, critical SAST flaws, and exposed secrets.

## Features
- **Zero-Trust Sandboxing**: All `git clone` operations happen inside an isolated container.
- **Deep Taint Analysis**: Powered by Semgrep to find complex code flow vulnerabilities.
- **Advanced Secret Scanning**: Powered by Gitleaks to find high-entropy secrets.
- **Seamless Interception**: Automatically intercepts `git clone` commands from your terminal.

## Installation

1. Ensure [Docker Desktop](https://www.docker.com/products/docker-desktop/) is installed and running.
2. Install the Python dependencies:
   ```bash
   cd cli
   pip install -r requirements.txt
   ```
3. Install the shell interceptor:
   ```bash
   python main.py install
   ```

## Usage

Simply use `git clone` as you normally would, or call the tool directly:
```bash
reposhield clone https://github.com/user/repo
```