
import subprocess
import simplejson
import urllib
import os

import mount
from sh import sh

HOME="/var/run/fslayers"

class Stack(object):

    def __init__(self, mountpoint):
        self.mountpoint = os.path.normpath(os.path.abspath(mountpoint))

    def get_mounted(self):
        return self.mountpoint in mount.Mount.all()
    mounted = property(get_mounted)

    def get_home(self):
        return os.path.join(HOME, self.id)
    home = property(get_home)

    def get_id(self):
        return urllib.quote(self.mountpoint, safe="")
    id = property(get_id)

    def get_layers(self):
        fs = mount.Mount.all().get(self.mountpoint)
        if fs and fs.type == "aufs":
            return fs.layers
        else:
            return []

    def set_layers(self, layers):
        if layers:
            opt = ":".join(["br"] + [path + "=" + access for (path, access) in layers])
            sh(("mount", "-t", "aufs", "-o", ("remount," if self.mounted else "") + opt, "none", self.mountpoint))
        elif self.mounted:
            sh(("umount", self.mountpoint))

    layers = property(get_layers, set_layers)

