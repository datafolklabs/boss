
import os
import shutil
from subprocess import Popen, PIPE

def abspath(path):
    return os.path.abspath(os.path.expanduser(path))

def exec_cmd(cmd_args):
    proc = Popen(cmd_args, stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = proc.communicate()
    proc.wait()
    return (stdout, stderr, proc.returncode)

def exec_cmd2(cmd_args):
    proc = Popen(cmd_args)
    proc.wait()
    return proc.returncode

def safe_backup(path, suffix='.bak', keep_original=True):
    """
    Rename a file or directory safely without overwriting an existing
    backup of the same name.
    """
    count = -1
    new_path = None
    while True:
        if os.path.exists(path):
            if count == -1:
                new_path = "%s%s" % (path, suffix)
            else:
                new_path = "%s%s.%s" % (path, suffix, count)
            if os.path.exists(new_path):
                count += 1
                continue
            else:
                if keep_original:
                    if os.path.isfile(path):
                        shutil.copy(path, new_path)
                    elif os.path.isdir(path):
                        shutil.copytree(path, new_path)
                else:
                    shutil.move(path, new_path)
                break
        else:
            break
    return new_path
