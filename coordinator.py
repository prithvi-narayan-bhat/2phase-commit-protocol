##################################################################
# Project:  CSE-5306-2 Phase Commit Protocol
# File:     coordinator
# Date:     Sunday 16 October 2022
# Authors:  Prithvi Bhat (pnb3598@mavs.uta.edu)
##################################################################

from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import time

C_PORT          = 8000
P1_PORT         = 8001          # Port to bind socket to
P2_PORT         = 8002          # Port to bind socket to
P3_PORT         = 8003          # Port to bind socket to
HOSTNAME        = "0.0.0.0"     # Server Host address
MAX_PARTICIPANT = 3

participant_port = [8001, 8002, 8003]
participant_response_states = [False, False, False]


"""
    Function to bind to the server proxies of the specified participant
"""
def connect(participant_id):

    endpoint = 'http://{}:{}'.format(HOSTNAME, participant_port[participant_id])    # Set an endpoint for the client to communicate to
    return (xmlrpc.client.ServerProxy(endpoint))                                    # Bind server proxy

"""
    Function to read the lof file and return the count of last transaction sent before coordinator went down
"""
def get_last_log_entry():

    try:
        with open('log_file', 'r') as log_handle_r:                                 # Open file in read mode
            last_entry = log_handle_r.readlines()[-1]                               # Get last line
        log_handle_r.close()                                                        # Close file handle
        return int(last_entry)                                                      # Return last entry as integer
    except:
        print("Empty log file detected. Creating one now")                          # Create a file if one doesn't already exist

def Main():

    coordinator = SimpleXMLRPCServer((HOSTNAME, C_PORT))                            # Bind server to port
    print("Coordinator online on port [" + str(C_PORT) + "]")

    request_number = 0                                                              # set default request number

    while(1):
        if (get_last_log_entry() == None):                                          # Arises for first transaction of coordinator
            request_number = 0                                                      # Set default value
        else:
            request_number = get_last_log_entry()                                   # Get last value

        log_handle_w = open('log_file', 'a')                                        # Initialise logger handle
        log_handle_w.write((str(request_number)+"\n"))

        participant_proxy = []                                                      # List to hold the states of all participants

        print("\nSending \"Prepare Message\"")

        for participant_id in range(0, MAX_PARTICIPANT):                            # Iteratively check if each of the participants are up
            try:
                participant_proxy.append(connect(participant_id))                   # They're up!
            except:
                participant_response_states[participant_id] = False                 # Update state in list if not up
            else:
                try:
                    participant_response_states[participant_id] = participant_proxy[participant_id].req_recv(request_number)        # Try invoking the participants RPC if up
                except:
                    participant_response_states[participant_id] = False                                                             # Update state if not responsive

            go_phase2 = False

            if (participant_response_states[participant_id] == True):               # Go to phase 2 only if all participants are up and communicating
                go_phase2 = True
            else:
                go_phase2 = False
                break

        if (go_phase2 == True):
            request_number = request_number + 1                                     # Increase request number to include latest commit message count

            log_handle_w.write((str(request_number+1)+"\n"))                        # Log the new request number value
            print("All Participants up. Sending \"Commit Message\"")
            user_input = input("Enter 1 to continue without stall: ")
            if (user_input == '1'):
                for participant_id in range(0, MAX_PARTICIPANT):
                    try:
                        participant_proxy[participant_id].msg_recv(request_number, "Phase 2: Hello World")                              # Send "Commit Message" to all participants iteratively
                    except:
                        continue
            else:
                break
        else:
            print("One or more Participants non responsive. Waiting..\n")           # One of the participants have some issue. Wait until all are back and responsive

        log_handle_w.close()                                                        # Close log file handle
        time.sleep(5)

    try:
        coordinator.serve_forever()
    except KeyboardInterrupt:
        print("Killing Coordinator")


if __name__ == '__main__':
    Main()