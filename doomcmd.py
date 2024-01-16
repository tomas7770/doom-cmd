import argparse
import configparser
import subprocess

engines = dict()

selected_engine = None

def init_config():
    engines_cfg = configparser.ConfigParser()
    engines_cfg.read("engines.ini")
    for engine_name in engines_cfg.sections():
        if not engines_cfg[engine_name].get("Path"):
            raise(ValueError("Engine " + engine_name + " does not have a path!"))
        engine = dict()
        engine["path"] = engines_cfg[engine_name]["Path"]
        engines[engine_name] = engine

def init_args():
    global selected_engine
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", help = "source port to use")
    args = parser.parse_args()
    if not args.engine:
        raise(NotImplementedError("Default engine not implemented, must specify manually"))
    selected_engine = args.engine
    if not engines.get(selected_engine):
        raise(ValueError("Specified engine does not exist"))

def main():
    init_config()
    init_args()
    subprocess.run(engines[selected_engine]["path"])

if __name__ == "__main__":
    main()
