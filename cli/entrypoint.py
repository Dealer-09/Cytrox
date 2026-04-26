import sys
import subprocess
import json
import os
import shutil

def run_command(cmd, cwd=None):
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        return ""

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No repository URL provided"}))
        sys.exit(1)

    repo_url = sys.argv[1]
    clone_dir = "/scan_repo"

    # Clone the repository
    clone_result = subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, clone_dir],
        capture_output=True,
        text=True
    )

    if clone_result.returncode != 0:
        print(json.dumps({"error": f"Failed to clone repository: {clone_result.stderr.strip()}"}))
        sys.exit(1)

    findings = {
        "secrets": [],
        "sast": [],
        "bandit": []
    }

    # 1. Run Gitleaks
    gitleaks_cmd = ["gitleaks", "detect", "--no-git", "--report-format", "json", "--report-path", "/gitleaks.json"]
    subprocess.run(gitleaks_cmd, cwd=clone_dir, capture_output=True)
    if os.path.exists("/gitleaks.json"):
        try:
            with open("/gitleaks.json", "r") as f:
                findings["secrets"] = json.load(f)
        except:
            pass

    # 2. Run Semgrep
    semgrep_cmd = ["semgrep", "scan", "--config=auto", "--json", "-o", "/semgrep.json"]
    subprocess.run(semgrep_cmd, cwd=clone_dir, capture_output=True)
    if os.path.exists("/semgrep.json"):
        try:
            with open("/semgrep.json", "r") as f:
                data = json.load(f)
                findings["sast"] = data.get("results", [])
        except:
            pass

    # 3. Run Bandit
    bandit_cmd = ["bandit", "-r", ".", "-f", "json", "-o", "/bandit.json"]
    subprocess.run(bandit_cmd, cwd=clone_dir, capture_output=True)
    if os.path.exists("/bandit.json"):
        try:
            with open("/bandit.json", "r") as f:
                data = json.load(f)
                findings["bandit"] = data.get("results", [])
        except:
            pass

    # Output final aggregated JSON to stdout
    print(json.dumps(findings))

if __name__ == "__main__":
    main()
