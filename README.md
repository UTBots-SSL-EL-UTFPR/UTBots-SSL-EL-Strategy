Dependencias

/--------------------------------------------------------/
Como configurar o Projeto

# instalação dos arquivos protobuf

1.  sudo apt update
    sudo apt install protobuf-compiler
    protoc --version
    se tudo estiver correto, aparecerá a sua versão instalada

2.  após isso, dentro da pasta communication/protobuf execute o seguinte comando

    protoc --proto_path=./proto --python_out=. ./proto/\*.proto

    se tudo der certo, varios arquivos .py aparecerão na pasta communication/protobuf

# TODO

    - diagrama do projeto (pastas e classes)
