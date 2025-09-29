import numpy as np

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

def sub_image(image,boxes):
    images=[]
    for box in boxes:
        bbox=box["coordinate"]
        if len(bbox) == 4:
            xmin, ymin, xmax, ymax = bbox
        elif len(bbox) == 8:
            x1, y1, x2, y2, x3, y3, x4, y4 = bbox
            xmin, ymin, xmax, ymax = min(x1, x2, x3, x4), min(y1, y2, y3, y4), max(x1, x2, x3, x4), max(y1, y2, y3, y4)
        # 创建ROI的副本，避免修改原始图像
        roi=image[int(ymin):int(ymax),int(xmin):int(xmax)].copy()
        images.append(roi)
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
