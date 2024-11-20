from model.visionreader_bart_vqa import Bart_VQA_Model
from model.visionreader_t5_vqa import T5_VQA_Model
from model.exp1_t5 import T5_VQA_Model_exp1
from model.exp2_t5 import T5_VQA_Model_exp2
from model.exp3_t5 import T5_VQA_Model_exp3
from model.exp4_t5 import T5_VQA_Model_exp4
from peft import get_peft_model, PrefixTuningConfig, TaskType
from peft import PrefixTuningConfig
from transformers import T5Config

def build_model(config):
    if config['model']['type_model'] == 'visionreader_t5':
        return T5_VQA_Model(config)
    if config['model']['type_model'] == 'visionreader_bart':
        return Bart_VQA_Model(config)
    if config['model']['type_model'] == 't5_ep1':
        return T5_VQA_Model_exp1(config)
    if config['model']['type_model'] == 't5_ep2':
        return T5_VQA_Model_exp2(config)
    if config['model']['type_model'] == 't5_ep3':
        return T5_VQA_Model_exp3(config)
    if config['model']['type_model'] == 't5_ep4':
        return T5_VQA_Model_exp4(config)
    if config['model']['type_model'] == 't5_ep4_ver2':
        return T5_VQA_Model_exp4(config)
    