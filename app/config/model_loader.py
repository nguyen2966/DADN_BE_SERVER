import tensorflow as tf

# Load AI model 1 lần duy nhất để tái sử dụng
print("Loading TF Model...")
model = tf.keras.models.load_model("path_to_your_model.h5")
LABELS = ["Organic", "Recycle"]