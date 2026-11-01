import os
import cv2
import numpy as np
def safe_crop_roi(image,x,y,w,h):
    if image is None:
        print("[Error] 输入图像为空! ")
        return None
    img_h,img_w=image.shape[:2]
    if w<=0 or h<=0:
        print(f"[Warning] 裁剪框尺寸不合法: w={w},h={h}(必须大于0)")
        return None
    x1=max(0,min(x,img_w))
    y1=max(0,min(y,img_h))
    x2=max(0,min(x+w,img_w))
    y2=max(0,min(y+h,img_h))
    if x1>=x2 or y1>=y2:
        print(f"[Warning] 裁剪区域完全越界 原始请求: x={x},y={y},w={w},h={h}"
        f"截断后无有效像素"
    )
        return None
    cropped=image[y1:y2,x1:x2]
    print (
        f"[Info] 成功裁剪 ROI: 原始(x={x},y={y},w={w},h={h}) ->"
        f" 实际生效区域({x1},{y1}到{x2},{y2})"
    )
    return cropped
def main():
    os.makedirs("outputs",exist_ok=True)
    canvas = np.zeros((480,640,3),dtype=np.uint8)
    canvas[:]=(50,50,50)
    img_h,img_w=canvas.shape[:2]
    center_x,center_y=img_w//2,img_h//2
    cv2.circle(canvas,(center_x,center_y),5,(0,0,255),-1)
    cv2.line(
        canvas,
        (center_x-20,center_y),
        (center_x+20,center_y),
        (0,255,255),
        2,
    )
    cv2.line(
        canvas,
        (center_x,center_y-20),
        (center_x,center_y+20),
        (0,255,255),
        2,
    )
    roi_x,roi_y,roi_w,roi_h=150,100,200,150
    cv2.rectangle(
        canvas,
        (roi_x,roi_y),
        (roi_x+roi_w,roi_y+roi_h),
        (0,255,0),
        2,
    )
    cv2.putText(
        canvas,
        "Fixed ROI",
        (roi_x,roi_y-10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0,255,0),
        2,
    )
    normal_crop=safe_crop_roi(canvas,roi_x,roi_y,roi_w,roi_h)
    if(normal_crop is not None):
        cv2.imwrite("outputs/normal_crop.png",normal_crop)
    print("\n--- 开始测试边界与异常输入 ---")
    # 测试用例 A: 坐标部分越界（超出右下角边界）
    safe_crop_roi(canvas, 500, 350, 300, 200)

    # 测试用例 B: 坐标完全在画面外部（负数坐标）
    safe_crop_roi(canvas, -50, -50, 100, 100)

    # 测试用例 C: 宽高为零或负数
    safe_crop_roi(canvas, 100, 100, 0, 150)
    safe_crop_roi(canvas, 100, 100, 100, -20)

    cv2.imwrite("output/d4_canvas_annotated.png",canvas)
if __name__ =="__main__":
    main()

