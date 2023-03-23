from preprocessData import preprocess_data
from trainModel import create_model

data = preprocess_data()

X_train = data[0]
X_test = data[1]
y_train = data[2]
y_test = data[3]

model = create_model(X_train, y_train, X_test, y_test)
