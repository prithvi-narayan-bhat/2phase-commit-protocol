# 2 Phase Commit Protocol
Application to implement an 2 Phase Commit Protocol Distributed system

## Usage
Run coordinator.py, participant1.py, participant2.py, participant3.py in any order in three different terminal consoles to observe a simple implementation of 2 Phase Commit Protocol

## Expected Behavior
### Ideal Path
1. Coordinator and all three participants are running
2. Coordinator sends request and all three participants respond with an "ack"
3. Coordinator, within 5 seconds of receiving the "ack" from all three participants will send out a message request

### Faulty Path 1
1. One or more participants are down
2. Coordinator sends request not all participants respond with an "ack"
3. Coordinator retries every 5 seconds until all three participants return on-line and respond with an "ack"

### Faulty Path 2
1. All three participants are running but the Coordinator is down
2. Participants receive a request from Coordinator before it went down but do not receive a message request within 10 seconds since responding with an "ack"
3. Participants assume Coordinator is down and wait for the next request
4. Once back up, the Coordinator will retrieve the last successful message from the logs and retry sending the same to the Participants
