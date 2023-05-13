##################################################################
# Project:  CSE-5306 2-Phase Commit Protocol
# File:     participant-3
# Date:     Sunday 16 October 2022
# Authors:  Prithvi Bhat (pnb3598@mavs.uta.edu)
##################################################################

from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
from threading import Timer

C_PORT          = 8000
P3_PORT         = 8003                                                      # Port to bind socket to
HOSTNAME        = "0.0.0.0"                                                 # Server Host address

coordinator_endpoint = 'http://{}:{}'.format(HOSTNAME, C_PORT)              # Set an endpoint for the client to communicate to
coordinator_proxy = xmlrpc.client.ServerProxy(coordinator_endpoint)         # Bind

def start_timer(timeout, timeout_handler):
    timer = Timer(timeout, timeout_handler)
    timer.start()                                                           # Start timer
    return timer                                                            # Return timer handle

def reset_timer(timer_handle):
    timer_handle.cancel()                                                   # Clear timer
    return True

"""
    Function to handle watchdog timeout
"""
def message_timeout_handler():
  print("No message received. Coordinator possibly down..")
  return True

def _req(request_number):
    print("\nRequest ", request_number, " received\tResponse relayed")
    global timeout_handle
    timeout_handle = start_timer(10, message_timeout_handler)               # Start watchdog timer and assign timeout handler
    return True

def request_receive(request_number):
    return (_req(request_number))

def message_receive(request_number, message):
    print("\nRequest: ", request_number, "\tMessage: ", message)
    global timeout_handle
    reset_timer(timeout_handle)                                             # Reset watchdog on receiving the message before set time
    return True


def Main():
    P1 = SimpleXMLRPCServer((HOSTNAME, P3_PORT))                            # Bind server to port
    print("Participant 3 online on port [" + str(P3_PORT) + "]")
    P1.register_function(request_receive, 'req_recv')                       # Register RPC
    P1.register_function(message_receive, 'msg_recv')                       # Register RPC
    try:
        P1.serve_forever()
    except KeyboardInterrupt:
        print("Killing Participant 3")

if __name__ == '__main__':
    Main()
