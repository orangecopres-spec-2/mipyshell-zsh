'''
Created by Valentin Solina, Part of mipyshell project
Super simple, MicroPython based, VT100 compatible POSIX shell imitation
'''
"""
pacman.py - Package manager for mipyshell
Compatible with Valentin Solina's mipyshell (sh.py)
"""

__version__ = "0.2.0"

import sys
import os

def __main__(args):
    """
    Called by python_imp() in sh.py
    args format: ['python', '/bin/pacman.py', ...user args...]
    """
    # Remove the first two arguments (python + script name)
    run(args[2:] if len(args) > 2 else [])


def run(argv):
    if not argv or argv[0] in ('-h', '--help', 'help'):
        show_help()
        return

    cmd = argv[0].lower()

    try:
        if cmd in ('install', 'i'):
            install_package(" ".join(argv[1:]))

        elif cmd in ('search', 's'):
            search_package(" ".join(argv[1:]))

        elif cmd in ('update', 'u'):
            update_index()

        elif cmd in ('list', 'ls'):
            list_packages()

        elif cmd in ('remove', 'rm', 'uninstall'):
            remove_package(argv[1] if len(argv) > 1 else None)

        else:
            print(f"pacman: unknown command '{cmd}'")
            print("Type 'pacman --help' for usage.")

    except Exception as e:
        print("Error:", e)
        sys.print_exception(e)


def show_help():
    print("""pacman.py v{} - MicroPython Package Manager

Usage:
  pacman install <package>     Install a package
  pacman search <name>         Search for packages
  pacman update                Refresh package index
  pacman list                  List loaded modules
  pacman remove <package>      Remove a package

Examples:
  pacman install requests
  pacman install micropython-umqtt.simple
  pacman install github:org/repo@branch
  pacman install -t /lib custompkg
""".format(__version__))


def install_package(pkg):
    if not pkg:
        print("Usage: pacman install <package>")
        return

    print(f"Installing {pkg}...")

    try:
        # Prefer modern mip (MicroPython 1.20+)
        import mip
        print("Using mip...")
        mip.install(pkg, target="/")
        print("✓ Successfully installed")
    except ImportError:
        # Fallback to upip (older boards)
        try:
            import upip
            print("Using upip...")
            upip.install(pkg)
            print("✓ Successfully installed")
        except ImportError:
            print("❌ Neither 'mip' nor 'upip' is available on this board.")
    except Exception as e:
        print("❌ Installation failed:", e)


def search_package(query):
    if not query:
        print("Usage: pacman search <name>")
        return
    print(f"Searching for '{query}'...")
    print("mip doesn't support full search yet.")
    print("Tip: Try `pacman install <exact-package-name>`")


def update_index():
    print("Updating package index...")
    print("mip uses live index from micropython-lib - no update needed.")
    print("Tip: Just run `pacman install <package>`")


def list_packages():
    print("Currently loaded modules:")
    modules = sorted([m for m in sys.modules.keys() if not m.startswith("_")])
    for m in modules:
        print("  " + m)


def remove_package(pkg):
    if not pkg:
        print("Usage: pacman remove <package>")
        return

    print(f"Removing {pkg}...")

    paths = [
        f"/lib/{pkg}.py",
        f"/lib/{pkg}.mpy",
        f"lib/{pkg}.py",
        f"lib/{pkg}.mpy",
    ]

    removed = False
    for path in paths:
        try:
            os.remove(path)
            print(f"✓ Removed {path}")
            removed = True
        except:
            pass

    if not removed:
        print(f"Could not find {pkg} in /lib/")


# Support direct execution (if someone runs python pacman.py directly)
if __name__ == "__main__" or 'ARGV' in locals():
    run(ARGV[1:] if 'ARGV' in locals() else sys.argv[1:])
