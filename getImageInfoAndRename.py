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
    xmp_data = image.info.get('xmp', '')  # 获取 xmp 数据
    if not xmp_data:
        print(f"无法从 {image_path} 获取 XMP 数据")
        return None

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

def get_files(directory):
    # 获取指定目录下所有的 .NEF 和 .XMP 文件路径
    files = []
    
    for root, dirs, files_in_dir in os.walk(directory):
        for file in files_in_dir:
            if file.lower().endswith('.nef'):#  or file.lower().endswith('.xmp'):
                files.append(os.path.join(root, file))
    
    return files

def ensure_unique_file_name(target_directory, file_name, file_extension):
    # 检查文件是否已存在，并确保文件名唯一
    new_file_name = file_name + file_extension
    counter = 1
    while os.path.exists(os.path.join(target_directory, new_file_name)):
        # 文件已存在，添加递增数字
        new_file_name = f"{file_name}_{counter}{file_extension}"
        counter += 1
    return new_file_name

def copy_and_rename_files(img_path, target_directory):
    _, file_extension = os.path.splitext(img_path)
    new_file_name = get_and_rename(img_path)  # 获取新文件名
    if new_file_name is None:
        return

    # 确保文件名唯一
    new_file_name = ensure_unique_file_name(target_directory, new_file_name, file_extension)
    new_file_path = os.path.join(target_directory, new_file_name)

    shutil.copy2(img_path, new_file_path)  # 拷贝 .NEF 文件

    # 查找是否有对应的 .XMP 文件并重命名拷贝
    # if file_extension.lower() == '.nef':
    xmp_file = img_path.replace('.NEF', '.xmp')
    acr_file = img_path.replace('.NEF', '.acr')
    
    if os.path.exists(xmp_file):
        # print("img_path", img_path)
        # print("xmp_file", xmp_file)
        
        xmp_new_file_name = new_file_name.replace('.NEF', '.xmp')
        xmp_new_file_path = os.path.join(target_directory, xmp_new_file_name)

        shutil.copy2(xmp_file, xmp_new_file_path)  # 拷贝 .XMP 文件
        # print(f"文件 {xmp_file} 已拷贝并重命名为: {xmp_new_file_path}")

    if os.path.exists(acr_file):
        # print("img_path", img_path)
        # print("acr_file", acr_file)
        
        acr_new_file_name = new_file_name.replace('.NEF', '.acr')
        acr_new_file_path = os.path.join(target_directory, acr_new_file_name)

        shutil.copy2(acr_file, acr_new_file_path)  # 拷贝 .XMP 文件
        # print(f"文件 {acr_file} 已拷贝并重命名为: {acr_new_file_path}")
        # exit()

    # print(f"文件 {img_path} 已拷贝并重命名为: {new_file_path}")

def main(src_folder, target_directory):
    start_time = time.time()
    image_paths = get_files(src_folder)

    # 使用 tqdm 显示进度条
    with tqdm(total=len(image_paths), desc="Processing files", unit="file") as pbar:
        for img_path in image_paths:
            copy_and_rename_files(img_path, target_directory)  # 拷贝并重命名文件
            pbar.update(1)  # 更新进度条

    # 记录结束时间
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"总共耗时: {elapsed_time:.2f} 秒")

if __name__ == "__main__":
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="Renames and copies NEF and XMP files.")
    parser.add_argument('src_folder', type=str, help="源文件夹路径（.NEF 和 .XMP 文件所在的文件夹）")
    parser.add_argument('target_directory', type=str, help="目标文件夹路径（拷贝并重命名后的文件夹）")

    # 解析命令行参数
    args = parser.parse_args()

    # 调用主函数
    main(args.src_folder, args.target_directory)
