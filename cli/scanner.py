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
    Orchestrates the two-container handoff for maximum security.
    Container A: Network enabled, clones repo to volume.
    Container B: Network disabled, read-only root, scans volume.
    """
    client = docker.from_env()
    build_or_pull_image(client)
    
    import uuid
    vol_name = f"reposhield_scan_{uuid.uuid4().hex}"
    
    try:
        # Create a volume to pass data between the two isolated containers
        volume = client.volumes.create(name=vol_name)
        
        # ---------------------------------------------------------
        # Container A: The Cloner (Needs Network)
        # ---------------------------------------------------------
        try:
            client.containers.run(
                IMAGE_NAME,
                command=["clone", repo_url],
                remove=True,
                network_disabled=False,
                user="root",  # Run as root to write to the Docker volume
                volumes={vol_name: {'bind': '/scan_repo', 'mode': 'rw'}}
            )
        except docker.errors.ContainerError as e:
            err_msg = e.stderr.decode("utf-8").strip() if e.stderr else str(e)
            return {"error": f"Failed to clone repository during isolation phase: {err_msg}"}

        # ---------------------------------------------------------
        # Container B: The Scanner (Zero Network, Read-Only, Unprivileged)
        # ---------------------------------------------------------
        try:
            logs = client.containers.run(
                IMAGE_NAME,
                command=["scan"],
                remove=True,
                stdout=True,
                stderr=False,
                mem_limit="512m",
                nano_cpus=500000000,
                network_disabled=True,
                read_only=True,
                tmpfs={"/tmp": ""},
                cap_drop=["ALL"],
                security_opt=["no-new-privileges:true"],
                volumes={vol_name: {'bind': '/scan_repo', 'mode': 'ro'}}
            )
            # Parse the output
            output_str = logs.decode("utf-8").strip()
            
            try:
                return json.loads(output_str)
            except json.JSONDecodeError:
                console.print("[bold red]Failed to parse scanner output. Raw output:[/bold red]")
                console.print(output_str)
                return {"error": "Invalid JSON output from scanner"}
                
        except docker.errors.ContainerError as e:
            err_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            console.print(f"[bold red]Scanner container failed to execute:[/bold red]\n{err_msg}")
            return {"error": "Scanner container execution failed"}
            
    except Exception as e:
        return {"error": f"Unexpected error during scan orchestration: {str(e)}"}
        
    finally:
        # Always clean up the volume to prevent leaks
        try:
            volume = client.volumes.get(vol_name)
            volume.remove(force=True)
        except docker.errors.NotFound:
            pass
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to cleanup volume {vol_name}: {e}[/yellow]")

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