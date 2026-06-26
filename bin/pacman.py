"""
pacman.py - Package manager for mipyshell
"""

__version__ = "0.4.0"

import sys
import os

def __main__(args):
    """This is called by the shell"""
    # args looks like: ['python', '/bin/pacman.py', '--help']
    run(args[2:] if len(args) > 2 else [])


def run(argv):
    if not argv or argv[0] in ('-h', '--help', 'help'):
        show_help()
        return

    cmd = argv[0].lower()

    if cmd in ('install', 'i'):
        install(" ".join(argv[1:]))
    elif cmd in ('list', 'ls'):
        list_modules()
    elif cmd in ('remove', 'rm', 'uninstall'):
        remove(argv[1] if len(argv) > 1 else None)
    else:
        print(f"Unknown command: {cmd}")
        show_help()


def show_help():
    print(f"""pacman v{__version__} - MicroPython Package Manager

Commands:
  pacman install <package>     Install package
  pacman list                  List loaded modules
  pacman remove <package>      Remove package
  pacman --help                Show this help

Example:
  pacman install micropython-umqtt.simple
""")


def install(pkg):
    if not pkg:
        print("Usage: pacman install <package>")
        return
    print(f"Installing {pkg} ...")
    try:
        import mip
        mip.install(pkg, target="/")
        print("✓ Success!")
    except ImportError:
        print("mip not available on this board.")
    except Exception as e:
        print("Install failed:", e)


def list_modules():
    print("Loaded modules:")
    for m in sorted(sys.modules.keys()):
        if not m.startswith("_"):
            print("  " + m)


def remove(pkg):
    if not pkg:
        print("Usage: pacman remove <package>")
        return
    print(f"Removing {pkg
