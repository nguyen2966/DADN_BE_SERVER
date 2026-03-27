# import os
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# from keras.models import load_model



# # Load AI model 1 lần duy nhất để tái sử dụng
# print("Loading TF Model...")
# model = load_model("E:/Webs_252/DADN/AI_server/AI_Server/smart-bin-backend/app/core/waste_cnn_model.keras")
# LABELS = ["non-recycle", "recycle"]


import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


import tensorflow as tf
from keras.models import load_model


tf.get_logger().setLevel('ERROR')

# Load model ONCE
model = load_model('E:/Webs_252/DADN/AI_server/AI_Server/smart-bin-backend/app/core/clean_model.keras')
LABELS = ["non-recycle", "recycle"]