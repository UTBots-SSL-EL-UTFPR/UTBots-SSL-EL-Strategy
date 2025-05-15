from communication.referee_receiver import RefereeReceiver
from communication.parsers.referee_parser import RefereeParser

def test_referee_receiver():
    receiver = RefereeReceiver(interface_ip = "172.17.0.1") # Passa o Ip de interface do docker
    message = receiver.receive_raw() #Chama o método do Reciver que recebe os dados brutos

    #Comando no terminal para estabelecer a conexão do docker com o localhost: sudo docker run --network host robocupssl/ssl-game-controller -address :8081

    if message:
        parser = RefereeParser()
        parsed = parser.parse(message)

        print("=== Mensagem Recebida ===")
        print(f"Stage: {parsed.stage}")
        print(f"Command: {parsed.command}")
        print(f"Command Counter: {parsed.command_counter}")
        print(f"Packet Timestamp: {parsed.packet_timestamp}")
        for event in parsed.game_events:
            print(f"Game Event: {event}")
    else:
        print("Nenhum dado recebido.")

if __name__ == "__main__":
    test_referee_receiver()
