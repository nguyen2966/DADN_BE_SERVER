import os
from pathlib import Path
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


import tensorflow as tf
from keras.models import load_model


tf.get_logger().setLevel('ERROR')

# Load model ONCE
curr_dir = Path(__file__).parent.absolute()
model_path = curr_dir.parent / "core" / "clean_model.keras"
model = load_model(f"{model_path}")
LABELS = ["non-recycle", "recycle"]