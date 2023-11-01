# ControleSg
> Controla o Aplicacoes Windows por interface web

## Aviso
    - Tive que censurar muita parte do codigo, pode causar alguns conflitos, mas nada muito dificil de se resolver
    - Caso queira executar o script no windows, você vai precisar mudar alguns metodos relacionado a terminar o processo, nada muito dificil tambem


## Dependencias
```sh
Python
 - psutil
 - flask
 - mysql-connector-python
 - paramiko
 - pythonping
```

## Instalacao
Linux/Windows:
```sh
flask:
    - pip install flask  
psutil
    - pip install psutil
    - py -m pip install psutil
mysql-connect
    - pip install mysql-connector-python
paramiko
    - pip install paramiko
pythonping
    - pip install pythonping
```

## Uso:
    - Comando: python3 api.py
    - Interface web : http://127.0.0.1:5000