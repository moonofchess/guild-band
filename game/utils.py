import sys
import time
import os

# ANSI Color Codes for terminal formatting
RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

# Standard colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
GRAY = "\033[90m"

# Bright/Vibrant colors
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"

# Enable ANSI on Windows Command Prompt/PowerShell if needed
if sys.platform == "win32":
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def colorize(text, color):
    """Wrap text with the specified ANSI color."""
    return f"{color}{text}{RESET}"

def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_slow(text, delay=0.01):
    """Print text with a typewriter effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def print_header(title):
    """Print a styled section header."""
    width = 60
    print(colorize("=" * width, GRAY))
    print(colorize(title.center(width), BOLD + BRIGHT_CYAN))
    print(colorize("=" * width, GRAY))

def print_divider():
    """Print a simple divider line."""
    print(colorize("-" * 60, GRAY))

def get_input(prompt, valid_choices=None, is_numeric=False):
    """Get input from user, validating against a list of choices or checking if numeric."""
    while True:
        try:
            choice = input(prompt).strip()
            if not choice:
                continue
            if is_numeric:
                return int(choice)
            if valid_choices:
                if choice.lower() in [str(c).lower() for c in valid_choices]:
                    return choice
                else:
                    print(colorize(f"Invalid input. Choose from: {', '.join(map(str, valid_choices))}", RED))
            else:
                return choice
        except ValueError:
            print(colorize("Please enter a valid number.", RED))
        except (KeyboardInterrupt, EOFError):
            print(colorize("\nGame terminated.", RED))
            sys.exit(0)
