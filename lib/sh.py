

import uos
import os
import sys
import machine
import gc
import time

# Threading support
try:
    import _thread
    THREADS_ENABLED = True
except ImportError:
    THREADS_ENABLED = False

alive = True


# ====================== Utility Functions ======================
def abs_path(path):
    if path.startswith("/"):
        return path
    if path.startswith("~"):
        return "/" + path[1:].lstrip("/")
    cwd = os.getcwd()
    if cwd != "/":
        cwd = "/" + cwd.lstrip("/")
    if not cwd.endswith("/"):
        cwd += "/"
    return cwd + path.lstrip("/")


def get_bins():
    pybins = {}
    shbins = {}
    try:
        for f in os.listdir("/bin"):
            if f.endswith(".py"):
                pybins[f[:-3]] = f"/bin/{f}"
            elif f.endswith(".sh"):
                shbins[f[:-3]] = f"/bin/{f}"
    except:
        pass
    return pybins, shbins


# ====================== Built-in Commands ======================
def mkdir_imp(args):
    if len(args) < 2:
        print("Usage: mkdir <dir>")
        return
    try:
        os.mkdir(abs_path(args[1]))
        print("Directory created")
    except Exception as e:
        print("mkdir failed:", e)


def rmdir_imp(args):
    if len(args) < 2:
        print("Usage: rmdir <dir>")
        return
    try:
        os.rmdir(abs_path(args[1]))
        print("Directory removed")
    except Exception as e:
        print("rmdir failed:", e)


def touch_imp(args):
    if len(args) < 2:
        print("Usage: touch <file>")
        return
    try:
        with open(abs_path(args[1]), 'a'):
            pass
        print("File touched")
    except Exception as e:
        print("touch failed:", e)


def cd_imp(args):
    try:
        if len(args) < 2:
            os.chdir("/")
        else:
            os.chdir(abs_path(args[1]))
    except Exception as e:
        print("cd failed:", e)


def pwd_imp(args):
    print(abs_path(os.getcwd()))


def rm_imp(args):
    if len(args) < 2:
        print("Usage: rm <file>")
        return
    try:
        os.remove(abs_path(args[1]))
        print("File removed")
    except Exception as e:
        print("rm failed:", e)


def free_imp(args):
    gc.collect()
    micropython.mem_info()


def reset_imp(args):
    print("Rebooting...")
    time.sleep(0.5)
    machine.reset()


def modules_imp(args):
    print("Loaded modules:")
    for m in sorted(sys.modules):
        if not m.startswith("_"):
            print("   ", m)


# ====================== Special Commands ======================
def python_imp(args):
    """Fixed version - properly handles pacman and other scripts"""
    if len(args) < 2:
        global alive
        alive = False
        return

    script_path = args[1]
    
    # Clean script name
    if "/" in script_path:
        script_name = script_path.split("/")[-1]
    else:
        script_name = script_path
    if script_name.endswith(".py"):
        script_name = script_name[:-3]

    try:
        mod = __import__(script_name)
        
        if hasattr(mod, "__main__"):
            mod.__main__(args)                    # Full args for pacman
        elif hasattr(mod, "run"):
            mod.run(args[2:] if len(args) > 2 else [])
        else:
            print(f"No entry point found in {script_name}")
            
    except Exception as e:
        print(f"Error executing {script_name}:")
        sys.print_exception(e)
        
    finally:
        # Safe cleanup
        if script_name in sys.modules:
            del sys.modules[script_name]


def quit_imp(args):
    global alive
    alive = False


# ====================== Command Mapping ======================
cmds_integrated = {
    "mkdir": mkdir_imp,
    "rmdir": rmdir_imp,
    "touch": touch_imp,
    "cd": cd_imp,
    "pwd": pwd_imp,
    "rm": rm_imp,
    "free": free_imp,
    "reboot": reset_imp,
    "reset": reset_imp,
    "restart": reset_imp,
    "modules": modules_imp,
    "python": python_imp,
    "pacman": python_imp,      # Important for pacman
    "quit": quit_imp,
    "exit": quit_imp,
}


def all_commands(start=""):
    py, sh = get_bins()
    cmds = list(cmds_integrated.keys()) + list(py.keys()) + list(sh.keys())
    if start:
        cmds = [c for c in cmds if c.startswith(start)]
    return sorted(cmds)


def execute_command(command):
    if not command.strip():
        return
    args = [a for a in command.strip().split() if a]
    _exec_cmd(args)


def _exec_cmd(args):
    cmd_name = args[0]
    py_bins, sh_bins = get_bins()

    if cmd_name in cmds_integrated:
        cmds_integrated[cmd_name](args)
    elif cmd_name in py_bins:
        python_imp(['python', py_bins[cmd_name]] + args[1:])
    elif cmd_name in sh_bins:
        print("Shell scripts not fully supported yet")
    else:
        print(f"{cmd_name}: command not found")


# ====================== Interactive Shell ======================
from cmd import Cmd

class Shell(Cmd):
    def __init__(self):
        super().__init__()
        self.update_prompt()
        print("mipyshell started. Type 'pacman --help' to test package manager.")

    def update_prompt(self):
        try:
            cwd = os.getcwd() or "/"
            self.prompt = f"upy:{cwd} $ "
        except:
            self.prompt = "upy $ "

    def default(self, line):
        try:
            execute_command(line)
        except KeyboardInterrupt:
            print("\nInterrupted")
        self.update_prompt()

    def completedefault(self, text, line, begidx, endidx):
        return all_commands(text)


# ====================== Start ======================
def main():
    try:
        shell = Shell()
        shell.cmdloop()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print("Shell error:", e)

if __name__ == "__main__":
    main()
