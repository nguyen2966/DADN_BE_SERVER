import tensorflow as tf
model = tf.keras.models.load_model('./core/waste_cnn_model.keras', compile=False)
# Remove quantization_config layers bằng cách save lại
model.save('./core/clean_model.keras', include_optimizer=False)