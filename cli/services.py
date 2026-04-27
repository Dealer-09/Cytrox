import subprocess
import os
import json
from pathlib import Path

def is_docker_running() -> bool:
    """Checks if the Docker daemon is running."""
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        subprocess.run(["docker", "info"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def execute_scan(repo_url: str):
    """Executes the security scan via docker and parses findings."""
    from scanner import run_scan, parse_findings
    findings = run_scan(repo_url)
    is_clean, summary, detailed_issues = parse_findings(findings)
    return is_clean, summary, detailed_issues, findings

def generate_report(repo_url: str, detailed_issues: list, is_clean: bool, summary: str) -> str:
    """Generates the HTML report and returns its absolute path."""
    from report import generate_html_report
    html_content = generate_html_report(repo_url, detailed_issues, is_clean, summary)
    report_path = os.path.abspath("reposhield_report.html").replace("\\", "/")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return report_path
    
def execute_git_clone(repo_url: str, args: tuple):
    """Safely executes git clone on the host."""
    git_cmd = ["git", "clone", repo_url] + list(args)
    subprocess.run(git_cmd, check=True)

def install_powershell_interceptor(current_exe: str, profile_path: Path):
    """Installs the powershell alias scripts."""
    alias_script = f"""
# RepoShield Global Command
function reposhield {{
    {current_exe} $args
}}

# RepoShield Git Interceptor
function git {{
    if ($args[0] -eq 'clone') {{
        {current_exe} clone $args[1..($args.Length-1)]
    }} else {{
        git.exe $args
    }}
}}
"""
    with open(profile_path, "a", encoding="utf-8") as f:
        f.write("\n" + alias_script)