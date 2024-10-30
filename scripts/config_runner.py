import time
import yaml
import os, sys
from typing import Dict, Any
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from scripts.train.train_jsbsim import main
from scripts.render.render_jsbsim import main_render

# TRAIN_OR_RENDER = False
# if TRAIN_OR_RENDER == True:
#     filename = "share_selfplay"
# else:
#     filename = "render_share_selfplay"

class Config:
    def __init__(self, config_dict):
        for key, value in config_dict.items():
            setattr(self, key, value)

def load_config(file_path):
    with open(file_path, 'r') as file:
        config_dict = yaml.load(file, Loader=yaml.FullLoader)
    return config_dict

def merge_configs(default_config: Dict[str, Any], custom_config: Dict[str, Any]):
    merged_config = default_config.copy()
    merged_config.update(custom_config)
    return merged_config

def runner(file_path, train_flag: bool = True, tr_dir: str = None):
    default_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "configs", "default.yaml")
    default_config = load_config(default_path)
    config = load_config(file_path)
    config = merge_configs(default_config, config)
    config_t = Config(config)
    run_dir = None
    if train_flag:
        start_time = time.time()
        run_dir = main(config_t, False)
        end_time = time.time()
        print(f"Time taken with {config_t.n_training_threads} threads: {end_time - start_time} seconds")
    else:
        if tr_dir is not None:
            config_t.model_dir = tr_dir
        run_dir = main_render(config_t, False)
    return run_dir

if __name__ == '__main__':
    init = Config(load_config(os.path.join(os.path.dirname(os.path.realpath(__file__)), "configs", 'initial.yaml')))
    if init.train_or_render == 1:
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "configs", f'{init.filename}.yaml')
        runner(path, 1)
    elif init.train_or_render == 0:
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "configs", f'{init.render_filename}.yaml')
        runner(path, 0)
    elif init.train_or_render == 2:
        render_suffix = init.render_filename
        if render_suffix.startswith("render_"):
            render_suffix = render_suffix[len("render_"):]
        else:
            raise ValueError("render_filename must start with 'render_'")
        if init.filename != render_suffix:
            raise ValueError("render_filename must be the same as filename")
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "configs", f'{init.filename}.yaml')
        tr_dir = runner(path, 1)
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "configs", f'{init.render_filename}.yaml')
        runner(path, 0, tr_dir)
    