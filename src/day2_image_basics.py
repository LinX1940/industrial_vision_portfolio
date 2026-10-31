import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
def load_image(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"路径不存在: {path}")
    img =cv2.imread(path)
    if img is None:
        raise ValueError(f"文件存在但无法解析（可能已损坏或格式不支持）: {path}")
    return img
def analyze_image(img,name="当前图片"):
    height,width=img.shape[:2]
    if len(img.shape)==3:
        channels=img.shape[2]
    else:
        channels=1
    print(f"\n[ {name} 基础信息]")
    print(f"- 尺寸（宽*高）: {width}*{height}")
    print(f"- 通道数: {channels}")
    print(f"- 数据类型: {img.dtype}")
    print(f"- 像素范围: [{img.min()},{img.max()}]")
if __name__ == "__main__":
    if not os.path.exists("test_image"):
        print("未找到测试图片，将自己生成 一个蓝色图片 用于测试")
        test_img=np.ones((300,500,3),dtype=np.uint8)*255
        test_img[:]=[0,0,255]
        cv2.imwrite('test_image.jpg',test_img)
        # 生成一张灰度测试图
        gray_test_img = np.zeros((300, 500), dtype=np.uint8)
        gray_test_img[:150, :] = 255      # 上半部分白色
        gray_test_img[150:, :] = 100      # 下半部分深灰
        # 生成一张灰度测试图
        cv2.imwrite('outputs/gray_test.jpg', gray_test_img)
    if not os.path.exists('outputs'):
        os.makedirs('outputs')
    try:
        # img=load_image('error.jpg')
        img=load_image('test_image.jpg')
        analyze_image(img,"原图")
        cv2.imwrite('outputs/cv_original.jpg',img)

        img_rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        fig,axes=plt.subplots(1,2,figsize=(10,5))
        axes[0].imshow(img)
        axes[0].set_title('OpenCV BGR (Matplotlib 显示)')
        axes[0].axis('off')
        axes[1].imshow(img_rgb)
        axes[1].set_title('Converted RGB')
        axes[1].axis('off')
        # 灰度图
        gray_img = load_image('outputs/gray_test.jpg')
        analyze_image(gray_img, "灰度图")
        fig2, axes2 = plt.subplots(1, 2, figsize=(10, 5))
        axes2[0].imshow(gray_img,cmap='gray')
        axes2[0].set_title('Gray Image (Matplotlib 显示)')
        axes2[0].axis('off')
        axes2[1].imshow(gray_img,cmap='gray')
        axes2[1].set_title('Gray Image (OpenCV style)')
        axes2[1].axis('off')
        #灰度图
        plt.tight_layout()
        plt.savefig('outputs/matplorlib_compare.png',dpi=150)
        plt.show()
    except Exception as e:
        print(f"\n❌ 发生错误：{e}")