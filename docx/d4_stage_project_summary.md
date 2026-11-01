# D4 阶段：坐标系、ROI 裁剪与工业可视化实战总结

本文档为工业视觉项目 portfolio D4 阶段的归档文档，涵盖了坐标系基础、ROI（Region of Interest）裁剪逻辑、可视化绘图 API 规范、完整源码及边界异常防御机制。

---

## 一、 项目需求与核心概念

### 1. 核心目标
* **坐标系与参数掌握**：理清 OpenCV 在绘图 API（`cv2.rectangle`、`cv2.circle`、`cv2.putText`）中的坐标传参顺序与颜色空间（BGR）格式。
* **可视化标注**：在图像上标注画面中心点（十字准星）、绘制固定 ROI 区域及文字标签。
* **安全 ROI 裁剪**：实现工业级安全的 ROI 裁剪函数 `safe_crop_roi(image, x, y, w, h)`，防止由于算法输出异常坐标导致的程序崩溃。
* **边界防御测试**：验证函数在输入坐标部分越界、完全越界（负数坐标）、宽高为零或负数等极端条件下的防御能力。

### 2. 基础概念剖析

#### (1) 什么是 ROI (Region of Interest)？
在工业视觉中，整幅图像可能包含大量的背景噪音或无关区域。ROI 是指从图像中选定的**重点分析子区域**。
* **优势**：
  * **降低计算量**：仅对小范围像素进行特征提取或检测，大幅提高算法帧率（FPS）。
  * **减少噪声干扰**：剔除背景杂物与光照波动的影响，提升检测鲁棒性。

#### (2) OpenCV 坐标系与 NumPy 数组的映射关系
* **图像坐标系**：
  * 原点 $(0,0)$ 位于图像**左上角**。
  * $X$ 轴（列 / 宽度 Width）：水平向右为正。
  * $Y$ 轴（行 / 高度 Height）：垂直**向下**为正。
* **NumPy 切片陷阱**：
  * OpenCV 图形绘制 API 接收坐标顺序为 $(x, y)$。
  * 但图像在内存中以 NumPy 多维数组存储，维度顺序为 `(Height, Width, Channel)`。
  * 因此切片提取图像像素时必须采用 **`image[y1:y2, x1:x2]`** 格式（即 $Y$ 在前，$X$ 在后）。

---

## 二、 完整代码实现

以下为 `src/day4_roi_visualization.py` 的完整 Python 源码：

```python
import os
import cv2
import numpy as np


def safe_crop_roi(image, x, y, w, h):
  """工业级安全的 ROI 裁剪函数

  参数:
      image: 输入图像 (numpy 数组)
      x, y: 矩形框左上角起点坐标
      w, h: 矩形框的宽与高
  返回:
      cropped: 裁剪出的子图像，若完全越界或不合法则返回 None
  """
  # 1. 空值检查
  if image is None:
    print("[Error] 输入图像为空！")
    return None

  img_h, img_w = image.shape[:2]

  # 2. 检查宽高合法性
  if w <= 0 or h <= 0:
    print(f"[Warning] 裁剪框尺寸不合法: w={w}, h={h} (必须大于0)")
    return None

  # 3. 坐标边界截断 (Clipping 防御)
  x1 = max(0, min(x, img_w))
  y1 = max(0, min(y, img_h))
  x2 = max(0, min(x + w, img_w))
  y2 = max(0, min(y + h, img_h))

  # 4. 零面积检查
  if x1 >= x2 or y1 >= y2:
    print(
        f"[Warning] 裁剪区域完全越界: 原始请求(x={x}, y={y}, w={w}, h={h}),"
        f" 截断后无有效像素"
    )
    return None

  # 5. 执行 NumPy 矩阵切片 [y1:y2, x1:x2]
  cropped = image[y1:y2, x1:x2]
  print(
      f"[Info] 成功裁剪 ROI: 原始(x={x},y={y},w={w},h={h}) ->"
      f" 实际生效区域({x1},{y1} 到 {x2},{y2})"
  )
  return cropped


def main():
  # 创建输出目录
  os.makedirs("outputs", exist_ok=True)

  # 创建画布：640x480 分辨率，3 通道深灰色背景
  canvas = np.zeros((480, 640, 3), dtype=np.uint8)
  canvas[:] = (50, 50, 50)

  img_h, img_w = canvas.shape[:2]
  center_x, center_y = img_w // 2, img_h // 2

  # 1. 绘制画面中心十字准星与圆点
  cv2.circle(canvas, (center_x, center_y), 5, (0, 0, 255), -1)
  cv2.line(
      canvas,
      (center_x - 20, center_y),
      (center_x + 20, center_y),
      (0, 255, 255),
      2,
  )
  cv2.line(
      canvas,
      (center_x, center_y - 20),
      (center_x, center_y + 20),
      (0, 255, 255),
      2,
  )

  # 2. 绘制固定 ROI 矩形框与文字标签
  roi_x, roi_y, roi_w, roi_h = 150, 100, 200, 150
  cv2.rectangle(
      canvas,
      (roi_x, roi_y),
      (roi_x + roi_w, roi_y + roi_h),
      (0, 255, 0),
      2,
  )
  cv2.putText(
      canvas,
      "Fixed ROI",
      (roi_x, roi_y - 10),
      cv2.FONT_HERSHEY_SIMPLEX,
      0.6,
      (0, 255, 0),
      2,
  )

  # 3. 正常用例裁剪测试
  normal_crop = safe_crop_roi(canvas, roi_x, roi_y, roi_w, roi_h)
  if normal_crop is not None:
    cv2.imwrite("outputs/roi_normal.jpg", normal_crop)

  # 4. 边界与异常输入测试
  print("\n--- 开始测试边界与异常输入 ---")
  safe_crop_roi(canvas, 500, 350, 300, 200)  # 用例 A: 部分越界
  safe_crop_roi(canvas, -50, -50, 100, 100)  # 用例 B: 负数坐标
  safe_crop_roi(canvas, 100, 100, 0, 150)  # 用例 C: 宽度为 0
  safe_crop_roi(canvas, 100, 100, 100, -20)  # 用例 D: 高度为负

  # 保存带标注的主画布
  cv2.imwrite("outputs/d4_canvas_annotated.jpg", canvas)
  print("\n[Info] D4 测试完成！文件已保存至 outputs/ 目录。")


if __name__ == "__main__":
  main()
```

---

## 三、 代码逐段详细解析

### 1. 图像空值与非法尺寸校验
```python
if image is None:
  return None
if w <= 0 or h <= 0:
  return None
```
* **解析**：当输入图片解包失败（`None`）或输入的宽与高 $w \le 0, h \le 0$ 时立刻拦截，防止引发空指针或无效数据计算。

### 2. 边界截断算法 (Clipping)
```python
x1 = max(0, min(x, img_w))
y1 = max(0, min(y, img_h))
x2 = max(0, min(x + w, img_w))
y2 = max(0, min(y + h, img_h))
```
* **解析**：
  * `min(x, img_w)`：将坐标上限限定在图像最大宽度/高度内。
  * `max(0, ...)`：将坐标下限限定在 $0$ 以上。
  * 效果：自动将任意超出图像边界的 $(x, y, w, h)$ 矫正收缩至合法像素坐标区间内。

### 3. 零面积拦截与 NumPy 矩阵切片
```python
if x1 >= x2 or y1 >= y2:
  return None
cropped = image[y1:y2, x1:x2]
```
* **解析**：若截断后起点等于或大于终点，说明请求的 ROI 区域完全落于图像外部，判定为无有效像素。若有效，执行 `image[y1:y2, x1:x2]` 提取子矩阵。

### 4. OpenCV 绘图 API 传参详解
* **`cv2.circle(img, center, radius, color, thickness)`**
  * `center`: `(center_x, center_y)` 圆心坐标。
  * `color`: `(0, 0, 255)` 纯红色 (BGR 格式)。
  * `thickness`: `-1` 表示绘制**实心圆**。
* **`cv2.rectangle(img, pt1, pt2, color, thickness)`**
  * `pt1`: 左上角坐标 `(x1, y1)`。
  * `pt2`: 右下角坐标 `(x2, y2)`（即 `(x+w, y+h)`）。
  * `thickness`: `2` 表示线条厚度为 2 像素。
* **`cv2.putText(img, text, org, fontFace, fontScale, color, thickness)`**
  * `org`: 文本**左下角**起始点坐标。
  * `fontFace`: `cv2.FONT_HERSHEY_SIMPLEX` 标准无衬线字体。

---

## 四、 常见问题与解决方法 (Troubleshooting)

### 1. 误将 NumPy 切片写为 `image[x1:x2, y1:y2]`
* **现象**：裁剪出的图像发生了横竖翻转、尺寸错位或报错 `IndexError`。
* **原因**：OpenCV 图像是矩阵形式，其索引遵循 `[row, col]`（即 `[y, x]`）规则。
* **解决**：永远保持 **`image[y1:y2, x1:x2]`** 的切片顺序。

### 2. 负数坐标导致 NumPy 切片“倒序回绕”
* **现象**：输入 $x = -10$ 时，程序没有报错，但切掉了图像最右侧的像素。
* **原因**：NumPy 支持负数索引（如 `arr[-10:]` 表示取倒数第 10 个元素到结尾）。若未对坐标进行截断，负数坐标会导致切片语义变成“从图像尾部切片”。
* **解决**：在切片前必须通过 `max(0, ...)` 将所有负数坐标强制修正归零。

### 3. `cv2.rectangle` 传参传入了 `(x, y, w, h)`
* **现象**：绘制出来的矩形框非常小或形状异常。
* **原因**：`cv2.rectangle` 的第二个点参数要求传入**右下角坐标 `(x2, y2)`**，而不是宽度和高度。
* **解决**：传参时将右下角点写为 `(x + w, y + h)`。