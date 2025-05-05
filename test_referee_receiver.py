from communication.referee_receiver import RefereeReceiver

def test_referee_receiver():
    receiver = RefereeReceiver()
    message = receiver.receive()

    print("=== Mensagem Recebida ===")
    print(f"Stage: {message.stage}")
    print(f"Command: {message.command}")
    print(f"Command Counter: {message.command_counter}")
    print(f"Packet Timestamp: {message.packet_timestamp}")
    print(f"Event: {message.event}")

if __name__ == "__main__":
    test_referee_receiver()
