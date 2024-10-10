import json
import os
import shutil
import zipfile
path_dic = {
    'train' : r"C:\Users\VIET HOANG - VTS\Desktop\prompt-based-ViT5\ViTextVQA_train.json",
    "dev" : r"C:\Users\VIET HOANG - VTS\Desktop\prompt-based-ViT5\ViTextVQA_dev.json",
    "test" : r"C:\Users\VIET HOANG - VTS\Desktop\prompt-based-ViT5\ViTextVQA_test.json"
}

# bóc 10 samples mỗi loại từ train, dev,test, xong lấy id của các loại đó từ vinvl, swintext_spotter bỏ vô luôn
def moving_data(path):
    with open(path, 'r', encoding="utf-8") as file:
        data = json.load(file)
    path_vinvl = r"C:\Users\VIET HOANG - VTS\Desktop\VisionReader\data\vinvl_vinvl"
    path_swintext = r"C:\Users\VIET HOANG - VTS\Desktop\VisionReader\data\swintext_spotter"
    # path_images = r"C:\Users\VIET HOANG - VTS\Desktop\VisionReader\data\st_images"
    path_feature = r"C:\Users\VIET HOANG - VTS\Desktop\VisionReader\data\feature_ViT"
    id_dic = {}
    img_list = []
    for i in range(10):
        dt = data['images'][i]
        # print(dt)
        k = data['images'][i]['id']
        if k not in id_dic:
            id_dic[k] = 1
        img_list.append(dt)
    print(img_list)
    img_dic = {
        "images": img_list,
        "annotations": []
    }
    
    print(path, id_dic.keys())

    for row in data["annotations"]:
        if row["id"] in id_dic:
            img_dic["annotations"].append(row)
    
    file_name = path.split('_')[1]
    path_to_save = r"C:\Users\VIET HOANG - VTS\Desktop\VisionReader\data"
    with open(os.path.join(path_to_save, file_name), 'w', encoding='utf-8') as file:
        json.dump(img_dic, file, ensure_ascii=False)

    # moving files
    path_swintext_ori = r"C:\Users\VIET HOANG - VTS\Desktop\prompt-based-ViT5\swintext\swintext_spotter\swintext_spotter"
    # tim nhung file co ten la f'{id_dic.keys()}.npy' roi copy sang path_swintext
    for key in id_dic.keys():
        # Tạo tên file dựa trên key
        file_name = f'{key}.npy'
        # Tạo đường dẫn đầy đủ đến file gốc
        file_path_ori = os.path.join(path_swintext_ori, file_name)
        
        # Kiểm tra xem file có tồn tại ở thư mục gốc không
        if os.path.exists(file_path_ori):
            # Tạo đường dẫn đầy đủ đến file đích
            file_path_dest = os.path.join(path_swintext, file_name)
            # Sao chép file từ thư mục gốc sang thư mục đích
            shutil.copy(file_path_ori, file_path_dest)
            print(f'Sao chép file {file_name} thành công!')

    zip_vinvl_ori = r"C:\Users\VIET HOANG - VTS\Downloads\vinvl_vinvl-002.zip"
    # sao chep cac file co ten la f'{id_dic.keys()}.zip' sang path_vinvl

    with zipfile.ZipFile(zip_vinvl_ori, 'r') as zip_ref:
        # Lặp qua từng key trong id_dic
        for key in id_dic.keys():
            filename = f'{key}.npy'  # Tạo tên file cần tìm trong thư mục 'vinvl_vinvl'
            filepath_in_zip = f'vinvl_vinvl/{filename}'  # Đường dẫn tới tệp bên trong zip
            
            # Kiểm tra nếu tệp tồn tại trong zip
            if filepath_in_zip in zip_ref.namelist():
                # Extract file từ zip và lưu vào thư mục đích
                zip_ref.extract(filepath_in_zip, path_vinvl)
                print(f"Đã sao chép {filename} từ {filepath_in_zip} sang {path_vinvl}")
            else:
                print(f"Tệp {filename} không tồn tại trong {zip_vinvl_ori}")


for value in path_dic.values():
    moving_data(value)