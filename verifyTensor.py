import tensorflow as tf

print("TensorFlow version:", tf.__version__)
print("CUDA support:", "Yes" if tf.test.is_built_with_cuda() else "No")
print("GPU available:", "Yes" if tf.config.list_physical_devices('GPU') else "No")
