import argparse
import configparser
import subprocess
import os

iwad_paths = []
pwad_paths = []

engines = dict()

selected_engine = None
selected_iwad = None
selected_iwad_fp = False
selected_pwads = []
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

    if not cfg["General"].get("PWADPath"):
        raise(ValueError("Missing config key \"General/PWADPath\""))
    pwad_path_str = cfg["General"]["PWADPath"]
    for p in pwad_path_str.split(os.pathsep):
        pwad_paths.append(p)


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
    global selected_iwad_fp
    global selected_pwads
    global custom_params

    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", help = "source port to use")
    parser.add_argument("--iwad", help = "iwad to load from IWADPath")
    parser.add_argument("--pwad", help = "pwad(s) to load from PWADPath", nargs="+")
    parser.add_argument("--iwadfp", help = "iwad to load from a full path")
    parser.add_argument("--pwadfp", help = "pwad(s) to load from a full path", nargs="+")
    parser.add_argument("--params", help = "other parameters to pass to the source port")
    args = parser.parse_args()

    if not args.engine:
        raise(NotImplementedError("Default engine not implemented, must specify manually"))
    selected_engine = args.engine
    if not engines.get(selected_engine):
        raise(ValueError("Specified engine does not exist"))
    
    if args.iwad and args.iwadfp:
        raise(ValueError("--iwad and --iwadfp are mutually exclusive!"))
    elif args.iwad:
        selected_iwad = args.iwad
        selected_iwad_fp = False
    elif args.iwadfp:
        selected_iwad = args.iwadfp
        selected_iwad_fp = True
    
    if args.pwad:
        for pwad in args.pwad:
            selected_pwads.append((pwad, False))
    if args.pwadfp:
        for pwad in args.pwadfp:
            selected_pwads.append((pwad, True))

    if args.params:
        custom_params = args.params

def find_wad(wad_name, wad_paths, is_full_path):
    if is_full_path:
        if os.path.isfile(wad_name) or os.path.isdir(wad_name):
            return wad_name
        return None
    
    # Search for the file in wad_paths, case insensitive
    wad_name_split = os.path.split(wad_name)
    wad_filename = wad_name_split[1]
    for wp in wad_paths:
        p = wp
        # If the wad is in a subdirectory, try going to the subdirectory
        if wad_name_split[0] != "":
            sub_dir = os.path.join(p, wad_name_split[0])
            if not os.path.isdir(sub_dir):
                return None
            p = sub_dir
        files = os.listdir(p)
        # Match name exactly if possible,
        # otherwise look for a file with a known extension.
        # If two or more files are found, force user to specify.
        target_f = None
        for f in files:
            f_ext = os.path.splitext(f)[1].lower()
            if wad_filename.lower() == f.lower():
                return os.path.join(p, f)
            elif wad_filename.lower() == os.path.splitext(f)[0].lower() and \
            f_ext in {".wad", ".pk3", ".iwad", ".ipk3", ".pk7", ".zip"}:
                if target_f:
                    raise(ValueError("Ambiguous WAD \"" + wad_name +"\" specified, \
                                     please specify the file extension"))
                target_f = f
        if target_f:
            return os.path.join(p, target_f)
    return None

def find_iwad(iwad_name, is_full_path):
    wad = find_wad(iwad_name, iwad_paths, is_full_path)
    if not wad:
        raise(ValueError("Specified IWAD does not exist"))
    return wad

def find_pwad(pwad_name, is_full_path):
    wad = find_wad(pwad_name, pwad_paths, is_full_path)
    if not wad:
        raise(ValueError("Specified PWAD \"" + pwad_name + "\" does not exist"))
    return wad

def main():
    init_config()
    init_args()
    engine_path = engines[selected_engine]["path"]
    run_str = engine_path

    if selected_iwad:
        # Note: IWAD path must be resolved to a full ("real") path,
        # because of changing the working directory (see below)
        run_str += " -iwad " + os.path.realpath(find_iwad(selected_iwad, selected_iwad_fp))
    
    if selected_pwads != []:
        run_str += " -file"
        for pwad in selected_pwads:
            run_str += " " + os.path.realpath(find_pwad(pwad[0], pwad[1]))

    if custom_params:
        run_str += " " + custom_params

    # Change working directory for compatibility reasons
    # But first check if the directory is valid
    engine_dir = os.path.split(engine_path)[0]
    if os.path.isdir(engine_dir):
        os.chdir(engine_dir)

    subprocess.run(run_str)

if __name__ == "__main__":
    main()
