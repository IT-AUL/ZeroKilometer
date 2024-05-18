import cv2
from PIL import Image, ImageDraw


# Create a circular mask using Pillow
def create_circular_mask(h, w):
    mask = Image.new('L', (h, w), 0)
    draw = ImageDraw.Draw(mask)
    draw.pieslice([0, 0, h, w], 0, 360, fill=255)
    return mask


# Apply the mask to each frame of the video
def apply_mask_to_video(video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))

    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:

            h,w = img.size

            # creating luminous image
            lum_img = Image.new('L',[h,w] ,0)
            draw = ImageDraw.Draw(lum_img)
            draw.pieslice([(0,0),(h,w)],0,360,fill=255)
            img_arr = np.array(img)
            lum_img_arr = np.array(lum_img)
            display(Image.fromarray(lum_img_arr))
            out.write(frame)
        else:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()


# Use the function
apply_mask_to_video('video.mp4', 'output.wav')
