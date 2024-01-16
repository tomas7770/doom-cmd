import argparse
import configparser
import subprocess
import os

iwad_paths = []

engines = dict()

selected_engine = None
selected_iwad = None
custom_params = None

def init_config():
    cfg = configparser.ConfigParser()
    cfg.read("config.ini")
    if not "General" in cfg.sections():
        raise(ValueError("Missing config section \"General\""))
    if not cfg["General"].get("IWADPath"):
        raise(ValueError("Missing config key \"General/IWADPath\""))
    iwad_path_str = cfg["General"]["IWADPath"]
    for p in iwad_path_str.split(os.pathsep):
        iwad_paths.append(p)

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
    global selected_iwad
    global custom_params

    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", help = "source port to use")
    parser.add_argument("--iwad", help = "iwad to load")
    parser.add_argument("--params", help = "other parameters to pass to the source port")
    args = parser.parse_args()

    if not args.engine:
        raise(NotImplementedError("Default engine not implemented, must specify manually"))
    selected_engine = args.engine
    if not engines.get(selected_engine):
        raise(ValueError("Specified engine does not exist"))
    
    if args.iwad:
        selected_iwad = args.iwad

    if args.params:
        custom_params = args.params

def find_iwad(iwad_name):
    # First search for the file in iwad_paths
    for p in iwad_paths:
        files = os.listdir(p)
        for f in files:
            # Remove extension and see if it matches, case insensitive
            if iwad_name.lower() == os.path.splitext(f)[0].lower():
                return os.path.join(p, f)
    # If not found, interpret as a path, case sensitive
    if os.path.isfile(iwad_name) or os.path.isdir(iwad_name):
        return iwad_name
    raise(ValueError("Specified IWAD does not exist"))

def main():
    init_config()
    init_args()
    run_str = engines[selected_engine]["path"]

    if selected_iwad:
        run_str += " -iwad " + find_iwad(selected_iwad)

    if custom_params:
        run_str += " " + custom_params

    subprocess.run(run_str)

if __name__ == "__main__":
    main()
