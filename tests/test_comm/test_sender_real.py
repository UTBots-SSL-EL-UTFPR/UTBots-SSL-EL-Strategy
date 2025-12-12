import time
from communication.sender.command_builder_real import CommandBuilderReal
from communication.sender.command_sender_real import CommandSenderReal
from communication.sender.messages import FW_ABS_MAX

ROBOT_ID = 1
ROBOT_IP = "10.219.168.172"   # ip do robo na rede
ROBOT_PORT = 4210             # porta em que o robo escuta

def main():
    sender = CommandSenderReal()
    sender.register_robot(ROBOT_ID, ROBOT_IP, ROBOT_PORT)

    builder = CommandBuilderReal(robot_id=ROBOT_ID)

    w = int(0.8 * FW_ABS_MAX)  
    spin_cmd = builder.build(+w, -w, +w, kicker=False)
    stop_cmd = builder.build(0, 0, 0, kicker=False)

    print("alternando: gira 5s e dps para 5s ")
    while True:
        print("Girando...")
        t_end = time.time() + 5
        while time.time() < t_end:
            sender.send(spin_cmd)
            time.sleep(0.05)  # 20 Hz

        print("Parado...")
        t_end = time.time() + 5
        while time.time() < t_end:
            sender.send(stop_cmd)
            time.sleep(0.05)

if __name__ == "__main__":
    main()
