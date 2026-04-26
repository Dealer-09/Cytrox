import typer
import subprocess
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel

app = typer.Typer(help="RepoShield: Zero-Trust Git Clone CLI")
console = Console()

def check_docker():
    """Check if Docker is installed and running."""
    try:
        # Run docker --version to check if it's installed
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        # Check if daemon is running
        subprocess.run(["docker", "info"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def prompt_docker_installation():
    """Prompt the user to install Docker."""
    msg = """
[bold red]🛑 Docker Required[/bold red]

RepoShield requires Docker to safely isolate and scan code before it touches your machine. 
[blue][link=https://www.docker.com/products/docker-desktop/]Click Here to Download Docker Desktop[/link][/blue]

*(Press Enter once Docker is installed and running...)*
    """
    console.print(Panel(msg, title="Dependencies Missing", border_style="red"))
    input()
    # Check again after they press Enter
    if not check_docker():
        console.print("[bold red]Docker is still not running. Exiting...[/bold red]")
        raise typer.Exit(code=1)
    console.print("[bold green]✅ Docker detected![/bold green]")

@app.command()
def clone(repo_url: str):
    """
    Securely clone a repository by analyzing it inside an isolated sandbox first.
    """
    if not check_docker():
        prompt_docker_installation()
        
    console.print(f"🛡️  [bold blue]Initializing Secure Sandbox for:[/bold blue] {repo_url}")
    
    console.print("⏳ Pulling isolated scanner container and analyzing...")
    
    # Run the scanner
    from scanner import run_scan, parse_findings
    findings = run_scan(repo_url)
    
    is_clean, summary = parse_findings(findings)
    
    if is_clean:
        console.print("✅ [bold green]Codebase is clean. Cloning to host...[/bold green]")
        subprocess.run(["git", "clone", repo_url])
    else:
        console.print(f"[bold red]⚠️  Critical Issues Found![/bold red] {summary}")
        # Optionally print a table using rich
        if Confirm.ask("Are you sure you want to clone this to your host?"):
            subprocess.run(["git", "clone", repo_url])
        else:
            console.print("🚫 Clone aborted. Your machine remains safe.")

@app.command()
def install():
    """
    Install the git alias to automatically intercept `git clone` commands.
    """
    console.print("[bold yellow]This will configure PowerShell to intercept `git clone` commands.[/bold yellow]")
    if not Confirm.ask("Do you want to proceed?"):
        console.print("Installation aborted.")
        return

    # Check if we are on Windows since PowerShell is standard there
    if os.name != 'nt':
        console.print("[bold red]Automatic alias installation is currently only supported on Windows PowerShell.[/bold red]")
        return
        
    ps_profile = subprocess.run(["powershell", "-Command", "echo $PROFILE"], capture_output=True, text=True).stdout.strip()
    
    if not ps_profile:
        console.print("[bold red]Could not locate PowerShell profile.[/bold red]")
        return

    profile_path = Path(ps_profile)
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    
    alias_script = """
# RepoShield Git Interceptor
function git {
    if ($args[0] -eq 'clone') {
        python c:\\Code\\Cytrox\\cli\\main.py clone $args[1..($args.Length-1)]
    } else {
        git.exe $args
    }
}
"""
    
    # Check if already installed
    if profile_path.exists():
        content = profile_path.read_text(encoding="utf-8")
        if "RepoShield Git Interceptor" in content:
            console.print("[bold green]RepoShield interceptor is already installed![/bold green]")
            return
            
    # Append to profile
    with open(profile_path, "a", encoding="utf-8") as f:
        f.write("\n" + alias_script)
        
    console.print(f"[bold green]✅ Interceptor installed to {profile_path}[/bold green]")
    console.print("Please restart your terminal for the changes to take effect.")

if __name__ == "__main__":
    app()
