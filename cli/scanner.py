import docker
import json
from rich.console import Console

console = Console()
IMAGE_NAME = "reposhield/scanner:latest"

def build_or_pull_image(client):
    try:
        client.images.get(IMAGE_NAME)
    except docker.errors.ImageNotFound:
        console.print("[yellow]Scanner image not found locally. Building from Dockerfile...[/yellow]")
        import os
        import sys
        
        # Determine base path for Dockerfile.scanner
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Running as compiled PyInstaller executable
            base_path = os.path.join(sys._MEIPASS, 'cli')
        else:
            # Running as normal Python script
            base_path = os.path.dirname(os.path.abspath(__file__))

        dockerfile_name = "Dockerfile.scanner"
        
        try:
            client.images.build(
                path=base_path, 
                dockerfile=dockerfile_name, 
                tag=IMAGE_NAME, 
                rm=True
            )
            console.print("[green]Scanner image built successfully.[/green]")
        except Exception as e:
            console.print(f"[bold red]Failed to build Docker image: {e}[/bold red]")
            raise e

def run_scan(repo_url: str) -> dict:
    """
    Spins up the Docker container, passes the repo URL, and returns the parsed JSON results.
    """
    client = docker.from_env()
    build_or_pull_image(client)
    
    try:
        # Run the container with auto-remove
        logs = client.containers.run(
            IMAGE_NAME,
            command=[repo_url],
            remove=True,
            stdout=True,
            stderr=False
        )
        # Parse the output
        output_str = logs.decode("utf-8").strip()
        
        try:
            return json.loads(output_str)
        except json.JSONDecodeError:
            console.print("[bold red]Failed to parse scanner output. Raw output:[/bold red]")
            console.print(output_str)
            return {"error": "Invalid output from scanner"}
            
    except docker.errors.ContainerError as e:
        console.print(f"[bold red]Scanner container failed to execute:[/bold red]\n{e.stderr.decode('utf-8')}")
        return {"error": "Container execution failed"}
    except Exception as e:
        return {"error": str(e)}

def parse_findings(findings: dict):
    """
    Returns a tuple: (is_clean, summary_text, detailed_issues_list)
    """
    if "error" in findings:
        return False, findings["error"], []
        
    from config import load_config
    config = load_config()
    ignored_severities = [s.upper() for s in config.get("ignored_severities", [])]
    ignored_categories = config.get("ignored_categories", [])
        
    detailed_issues = []
    
    # Gitleaks results
    for r in findings.get("secrets", []):
        detailed_issues.append({
            "category": "Secret",
            "severity": "CRITICAL",
            "message": r.get("Description", "Hardcoded Secret")
        })
    
    # Semgrep results
    for r in findings.get("sast", []):
        severity = r.get("extra", {}).get("severity", "UNKNOWN")
        if severity in ("ERROR", "WARNING"):
            # Map ERROR to HIGH for consistency in the table
            display_severity = "HIGH" if severity == "ERROR" else "MEDIUM"
            detailed_issues.append({
                "category": "SAST",
                "severity": display_severity,
                "message": r.get("check_id", "Vulnerability Detected")
            })
            
    # Bandit results
    for r in findings.get("bandit", []):
        severity = r.get("issue_severity", "UNKNOWN")
        if severity in ("HIGH", "MEDIUM"):
            msg = f"{r.get('test_name', 'Security Issue')}: {r.get('issue_text', '')}"
            detailed_issues.append({
                "category": "Python SAST",
                "severity": severity,
                "message": msg
            })
            
    # Apply filtering based on policy
    filtered_issues = []
    for issue in detailed_issues:
        if issue["severity"] in ignored_severities:
            continue
        if issue["category"] in ignored_categories:
            continue
        filtered_issues.append(issue)
            
    if not filtered_issues:
        return True, "No issues found", []
        
    num_secrets = len([i for i in filtered_issues if i["category"] == "Secret"])
    num_sast = len([i for i in filtered_issues if i["category"] == "SAST"])
    num_bandit = len([i for i in filtered_issues if i["category"] == "Python SAST"])
    
    summary = f"Found {num_secrets} secrets, {num_sast} SAST vulnerabilities, and {num_bandit} Python specific issues."
    return False, summary, filtered_issues
