# pacman.py - Simple package manager for mipyshell (inspired by Arch's pacman)
__version__ = '0.1.0'

import sys
import os

def __main__(args):
    # args[0] = "python", args[1] = "pacman.py"
    run(args[2:])

def run(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print("""pacman.py - MicroPython Package Manager

Usage:
  pacman install <package>     # e.g. mip install micropython-umqtt.simple
  pacman search <name>
  pacman update
  pacman list
  pacman remove <package>

Examples:
  pacman install github:org/repo
  pacman install requests
""")
        return

    cmd = argv[0]

    try:
        if cmd == "install":
            pkg = " ".join(argv[1:])
            print(f"Installing {pkg}...")
            try:
                import mip
                mip.install(pkg)
                print("✓ Installed successfully")
            except ImportError:
                print("mip not available, trying upip...")
                try:
                    import upip
                    upip.install(pkg)
                except:
                    print("Error: Neither mip nor upip available")
        elif cmd == "search":
            print("Search not implemented (mip doesn't have a full index search yet)")
            print("Try: mip install <exact-name>")
        elif cmd == "update":
            print("Updating package index...")
            try:
                import mip
                # mip doesn't have explicit update, but reinstalling works
                print("Package index is live from micropython-lib")
            except:
                print("upip update not supported")
        elif cmd == "list":
            print("Installed packages/modules:")
            for m in sorted(sys.modules.keys()):
                print("  " + m)
        elif cmd == "remove":
            pkg = argv[1] if len(argv) > 1 else None
            if pkg:
                try:
                    os.remove(f"lib/{pkg}.mpy")  # or .py
                    print(f"Removed {pkg}")
                except:
                    print(f"Could not remove {pkg} (check lib/ directory)")
            else:
                print("Usage: pacman remove <package>")
        else:
            print(f"Unknown command: {cmd}")
    except Exception as e:
        print("Error:", e)
        sys.print_exception(e)

# Support direct execution
if __name__ == "__main__" or 'ARGV' in locals():
    run(ARGV if 'ARGV' in locals() else sys.argv[1:])
