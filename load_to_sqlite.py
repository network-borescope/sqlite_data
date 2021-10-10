import sqlite_manager
import datetime
import pytomlpp
import os
import sys

def get_pop_id(pop:str, pop_list:list):
    for i in range(len(pop_list)):
        if pop_list[i] == pop:
            return i+1

args = sys.argv[1:]
if len(args) != 2:
    print("python load_to_sqlite.py <toml file> <path to data files>")
    sys.exit(1)

toml, dir = args

config = pytomlpp.load(toml)


ID = ""
if "perfsonar" in config["config"]["data_source"]:
    src, dst = dir.split("\\")[-2:]
    src_id = get_pop_id(src, config["config"]["pop_id"])
    dst_id = get_pop_id(dst, config["config"]["pop_id"])
    ID = str(src_id) + str(dst_id) + str(config["config"]["id_sufix"])

else: ID = config["config"]["id"]


#sys.exit(0)
SEP = config["config"]["sep"]


prefix = os.getcwd()
files_path = prefix + "\\" + dir
files = os.listdir(files_path)

#print(files)

#sys.exit(0)
conn = sqlite_manager.create_connection("db_timeseries.db")
# TSX table
for fname in files:
    #print(fname)
    with open(files_path + "\\" + fname, "rt") as file:
        records = []
        count = 0

        last_epoch = 0
        buf = ''
        epoch = 0

        for linenl in file:
            line = linenl.strip()
            items = line.split(SEP)
            dt = datetime.datetime.strptime(items[0], '%Y-%m-%d %H:%M:%S')
            epoch = int((dt - datetime.datetime(1970,1,1)).total_seconds())

            if epoch == last_epoch or buf == '':
                buf = buf + '|' + line
            else:
                sqlite_manager.insert_row_tsx(conn, ID, epoch, buf)
                buf = ''
            last_epoch = epoch

        if buf != '':
            sqlite_manager.insert_row_tsx(conn, ID, epoch, buf)

# KV table
order = ""
for item in config["v_1"]["order"]:
    order += "|" + item
sqlite_manager.insert_row_kv(conn, ID, "ordem", txt=order)
sqlite_manager.insert_row_kv(conn, ID, "separador", txt=SEP)

if len(config["v_1"]["cols"]) != len(config["v_1"]["order"]):
    print("ERRO: len(order) != len(v1.cols)")
    sys.exit(1)

for i in range(len(config["v_1"]["cols"])):
    name = config["v_1"]["order"][i]
    type = config["v_1"]["cols"][i]["type"]
    sqlite_manager.insert_row_kv(conn, ID, name, type)
#    print(name, type)

# for col in config["v_1"]["cols"]:
#     sqlite_manager.insert_row_kv(conn, ID, col["name"], txt=col["type"])
#     print(col)

conn.close()
print("Done")