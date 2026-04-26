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
        dockerfile_path = os.path.dirname(os.path.abspath(__file__))
        client.images.build(path=dockerfile_path, tag=IMAGE_NAME, rm=True)
        console.print("[green]Scanner image built successfully.[/green]")

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
    Counts the number of critical/high findings to determine if it's safe.
    """
    if "error" in findings:
        return False, findings["error"]
        
    num_secrets = len(findings.get("secrets", []))
    
    # Semgrep results
    num_sast_high = 0
    for r in findings.get("sast", []):
        if r.get("extra", {}).get("severity") in ("ERROR", "WARNING"):
            num_sast_high += 1
            
    # Bandit results
    num_bandit_high = 0
    for r in findings.get("bandit", []):
        if r.get("issue_severity") in ("HIGH", "MEDIUM"):
            num_bandit_high += 1
            
    total_issues = num_secrets + num_sast_high + num_bandit_high
    
    if total_issues == 0:
        return True, "No issues found"
        
    summary = f"Found {num_secrets} secrets, {num_sast_high} SAST vulnerabilities, and {num_bandit_high} Python specific issues."
    return False, summary
