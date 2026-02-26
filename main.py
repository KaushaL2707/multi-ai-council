import os
import sys
import argparse
from dotenv import load_dotenv

from core.llm import OpenAIClient, AnthropicClient, OllamaClient
from core.orchestrator import CouncilOrchestrator

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import box

console = Console()

# ── Persona color/emoji map ───────────────────────────────────────────────────
PERSONA_STYLE = {
    "The Scientist":        {"emoji": "🔬", "color": "cyan"},
    "The Creative":         {"emoji": "🎨", "color": "magenta"},
    "The Devil's Advocate": {"emoji": "😈", "color": "red"},
    "The Pragmatist":       {"emoji": "🏗️",  "color": "yellow"},
    "The Theorist":         {"emoji": "📚", "color": "blue"},
    "The Judge":            {"emoji": "⚖️",  "color": "bright_green"},
}

def get_style(name):
    return PERSONA_STYLE.get(name, {"emoji": "🤖", "color": "white"})

def print_banner(provider, model):
    console.print()
    console.print(Panel.fit(
        "[bold bright_white]🧠  MULTI-AI COUNCIL[/bold bright_white]\n"
        "[dim]Multiple minds. One verdict.[/dim]",
        border_style="bright_blue",
        padding=(1, 4),
    ))
    console.print(
        f"  [dim]Provider:[/dim] [bold cyan]{provider.upper()}[/bold cyan]   "
        f"[dim]Model:[/dim] [bold cyan]{model}[/bold cyan]\n"
    )

def print_round_header(num, title):
    console.print()
    console.print(Rule(f"[bold white]  Round {num}: {title}  [/bold white]", style="bright_blue"))
    console.print()

def print_agent_panel(agent_name, response, subtitle, progress_obj=None):
    s = get_style(agent_name)
    emoji, color = s["emoji"], s["color"]
    text = response.strip()
    if len(text) > 1500:
        text = text[:1500] + "\n\n[dim]... (truncated)[/dim]"
    
    panel = Panel(
        Markdown(text),
        title=f"{emoji} [bold {color}]{agent_name}[/bold {color}]  [dim]{subtitle}[/dim]",
        border_style=color,
        padding=(1, 2),
    )
    
    # If rendering inside a live Progress bar, use its thread-safe print method
    if progress_obj:
        progress_obj.print(panel)
        progress_obj.print()
    else:
        console.print(panel)
        console.print()

def print_verdict(verdict):
    console.print()
    console.print(Rule("[bold bright_green]  ⚖️  THE JUDGE'S VERDICT  [/bold bright_green]", style="bright_green"))
    console.print()
    # Don't wrap in a Panel so the Markdown headers render without width interference
    console.print(Markdown(verdict.strip()))
    console.print()
    console.print(Rule("[dim]Council Adjourned[/dim]", style="dim"))
    console.print()

def print_summary(round_1, round_2):
    table = Table(
        title="📋 Council Summary",
        box=box.ROUNDED,
        border_style="bright_blue",
        header_style="bold bright_white",
        show_lines=True,
    )
    table.add_column("Agent",    min_width=24)
    table.add_column("R1 Words", justify="right", style="cyan")
    table.add_column("R2 Words", justify="right", style="magenta")
    table.add_column("Status",   justify="center")

    for name, response in round_1.items():
        s  = get_style(name)
        ok = "[green]✓[/green]" if "Error" not in response else "[red]✗[/red]"
        table.add_row(
            f"[{s['color']}]{s['emoji']} {name}[/{s['color']}]",
            str(len(response.split())),
            str(len(round_2.get(name, "").split())),
            ok,
        )
    console.print(table)
    console.print()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Multi-AI Council CLI")
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-p", "--prompt", type=str)
    input_group.add_argument("-f", "--file",   type=str)
    parser.add_argument("--provider", type=str, choices=["openai", "anthropic", "ollama"], default="ollama")
    parser.add_argument("--model",    type=str, default="")
    args = parser.parse_args()

    # ── Read input ────────────────────────────────────────────────────────────
    if args.prompt:
        user_input = args.prompt
    else:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                user_input = f"Please review the following file:\n\n```\n{f.read()}\n```"
        except Exception as e:
            console.print(f"[red]Error reading file:[/red] {e}")
            sys.exit(1)

    # ── Build LLM client ──────────────────────────────────────────────────────
    if args.provider == "openai":
        model_name = args.model or "gpt-4-turbo"
        if not os.getenv("OPENAI_API_KEY"):
            console.print("[red]Error:[/red] OPENAI_API_KEY not found.")
            sys.exit(1)
        llm_client = OpenAIClient(model=model_name)

    elif args.provider == "anthropic":
        model_name = args.model or "claude-3-5-sonnet-20240620"
        if not os.getenv("ANTHROPIC_API_KEY"):
            console.print("[red]Error:[/red] ANTHROPIC_API_KEY not found.")
            sys.exit(1)
        llm_client = AnthropicClient(model=model_name)

    else:  # ollama
        model_name = args.model or "llama3.1:8b"
        llm_client = OllamaClient(model=model_name)

    # ── Setup ─────────────────────────────────────────────────────────────────
    print_banner(args.provider, model_name)

    orchestrator  = CouncilOrchestrator(llm_client)
    from core.personas import PERSONAS

    agent_keys    = ["scientist", "creative", "devil_advocate", "pragmatist"]
    active_agents = [PERSONAS[k] for k in agent_keys if k in PERSONAS]
    judge         = PERSONAS["judge"]

    # ── Round 1 ───────────────────────────────────────────────────────────────
    print_round_header(1, "Individual Analysis")

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console, transient=True) as p:
        for agent in active_agents:
            s = get_style(agent.name)
            p.add_task(f"[{s['color']}]{s['emoji']} {agent.name}[/{s['color']}] [dim]thinking...[/dim]", total=None)

        def r1_callback(agent_name, response):
            print_agent_panel(agent_name, response, "Initial Analysis", progress_obj=p)

        round_1_results = orchestrator.run_round_1(user_input, active_agents, callback=r1_callback)

    # ── Round 2 ───────────────────────────────────────────────────────────────
    print_round_header(2, "Cross-Critique")

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console, transient=True) as p:
        for agent in active_agents:
            s = get_style(agent.name)
            p.add_task(f"[{s['color']}]{s['emoji']} {agent.name}[/{s['color']}] [dim]critiquing...[/dim]", total=None)

        def r2_callback(agent_name, response):
            print_agent_panel(agent_name, response, "Critique", progress_obj=p)

        round_2_results = orchestrator.run_round_2(user_input, round_1_results, active_agents, callback=r2_callback)

    # ── Round 3: Judge ────────────────────────────────────────────────────────
    print_round_header(3, "The Judge's Synthesis")

    with Progress(SpinnerColumn(style="bold bright_green"),
                  TextColumn("[bright_green]⚖️  The Judge[/bright_green] [dim]deliberating...[/dim]"),
                  console=console, transient=True) as p:
        p.add_task("", total=None)
        final_result = orchestrator.run_round_3(user_input, round_1_results, round_2_results, judge)

    print_verdict(final_result)
    print_summary(round_1_results, round_2_results)


if __name__ == "__main__":
    main()