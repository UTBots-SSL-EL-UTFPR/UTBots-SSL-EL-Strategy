from communication.referee_receiver import RefereeReceiver

def test_referee_receiver():
    receiver = RefereeReceiver(interface_ip = "172.17.0.1") # Passa o Ip de interface do docker
    message = receiver.receive_raw() #Chama o método do Reciver que recebe os dados brutos

    #Comando no terminal para estabelecer a conexão do docker com o localhost: sudo docker run --network host robocupssl/ssl-game-controller -address :8081

if __name__ == "__main__":
    test_referee_receiver()
