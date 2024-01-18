import argparse
import configparser
import subprocess
import os
import sys

cfg = None
iwad_paths = []
pwad_paths = []
default_engine = None
most_recent_engine = None
default_iwad = None
most_recent_iwad = None

engines = dict()

selected_engine = None
selected_iwad = None
selected_iwad_fp = False
selected_pwads = []
selected_skill = None
selected_warp = None
selected_complevel = None
custom_params = ""

def get_app_dir():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller bundle
        return os.path.split(sys._MEIPASS)[0]
    else:
        # Normal Python process
        return os.path.split(os.path.realpath(__file__))[0]

def get_config_path():
    return os.path.join(get_app_dir(), "config.ini")

def get_engines_path():
    return os.path.join(get_app_dir(), "engines.ini")

def init_config():
    global cfg
    global default_engine
    global most_recent_engine
    global default_iwad
    global most_recent_iwad

    cfg = configparser.ConfigParser()
    cfg.read(get_config_path())
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
    
    if not cfg["General"].get("DefaultEngine"):
        raise(ValueError("Missing config key \"General/DefaultEngine\""))
    default_engine = cfg["General"]["DefaultEngine"]
    if not cfg["General"].get("MostRecentEngine"):
        raise(ValueError("Missing config key \"General/MostRecentEngine\""))
    most_recent_engine = cfg["General"]["MostRecentEngine"]

    if not cfg["General"].get("DefaultIWAD"):
        raise(ValueError("Missing config key \"General/DefaultIWAD\""))
    default_iwad = cfg["General"]["DefaultIWAD"]
    if not cfg["General"].get("MostRecentIWAD"):
        raise(ValueError("Missing config key \"General/MostRecentIWAD\""))
    most_recent_iwad = cfg["General"]["MostRecentIWAD"]


    engines_cfg = configparser.ConfigParser()
    engines_cfg.read(get_engines_path())
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
    global selected_skill
    global selected_warp
    global selected_complevel
    global custom_params

    parser = argparse.ArgumentParser()
    iwad_group = parser.add_mutually_exclusive_group()
    parser.add_argument("--engine", help = "source port to use")
    iwad_group.add_argument("--iwad", help = "iwad to load from IWADPath")
    parser.add_argument("--pwad", help = "pwad(s) to load from PWADPath", nargs="+")
    iwad_group.add_argument("--iwadfp", help = "iwad to load from a full path")
    parser.add_argument("--pwadfp", help = "pwad(s) to load from a full path", nargs="+")
    iwad_group.add_argument("--noiwad", help = "force loading without an iwad", action="store_true")
    parser.add_argument("-s", "--skill", help = "skill/difficulty level")
    parser.add_argument("-w", "--warp", help = "map to warp to")
    parser.add_argument("--cl", help = "complevel")
    parser.add_argument("--params", help = "other parameters to pass to the source port")
    args_tuple = parser.parse_known_args()
    args = args_tuple[0]
    for extra_arg in args_tuple[1]:
        custom_params += " " + extra_arg

    if args.engine:
        selected_engine = args.engine
    else:
        # Use default engine
        if default_engine == "-1":
            selected_engine = most_recent_engine
        else:
            selected_engine = default_engine

    if not engines.get(selected_engine):
        raise(ValueError("Specified engine does not exist"))
    
    cfg["General"]["MostRecentEngine"] = selected_engine

    if args.iwad:
        selected_iwad = args.iwad
        selected_iwad_fp = False
    elif args.iwadfp:
        selected_iwad = args.iwadfp
        selected_iwad_fp = True
    elif not args.noiwad:
        # Use default IWAD
        if default_iwad == "-1":
            selected_iwad = most_recent_iwad
        else:
            selected_iwad = default_iwad
        selected_iwad_fp = False
    
    if selected_iwad and not selected_iwad_fp:
        cfg["General"]["MostRecentIWAD"] = selected_iwad
    
    if args.pwad:
        for pwad in args.pwad:
            selected_pwads.append((pwad, False))
    if args.pwadfp:
        for pwad in args.pwadfp:
            selected_pwads.append((pwad, True))
    
    if args.skill:
        selected_skill = args.skill
    if args.warp:
        selected_warp = args.warp
    if args.cl:
        selected_complevel = args.cl

    if args.params:
        custom_params += " " + args.params

def save_cfg():
    with open(get_config_path(), "w") as cfg_file:
        cfg.write(cfg_file)

def find_wad(wad_name, wad_paths, is_full_path):
    if is_full_path:
        if os.path.isfile(wad_name) or os.path.isdir(wad_name):
            return wad_name
        return None
    
    # Search for the file in wad_paths
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

        # Match name exactly if possible (case sensitive)
        for f in files:
            if wad_filename == f:
                return os.path.join(p, f)
        # Otherwise, try to match case insensitive
        # If two or more files are found, force user to specify.
        target_f = None
        for f in files:
            if wad_filename.lower() == f.lower():
                if target_f:
                    raise(ValueError("Ambiguous WAD \"" + wad_name +"\" specified, \
                                     please specify the file name with correct case and extension"))
                target_f = f
        if target_f:
            return os.path.join(p, target_f)
        # Otherwise, try to match the name with a known extension (also case insensitive)
        for f in files:
            f_ext = os.path.splitext(f)[1].lower()
            
            if wad_filename.lower() == os.path.splitext(f)[0].lower() and \
            f_ext in {".wad", ".pk3", ".iwad", ".ipk3", ".pk7", ".zip"}:
                if target_f:
                    raise(ValueError("Ambiguous WAD \"" + wad_name +"\" specified, \
                                     please specify the file name with correct case and extension"))
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
    save_cfg()
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
    
    if selected_skill:
        run_str += " -skill " + selected_skill
    if selected_warp:
        run_str += " -warp " + selected_warp
    if selected_complevel:
        run_str += " -complevel " + selected_complevel

    run_str += custom_params

    # Change working directory for compatibility reasons
    # But first check if the directory is valid
    engine_dir = os.path.split(engine_path)[0]
    if os.path.isdir(engine_dir):
        os.chdir(engine_dir)

    subprocess.run(run_str)

if __name__ == "__main__":
    main()
