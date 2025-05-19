import zmq
import json
import sys

def main():
    # Ask user for the port
    zmq_rep_port_str = input("Enter the ZMQ REP port number (e.g., 5555, check orchestrator logs for 'ZMQ REP server listening on tcp://*:PORT'): ")
    try:
        zmq_rep_port = int(zmq_rep_port_str)
    except ValueError:
        print(f"Invalid port number entered: {zmq_rep_port_str}", file=sys.stderr)
        sys.exit(1)

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    connect_address = f"tcp://localhost:{zmq_rep_port}"
    
    print(f"Attempting to connect to ZMQ REP server at {connect_address}...")
    
    try:
        # Set linger to 0 for quicker exit if server is not there on send
        socket.setsockopt(zmq.LINGER, 0)
        socket.connect(connect_address)
        # ZMQ REQ connect is immediate; actual connection test happens on first send/recv.
    except zmq.error.ZMQError as e: 
        # This typically shouldn't happen on connect for REQ unless system resources are an issue
        print(f"Unexpected ZMQ Error during connect: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Socket binding to {connect_address} scheduled. Sending commands...")

    commands_to_test = [
        {"action": "status"},
        {"action": "list_agents"}
    ]

    for command in commands_to_test:
        print(f"\nSending command: {command}")
        try:
            socket.send_json(command)
            
            # Wait for the reply with a timeout
            if socket.poll(7000): # 7 seconds timeout
                response = socket.recv_json()
                print("Received response:")
                print(json.dumps(response, indent=2))
            else:
                print("Error: Timeout waiting for ZMQ response.", file=sys.stderr)
                print(f"No response received from {connect_address} for command: {command.get('action', 'N/A')}", file=sys.stderr)
                print("Possible issues:", file=sys.stderr)
                print("1. Legion Orchestrator is not running or has crashed.", file=sys.stderr)
                print(f"2. Incorrect ZMQ REP port. You entered: {zmq_rep_port}. Check orchestrator logs for 'listening on tcp://*:PORT'.", file=sys.stderr)
                print("3. Orchestrator is busy, stuck, or not processing ZMQ commands.", file=sys.stderr)
                print("4. Firewall blocking localhost connections on this port (less likely for localhost).", file=sys.stderr)
                break 

        except zmq.error.ZMQError as e:
            print(f"ZMQ Error during command {command.get('action', 'N/A')}: {e}", file=sys.stderr)
            print(f"This might indicate the server at {connect_address} is not responding or an issue with ZMQ setup.", file=sys.stderr)
            break 
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)
            break

    print("\nSmoke test client finished.")
    socket.close()
    context.term()

if __name__ == "__main__":
    main() 