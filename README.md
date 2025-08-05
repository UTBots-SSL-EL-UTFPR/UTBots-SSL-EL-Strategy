# UTBots-SSL-EL-Strategy

Repositório oficial da equipe UTBots para a competição RoboCup SSL-EL. Este projeto implementa os módulos de comunicação e estratégia entre o software da equipe e o simulador grSim, bem como o Game Controller e o SSL-Vision.

---

## 🚀 Requisitos

- Python 3.8+
- `protoc` (Protocol Buffers Compiler) ≥ 3.21
- Biblioteca Python `protobuf`

### 📆 Instalação dos requisitos no Ubuntu:

```bash
sudo apt update
sudo apt install python3-venv protobuf-compiler
```

### 🛠️ Configurando o ambiente virtual e instalando dependências:

```bash
# Crie o ambiente virtual
python3 -m venv venv

# Ative o ambiente
source venv/bin/activate

# Instale as dependências
pip install protobuf
```

Se preferir, instale a partir de um `requirements.txt` (se estiver no repositório):

```bash
pip install -r requirements.txt
```

---

## 📁 Estrutura do Projeto

```
UTBots-SSL-EL-Strategy/
├── communication/
│   ├── command_builder.py          # Monta pacotes de comando para robôs
│   ├── command_sender.py           # Envia comandos via UDP
│   ├── receiver.py                 # Base para recepção UDP
│   ├── vision_receiver.py          # Recebe pacotes do SSL-Vision
│   ├── generated/                  # Arquivos *.pb2.py gerados pelo protoc
│   └── protobuf/
│       └── proto/                  # Arquivos .proto (definição das mensagens)
├── test_sender.py                 # Script de teste para envio de comandos
├── build_and_fix_protos.py        # Recompila os arquivos .proto e corrige imports
└── README.md                      # Este arquivo
```

---

## 🔧 Gerando os arquivos `.pb2.py` (Protocol Buffers)

Todos os arquivos `.proto` estão localizados em:

```
communication/protobuf/proto/
```

Para compilar os arquivos `.proto` e gerar os equivalentes `.pb2.py`, rode:

```bash
python3 build_and_fix_protos.py
```

Este script:
- Recompila todos os arquivos `.proto`
- Gera os arquivos `.pb2.py` dentro de `communication/generated/`
- Corrige automaticamente os `import` para funcionar com o pacote Python `communication.generated`

**Nunca edite arquivos `.pb2.py` manualmente.**

---

## 🧪 Testando o envio de comandos

Com o grSim rodando, você pode testar o envio de comandos com:

```bash
python3 test_sender.py
```

O robô de ID 0 deve se mover para frente. Ajuste os parâmetros dentro do script para testar outras velocidades ou robôs.

---

## 🤝 Contribuição

1. Fork o repositório
2. Crie uma branch com sua feature: `git checkout -b minha-feature`
3. Commit suas alterações: `git commit -m 'feat: minha feature'`
4. Push para a branch remota: `git push origin minha-feature`
5. Abra um Pull Request

---

## 📌 Ambiente Virtual

- Sempre ative seu ambiente virtual antes de rodar os scripts:

```bash
source venv/bin/activate
```

- Se der erro de import de `ssl_vision_detection_pb2`, verifique se você recompilou os `.proto` corretamente com o script.

- Adicione a pasta `venv/` ao `.gitignore`. Não envie ambientes virtuais para o repositório!

## Obs

Para importar corretamente os arquivos, escreva no terminal:

    nano ~/.bashrc 

Vai abrir um editor de texto. Role até a última linha e adicione:

    export PYTHONPATH=$PYTHONPATH:/home/futebol_de_robos/FutebolDeRobos/UTBots-SSL-EL-Strategy

Para salvar as alterações, use:

    Ctrl + O → isso salva o arquivo
    Pressione Enter para confirmar
    Ctrl + X → isso fecha o nano

Por fim, aplique as alterações.

    source ~/.bashrc



---

Feito por 🦊 UTBots.

