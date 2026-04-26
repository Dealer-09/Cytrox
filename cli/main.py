import typer
import subprocess
import sys
import os
import json
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel
from rich.table import Table

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
        r"/_/ |_/_____/_/    \____/        ____/_/ /_//___/_____//_____//_____/   "
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

@app.command(context_settings={"ignore_unknown_options": True})
def clone(
    ctx: typer.Context,
    repo_url: str
):
    if not check_docker():
        prompt_docker_installation()
        
    console.print(f"[bold cyan]◇[/bold cyan] 🛡️  [bold blue]Initializing Secure Sandbox for:[/bold blue] {repo_url}")
    
    console.print("[bold cyan]│[/bold cyan] ⏳ Pulling isolated scanner container and analyzing...")
    
    # Run the scanner
    from scanner import run_scan, parse_findings
    findings = run_scan(repo_url)
    
    is_clean, summary, detailed_issues = parse_findings(findings)
    
    git_cmd = ["git", "clone", repo_url] + ctx.args

    if is_clean:
        console.print("[bold cyan]◇[/bold cyan] ✅ [bold green]Codebase is clean. Cloning to host...[/bold green]")
        subprocess.run(git_cmd)
    else:
        console.print(f"[bold cyan]◇[/bold cyan] [bold red]⚠️  Critical Issues Found![/bold red] {summary}")
        
        if detailed_issues:
            if Confirm.ask("[bold cyan]◇[/bold cyan] Do you want to see the details?", default=False):
                table = Table(show_header=True, header_style="bold magenta", border_style="cyan")
                table.add_column("Severity", style="red", width=12)
                table.add_column("Category", style="yellow", width=15)
                table.add_column("Description", style="white")
                
                # Show up to 15 issues so we don't flood the terminal
                for issue in detailed_issues[:15]:
                    sev = issue['severity']
                    severity_colored = f"[bold red]{sev}[/bold red]" if sev == "CRITICAL" else f"[red]{sev}[/red]"
                    table.add_row(severity_colored, issue['category'], issue['message'])
                
                console.print(table)
                if len(detailed_issues) > 15:
                    console.print(f"[bold cyan]│[/bold cyan] [bold yellow]...and {len(detailed_issues) - 15} more issues hidden.[/bold yellow]")
            
            if Confirm.ask("[bold cyan]◇[/bold cyan] Do you want to generate a detailed report?", default=False):
                from report import generate_html_report
                import webbrowser
                # Write JSON
                with open("reposhield_report.json", "w", encoding="utf-8") as f:
                    json.dump(findings, f, indent=2)
                    
                # Write HTML
                html_content = generate_html_report(repo_url, detailed_issues, is_clean, summary)
                report_path = os.path.abspath("reposhield_report.html").replace("\\", "/")
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                    
                console.print(f"[bold green]✅ Here is your generated report: file:///{report_path}[/bold green]")
                console.print("[bold cyan]│[/bold cyan] Opening report in your default web browser...")
                console.print("[bold cyan]│[/bold cyan]")
                try:
                    webbrowser.open(f"file:///{report_path}")
                except Exception:
                    pass
        
        from config import load_config
        config = load_config()
        if config.get("strict_mode", False):
            console.print("[bold cyan]│[/bold cyan] [bold red]STRICT MODE ENABLED: Automatically blocking clone.[/bold red]")
            console.print("[bold cyan]│[/bold cyan] 🚫 Clone aborted. Your machine remains safe.")
            raise typer.Exit(code=1)
            
        if Confirm.ask("[bold cyan]◇[/bold cyan] Are you sure you want to clone this to your host?", default=False):
            subprocess.run(git_cmd)
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

@app.command()
def configure():
    from config import load_config, save_config
    from rich.prompt import Prompt
    
    config = load_config()
    console.print("[bold cyan]◇[/bold cyan] 🛡️  [bold blue]RepoShield Security Policy Configuration[/bold blue]")
    
    # Configure Ignored Severities
    current_sev = ", ".join(config.get("ignored_severities", [])) or "None"
    console.print(f"[bold cyan]│[/bold cyan] Current ignored severities: [yellow]{current_sev}[/yellow]")
    if Confirm.ask("[bold cyan]◇[/bold cyan] Do you want to ignore specific severities (e.g. MEDIUM)?", default=False):
        sevs = Prompt.ask("[bold cyan]│[/bold cyan] Enter severities to ignore (comma-separated, or leave blank)")
        if sevs.strip():
            config["ignored_severities"] = [s.strip().upper() for s in sevs.split(",")]
        else:
            config["ignored_severities"] = []
            
    # Configure Ignored Categories
    current_cat = ", ".join(config.get("ignored_categories", [])) or "None"
    console.print(f"[bold cyan]│[/bold cyan] Current ignored categories: [yellow]{current_cat}[/yellow]")
    if Confirm.ask("[bold cyan]◇[/bold cyan] Do you want to ignore specific categories (e.g. Python SAST)?", default=False):
        cats = Prompt.ask("[bold cyan]│[/bold cyan] Enter categories to ignore (comma-separated, or leave blank)")
        if cats.strip():
            config["ignored_categories"] = [c.strip() for c in cats.split(",")]
        else:
            config["ignored_categories"] = []
            
    # Configure Strict Mode
    current_strict = config.get("strict_mode", False)
    console.print(f"[bold cyan]│[/bold cyan] Current Strict Mode: [yellow]{'Enabled' if current_strict else 'Disabled'}[/yellow]")
    if Confirm.ask("[bold cyan]◇[/bold cyan] Do you want to enable Strict Mode (automatically blocks clones without asking)?", default=current_strict):
        config["strict_mode"] = True
    else:
        config["strict_mode"] = False
        
    save_config(config)
    console.print("[bold green]✅ Security policies updated successfully![/bold green]")

@app.command()
def uninstall():
    """
    Removes RepoShield's integration from PowerShell and deletes configuration files.
    """
    console.print("[bold cyan]◇[/bold cyan] [bold red]This will remove RepoShield's integration from your system.[/bold red]")
    if not Confirm.ask("[bold cyan]◇[/bold cyan] Are you sure you want to proceed?"):
        return

    # 1. Remove from PowerShell profile
    documents_dir = os.path.join(os.environ.get('USERPROFILE', os.path.expanduser('~')), 'Documents')
    ps_profile = os.path.join(documents_dir, 'WindowsPowerShell', 'Microsoft.PowerShell_profile.ps1')
    profile_path = Path(ps_profile)

    if profile_path.exists():
        content = profile_path.read_text(encoding="utf-8")
        if "# RepoShield" in content:
            console.print("[bold cyan]│[/bold cyan] Removing PowerShell interceptors...")
            
            import re
            # Pattern to match any RepoShield block in the profile
            # We look for either Global Command or Git Interceptor markers and their respective functions
            patterns = [
                r"\s*# RepoShield Global Command.*?function reposhield \{.*?\}\s*",
                r"\s*# RepoShield Git Interceptor.*?function git \{.*?\}\s*"
            ]
            
            new_content = content
            for p in patterns:
                new_content = re.sub(p, "\n", new_content, flags=re.DOTALL)
            
            profile_path.write_text(new_content.strip() + "\n", encoding="utf-8")
            console.print("[bold green]✅ PowerShell profile cleaned.[/bold green]")
        else:
            console.print("[bold yellow]│[/bold yellow] No RepoShield integration found in PowerShell profile.")
    else:
        console.print("[bold yellow]│[/bold yellow] PowerShell profile not found. Skipping profile cleanup.")

    # 2. Delete config directory
    home = Path(os.path.expanduser("~"))
    reposhield_dir = home / ".reposhield"
    if reposhield_dir.exists():
        import shutil
        try:
            shutil.rmtree(reposhield_dir)
            console.print("[bold green]✅ Configuration directory (~/.reposhield) removed.[/bold green]")
        except Exception as e:
            console.print(f"[bold red]❌ Failed to remove config directory: {e}[/bold red]")

    # 3. Docker cleanup
    if Confirm.ask("[bold cyan]◇[/bold cyan] Do you want to remove the Docker scanner image to free up space?", default=True):
        try:
            import docker
            client = docker.from_env()
            from scanner import IMAGE_NAME
            console.print(f"[bold cyan]│[/bold cyan] Removing Docker image {IMAGE_NAME}...")
            client.images.remove(IMAGE_NAME, force=True)
            console.print(f"[bold green]✅ Docker image removed.[/bold green]")
        except Exception as e:
            console.print(f"[yellow]⚠️ Could not remove Docker image: {e}[/yellow]")

    console.print("\n[bold green]✨ RepoShield has been successfully uninstalled![/bold green]")
    console.print("[bold yellow]Note:[/bold yellow] You can now safely delete the executable and this source folder.")

if __name__ == "__main__":
    app()
