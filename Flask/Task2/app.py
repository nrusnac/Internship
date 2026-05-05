from model import predict_value, load_model

from flask import Flask, request
app = Flask(__name__)

model = load_model('wine_model.pkl')

@app.post('/predict')
def predict():
    input_data = request.get_json()['data']
    prediction = predict_value(model, input_data)[0]
    return { "prediction": int(prediction) }, 201

if __name__ == '__main__':
    app.run()