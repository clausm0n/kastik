#!/bin/bash

# Check if CUDA is installed
if [ -x "$(command -v nvcc)" ]; then
  echo "CUDA is installed."
  nvcc --version
else
  echo "CUDA is not installed."
fi

# Create a temporary Python script to check TensorFlow's CUDA support and GPU availability
cat > check_tf_cuda.py << EOF
import tensorflow as tf

print("TensorFlow version:", tf.__version__)
print("CUDA support:", "Yes" if tf.test.is_built_with_cuda() else "No")
print("GPU available:", "Yes" if tf.config.list_physical_devices('GPU') else "No")
EOF

# Run the Python script
python check_tf_cuda.py

# Remove the temporary Python script
rm check_tf_cuda.py
