import sys

COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_RESET = "\033[0m"

def print_colored(msg: str, color: str = COLOR_RESET):
    """
    Imprime uma mensagem colorida no terminal usando códigos de escape ANSI 
    apenas se a saída padrão for um terminal interativo (TTY).

    Args:
        msg (str): A mensagem a ser impressa.
        color (str): Código de escape ANSI da cor (ex: COLOR_RED).
    """
    # codeql[py/clear-text-logging-sensitive-data]
    if sys.stdout.isatty():
        print(f"{color}{msg}{COLOR_RESET}")
    else:
        print(msg)
