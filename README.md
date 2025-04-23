# UTBots SSL-EL Strategy

## 📦 Dependências

Antes de rodar o projeto, é necessário instalar o compilador do Protocol Buffers:

```bash
sudo apt update
sudo apt install protobuf-compiler
protoc --version
```

Se tudo estiver correto, será exibida a versão do `protoc` instalada (de preferência `libprotoc 3.21.12`).

---

## ⚙️ Como configurar o projeto

### 1. Gerar os arquivos Python a partir dos `.proto`

Os arquivos `.proto` definem as estruturas de comunicação com o SSL-Vision, Game Controller e grSim. Para transformá-los em arquivos `.py` que podem ser usados no Python:

#### Método direto (manual):

Dentro da pasta `communication/protobuf`, execute:

```bash
protoc --proto_path=./proto --python_out=. ./proto/*.proto
```

Isso irá gerar os arquivos `*_pb2.py` diretamente dentro de `communication/protobuf`.

#### Método automatizado (recomendado):

Execute o script `compile_protos.py` na raiz do projeto:

```bash
python3 compile_protos.py
```

Esse script:
- Cria a pasta `communication/generated/` (se ainda não existir)
- Garante que haja um `__init__.py` para suportar importações
- Remove arquivos `.py` antigos gerados automaticamente
- Compila todos os `.proto` da pasta `communication/protobuf/proto`

Você deve rodar esse script **sempre que adicionar ou modificar** qualquer arquivo `.proto`.

---

## 🧠 Estrutura recomendada do projeto

(⚠️ *Em construção. Será adicionado um diagrama visual.*)

```
UTBots-SSL-EL-Strategy/
├── communication/
│   ├── receiver.py
│   ├── vision_receiver.py
│   ├── referee_receiver.py
│   ├── command_sender.py
│   ├── generated/                  ← arquivos .py gerados pelo protoc
│   │   ├── __init__.py
│   │   └── *_pb2.py
│   └── protobuf/
│       └── proto/                  ← arquivos .proto
├── strategy/
│   └── strategy.py
├── main.py
├── compile_protos.py              ← script para gerar os .pb2.py
└── README.md
```

---

## ✅ TODO

- [ ] Adicionar diagrama do projeto (pastas e classes)
- [ ] Documentar a estrutura dos módulos `datatypes/` e `strategy/`
- [ ] Especificar pontos de entrada e exemplos de execução
