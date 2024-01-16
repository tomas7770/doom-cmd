import argparse
import configparser
import subprocess

engines = dict()

selected_engine = None
custom_params = None

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
    global custom_params

    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", help = "source port to use")
    parser.add_argument("--params", help = "other parameters to pass to the source port")
    args = parser.parse_args()
    if not args.engine:
        raise(NotImplementedError("Default engine not implemented, must specify manually"))
    selected_engine = args.engine
    if not engines.get(selected_engine):
        raise(ValueError("Specified engine does not exist"))
    if args.params:
        custom_params = args.params

def main():
    init_config()
    init_args()
    run_str = engines[selected_engine]["path"]
    if custom_params:
        run_str += " " + custom_params
    subprocess.run(run_str)

if __name__ == "__main__":
    main()
