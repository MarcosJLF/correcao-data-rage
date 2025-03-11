import re
import os

data = {
    "up": [],
    "down": [],
    "range": {
        "sinal": [],
        "TR": [],
        "TT": []
    }
}

def extract_final_bandwidth(filename):
    if not os.path.exists(filename):
        print(f"Arquivo não encontrado: {filename}")
        return

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
        print(f"Erro ao processar o arquivo: {e}")

# Exemplo de uso

for i in range(1, 4):
    extract_final_bandwidth(f"up-{i}.txt")

print(data)