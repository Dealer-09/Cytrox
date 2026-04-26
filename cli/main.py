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

from rich.text import Text
from rich.color import Color

def get_gradient_banner():
    banner_lines = [
        r"    ____  __________  ____         _____ __  __ _________  __     ____  ",
        r"   / __ \/ ____/ __ \/ __ \       / ___// / / //  _/ ____// /    / __ \ ",
        r"  / /_/ / __/ / /_/ / / / / ____  \__ \/ /_/ / / // __/  / /    / / / / ",
        r" / _, _/ /___/ ____/ /_/ /  ___  ___/ / __  /_/ // /___ / /___ / /_/ /  ",
        r"/_/ |_/_____/_/    \____//       ____/_/ /_//___/_____//_____//_____/   "
    ]
    
    text = Text()
    # Gradient from Cyan (#00FFFF) to Pink/Purple (#FF00FF)
    start_r, start_g, start_b = 0, 255, 255
    end_r, end_g, end_b = 255, 0, 255
    
    max_len = max(len(line) for line in banner_lines)
    
    for i, line in enumerate(banner_lines):
        for j, char in enumerate(line):
            ratio = j / max_len if max_len > 0 else 0
            r = int(start_r + (end_r - start_r) * ratio)
            g = int(start_g + (end_g - start_g) * ratio)
            b = int(start_b + (end_b - start_b) * ratio)
            
            text.append(char, style=f"bold rgb({r},{g},{b})")
        if i < len(banner_lines) - 1:
            text.append("\n")
            
    return text

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        console.print(get_gradient_banner())
        console.print(ctx.get_help())
    else:
        console.print(get_gradient_banner())

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
    if not check_docker():
        prompt_docker_installation()
        
    console.print(f"[bold cyan]◇[/bold cyan] 🛡️  [bold blue]Initializing Secure Sandbox for:[/bold blue] {repo_url}")
    
    console.print("[bold cyan]│[/bold cyan] ⏳ Pulling isolated scanner container and analyzing...")
    
    # Run the scanner
    from scanner import run_scan, parse_findings
    findings = run_scan(repo_url)
    
    is_clean, summary = parse_findings(findings)
    
    if is_clean:
        console.print("[bold cyan]│[/bold cyan]")
        console.print("[bold cyan]◇[/bold cyan] ✅ [bold green]Codebase is clean. Cloning to host...[/bold green]")
        subprocess.run(["git", "clone", repo_url])
    else:
        console.print("[bold cyan]│[/bold cyan]")
        console.print(f"[bold cyan]◇[/bold cyan] [bold red]⚠️  Critical Issues Found![/bold red] {summary}")
        # Optionally print a table using rich
        if Confirm.ask("[bold cyan]◇[/bold cyan] Are you sure you want to clone this to your host?"):
            subprocess.run(["git", "clone", repo_url])
        else:
            console.print("[bold cyan]│[/bold cyan] 🚫 Clone aborted. Your machine remains safe.")

@app.command()
def install():
    console.print("[bold cyan]◇[/bold cyan] [bold yellow]This will configure PowerShell to intercept `git clone` commands.[/bold yellow]")
    if not Confirm.ask("[bold cyan]◇[/bold cyan] Do you want to proceed?"):
        console.print("[bold cyan]│[/bold cyan] Installation aborted.")
        return

    # Reliably get PowerShell profile path without subprocess encoding issues
    documents_dir = os.path.join(os.environ.get('USERPROFILE', os.path.expanduser('~')), 'Documents')
    ps_profile = os.path.join(documents_dir, 'WindowsPowerShell', 'Microsoft.PowerShell_profile.ps1')
    
    if not ps_profile:
        console.print("[bold red]Could not determine PowerShell profile path.[/bold red]")
        return

    profile_path = Path(ps_profile)
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get the path to the current executable or script
    if getattr(sys, 'frozen', False):
        current_exe = f'& "{sys.executable}"'
    else:
        current_exe = f'python "{os.path.abspath(__file__)}"'

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
    
    # Check if already installed
    if profile_path.exists():
        content = profile_path.read_text(encoding="utf-8")
        if "RepoShield Global Command" in content:
            console.print("[bold green]RepoShield is already fully installed and up to date![/bold green]")
            return
        
        if "RepoShield Git Interceptor" in content:
            console.print("[bold yellow]Found old version of RepoShield. Updating to latest...[/bold yellow]")
            # Remove old interceptor to avoid duplicates (simplified)
            # We'll just append the new version if not fully present

            
    # Append to profile
    with open(profile_path, "a", encoding="utf-8") as f:
        f.write("\n" + alias_script)
        
    console.print(f"[bold green]✅ Interceptor installed to {profile_path}[/bold green]")
    console.print("Please restart your terminal for the changes to take effect.")

if __name__ == "__main__":
    app()
