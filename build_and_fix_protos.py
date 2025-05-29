import os
import subprocess

PROTO_SRC_DIR = "communication/protobuf/proto"
PY_OUT_DIR = "communication/generated"
PROTO_IMPORTS = [
    "ssl_vision_detection_pb2",
    "ssl_vision_geometry_pb2",
    "ssl_vision_wrapper_pb2"
]

def compile_protos():
    print("recompilando arquivos .proto...")

    for f in os.listdir(PY_OUT_DIR):             # remove arquivos gerados antigos
        if f.endswith("_pb2.py"):
            os.remove(os.path.join(PY_OUT_DIR, f))

    result = subprocess.run([                   # gera todos os arquivos .pb2.py
        "protoc",
        f"--proto_path={PROTO_SRC_DIR}",
        f"--python_out={PY_OUT_DIR}",
        *[os.path.join(PROTO_SRC_DIR, f) for f in os.listdir(PROTO_SRC_DIR) if f.endswith(".proto")]
    ])

    if result.returncode != 0:
        print("erro ao compilar os arquivos .proto")
        exit(1)

    print("compilação concluída!")

def fix_imports():                              #pqp finalmente corrigindo esses imports do jeito certo
    print("corrigindo imports nos arquivos .pb2.py...")
    for fname in os.listdir(PY_OUT_DIR):
        if fname.endswith("_pb2.py"):
            fpath = os.path.join(PY_OUT_DIR, fname)
            with open(fpath, "r", encoding="utf-8") as file:
                content = file.read()

            for mod in PROTO_IMPORTS:
                original = f"import {mod}"
                fixed = f"from communication.generated import {mod}"
                content = content.replace(original, fixed)

            with open(fpath, "w", encoding="utf-8") as file:
                file.write(content)
    print("imports corrigidos!")

if __name__ == "__main__":
    compile_protos()
    fix_imports()
