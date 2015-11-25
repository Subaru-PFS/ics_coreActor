#!/usr/bin/env python

import subprocess

import opscore.protocols.keys as keys
import opscore.protocols.types as types
from opscore.utility.qstr import qstr

class TopCmd(object):

    def __init__(self, actor):
        # This lets us access the rest of the actor.
        self.actor = actor

        # Declare the commands we implement. When the actor is started
        # these are registered with the parser, which will call the
        # associated methods when matched. The callbacks will be
        # passed a single argument, the parsed and typed command.
        #
        self.vocab = [
            ('ping', '', self.ping),
            ('status', '', self.status),
            ('inventory', '', self.inventory),
            ('power', '@(on|off) <cam> <device>', self.power),
            ('powerBEE', '<cam>', self.powerBEE),
        ]

        # Define typed command arguments for the above commands.
        self.keys = keys.KeysDictionary("core_core", (1, 1),
                                        keys.Key("device", types.String(),
                                                 help='device name, probably like bee_r1'),
                                        keys.Key("cam", types.String(),
                                                 help='camera name, e.g. r1'),
                                        )

    def inventory(self, cmd):
        """ """
        cmd.finish()
    
    def powerBEE(self, cmd):
        """Try to power on a given BEE. 

        Why this command? Because otherwise we would have to run a
        command line program to get a PCM to power up a BEE port.
        """

        cam = cmd.cmd.keywords['cam'].values[0]

        cmdStr = "pcm.py --cam=%s --on=bee" % (cam)
        cmd.inform('text="trying to turn on the %s BEE board"' % (cam))

        try:
            subprocess.check_output(cmdStr, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            cmd.fail('text="failed to power up %s BEE. retcode=%s, error=%s"' % (cam,
                                                                                 e.returncode,
                                                                                 e.output))
            return
        
        cmd.finish('text="BEE probably booting up. Wait about 45s for it to appear"')
    
    def power(self, cmd):
        raise NotImplementedError()
    
    def ping(self, cmd):
        """Query the actor for liveness/happiness."""

        cmd.warn("text='I am an empty and fake actor'")
        cmd.finish("text='Present and (probably) well'")

    def status(self, cmd):
        """Report camera status and actor version. """

        self.actor.sendVersionKey(cmd)
        
        cmd.inform('text="Present!"')
        cmd.finish()

