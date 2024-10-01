import ctypes
import json
import sys
import time
from configparser import ConfigParser

def generate_log(funcName: str, usrRet: int) -> str:
    ret = f"""
Local Time: {time.asctime()}
Run {funcName} from config.ini
User Choosed: {usrRet}
"""
    return ret

logName = time.strftime("%a-%b-%d-%H-%M-%S-%Y", time.localtime()) + ".log"

try:
    ErrorReportMain = ctypes.CDLL("./ErrorReportMain.dll")
except OSError:
    print("ErrorReportMain.dll not found.")
    with open(f"./{logName}", "w") as f:
        f.write("Run failed, because ErrorReportMain.dll not found.")
    sys.exit(1)

conf = ConfigParser()
if conf.read("./config.ini") == []:
    print("config.ini invalid or not exist.", file=sys.stderr)
    sys.exit(1)
    
main_param = {
    "MEMORY_ERROR": {
        "ErrorProgram": "svchost.exe",
        "Operate": "0x00000000",
        "Address": "0x00000000",
        "CannotBe": "read",
    },
    "DLL_MISSING_ERROR": {
        "ErrorProgram": "svchost.exe",
        "MissingDll": "coredpus.dll",
    },
    "EXE_ERROR": {
        "ErrorProgram": "svchost.exe",
        "ErrorName": "unknown software exception",
        "ErrorCode": "0x00000000",
        "Address": "0x0000000000000000",
    },
}

with open(f"./{logName}", "w") as f:
    f.write(f"Beginning at {time.asctime()}\n\n")

try:
    i = 1
    while True:
        cmd_id = "Command" + str(i)
        i += 1
        cmd_str = conf[cmd_id]["Command"]
        cmd_par = []
        for k in main_param[cmd_str].keys():
            try:
                cmd_par.append(conf[cmd_id][k])
            except KeyError:
                cmd_par.append(main_param[cmd_str][k])
        usrRet = None
        exec(f"usrRet = ErrorReportMain.{cmd_str}(*cmd_par)")
        with open(f"./{logName}", "a") as f:
            f.write(generate_log(cmd_str, usrRet))
except KeyError:
    pass