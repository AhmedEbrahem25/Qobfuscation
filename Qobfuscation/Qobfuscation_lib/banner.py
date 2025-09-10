import os, time, random
from pyfiglet import Figlet
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

console = Console()

COLORS = ["bold cyan", "bold magenta", "bold red", "bold green", "bold yellow"]

FONTS = ["slant", "doom", "ansi_shadow", "cyberlarge", "standard"]

def glitch_text(text, cycles=8, delay=0.05):
    chars = "!@#$%^&*()_+=-<>?/\\|[]{}"
    text_list = list(text)
    for _ in range(cycles):
        glitched = text_list[:]
        for _ in range(random.randint(1, len(text)//3)):
            idx = random.randint(0, len(text)-1)
            glitched[idx] = random.choice(chars)
        console.print("".join(glitched), style=random.choice(COLORS))
        time.sleep(delay)
        os.system("cls" if os.name == "nt" else "clear")
    console.print(text, style="bold bright_cyan")

def animated_banner():
    glitch_text("QOBFUSCATION", cycles=6, delay=0.07)

    font = random.choice(FONTS)
    f = Figlet(font=font)
    banner_text = f.renderText("Qobfuscation")
    color = random.choice(COLORS)

    console.print(Text(banner_text, style=color))

    console.print(
        Panel.fit(
            "[bold cyan]⚡ Quantum Obfuscation Framework ⚡\n"
            "[bold white]🌀 Smart Noise   🔐 Entanglement \n"
            "[bold magenta]Version: 1.0.0 | Author: 0xVnex",
            title="[ Pro Mode ]",
            border_style="bright_magenta",
        )
    )

if __name__ == "__main__":
    animated_banner()
