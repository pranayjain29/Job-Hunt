import os
import sys
import subprocess
import shutil
from pathlib import Path
from dotenv import load_dotenv

def check_dependencies():
    """Check if dependencies are installed, prompt to run setup if not"""
    try:
        import dotenv
        return True
    except ImportError:
        print("\n" + "="*50)
        print("  Dependencies not installed!")
        print("="*50)
        print("\nPlease run setup first:")
        print("  python setup.py")
        return False

def check_uv():
    """Check if uv is installed, prompt if not"""
    if shutil.which("uv"):
        return True
    
    print("\n" + "="*50)
    print("  uv not found!")
    print("="*50)
    print("\nThis project uses uv for fast dependency management.")
    print("Would you like to install it? [y]/n: ", end="")
    
    response = input().strip().lower()
    if response in ("", "y", "yes"):
        print("\nInstalling uv...")
        if sys.platform == "win32":
            try:
                subprocess.run(["powershell", "-Command", "irm https://astral.sh/uv/get.ps1 | iex"], check=True)
                print("uv installed!")
                return True
            except:
                pass
        
        print("\nPlease install uv manually:")
        print("  Windows: powershell -Command \"irm https://astral.sh/uv/get.ps1 | iex\"")
        print("  Mac/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("\nThen run: uv sync")
        return False
    return False

def load_settings():
    """Load settings from .env file"""
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    
    if not api_key:
        return None
    
    return {
        "api_key": api_key,
        "roles": [r.strip() for r in os.getenv("TARGET_ROLES", "").split(",") if r.strip()],
        "locations": [l.strip() for l in os.getenv("LOCATIONS", "").split(",") if l.strip()],
        "min_score": int(os.getenv("MIN_SCORE_THRESHOLD", "50")),
        "resume_path": os.getenv("RESUME_PATH", ""),
    }

def verify_config():
    """Verify configuration exists, prompt to configure if not"""
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    
    if not api_key:
        print("\n" + "="*50)
        print("  Configuration needed!")
        print("="*50)
        print("\n1. Get free API key at https://openrouter.ai")
        print("2. Add it to .env file")
        print("\nExample .env:")
        print("  OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx")
        print("  TARGET_ROLES=Data Analyst,AI Engineer")
        print("  LOCATIONS=Chennai,Bangalore")
        print("\nPress Enter when done...", end="")
        input()
        # Reload after user input
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        if not api_key:
            return None
    
    return load_settings()

def print_banner():
    print("\n" + "="*40)
    print("  JOB HUNT 2")
    print("  AI-Powered Job Search")
    print("="*40)

def show_settings(settings):
    print("\n--- Current Settings ---")
    r = ", ".join(settings["roles"]) if settings["roles"] else "not set"
    l = ", ".join(settings["locations"]) if settings["locations"] else "not set"
    k = f"{settings['api_key'][:15]}..." if settings["api_key"] else "not set"
    
    print(f"Job Titles:  {r}")
    print(f"Locations:  {l}")
    print(f"Min Score:  {settings['min_score']}")
    print(f"Resume:     {settings['resume_path'] or 'not set'}")
    print(f"API Key:    {k}")

def edit_settings(settings):
    print("\n--- Edit Settings ---")
    
    default_roles = ", ".join(settings["roles"]) if settings["roles"] else "Data Analyst,AI Engineer"
    roles = input(f"Job titles (comma-separated) [{default_roles}]: ").strip()
    if not roles:
        roles = default_roles
    
    default_locs = ", ".join(settings["locations"]) if settings["locations"] else "Chennai,Bangalore"
    locations = input(f"Locations (comma-separated) [{default_locs}]: ").strip()
    if not locations:
        locations = default_locs
    
    default_score = str(settings["min_score"])
    min_score = input(f"Min score threshold [{default_score}]: ").strip() or default_score
    
    default_resume = settings["resume_path"] or "resume.pdf"
    resume_path = input(f"Resume PDF path [{default_resume}]: ").strip()
    if not resume_path:
        resume_path = default_resume
    
    with open(".env", "w") as f:
        f.write(f"""OPENROUTER_API_KEY={settings['api_key']}
TARGET_ROLES={roles}
LOCATIONS={locations}
MIN_SCORE_THRESHOLD={min_score}
RESUME_PATH={resume_path}
OPENROUTER_MODEL=minimax/minimax-m2.5:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
""")
    
    print("Settings saved!")
    return load_settings()

async def run_scraper():
    from src.agents.scraper import NaukriScraperRunner
    print("\n[Starting scraper...]")
    jobs = await NaukriScraperRunner.run_async()
    print(f"Scraped {len(jobs)} jobs")
    return jobs

async def run_evaluator(jobs):
    from src.agents.evaluator import EvaluatorAgent
    from src.config import MIN_SCORE_THRESHOLD
    
    print("\n[Evaluating jobs with AI...]")
    evaluator = EvaluatorAgent()
    quality_jobs = await evaluator.filter_quality_jobs(jobs, min_score=MIN_SCORE_THRESHOLD)
    print(f"Found {len(quality_jobs)} quality jobs (score >= {MIN_SCORE_THRESHOLD})")
    return quality_jobs

def save_jobs(jobs):
    from src.agents.data_engineer import DataEngineerAgent
    
    agent = DataEngineerAgent()
    agent.save_jobs(jobs)
    print(f"Saved {len(jobs)} jobs to {agent.file_path}")
    return agent.load_existing_jobs()

def open_dashboard():
    print("\n[Opening dashboard at http://localhost:8501]")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "src/agents/dashboard.py"])

def show_summary(jobs):
    print("\n--- Jobs Found ---")
    for job in jobs[:10]:
        print(f"  {job.title[:40]:<40} | {job.company[:20]:<20} | {job.location:<15} | {job.score:.0f}")
    if len(jobs) > 10:
        print(f"... and {len(jobs) - 10} more")

async def run_workflow(auto_confirm=False):
    print_banner()
    
    settings = verify_config()
    if not settings:
        return
    
    show_settings(settings)
    
    if not auto_confirm:
        while True:
            print()
            choice = input("Use these settings? [y]es / [e]dit / [q]uit: ").strip().lower()
            
            if choice in ("", "y", "yes"):
                break
            elif choice in ("e", "edit"):
                settings = edit_settings(settings)
                show_settings(settings)
            elif choice in ("q", "quit"):
                print("bye!")
                return
            else:
                print("Invalid. Enter y, e, or q")
    else:
        print("\n[Auto-confirming settings...]")
    
    print("\n--- SCRAPING ---")
    jobs = await run_scraper()
    if not jobs:
        print("No jobs found!")
        return
    
    quality_jobs = await run_evaluator(jobs)
    if not quality_jobs:
        print("No quality jobs found!")
        return
    
    saved_jobs = save_jobs(quality_jobs)
    show_summary(saved_jobs)
    print("\n")
    open_dashboard()

async def cmd_scrape():
    print_banner()
    jobs = await run_scraper()
    if not jobs:
        print("No jobs scraped!")
        return
    
    quality_jobs = await run_evaluator(jobs)
    if not quality_jobs:
        print("No quality jobs found!")
        return
    
    saved_jobs = save_jobs(quality_jobs)
    show_summary(saved_jobs)
    print("\nScrape complete!")

async def cmd_evaluate():
    from src.agents.data_engineer import DataEngineerAgent
    from src.config import MIN_SCORE_THRESHOLD
    
    print_banner()
    
    agent = DataEngineerAgent()
    all_jobs = agent.load_existing_jobs()
    
    unscored = [j for j in all_jobs if j.score is None]
    already_scored = [j for j in all_jobs if j.score is not None]
    
    if already_scored:
        print(f"Already scored: {len(already_scored)} jobs")
    if unscored:
        print(f"Found {len(unscored)} unscored jobs")
        quality_jobs = await run_evaluator(unscored)
        if not quality_jobs:
            print("No quality jobs found!")
            return
        saved_jobs = save_jobs(quality_jobs)
        show_summary(saved_jobs)
        print("\nEvaluate complete!")
    else:
        print("No unscored jobs to evaluate!")

def cmd_dashboard():
    open_dashboard()

def main():
    import argparse
    
    # Parse args first to check for help
    parser = argparse.ArgumentParser(description="Job Hunt 2", add_help=False)
    parser.add_argument("command", choices=["run", "scrape", "evaluate", "dashboard"], default="run", nargs="?")
    parser.add_argument("-y", "--yes", action="store_true", help="Auto-confirm settings")
    args, _ = parser.parse_known_args()
    
    # Show help without checking prerequisites
    if "-h" in sys.argv or "--help" in sys.argv:
        parser.print_help()
        return
    
    # Check prerequisites
    if not check_dependencies():
        return

    if not check_uv():
        return
    
    # Check configuration
    settings = verify_config()
    if not settings:
        return
    
    if args.command == "run":
        import asyncio
        asyncio.run(run_workflow(auto_confirm=args.yes))
    elif args.command == "scrape":
        import asyncio
        asyncio.run(cmd_scrape())
    elif args.command == "evaluate":
        import asyncio
        asyncio.run(cmd_evaluate())
    elif args.command == "dashboard":
        cmd_dashboard()

if __name__ == "__main__":
    main()