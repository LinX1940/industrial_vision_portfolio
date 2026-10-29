import sys
import cv2
import numpy as np
def main():
    print("python version:",sys.version.strip())
    print("python executable:",sys.executable)
    print("OpenCV version:",cv2.__version__)
    print("NumPy version:",np.__version__)
    test_img=np.zeros((200,400,3),dtype=np.uint8)
    cv2.putText(test_img,"OpenCV OK",(60,120),cv2.FONT_HERSHEY_SIMPLEX,1.2,(255,255,255),2,)
    input_path="test_input.jpg"
    output_path="test_output.jpg"
    cv2.imwrite(input_path,test_img)
    print(f"test image saved to {input_path}")
    img=cv2.imread(input_path)
    if img is None:
        print("Error:failed to read image.")
        sys.exit(1)
    print(f"image shape:{img.shape}")
    print(f"image dtype:{img.dtype}")
    cv2.imwrite(output_path,img)
    print(f"Image copy saved to {output_path}")
if __name__ == "__main__":
    main()