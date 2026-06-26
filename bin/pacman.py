__version__ = "0.3.0"

import sys
import os

def __main__(args):
    run(args[2:] if len(args) > 2 else [])


def run(argv):
    if not argv or argv[0] in ('-h', '--help', 'help'):
        show_help()
        return

    cmd = argv[0].lower()

    try:
        if cmd in ('install', 'i'):
            install(" ".join(argv[1:]))
        elif cmd in ('search', 's'):
            search(" ".join(argv[1:]))
        elif cmd in ('update', 'u', 'refresh'):
            update()
        elif cmd in ('list', 'ls'):
            list_installed()
        elif cmd in ('remove', 'rm', 'uninstall', 'delete'):
            remove(argv[1] if len(argv) > 1 else None)
        else:
            print(f"pacman: command '{cmd}' not found")
            print("Try 'pacman --help' for a list of commands.")
    except Exception as e:
        print("Something went wrong:")
        sys.print_exception(e)


def show_help():
    print(f"""pacman.py v{__version__} - MicroPython Package Manager

Usage:
  pacman install <package>     Install from mip/upip or local .mpy.pkg
  pacman search <name>         Search (basic)
  pacman update                Refresh package info
  pacman list                  Show loaded modules
  pacman remove <package>      Remove package
To_Get_.mpy.pkg:
  go to https://github.com/orangecopres-spec-2/.mpy.pkg

Examples:
  pacman install requests
  pacman install github:org/repo
  pacman install mycoollib.mpy.pkg
  pacman remove umqtt.simple
""")


def install(pkg):
    if not pkg:
        print("Usage: pacman install <package or .mpy.pkg file>")
        return

    # Handle local .mpy.pkg file
    if pkg.endswith('.mpy.pkg'):
        install_mpy_pkg(pkg)
        return

    print(f"Installing {pkg}...")
    try:
        import mip
        print("→ Using mip (recommended)")
        mip.install(pkg, target="/")
        print("✓ Done!")
    except ImportError:
        try:
            import upip
            print("→ Using upip (older method)")
            upip.install(pkg)
            print("✓ Done!")
        except ImportError:
            print("❌ Neither mip nor upip available. Try installing a .mpy.pkg file instead.")
    except Exception as e:
        print("Installation failed:", e)


def install_mpy_pkg(pkg_path):
    """Install a local .mpy.pkg file"""
    if not os.path.exists(pkg_path):
        # Try relative to current dir too
        cwd = os.getcwd()
        if cwd != "/":
            alt_path = cwd.rstrip("/") + "/" + pkg_path.lstrip("/")
            if os.path.exists(alt_path):
                pkg_path = alt_path
            else:
                print(f"❌ File not found: {pkg_path}")
                return
        else:
            print(f"❌ File not found: {pkg_path}")
            return

    print(f"Installing local package: {pkg_path}")

    try:
        # For now: simple copy to /lib/ with .mpy extension
        # You can extend this later to support zip/tar extraction if needed
        filename = os.path.basename(pkg_path)
        module_name = filename[:-8]  # remove .mpy.pkg

        target = f"/lib/{module_name}.mpy"

        with open(pkg_path, 'rb') as src:
            with open(target, 'wb') as dst:
                while True:
                    chunk = src.read(512)
                    if not chunk:
                        break
                    dst.write(chunk)

        print(f"✓ Installed as {target}")
        print(f"   You can now import {module_name}")
    except Exception as e:
        print("❌ Failed to install .mpy.pkg:", e)
        sys.print_exception(e)


def search(query):
    if not query:
        print("Usage: pacman search <name>")
        return
    print(f"Searching for '{query}'...")
    print("mip doesn't have a full search yet.")
    print("Try installing directly or check https://github.com/micropython/micropython-lib")


def update():
    print("Updating package index...")
    print("mip pulls the latest info automatically.")
    print("No manual update needed — just install what you want!")


def list_installed():
    print("Currently available modules:")
    modules = sorted(m for m in sys.modules if not m.startswith("_"))
    if modules:
        for m in modules:
            print("   ", m)
    else:
        print("   (none found)")


def remove(pkg):
    if not pkg:
        print("Usage: pacman remove <package>")
        return

    print(f"Removing {pkg}...")

    removed = False
    for ext in ['.mpy', '.py']:
        for base in ['/lib/', 'lib/']:
            path = f"{base}{pkg}{ext}"
            try:
                os.remove(path)
                print(f"✓ Removed {path}")
                removed = True
            except:
                pass

    if not removed:
        print(f"Could not find {pkg} in /lib/")


# Allow running directly
if __name__ == "__main__" or 'ARGV' in locals():
    run(ARGV[1:] if 'ARGV' in locals() else sys.argv[1:])
