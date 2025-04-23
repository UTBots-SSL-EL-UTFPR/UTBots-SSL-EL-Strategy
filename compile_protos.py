import os
import sys
import shutil
from pathlib import Path
import subprocess

# Diretório base do projeto (assumindo que este script está no root do projeto)
base_dir = Path(__file__).resolve().parent  # ajuste se o script estiver em subpasta
proto_dir = base_dir / "communication" / "protobuf" / "proto" # pasta onde estão os .proto
out_dir = base_dir / "communication" / "generated"  # pasta de saída desejada

# Garantir que o diretório de saída existe
out_dir.mkdir(parents=True, exist_ok=True)

# Encontrar caminho do protoc
protoc_path = os.environ.get("PROTOC") or shutil.which("protoc")
if not protoc_path:
    sys.stderr.write("Erro: protoc não encontrado. Por favor instale o Protobuf ou defina a variável PROTOC.\n")
    sys.exit(1)

# Obter lista de arquivos .proto para compilar
proto_files = list(proto_dir.rglob("*.proto"))
if not proto_files:
    sys.stderr.write(f"Nenhum arquivo .proto encontrado em {proto_dir}\n")
    sys.exit(0)

# Compilar cada arquivo .proto
for proto_file in proto_files:
    proto_file = proto_file.resolve()  # caminho absoluto do arquivo .proto
    command = [
        protoc_path,
        f"-I={proto_dir.resolve()}",
        f"--python_out={out_dir.resolve()}",
        str(proto_file)
    ]
    result = subprocess.run(command)
    if result.returncode != 0:
        sys.stderr.write(f"Erro ao compilar {proto_file.name}\n")
        sys.exit(result.returncode)

print("Compilação Protobuf concluída com sucesso.")
