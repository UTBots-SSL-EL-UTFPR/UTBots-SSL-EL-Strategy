"""Testes do CommandSenderRobot (protocolo do firmware) sem robô: escuta UDP em 127.0.0.1.

Rodar da raiz do repositório:  python -m pytest tests/test_comm/test_robot_sender.py -v
"""
import socket
import struct
import time

import pytest

from communication.generated import grSim_Packet_pb2
from communication.sender.command_sender_robot import CommandSenderRobot

FMT = "<BBhhhh?"


@pytest.fixture
def robo():
    """Sender novo apontando para uma porta local; devolve (sender, socket que faz o papel do ESP)."""
    esp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    esp.bind(("127.0.0.1", 0))
    esp.settimeout(1.0)
    CommandSenderRobot._instance = None
    sender = CommandSenderRobot({
        "port": esp.getsockname()[1],
        "robots": {"1": {"ip": "127.0.0.1", "id": 1}},
        "wheel_map": [1, 2, 3], "pwm_per_rad_s": 200, "max_pwm": 4095,
        "send_hz": 50, "timeout_ms": 300, "kick_ms": 300, "kick_cooldown_ms": 600,
    })
    yield sender, esp
    sender.stop_all()
    CommandSenderRobot._instance = None
    esp.close()


def pacote_grsim(robot_id, wheels=None, kick=0.0):
    p = grSim_Packet_pb2.grSim_Packet()  # type: ignore
    p.commands.timestamp = 0
    p.commands.isteamyellow = False
    c = p.commands.robot_commands.add()
    c.id, c.kickspeedx, c.kickspeedz = robot_id, kick, 0
    c.veltangent = c.velnormal = c.velangular = 0
    c.spinner = False
    c.wheelsspeed = wheels is not None
    c.wheel1, c.wheel2, c.wheel3, c.wheel4 = wheels or (0, 0, 0, 0)
    return p.SerializeToString()


def recebe(esp, segundos):
    fim, pacotes = time.time() + segundos, []
    while time.time() < fim:
        try:
            data = esp.recv(64)
        except socket.timeout:
            break
        assert len(data) == 11
        pacotes.append(struct.unpack(FMT, data))
    return pacotes


def test_velocidade_vira_pwm_no_formato_do_firmware(robo):
    sender, esp = robo
    sender.send(pacote_grsim(1, wheels=(10, -5, 2.5, 99)))
    msg_id, robot_id, v1, v2, v3, v4, kick = recebe(esp, 0.1)[-1]
    assert robot_id == 1 and 0 <= msg_id <= 100
    assert (v1, v2, v3, v4, kick) == (2000, -1000, 500, 0, False)


def test_satura_em_max_pwm(robo):
    sender, esp = robo
    sender.send(pacote_grsim(1, wheels=(120, -120, 0, 0)))
    assert recebe(esp, 0.1)[-1][2:4] == (4095, -4095)


def test_ignora_robo_nao_mapeado(robo):
    sender, esp = robo
    sender.send(pacote_grsim(2, wheels=(10, 10, 10, 10)))
    assert all(p[2:5] == (0, 0, 0) for p in recebe(esp, 0.1))


def test_para_sozinho_sem_comando(robo):
    sender, esp = robo
    sender.send(pacote_grsim(1, wheels=(10, 10, 10, 0)))
    assert recebe(esp, 0.1)[-1][2:5] == (2000, 2000, 2000)
    time.sleep(0.4)  # > timeout_ms
    assert recebe(esp, 0.1)[-1][2:5] == (0, 0, 0)


def test_chute_vira_pulso_de_kicker_com_intervalo(robo):
    sender, esp = robo
    sender.send(pacote_grsim(1, kick=3.0))
    pacotes = recebe(esp, 0.45)
    ligados = [p for p in pacotes if p[6]]
    assert ligados and pacotes[-1][6] is False  # liga e depois desliga
    assert 0.2 <= len(ligados) / 50 <= 0.4      # ~300 ms a 50 Hz
    sender.send(pacote_grsim(1, kick=3.0))      # dentro do cooldown: ignorado
    assert not any(p[6] for p in recebe(esp, 0.3))


def test_stop_all_manda_zero(robo):
    sender, esp = robo
    sender.send(pacote_grsim(1, wheels=(10, 10, 10, 0)))
    recebe(esp, 0.1)
    sender.stop_all()
    assert recebe(esp, 0.3)[-1][2:5] == (0, 0, 0)
