import pandas as pd
from subprocess import Popen
from pathlib import Path
import uuid
import os

class JFruit2:
    observed = str(Path("data", "observation", "obs_apple_optim_GS.csv"))
    
    def __init__(self):
        self.sim_id = str(uuid.uuid4())
        self.bin_file = str(Path("data", "bin", "jfruit2-1.3.6.jar"))
        self.cmd = f"java -jar -Djava.awt.headless=true {self.bin_file}" 
        self.inpath = str(Path("data", "input", "GS_Golden.csv"))
        self.properties = str(Path("data", "properties", "GS_apple_sim.properties"))
        self.outpath = str(Path("data", "out", self.sim_id))
        self.results = None

    @staticmethod
    def get_observed_data() -> pd.DataFrame:
        df = pd.read_csv(JFruit2.observed, sep=";")
        return df
        
    def load_properties(self, properties: str | None = None) -> dict:
        if properties is None:
            properties = self.properties
            
        props = {}
        with open(properties, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key_value = line.split('=', 1)
                    if len(key_value) == 2:
                        key, value = key_value
                        props[key.strip()] = value.strip()
        return props

    def save_properties(self, props: dict, outpath: str | None = None):
        if outpath is None:
            outpath = f"{self.outpath}.properties"
            
        with open(outpath, 'w') as f:
            for key, value in props.items():
                f.write(f"{key}={value}\n")
    def run(
        self, 
        begin: int = 2, 
        end: int = 159,
        inpath: str | None = None,
        properties: str | None = None,
        outpath: str | None = None
    ) -> None:
        if inpath is None:
            inpath = self.inpath
        if properties is None:
            properties = self.properties
        if outpath is None:
            outpath = f"{self.outpath}.csv"
            
        cmd = f"{self.cmd} -b {begin} -e {end} -p {properties} -i {inpath} -o {outpath}"
        Popen(cmd, shell=True).wait()

        self.results = pd.read_csv(outpath, sep=";")
        os.unlink(outpath)
        
        if properties.endswith(f"{self.sim_id}.properties"):
            os.unlink(properties)
        