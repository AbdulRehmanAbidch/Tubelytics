# run_etl.py

import subprocess, sys

SCRIPTS = [
  "etl/extract.py",
  "etl/checking.py",
  "etl/transform_and_load.py",
  "etl/load.py",
  "etl/scheduler.py"  
]

if __name__ == "__main__":
    for script in SCRIPTS:
        print(f" Running {script}")
        res = subprocess.run([sys.executable, script])
        if res.returncode != 0:
            print(f" {script} failed with code {res.returncode}")
            sys.exit(res.returncode)
    print(" All ETL steps completed!")
