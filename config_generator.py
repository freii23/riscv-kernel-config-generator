import json, argparse

# считываем список конфигов для изменения, старый конфиг,
# срез списка конфигов, которые хотим менять
parser = argparse.ArgumentParser()
parser.add_argument("notarch_output_config_json")
parser.add_argument("current_config_txt")
parser.add_argument("start_pos")
parser.add_argument("end_pos")
args = parser.parse_args()

# читаем json
new_config_lst = []
with open(f"{args.notarch_output_config_json}", "r") as new_config_json:
    new_config_lst = json.load(new_config_json)

# составляем словарь конфигов из диапазона,
# указанного пользователем
new_config_dct = {}
for new_cnf in new_config_lst:
    if int(args.start_pos) <= new_cnf["id"] <= int(args.end_pos):
        new_config_dct[new_cnf["config"]] = new_cnf["true_value"]

# читаем старый конфиг, генерируем новый
new_config_str = ""
with open(f"{args.current_config_txt}", "r") as current_config_txt:
    while(line := current_config_txt.readline()):
        eql_pos = line.find('=', 0)
        ins_pos = line.find("is not set", 0)
        if eql_pos != -1:
            cur_cnfname = line.split('=')[0]
            if cur_cnfname in new_config_dct:
                if new_config_dct[cur_cnfname] == "is not set":
                    new_config_str += f"# {cur_cnfname} is not set" + "\n"
                else:
                    new_config_str += f"{cur_cnfname}={new_config_dct[cur_cnfname]}" + "\n"
            else:
                new_config_str += line            

        elif ins_pos != -1:
            cur_cnfname = line[2:ins_pos-1]
            if cur_cnfname in new_config_dct:
                new_config_str += f"{cur_cnfname}={new_config_dct[cur_cnfname]}" + "\n"
            else:
                new_config_str += line            

        else:
            new_config_str += line 

# записываем новый конфиг в файл
with open(f"new_config.txt", "w") as new_config_txt:
    new_config_txt.write(new_config_str)
    print("Сформирован конфигурационный файл: new_config.txt")
