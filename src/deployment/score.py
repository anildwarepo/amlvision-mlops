import mlflow.pyfunc
import os
import pandas as pd
import base64

def init():
    global pyfunc_model
    # Get the path to the deployed model file and load it
    #model_dir =os.getenv('AZUREML_MODEL_DIR')
    model_path = os.path.join(os.getenv("AZUREML_MODEL_DIR"), "mlflow-model")
    #model_file = os.listdir(model_dir)[0]
    #model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), model_file)
    pyfunc_model = mlflow.pyfunc.load_model(model_path)


def read_image(image_path):
    with open(image_path, "rb") as f:
        return f.read()


#base64.encodebytes is used to convert the image to a string of bytes
def run(raw_data):
    test_df = pd.DataFrame(
    data=[
        raw_data
    ],
    columns=["image"],)
    result = pyfunc_model.predict(test_df).to_json(orient="records")
    return result
