import numpy as np
import cv2
    
"""
Workflow 工具类，包含通用的工作流辅助函数
"""

def parse_port(port: str) -> tuple[str, str]:
    """
    解析端口字符串为端口类型和端口名称

    Args:
        port: 端口字符串，格式应为 'port_type.port_name'

    Returns:
        tuple: (port_type, port_name) 二元组

    Raises:
        ValueError: 当端口格式不正确时抛出
    """
    port_parts = port.split('.', 1)
    if len(port_parts) == 2:
        return port_parts[0], port_parts[1]
    else:
        raise ValueError(f"端口格式不正确: {port}，应为 'port_type.port_name' 格式")

def sub_image(image, boxes):
    """
    根据边界框从原始图像中裁剪出子图像，支持旋转矩形
    
    Args:
        image: 原始图像，ndarray类型
        boxes: 边界框列表，每个边界框包含'coordinate'字段，
              可以是4点格式[xmin, ymin, xmax, ymax]或8点格式[x1, y1, x2, y2, x3, y3, x4, y4]
    
    Returns:
        list: 裁剪后的子图像列表
    """

    images = []
    for box in boxes:
        try:
            bbox = box["coordinate"]
            if len(bbox) == 4:
                # 处理普通矩形
                xmin, ymin, xmax, ymax = map(int, map(round, bbox))
                
                # 确保坐标在图像范围内
                img_height, img_width = image.shape[:2]
                xmin_clamped = max(0, xmin)
                ymin_clamped = max(0, ymin)
                xmax_clamped = min(img_width, xmax)
                ymax_clamped = min(img_height, ymax)
                
                # 跳过无效的边界框
                if xmax_clamped <= xmin_clamped or ymax_clamped <= ymin_clamped:
                    continue
                
                # 创建ROI的副本
                roi = image[ymin_clamped:ymax_clamped, xmin_clamped:xmax_clamped].copy()
                images.append(roi)
            elif len(bbox) == 8:
                # 使用掩码方式处理旋转矩形
                # 将8点转换为4个角点（假设顺序是顺时针或逆时针的四个顶点）
                pts = np.array(bbox, dtype=np.int32).reshape((-1, 1, 2))
                
                # 创建与原图相同大小的掩码
                mask = np.zeros(image.shape[:2], dtype=np.uint8)
                
                # 在掩码上填充旋转矩形区域
                cv2.fillPoly(mask, [pts], 255)
                
                # 计算包围盒
                x_coords = pts[:, 0, 0]
                y_coords = pts[:, 0, 1]
                xmin = max(0, int(min(x_coords)))
                ymin = max(0, int(min(y_coords)))
                xmax = min(image.shape[1], int(max(x_coords)))
                ymax = min(image.shape[0], int(max(y_coords)))
                
                # 跳过无效的边界框
                if xmax <= xmin or ymax <= ymin:
                    continue
                
                # 裁剪原始图像和掩码
                roi = image[ymin:ymax, xmin:xmax].copy()
                cropped_mask = mask[ymin:ymax, xmin:xmax].copy()
                
                # 应用掩码 - 使用NumPy的索引操作
                # 将掩码为0的区域设为0
                roi[cropped_mask == 0] = 0
                
                images.append(roi)
        except Exception as e:
            print(f"处理边界框时出错: {e}")
            continue
    
    return images

def sub_image_with_mask(image, boxes, masks):
    """
    简化版：直接根据bbox的位置和mask的宽高从原图像中裁剪出目标区域
    
    Args:
        image: 原始图像
        boxes: 边界框列表
        masks: 对应每个矩形内的mask，形状为[行,列]，ndarray类型
        
    Returns:
        list: 裁剪后的图像列表
    """

    images = []
    
    # 确保boxes和masks数量一致
    if len(boxes) != len(masks):
        raise ValueError(f"boxes和masks数量不匹配: {len(boxes)} vs {len(masks)}")
        
    for box, mask in zip(boxes, masks):
        try:
            # 确保mask是ndarray类型并为二维
            if not isinstance(mask, np.ndarray):
                mask = np.array(mask)
            
            if len(mask.shape) != 2 or mask.size == 0:
                continue  # 跳过无效mask
            
            # 获取bbox坐标
            bbox = box["coordinate"]
            if len(bbox) == 4:
                xmin, ymin, xmax, ymax = map(int, map(round, bbox))
            elif len(bbox) == 8:
                # 处理8点边界框
                x_coords = bbox[::2]  # x1, x2, x3, x4
                y_coords = bbox[1::2]  # y1, y2, y3, y4
                xmin, ymin = int(round(min(x_coords))), int(round(min(y_coords)))
                xmax, ymax = int(round(max(x_coords))), int(round(max(y_coords)))
            else:
                raise ValueError(f"边界框格式不正确: {bbox}")
            
            # 确保坐标在图像范围内
            img_height, img_width = image.shape[:2]
            xmin_clamped = max(0, xmin)
            ymin_clamped = max(0, ymin)
            xmax_clamped = min(img_width, xmax)
            ymax_clamped = min(img_height, ymax)
            
            # 如果边界框无效，跳过
            if xmax_clamped <= xmin_clamped or ymax_clamped <= ymin_clamped:
                continue
            
            # 裁剪原始图像
            roi = image[ymin_clamped:ymax_clamped, xmin_clamped:xmax_clamped].copy()
            
            # 确保mask是二值图像
            mask = (mask > 0).astype(np.uint8)
            
            # 如果mask尺寸与ROI不一致，直接裁剪mask到ROI大小
            if mask.shape[:2] != roi.shape[:2]:
                # 直接裁剪mask到ROI尺寸（取左上角部分）
                mask = mask[:roi.shape[0], :roi.shape[1]]
            
            # 应用掩码 - 使用NumPy的广播机制，同时支持彩色和灰度图像
            roi[mask == 0] = 0
            
            images.append(roi)
        except Exception as e:
            print(f"处理图像时出错: {e}")
            continue
    
    return images

def sub_image_with_pred(image, pred):
    """
    根据语义分割掩码截取图片，为每种类型掩码值返回一张图片，图片大小与原图相同
    
    Args:
        image: 原始图像，ndarray类型，形状为[行,列,通道]
        pred: 语义分割掩码，ndarray类型，形状为[行,列]，值为每个像素对应的类别掩码值
    
    Returns:
        list: 不同类别掩码对应的子图像列表，每个元素是一个字典，包含'image'和'category'键
    """
    images = []
    
    try:
        # 确保pred是ndarray类型并为二维
        if not isinstance(pred, np.ndarray):
            pred = np.array(pred)
        
        # 检查pred和image的尺寸是否匹配，如果不匹配则缩放pred到图像尺寸
        if pred.shape[:2] != image.shape[:2]:
            # 使用cv2.resize将pred缩放到与image相同的尺寸
            # 使用INTER_NEAREST插值方法以保持像素的类别值不变
            pred = cv2.resize(pred, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
        
        # 获取所有不同的类别值
        unique_categories = np.unique(pred)
        
        # 对每个类别值生成对应的图像
        for category in unique_categories:
            # 跳过背景类别（假设背景类别为0）
            # if category == 0:
            #     continue
            
            # 创建原图的副本
            result_img = image.copy()
            result_img[pred != category] = 0
            images.append(result_img)
            
    except Exception as e:
        print(f"处理语义分割掩码时出错: {e}")
        
    return images
