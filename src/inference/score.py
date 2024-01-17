import urllib.request
import json
import os
import ssl
import base64
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
from PIL import Image
import numpy as np
import json

def visualize_detection(sample_image, detections):
    IMAGE_SIZE = (18, 12)
    plt.figure(figsize=IMAGE_SIZE)
    img_np = mpimg.imread(sample_image)
    img = Image.fromarray(img_np.astype("uint8"))
    x, y = img.size

    fig, ax = plt.subplots(1, figsize=(15, 15))
    # Display the image
    ax.imshow(img_np)

    # draw box and label for each detection
    for detect in detections["boxes"]:
        label = detect["label"]
        box = detect["box"]
        conf_score = detect["score"]
        if conf_score > 0.2:
            ymin, xmin, ymax, xmax = (
                box["topY"],
                box["topX"],
                box["bottomY"],
                box["bottomX"],
            )
            topleft_x, topleft_y = x * xmin, y * ymin
            width, height = x * (xmax - xmin), y * (ymax - ymin)
            print(
                f"{detect['label']}: [{round(topleft_x, 3)}, {round(topleft_y, 3)}, "
                f"{round(width, 3)}, {round(height, 3)}], {round(conf_score, 3)}"
            )

            color = np.random.rand(3)  #'red'
            rect = patches.Rectangle(
                (topleft_x, topleft_y),
                width,
                height,
                linewidth=3,
                edgecolor=color,
                facecolor="none",
            )

            ax.add_patch(rect)
            plt.text(topleft_x, topleft_y - 10, label, color=color, fontsize=20)
    plt.show()

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

# Request data goes here
# The example below assumes JSON formatting which may be updated
# depending on the format your endpoint expects.
# More information can be found here:
# https://docs.microsoft.com/azure/machine-learning/how-to-deploy-advanced-entry-script


script_path = os.path.abspath(__file__)
script_directory = os.path.dirname(script_path)
image_path = os.path.join(script_directory,"test_set" ,"with_doors" ,"Rinker_047.jpg")
test_image_paths = []

with open(image_path, "rb") as f:
    data = f.read()
    base64_data = base64.encodebytes(data).decode("utf-8")
test_image_paths.append(image_path)   

body = str.encode(base64_data)

url = 'https://construction-od-endpoint.westus.inference.ml.azure.com/score'
# Replace this with the primary/secondary key or AMLToken for the endpoint
api_key = ''
if not api_key:
    raise Exception("A key should be provided to invoke the endpoint")

# The azureml-model-deployment header will force the request to go to a specific deployment.
# Remove this header to have the request observe the endpoint traffic rules
headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': 'green' }

req = urllib.request.Request(url, body, headers)

try:
    response = urllib.request.urlopen(req)

    result = response.read()
    decoded_result = result.decode("utf-8")[1:-1].replace('\\"', '"')
    print(result)

    for img, det in zip(test_image_paths, json.loads(decoded_result)):
        visualize_detection(img, det)
    
    #read key input
    key = input("Press any key to continue...")
except urllib.error.HTTPError as error:
    print("The request failed with status code: " + str(error.code))

    # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
    print(error.info())
    print(error.read().decode("utf8", 'ignore'))
