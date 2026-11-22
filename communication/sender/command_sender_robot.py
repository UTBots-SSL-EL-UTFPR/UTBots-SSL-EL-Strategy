"""Envia os comandos da estratégia para o robô físico, no protocolo do firmware (Firmware/esp32_slave).

Pacote UDP de 11 bytes (little-endian, empacotado), porta 4210:
    struct.pack("<BBhhhh?", message_id, robot_id, v1, v2, v3, v4, kicker)
    message_id 0..100 = comando (101/102 = ping/pong), v1..v3 = PWM de M1..M3 (-4095..4095),
    v4 não usado, kicker dispara um pulso na transição false -> true.

A estratégia continua montando o pacote do grSim; este sender lê os comandos de cada robô
mapeado em configuration.json ("Robot_real") e reenvia no formato do firmware:
    - velocidade das rodas (rad/s) * pwm_per_rad_s, saturada em max_pwm;
    - roda do grSim que alimenta cada motor: wheel_map (ex.: [1, 2, 3] -> M1, M2, M3);
    - chute (kick_ball, sem wheelsspeed) vira kicker=true por kick_ms.
Uma thread reenvia o último comando a send_hz. O firmware não tem timeout de comunicação, então
se a estratégia ficar timeout_ms sem mandar comando o robô recebe velocidade zero, e ao sair do
programa (atexit) também.
"""
import atexit
import socket
import struct
import threading
import time

from communication.generated import grSim_Packet_pb2

PACKET_FMT = "<BBhhhh?"  # message_id, robot_id, v1, v2, v3, v4, kicker (11 bytes)


class RobotLink:
    """Um robô físico: IP, id no firmware e o último comando recebido da estratégia."""

    def __init__(self, ip: str, firmware_id: int):
        self.address = (ip, 0)
        self.firmware_id = firmware_id
        self.pwm = [0, 0, 0]
        self.last_command = 0.0
        self.kick_until = 0.0
        self.last_kick = 0.0
        self.message_id = 0


class CommandSenderRobot:
    _instance = None

    def __new__(cls, *args, **kwargs):  # singleton, como o CommandSenderSim
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, settings: dict | None = None):
        if self._initialized:
            return
        settings = settings or {}
        self.port = int(settings.get("port", 4210))
        self.pwm_per_rad_s = float(settings.get("pwm_per_rad_s", 200))
        self.max_pwm = int(min(4095, settings.get("max_pwm", 4095)))
        self.wheel_map = list(settings.get("wheel_map", [1, 2, 3]))
        self.send_period = 1.0 / float(settings.get("send_hz", 20))
        self.timeout = float(settings.get("timeout_ms", 300)) / 1000.0
        self.kick_time = float(settings.get("kick_ms", 300)) / 1000.0
        self.kick_cooldown = float(settings.get("kick_cooldown_ms", 600)) / 1000.0

        self.robots: dict[int, RobotLink] = {}
        for strategy_id, robot in settings.get("robots", {}).items():
            link = RobotLink(robot["ip"], int(robot.get("id", 1)))
            link.address = (robot["ip"], self.port)
            self.robots[int(strategy_id)] = link

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.lock = threading.Lock()
        self._running = True
        self._initialized = True
        self._thread = threading.Thread(target=self._loop, name="RobotSender", daemon=True)
        self._thread.start()
        atexit.register(self.stop_all)

    # ---------- conversão grSim -> firmware ----------
    def wheel_to_pwm(self, rad_s: float) -> int:
        pwm = int(round(rad_s * self.pwm_per_rad_s))
        return max(-self.max_pwm, min(self.max_pwm, pwm))

    def send(self, packet_bytes: bytes):
        """Recebe o mesmo pacote serializado que vai para o grSim."""
        packet = grSim_Packet_pb2.grSim_Packet()  # type: ignore
        packet.ParseFromString(packet_bytes)
        now = time.time()
        with self.lock:
            for cmd in packet.commands.robot_commands:
                link = self.robots.get(cmd.id)
                if link is None:
                    continue
                if cmd.wheelsspeed:
                    wheels = [cmd.wheel1, cmd.wheel2, cmd.wheel3, cmd.wheel4]
                    link.pwm = [self.wheel_to_pwm(wheels[w - 1]) for w in self.wheel_map]
                    link.last_command = now
                elif cmd.kickspeedx > 0 and now - link.last_kick >= self.kick_cooldown:
                    link.pwm = [0, 0, 0]  # kick_ball manda rodas paradas
                    link.last_command = now
                    link.kick_until = now + self.kick_time
                    link.last_kick = now

    # ---------- envio periódico ----------
    def _packet(self, link: RobotLink, pwm: list[int], kick: bool) -> bytes:
        data = struct.pack(PACKET_FMT, link.message_id, link.firmware_id, pwm[0], pwm[1], pwm[2], 0, kick)
        link.message_id = (link.message_id + 1) % 101
        return data

    def _loop(self):
        while self._running:
            now = time.time()
            with self.lock:
                for link in self.robots.values():
                    pwm = link.pwm if now - link.last_command <= self.timeout else [0, 0, 0]
                    kick = now < link.kick_until
                    self.sock.sendto(self._packet(link, pwm, kick), link.address)
            time.sleep(self.send_period)

    def stop_all(self):
        """Para a thread e manda velocidade zero para todos os robôs."""
        self._running = False
        with self.lock:
            for link in self.robots.values():
                link.pwm = [0, 0, 0]
                link.kick_until = 0.0
                for _ in range(5):
                    self.sock.sendto(self._packet(link, [0, 0, 0], False), link.address)
                    time.sleep(0.02)
