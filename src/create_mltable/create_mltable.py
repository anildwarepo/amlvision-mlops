import os
import argparse
import sys
import mlflow


sys.path.insert(0, "./jsonl-conversion/")
from base_jsonl_converter import write_json_lines
from coco_jsonl_converter import COCOJSONLConverter

def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--input_folder", type=str)
    parser.add_argument("--output_folder", type=str)
    parser.add_argument("--run_mode", type=str, default="local")
    parser.add_argument("--azure_storage_url", type=str)
    # parse args
    args = parser.parse_args()    
    # return args
    return args


def create_ml_table_file(filename):
    """Create ML Table definition"""

    return (
        "paths:\n"
        "  - file: ./{0}\n"
        "transformations:\n"
        "  - read_json_lines:\n"
        "        encoding: utf8\n"
        "        invalid_lines: error\n"
        "        include_path_column: false\n"
        "  - convert_column_types:\n"
        "      - columns: image_url\n"
        "        column_type: stream_info"
    ).format(filename)


def save_ml_table_file(output_path, mltable_file_contents):
    with open(os.path.join(output_path, "MLTable"), "w") as f:
        f.write(mltable_file_contents)

def create_ml_table(filename, output_path):
    # Create and save train mltable
    mltable_file_contents = create_ml_table_file(
        os.path.basename(filename)
    )
    save_ml_table_file(output_path, mltable_file_contents)

def create_jsonl_file(training_data_folder_path, output_folder_path, azure_storage_url):
    base_url = os.path.join(training_data_folder_path)
    jsonl_annotations = os.path.join(output_folder_path, "coco_labelled", "construction_drawing_coco_labeled.jsonl")
    converter = COCOJSONLConverter(azure_storage_url, f"{base_url}/coco_labelled/construction_drawing_coco_labelled.json")
    write_json_lines(converter, jsonl_annotations)
    create_train_val_jsonl(jsonl_annotations, output_folder_path)


def create_train_val_jsonl(jsonl_annotations, output_folder_path):
    # We'll copy each JSONL file within its related MLTable folder
    training_mltable_path = os.path.join(output_folder_path, "training-mltable-folder")
    validation_mltable_path = os.path.join(output_folder_path, "validation-mltable-folder")

    # First, let's create the folders if they don't exist
    os.makedirs(training_mltable_path, exist_ok=True)
    os.makedirs(validation_mltable_path, exist_ok=True)

    train_validation_ratio = 5

    # Path to the training and validation files
    train_annotations_file = os.path.join(training_mltable_path, "train_annotations.jsonl")
    validation_annotations_file = os.path.join(
        validation_mltable_path, "validation_annotations.jsonl"
    )

    with open(jsonl_annotations, "r") as annot_f:
        json_lines = annot_f.readlines()

    index = 0
    with open(train_annotations_file, "w") as train_f:
        with open(validation_annotations_file, "w") as validation_f:
            for json_line in json_lines:
                if index % train_validation_ratio == 0:
                    # validation annotation
                    validation_f.write(json_line)
                else:
                    # train annotation
                    train_f.write(json_line)
                index += 1    

    create_ml_table(train_annotations_file, training_mltable_path)
    create_ml_table(validation_annotations_file, validation_mltable_path)



def main(args):
   create_jsonl_file(args.input_folder, args.output_folder, args.azure_storage_url)

# run script
if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main function
    main(args)