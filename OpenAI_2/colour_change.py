import base64
from openai import OpenAI
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')  # Go up one directory
load_dotenv(dotenv_path=dotenv_path)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def colour_change(image_paths, colour):
    """
    Modifies the colour of a specified object in a list of images and saves
    the modified images into a new folder called "Task2_result".

    Args:
        image_paths: A list of paths to the images.  It's assumed the object
                     you want to change is similar across these images.
        colour: The desired colour (e.g., "red", "blue", "green").
    """

    # Construct the prompt.  This needs to be VERY carefully crafted.
    prompt = f"""
    You are an AI that can take a set of images and change the color of a specific item within them to a user-provided color. 
    The user will provide a list of images, and the target item is assumed to be visually similar across all images.
    The desired color is {colour}.

    The images provided depict a variety of items. Your task is to identify the common, prominent object
    across all images and change *only* that object's color to {colour}. It is very important that you only modify the
    color of this target object, and leave the rest of the image unchanged. Try to keep as much of the surrounding image
    as original as possible.

    Do not generate new objects, change the background, or significantly alter anything other than the target object's color.
    Preserve the original style, composition, and overall feel of the images as much as possible, only changing the target object to {colour}.

    Focus on accuracy. The specified color is {colour}, and the outputted images should reflect *that* color, and only change the item to that color.
    """

    # Prepare the image files for the API call
    images = [open(path, "rb") for path in image_paths]

    result = client.images.edit(
        model="gpt-image-1",
        image=images,
        prompt=prompt
    )

    # Create the "Task2_result" folder if it doesn't exist
    output_folder = "Task2_result"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Process the results
    for i, data in enumerate(result.data):
        image_base64 = data.b64_json
        image_bytes = base64.b64decode(image_base64)

        # Generate output filename within the new folder
        base_filename = os.path.basename(image_paths[i]).split('.')[0] # Get filename without extension
        output_filename = os.path.join(output_folder, f"{base_filename}_modified.png")

        with open(output_filename, "wb") as f:
            f.write(image_bytes)
        print(f"Modified image saved to: {output_filename}")

    # Close the image files
    for image in images:
        image.close()


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__)) #get path of colour_change.py
    # Go up one directory from script_dir to reach the project root (taikooResearch)
    # then join with taikoo_images
    image_folder = os.path.join(os.path.dirname(script_dir), 'taikoo_images')
    image_list = [
        os.path.join(image_folder, 'backpack.png'),
        os.path.join(image_folder, 'clothes.png'),
        os.path.join(image_folder, 'jeans.png'),  # Corrected the image name
        # os.path.join(image_folder, 'body-lotion.png') #removed this path as it not in file

    ]
    colour_change(image_list, "blue")