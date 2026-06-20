To install the requirements, simply run

pip install -r requirements.txt

inside a virtual environment.

Before running the code, download the folder at the following link:

https://surreyac-my.sharepoint.com/:f:/g/personal/jw02520_surrey_ac_uk/IgC5Eb1kDJdmQLglFlpJ2e_xAc51yp_C-Sohu0nrkL7zFQw

This is only accessible using a University of Surrey account, so please ensure you are logged in. Place the facebook folder and everything inside it in ./vision/models in order to run SAM3 locally.

To run the code, run the file main.py and interact with the User Interface. When prompted, select either a video or image depending on which branch you used. Turn on Debug mode to view outputs such as objects, bounding boxes, or SAM masks.

To switch from BLIP to BLIP2 for slower code but better descriptions, change lines 40-42 from:
 from vision.BLIP_scene import BLIP_caption
 text = str(BLIP_caption(maskedImg)) + ". "
 del BLIP_caption
to:
 from vision.BLIP2_scene import BLIP2_caption
 text = str(BLIP2_caption(maskedImg)) + ". "
 del BLIP2_caption
BLIP2 is a very large download and quite slow, so it is much better to stick with BLIP.

To run the evaluation code, run the following code in PowerShell:
python evaluation/main_eval.py `
  --images-dir coco_100/val2017 `
  --instances coco_100/annotations/instances_val2017_100.json `
  --captions coco_100/annotations/captions_val2017_100.json `
  --limit 100

Adjust limit to change how many images are tested.
