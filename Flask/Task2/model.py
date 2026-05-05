import joblib
import pandas as pd

# Feature names used during training
FEATURE_NAMES = ['alcohol', 'malic_acid', 'ash', 'alcalinity_of_ash', 'proanthocyanins',
                 'color_intensity', 'hue', 'od280/od315_of_diluted_wines', 'proline']

def load_model(filepath):
    return joblib.load(filepath)

def predict_value(model, input_data):
    input_df = pd.DataFrame([input_data], columns=FEATURE_NAMES)
    return model.predict(input_df)

if __name__ == "__main__":
    # test
    input_data = [13.2, 1.78, 2.14, 11.2, 1.28, 4.38, 1.05, 3.4, 1050]
    prediction = predict_value(input_data)
    print(f"Predicted class: {prediction[0]}")