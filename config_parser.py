import json, argparse, requests
from bs4 import BeautifulSoup   

# current_config - файл .config нашей сборки, 
# perfect_config - файл, полученный hardening_checker'ом в виде json 
parser = argparse.ArgumentParser()
parser.add_argument("current_config_txt")
parser.add_argument("perfect_config_json")
args = parser.parse_args()

# читаем json
perfect_config_lst = []
with open(f"{args.perfect_config_json}", "r") as perfect_config_json:
    perfect_config_lst = json.load(perfect_config_json)

perfect_config_dct = {}
for perf_cnf in perfect_config_lst:
    perfect_config_dct[perf_cnf["option_name"]] = perf_cnf["desired_val"]

# далее надо прочитать current_config.txt
current_config_dct = {}
with open(f"{args.current_config_txt}", "r") as current_config_txt:
    while(line := current_config_txt.readline()):
        if line.find('=', 0) != -1:
            lst_args = line.split('=')
            current_config_dct[lst_args[0]] = lst_args[1][:-1]
        
        elif line.find("is not set", 0) != -1:
            ins_pos = line.find("is not set", 0)
            config_name = line[2:ins_pos-1]
            current_config_dct[config_name] = "is not set"

# запись названий исправленных конфигов в список
fixed_cnfname_lst = []
for perf_cnf_name in perfect_config_dct:
    if perf_cnf_name in current_config_dct:
        if perfect_config_dct[perf_cnf_name] != current_config_dct[perf_cnf_name]:
            fixed_cnfname_lst.append(perf_cnf_name)

# перебор и вывод в текстовый файл
with open(f"output_config.txt", "w") as output_config:
    output_config.write("{:60}".format("config name") + "|" + "true value" + "|" + "old value  \n")
    output_config.write("{:-^82}".format("") + "\n")
    for cnfname in fixed_cnfname_lst:
        output_config.write("{:60}".format(cnfname) + "|" + "{:10}".format(perfect_config_dct[cnfname]) + "|" + "{:10}".format(current_config_dct[cnfname]) + "\n")

# парсим инфу о конфигах в html и 
# отбираем аппаратно-независимые конфиги
not_arch_cnf_lst = []
id = 0
with open(f"config_info.html", "w") as config_info:
    for cnfname in fixed_cnfname_lst:
        url = f"https://cateee.net/lkddb/web-lkddb/{cnfname[7:]}.html"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        header = str(soup.find("h1"))

        text = str(soup)
        start_pos = text.find("<h2>General informations</h2>")
        end_pos = text.find("<h2>Hardware</h2>")
        output_text = text[start_pos:end_pos]

        config_info.write(header + output_text)

        # отбираем конфиги
        if (output_text.find("riscv") == -1 and output_text.find("arm64") == -1 
        and output_text.find("/arm") == -1 and header.find("ARCH") == -1):
            id += 1
            not_arch_cnf_lst.append({"id": id, "config": cnfname, "true_value": perfect_config_dct[cnfname], "old_value": current_config_dct[cnfname]})
    
print("Сформирован конфигурационный файл: config_info.html")


# записываем в json аппаратно независимые конфиги и выводим их количество в консоль
with open(f"notarch_output_config.json", "w") as notarch_output_config:
    json.dump(not_arch_cnf_lst, notarch_output_config)

with open(f"notarch_output_count.txt", "w") as notarch_output_count:
    notarch_output_count.write("Arch-independent configs count:" + str(len(not_arch_cnf_lst)))

print("Сформирован файл с списком конфигов, рекомендуемых к изменению: notarch_output_config.json")
