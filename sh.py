
import subprocess
import sys

def sh(cmd):
    sys.stderr.write("# " + " ".join(cmd) + "\n")
    return subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

