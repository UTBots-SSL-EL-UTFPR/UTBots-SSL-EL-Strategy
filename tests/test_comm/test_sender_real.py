# teste_command_real.py
import time
from communication.sender.command_builder_real import CommandBuilderReal
from communication.sender.command_sender_real import CommandSenderReal
from communication.sender.messages import FW_ABS_MAX

ROBOT_ID = 1
ROBOT_IP = "10.219.168.172"   # IP do robô
ROBOT_PORT = 4210             # Porta em que o robô escuta

def main():
    sender = CommandSenderReal()
    sender.register_robot(ROBOT_ID, ROBOT_IP, ROBOT_PORT)

    builder = CommandBuilderReal(robot_id=ROBOT_ID)

    # Velocidade para "rodar" (ajuste conforme o sentido desejado)
    w = int(0.8 * FW_ABS_MAX)   # 50% do PWM máximo (≈ 2047 em 12-bit)
    spin_cmd = builder.build(+w, -w, +w, kicker=False)
    stop_cmd = builder.build(0, 0, 0, kicker=False)

    print("Alternando: gira 5 s  →  para 5 s  (Ctrl+C para sair)")
    while True:
        # 5 s girando
        print("Girando...")
        t_end = time.time() + 5
        while time.time() < t_end:
            sender.send(spin_cmd)
            time.sleep(0.05)  # 20 Hz

        # 5 s parado
        print("Parado...")
        t_end = time.time() + 5
        while time.time() < t_end:
            sender.send(stop_cmd)
            time.sleep(0.05)

if __name__ == "__main__":
    main()
