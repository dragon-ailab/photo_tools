import argparse
from PIL import Image
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import shutil
import time
from tqdm import tqdm

def get_and_rename(image_path):
    image = Image.open(image_path)
    xmp_data = image.info['xmp']  # xmp 数据（你可以从 image.info['xmp'] 获取）
    root = ET.fromstring(xmp_data)  # 解析 xmp 数据
    # 提取时间信息
    create_date = root.find('.//xmp:CreateDate', namespaces={'xmp': 'http://ns.adobe.com/xap/1.0/'})
    # 提取相机信息
    creator_tool = root.find('.//xmp:CreatorTool', namespaces={'xmp': 'http://ns.adobe.com/xap/1.0/'})

    if create_date is not None:
        create_date_obj = datetime.strptime(create_date.text, '%Y-%m-%dT%H:%M:%S.%f')
        formatted_time = create_date_obj.strftime('%Y-%m-%d.%H-%M-%S')
    else:
        print(f"未找到创建时间: {image_path}")
        return None

    if creator_tool is not None:
        camera_model = creator_tool.text.strip().split(' Ver')[0].replace(" ", "_")
    else:
        print(f"未找到相机型号: {image_path}")
        return None

    file_name = f"{camera_model}.{formatted_time}"
    return file_name

def get_nef_files(directory):
    # 获取指定目录下所有的 .NEF 文件路径
    nef_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.nef'):
                nef_files.append(os.path.join(root, file))
    
    return nef_files

def ensure_unique_file_name(target_directory, file_name, file_extension):
    # 检查文件是否已存在，并确保文件名唯一
    new_file_name = file_name + file_extension
    counter = 1
    while os.path.exists(os.path.join(target_directory, new_file_name)):
        # 文件已存在，添加递增数字
        new_file_name = f"{file_name}_{counter}{file_extension}"
        counter += 1
    return new_file_name

def main(src_folder, target_directory):
    start_time = time.time()
    image_paths = get_nef_files(src_folder)

    # 使用 tqdm 显示进度条
    with tqdm(total=len(image_paths), desc="Processing images", unit="file") as pbar:
        for img_path in image_paths:
            _, file_extension = os.path.splitext(img_path)
            new_file_name = get_and_rename(img_path)  # 获取新文件名
            if new_file_name is None:
                pbar.update(1)  # 进度条更新
                continue  # 如果文件名无效，则跳过该文件
            new_file_name = ensure_unique_file_name(target_directory, new_file_name, file_extension)  # 确保文件名唯一
            new_file_path = os.path.join(target_directory, new_file_name)
            shutil.copy2(img_path, new_file_path)
            # print(f"文件已拷贝并重命名为: {new_file_path}")
            pbar.update(1)  # 进度条更新

    # 记录结束时间
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"总共耗时: {elapsed_time:.2f} 秒")

if __name__ == "__main__":
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="重命名并拷贝NEF文件")
    parser.add_argument('src_folder', type=str, help="源文件夹路径（.NEF 文件所在的文件夹）")
    parser.add_argument('target_directory', type=str, help="目标文件夹路径（拷贝并重命名后的文件夹）")

    # 解析命令行参数
    args = parser.parse_args()

    # 调用主函数
    main(args.src_folder, args.target_directory)
