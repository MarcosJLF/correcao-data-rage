import json 
import os
import time
import subprocess
import sys
import re

par = "False"
if len(sys.argv) > 1:
    par = sys.argv[1].upper()

if par == "CLEAR":
    os.system("cls")

config = {
    "ip": None,
    "host": None,
    "time":None,
    "run": None
}

files = {
        "down": ["down-1.txt", "down-2.txt", "down-3.txt"],
        "up": ["up-1.txt", "up-2.txt", "up-3.txt"],
        "netsh": ["netsh-1.txt","netsh-2.txt","netsh-3.txt" ]
}

def path_json():

    way = "./config.json"

    if not os.path.exists(way):
        raise FileNotFoundError (f" config not found {way}")
    with open(way, "r", encoding="utf-8") as file:
        data = json.load(file)

    config["ip"] = data.get("ip", "10.0.0.2")
    config["host"] = data.get("host", "50.0.0.10")
    config["time"] = int(data.get("time", 30))
    config["run"] = int(data.get("run", 3))

    return config

def write_json(ip, host, time, vezes):

    data = {
    "ip": ip,
    "host": host,
    "time":time,
    "run": vezes
    }

    path_json = './config.json'

    with open(path_json, "w") as file:
        json.dump(data, file, indent=4)

path_json()

command = {
    "down": (f"iperf3 -c {config['host']} -B {config['ip']} -t{config['time']}"),
    "up": (f"iperf3 -c {config['host']} -B {config['ip']} -t{config['time']} -R"),
    "netsh": ("netsh wlan show interface")
}

def run_script(command):

    print(command)

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        return result.stdout
    
    except Exception as e:
        print(f"Error: {e}")

def save_to_file(filename, content):

    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)

"""
Meu programa até está, colocando as configurações, como lendo o json e reformatando as configurações. Está executando o comando e escrevendo em um arquivo
"""

data = {
    "up": [],
    "down": [],
    "range": {
        "sinal" : [],
        "TR": [],
        "TT": []
    }
}

def read_file(opetion, filename):

    if not os.path.exists(filename):
        print(f"not found: {filename}")
        return None

    
    if opetion == "netsh":
        
        padroes = {
            "Taxa de recepção": r"Taxa de recep[\s\S]*?\(Mbps\)\s*:\s*(\d+)",
            "Taxa de transmissão": r"Taxa de transmiss[\s\S]*?\(Mbps\)\s*:\s*(\d+)",
            "Sinal": r"Sinal\s*:\s*(\d+)%"
        }
        try:

            result = {}
            with open(filename, "r", encoding="utf-8") as f:
                conteudo = f.read()

                for c, p in padroes.items():
                    match = re.search(p, conteudo)
                    if match:
                        result[c] = match.group(1)
            
            data['range']['TT'].append(result['Taxa de transmissão'])
            data['range']['TR'].append(result["Taxa de recepção"])
            data['range']['sinal'].append(result["Sinal"])
        
        except Exception as e:
            print(f"Erro {e}")

    elif opetion == "down":

        try:

            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()

            pattern = r"\[\s*\d+\]\s+0.00-30.00\s+sec\s+[\d\.]+\s+[GM]Bytes\s+([\d\.]+)\s+Mbits/sec\s+receiver"

            match = re.search(pattern, content)
            if match:
                bandwidth = float(match.group(1))
                data["down"].append(bandwidth)
            else:
                print("Nenhum valor final de Bandwidth encontrado.")

        except Exception as e:
            print(f"Erro: {e}")



    
    elif opetion == "up":

        try:

            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()

            pattern = r"\[\s*\d+\]\s+0.00-30.00\s+sec\s+[\d\.]+\s+[GM]Bytes\s+([\d\.]+)\s+Mbits/sec\s+receiver"

            match = re.search(pattern, content)
            if match:
                bandwidth = float(match.group(1))
                data["up"].append(bandwidth)
            else:
                print("Nenhum valor final de Bandwidth encontrado.")

        except Exception as e:
            print(f"Erro: {e}")
        
    return data

"""
Até aqui ele está, lendo os arquivos que conterá os dados e armazenando em um dic
"""

def set_data():
    files = {
        "down": ["down-1.txt", "down-2.txt", "down-3.txt"],
        "up": ["up-1.txt", "up-2.txt", "up-3.txt"],
        "netsh": ["netsh-1.txt","netsh-2.txt","netsh-3.txt" ]
    }

    for category, file_list in files.items():
        for file_name in file_list:
            read_file(category, file_name)

def format_table(data):
    set_data()

    header = "+---------+----+------+----------------------------------------------------+"
    title = "| Rodadas | Up    |  Down |                     Data                        |"
    
    num_rodadas = len(data["up"])
    
    rows = []
    for i in range(num_rodadas):
        up = data["up"][i]
        down = data["down"][i]
        sinal = data["range"]["sinal"][i]
        tr = data["range"]["TR"][i]
        tt = data["range"]["TT"][i]
        
        row = f"|    {i+1}    | {up}     |  {down}     | 'Rec.': '{tr}', 'Tra.': '{tt}', 'S': '{sinal}' |"
        rows.append(row)
    
    table = f"\nTabela de Resultados:\n{header}\n{title}\n{header}\n" + "\n".join(rows) + f"\n{header}"
    

    with open("table.txt", "w", encoding= "utf-8") as f:
        f.write(table)

    return table


def main():

    # files = {
    #     "down": ["down-0.txt", "down-1.txt", "down-2.txt"],
    #     "up": ["up-0.txt", "up-1.txt", "up-2.txt"],
    #     "netsh": ["netsh-0.txt", "netsh-1.txt", "netsh-2.txt"]
    # }

    run = config["run"]

    c = 1

    for i in range(0, 3):
        print(f"Executando rodada {i+1}...")

        print("Executando teste de download...")
        down_output = run_script(command["down"] + f" --logfile down-{i + c}.txt")
        time.sleep(31)  

        print("Executando teste de upload...")
        up_output = run_script(command["up"] + f" --logfile up-{i + c}.txt")
        time.sleep(31)  

        print("Executando análise de rede...")
        netsh_output = run_script(command["netsh"])
        save_to_file(files["netsh"][i], netsh_output)
        time.sleep(2)  

        c = 0

    set_data()

    tabela = format_table(data)
    print(tabela)
    print("Tabela de resultados salva em 'table.txt'.")


c = {
    "ip":None,
    "host":None,
    "time": 30,
    "run": 3
}

def read(opetion=None, number=3):

    # files = {
    #     "down": ["down-1.txt","down-2.txt","down-3.txt"],
    #     "up": ["up-1.txt","up-2.txt","up-3.txt"],
    #     "netsh": ["netsh-1.txt","netsh-2.txt","netsh-3.txt"]
    # }

    ope = opetion.upper()

    if ope is None:
        print("Escolha uma opção\n Down\n Up\n Netsh")

    if ope == "DOWN":

        for i in range(0,3):

            with open(files["down"][i], "r", encoding="utf-8") as f:
                result = f.read()
                print(result)
    
    if ope == "UP":

        for i in range(0,3):

            with open(files["up"][i], "r", encoding="utf-8") as f:
                result = f.read()
                print(result)
    
    if ope == "NETSH":

        for i in range(0,3):

            with open(files["netsh"][i], "r", encoding="utf-8") as f:
                result = f.read()
                print(result)


def show_help():
    help_text = """
Uso: python main.py [OPÇÃO] [ARGUMENTOS]

Opções disponíveis:
  INFO, -I                             Exibe a configuração atual do setup.
  CONFIG, -C <IP> <HOST> <TIME> <RUN>  Define a configuração e salva no JSON.
  RUN, -R                              Executa o script principal.
  LOG, -L   <file>                     Mostra todos os logs dos arquivos
  DELETE, -D                           Deleta todos os arquivos de log.

Exemplos:
  python main.py INFO
  python main.py CONFIG 192.168.1.1 myserver.com 30 3
  python main.py RUN
  python main.py LOG down
  python main.py DELETE
"""
    print(help_text)

def delete_files():

    for category, file_list in files.items():
        for file in file_list:
            if os.path.exists(file):
                os.remove(file)
                print(f"Arquivo removido: {file}")
            else:
                print(f"Arquivo não encontrado: {file}")

def parse_args():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    par = sys.argv[1].upper()
    comandos = {
        "INFO": handle_info,
        "-I": handle_info,
        "CONFIG": handle_config,
        "-C": handle_config,
        "RUN": handle_run,
        "-R": handle_run,
        "LOG": handle_log,
        "-L": handle_log,
        "-D": delete_files,
        "DELETE": delete_files
    }

    if par in comandos:
        comandos[par]()
    else:
        print("Erro: Comando desconhecido.")
        show_help()
        sys.exit(1)

def handle_info():
    config = path_json()
    print(f"Seu setup está configurado da seguinte forma:\n"
          f"IP: {config['ip']}\n"
          f"HOST: {config['host']}\n"
          f"TIME: {config['time']}\n"
          f"RUN: {config['run']}")

def handle_config():
    if len(sys.argv) != 6:
        print("Erro: Argumentos insuficientes para CONFIG. Use:")
        print("python main.py CONFIG <IP> <HOST> <TIME> <RUN>")
        sys.exit(1)
    
    ip, host, time, run = sys.argv[2:6]
    write_json(ip, host, time, run)

def handle_run():
    main()

def handle_log():
    if len(sys.argv) < 3:
        print("Necessário passar um nome de arquivo. Opções: [up, down, netsh]")
        return
    
    result = sys.argv[2].upper()
    opcoes_validas = {"DOWN": "down", "UP": "UP", "NETSH": "NETSH"}
    
    if result in opcoes_validas:
        print(result)
        read(opcoes_validas[result])
    else:
        print("Escolha uma opção válida:\nOpções: [down, up, netsh]")

a = format_table(data)
print(a)