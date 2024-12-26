import subprocess

for i in range(100):
    subprocess.run(["python", "../src/emit_log_direct.py"])
    print(subprocess.check_output(["python", "../src/emit_log_direct.py"]))