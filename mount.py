
import os
import re
import sys
from sh import sh

import simplejson

class dict_object(object):
    def __repr__(self):
        return repr(self.__dict__)

class Mount(dict_object):

    re_mount = re.compile("^(.*) on ([^ ]*) type (.*) \((.*)\)$")

    @classmethod
    def subclass(cls, mount_type):
        subcls = globals().get("%sMount" % mount_type.upper())
        if not subcls:
            return cls
        if not issubclass(subcls, cls):
            return cls
        return subcls

    @classmethod
    def all(cls):
        return dict([
                    (mount.mountpoint, mount)
                    for mount in (
                            (cls.subclass(groups[2]))(
                                source      = groups[0],
                                mountpoint  = os.path.normpath(groups[1]),
                                type        = groups[2],
                                options     = groups[3].split(",")
                            )
                        for groups in (
                            line_match.groups()
                            for line_match in map(cls.re_mount.match, sh(["mount"]).strip().split("\n"))
                            if line_match
                        )
                    )
                ])

    def __init__(self, source, mountpoint, type, options):
        self.source = source
        self.mountpoint = mountpoint
        self.type = type
        self.options = options

class AUFSMount(Mount):

    def get_layers(self):
        return reduce(list.__add__, [
            [
                layer.split("=", 1)
                for layer in option.split(":")[1:]
            ]
            for option in self.options
            if option.startswith("br:")
        ])
    layers = property(get_layers)

