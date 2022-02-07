from .modules import *
from .utils import *
import pandas as pd
# Implementing roberta multi input multi task

model_obj = RoBERTa_multi_input_multi_task_plus()

df = pd.load_csv("./dataset/train/train-empathy-distress-prediction-task-gold-text-normalization-Empath-normalize-custom-percent.csv")
inputs = model_obj.prepare_input(Preprocess(), Utils(), df)
outputs = model_obj.prepare_output(df)
