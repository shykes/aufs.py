
import os
import re
import sys
import subprocess

import simplejson

def sh(cmd, debug=False):
    if debug:
        sys.stderr.write("# " + " ".join(cmd) + "\n")
    return subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

re_mtab = re.compile("^(.*) on ([^ ]*) type (.*) \((.*)\)$")
def mtab(typefilter=None):
    """ Return a dictionary of all mounted filesystems, keyed by mountpoint """
    return dict([
                (fs["mountpoint"], fs)
                for fs in (
                        dict(
                            source      = groups[0],
                            mountpoint  = os.path.normpath(groups[1]),
                            type        = groups[2],
                            options     = groups[3].split(",")
                        )
                    for groups in (
                        line_match.groups()
                        for line_match in map(re_mtab.match, sh(["mount"]).strip().split("\n"))
                        if line_match
                    )
                )
                if (not typefilter) or (typefilter == fs["type"])
            ])

class AUFS(object):
    """ An AUFS mountpoint. see http://aufs.sourceforge.net/
    
    Use the 'layers' property to access or change currently mounted AUFS layers

    Examples:

    # Mount /etc (read-only) in /tmp/etc, and store any changes in /tmp/etc_changes
    >>> AUFS('/tmp/etc').layers = [("/tmp/etc_changes", "rw"), ("/etc", "ro")]

    # Unmount /tmp/etc
    >>> AUFS('/tmp/etc').layers = []
    """

    def __init__(self, mountpoint):
        self.mountpoint = self.cleanpath(mountpoint)

    @staticmethod
    def cleanpath(path):
        return os.path.normpath(os.path.abspath(path))

    def get_layers(self):
        mtab_entry = mtab().get(self.mountpoint)
        if not mtab_entry:
            return []
        return [
            (self.cleanpath(path), access)
            for (path, access) in reduce(list.__add__, [
                    [
                        layer.split("=", 1)
                        for layer in option.split(":")[1:]
                    ]
                    for option in mtab_entry["options"]
                    if option.startswith("br:")
            ])
        ]

    def set_layers(self, layers):
        layers = [(self.cleanpath(path), access) for (path, access) in layers]
        if layers == self.layers:
            return
        if self.layers:
            sh(("umount", self.mountpoint))
        if layers:
            opt = ":".join(["br"] + [path + "=" + access for (path, access) in layers])
            sh(("mount", "-t", "aufs", "-o", opt, "none", self.mountpoint))

    layers = property(get_layers, set_layers)
