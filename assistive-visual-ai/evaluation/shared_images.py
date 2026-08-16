import json


def get_image_file_names(instances_path, limit):
    with open(instances_path) as file:
        data = json.load(file)

    image_file_names = []
    for image in data["images"][:limit]:
        image_file_names.append(image["file_name"])

    return image_file_names
