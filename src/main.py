import yaml
import argparse
import logging
from typing import Text
import transformers
from task.train import Training
from task.inference import Predict

def main(config_paths) -> None:
    transformers.logging.set_verbosity_error()
    logging.basicConfig(level=logging.INFO)

    for config_path in config_paths:
        with open(config_path) as conf_file:
            config = yaml.safe_load(conf_file)
        
        logging.info(f"Training started for config: {config_path}...")
        task_train = Training(config)
        task_train.training()
        logging.info(f"Training complete for config: {config_path}")
        
        logging.info(f'Now evaluating on test data for config: {config_path}...')
        task_infer = Predict(config)
        task_infer.predict_submission()
        logging.info(f'Task done for config: {config_path}!!!')
    
if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--config', dest='config', required=True, nargs='+', help='List of config files')
    args = args_parser.parse_args()
    main(args.config)