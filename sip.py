#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pjsua as pj
import threading
import sys
from dotenv import load_dotenv
import os

load_dotenv()

LOG_LEVEL = 3
SIP_DOMAIN = os.getenv('SIP_OUTBOUND_HOST')
SIP_USER = os.getenv('SIP_OUTBOUND_USER')
SIP_PASSWD = os.getenv('SIP_OUTBOUND_PASS')
SIP_PORT = int(os.getenv('SIP_OUTBOUND_PORT', 5060))


# Define callback to receive events
class MyAccountCallback(pj.AccountCallback):
    sem = None

    def __init__(self, account=None):
        pj.AccountCallback.__init__(self, account)

    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()

    def on_incoming_call(self, call):
        print("Incoming call...")
        # Here you can handle incoming calls. Since you don't want audio, you might just want to auto-answer or ignore.

    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:  # Registration successful
                self.sem.release()


# Create library instance
lib = pj.Lib()

try:
    # Init library with default config and some logging
    lib.init(log_cfg=pj.LogConfig(level=LOG_LEVEL))

    # Create UDP transport which listens to any available port
    transport = lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(SIP_PORT))

    # Start the library
    lib.start()

    # Create local/user-less account
    acc = lib.create_account_for_transport(transport, cb=MyAccountCallback())

    # Register to SIP server by creating another account
    acc_cb = MyAccountCallback()
    acc = lib.create_account(
        pj.AccountConfig(domain=SIP_DOMAIN, username=SIP_USER, password=SIP_PASSWD),
        cb=acc_cb
    )

    acc_cb.wait()

    print("\nListening for incoming calls... Press <ENTER> to quit\n")
    input()
    print("Shutting down...")

except pj.Error as e:
    print("Exception: " + str(e))
    lib.destroy()
    lib = None
    sys.exit(1)

finally:
    if lib:
        lib.destroy()
        lib = None
