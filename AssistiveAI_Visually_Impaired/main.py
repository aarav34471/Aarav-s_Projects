import cv2, math, os, time, threading

from vision.object_detection import initModel, get_bounding_boxes_from_frame
from vision.scene_understanding import place_object_in_scene
from language.scene_description import construct_sentence
from audio.tts import speak_text

import tkinter as tk
import tkinter.messagebox
from tkinter import Button, Label, simpledialog
from tkinter.filedialog import askopenfilename

def is_debugging_mode():
    global debug
    debug = not debug
    global label_isd_ebugging_mode
    label_isd_ebugging_mode.destroy()
    label_isd_ebugging_mode = Label(window, text = "Debug mode: " + str(debug))
    label_isd_ebugging_mode.config(font =("Courier", 14))
    label_isd_ebugging_mode.pack(side='top')

def process_frame(frame, is_video):
    global debug
    def thread(frame, is_video):
        bounding_boxes = get_bounding_boxes_from_frame(frame, model, class_names, debug)
        text = ""

        if (is_video):
            scene_understanding = place_object_in_scene(bounding_boxes, frame, debug, filter_threshold)
            text = construct_sentence(scene_understanding)
            
            os.remove(frame)
        else:
            from vision.SAM3_seg import SAM
            maskedImg, objects = SAM(bounding_boxes, frame)
            del SAM
            #BLIP scene descrtipyion. BLIP2_caption from vision.BLIP2_scene gives better results, but is slower and requires a larger download to run
            #BLIP_caption from vision.BLIP_scene is faster and doesn't require a large download, but gives worse results. Both work the same, so use BLIP_caption
            #for any testing.
            from vision.BLIP_scene import BLIP_caption
            text = str(BLIP_caption(maskedImg)) + ". "
            del BLIP_caption
            text += construct_sentence(objects)
            if (debug):
                maskedImg.show()
                for object in objects:
                    print(str(object) + "\n")
                
        if (debug):
            print(text)
        speak_text(text)
        global start
        start = time.time()
        global can_speak
        can_speak = True
        return
    threading.Thread(target=thread, args=(frame, is_video,)).start()
    return

def video_input():
    global can_speak
    global debug
    tk.Tk().withdraw()

    wait_time = simpledialog.askstring(title="Wait time input",prompt="Enter wait time (in seconds) between scene description:")

    if not wait_time.isdigit():
        tkinter.messagebox.showinfo("Invalid entry",  "Invalid wait time input. Ensure it is a number greater than 0.")
        return
    if int(wait_time) <= 0:
        tkinter.messagebox.showinfo("Invalid entry",  "Invalid wait time input. Ensure it is a number greater than 0.")
        return

    wait_time = int(wait_time)

    video = askopenfilename()
    file_extension = video[-4:]
    if (file_extension != ".mp4"):
        tkinter.messagebox.showinfo("Invalid file extension",  "Invalid file extension. Ensure it is a .mp4 for videos.")
        return
    video = cv2.VideoCapture(video)
    fps = video.get(cv2.CAP_PROP_FPS)
    i = 1
    global start
    start = time.time()
    while True:
        _, img = video.read()
        font = cv2.FONT_HERSHEY_PLAIN
        end = time.time()
        elapsed = end - start
        cv2.putText(img, "Press 'Q' to exit video. Time elapsed since last speech: " + str(round(elapsed,1)), (20, 40),
                    font, 2, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow('Live video simulatio/placeholder', img)

        key = cv2.waitKey(math.floor((500/fps)))
        if key == ord('q'):
            video.release()
            cv2.destroyAllWindows()
            break

        end = time.time()
        elapsed = end - start
        if elapsed >= wait_time and can_speak == True:
            can_speak = False
            filename = 'Frame_'+str(i)+'.jpg'            
            cv2.imwrite(filename, img)
            process_frame(filename, is_video=True)
            i = i+1

    video.release()
    cv2.destroyAllWindows()

def image_input():
    global debug
    tk.Tk().withdraw()
    frame = askopenfilename()
    file_extension = frame[-4:]
    if (file_extension != ".jpg" and file_extension != ".png"):
        tkinter.messagebox.showinfo("Invalid file extension",  "Invalid file extension. Ensure it is a .jpg or .png for images.")
        return
    process_frame(frame, is_video=False)
    return

def terminate():
    window.destroy()
    quit()

debug = False
filter_threshold = 3 #determines how many objects of lower priority (1 or 2) are mentioned in the scene descriptiom
model, class_names = initModel()
start = time.time()
can_speak = True

window = tkinter.Tk()
window.title("Choose input")
window.geometry('500x300')
button_video = Button(window, text="Video", command= lambda: video_input(), height=10, width=20)
button_image = Button(window, text="Image", command= lambda: image_input(), height=10, width=20)
button_debug = Button(window, text="Debug ON/OFF", command= lambda: is_debugging_mode(), height=10, width=20)
label_isd_ebugging_mode = Label(window, text = "Debug mode: " + str(debug))
label_isd_ebugging_mode.config(font =("Courier", 14))
button_video.pack(side='left')
button_image.pack(side='right')
button_debug.pack(side='bottom')
label_isd_ebugging_mode.pack(side='top')
window.protocol("WM_DELETE_WINDOW", terminate)
window.eval('tk::PlaceWindow . center')
window.mainloop()