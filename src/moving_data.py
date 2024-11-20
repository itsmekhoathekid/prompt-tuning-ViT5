import json
import os
import shutil
import zipfile
path_dic = {
    'train' : r"C:\Users\VIET HOANG - VTS\Desktop\prompt-based-ViT5\ViTextVQA_train.json",
    "dev" : r"C:\Users\VIET HOANG - VTS\Desktop\prompt-based-ViT5\ViTextVQA_dev.json",
    "test" : r"C:\Users\VIET HOANG - VTS\Desktop\prompt-based-ViT5\ViTextVQA_test.json"
}

# # bóc 10 samples mỗi loại từ train, dev,test, xong lấy id của các loại đó từ vinvl, swintext_spotter bỏ vô luôn
# def moving_data(path):
#     with open(path, 'r', encoding="utf-8") as file:
#         data = json.load(file)
#     path_vinvl = r"C:\Users\VIET HOANG - VTS\Desktop\VisionReader\data\vinvl_vinvl"
#     path_swintext = r"C:\Users\VIET HOANG - VTS\Desktop\VisionReader\data\swintext_spotter"
#     # path_images = r"C:\Users\VIET HOANG - VTS\Desktop\VisionReader\data\st_images"
#     path_feature = r"C:\Users\VIET HOANG - VTS\Desktop\VisionReader\data\feature_ViT"
#     id_dic = {}
#     img_list = []
#     count = 0
#     # Tìm những annotation và image có ID khớp nhau
#     for annotation in data['annotations']:
#         annotation_id = annotation['image_id']  # Lấy ID của image từ annotations

#         # Kiểm tra nếu ID tồn tại trong 'images'
#         for image in data['images']:
#             if image['id'] == annotation_id:  # Nếu ID khớp trong cả annotations và images
#                 img_list.append(annotation)  # Thêm annotation vào danh sách
#                 id_dic[annotation_id] = True  # Đánh dấu ID này đã được thêm vào
                
#                 count += 1  # Tăng biến đếm
#         if count == 30:
#             break

#     # Tạo img_dic để lưu các cặp khớp
#     img_dic = {
#         "images": [],
#         "annotations": img_list
#     }

#     # Thêm các hình ảnh có ID tương ứng với annotations
#     for image in data['images']:
#         if image['id'] in id_dic:  # Chỉ thêm các image có ID đã khớp với annotations
#             img_dic['images'].append(image)

#     print(id_dic.keys())
#     print(len(img_dic["images"]))
    # file_name = path.split('_')[1]
    # path_to_save = r"C:\Users\VIET HOANG - VTS\Desktop\VisionReader\data"
    # with open(os.path.join(path_to_save, file_name), 'w', encoding='utf-8') as file:
    #     json.dump(img_dic, file, ensure_ascii=False)

    # # moving files
    # path_swintext_ori = r"C:\Users\VIET HOANG - VTS\Desktop\prompt-based-ViT5\swintext\swintext_spotter\swintext_spotter"
    # # tim nhung file co ten la f'{id_dic.keys()}.npy' roi copy sang path_swintext
    # for key in id_dic.keys():
    #     # Tạo tên file dựa trên key
    #     file_name = f'{key}.npy'
    #     # Tạo đường dẫn đầy đủ đến file gốc
    #     file_path_ori = os.path.join(path_swintext_ori, file_name)
        
    #     # Kiểm tra xem file có tồn tại ở thư mục gốc không
    #     if os.path.exists(file_path_ori):
    #         # Tạo đường dẫn đầy đủ đến file đích
    #         file_path_dest = os.path.join(path_swintext, file_name)
    #         # Sao chép file từ thư mục gốc sang thư mục đích
    #         shutil.copy(file_path_ori, file_path_dest)
    #         print(f'Sao chép file {file_name} thành công!')

    # zip_vinvl_ori = r"C:\Users\VIET HOANG - VTS\Downloads\vinvl_vinvl-002.zip"
    # # sao chep cac file co ten la f'{id_dic.keys()}.zip' sang path_vinvl

    # with zipfile.ZipFile(zip_vinvl_ori, 'r') as zip_ref:
    #     # Lặp qua từng key trong id_dic
    #     for key in id_dic.keys():
    #         filename = f'{key}.npy'  # Tạo tên file cần tìm trong thư mục 'vinvl_vinvl'
    #         filepath_in_zip = f'vinvl_vinvl/{filename}'  # Đường dẫn tới tệp bên trong zip
            
    #         # Kiểm tra nếu tệp tồn tại trong zip
    #         if filepath_in_zip in zip_ref.namelist():
    #             # Extract file từ zip và lưu vào thư mục đích
    #             zip_ref.extract(filepath_in_zip, path_vinvl)
    #             print(f"Đã sao chép {filename} từ {filepath_in_zip} sang {path_vinvl}")
    #         else:
    #             print(f"Tệp {filename} không tồn tại trong {zip_vinvl_ori}")


# for value in path_dic.values():
#     moving_data(value)


# import os
# import shutil

# # Đường dẫn đến các tệp .npy trong vinvl_vinvl và swintext_spotter
# path_vinvl = r"C:\Users\VIET HOANG - VTS\Desktop\VisionReader\data\vinvl_vinvl"
# path_swintext = r"C:\Users\VIET HOANG - VTS\Desktop\VisionReader\data\swintext_spotter"

# # Đường dẫn tới thư mục chứa ảnh
# source_images_folder = r"C:\Users\VIET HOANG - VTS\Desktop\prompt-based-ViT5\ViTextVQA_images\st_images"

# # Đường dẫn đến thư mục đích để lưu các tệp ảnh đã sao chép
# destination_folder = r"C:\Users\VIET HOANG - VTS\Desktop\VisionReader\data\st_images"

# # Đảm bảo rằng thư mục đích tồn tại
# os.makedirs(destination_folder, exist_ok=True)

# # Hàm để sao chép tệp ảnh dựa trên danh sách tệp .npy từ một thư mục nhất định
# def copy_images_from_npy_folder(npy_folder):
#     # Lấy danh sách các tệp .npy trong thư mục
#     npy_files = [f for f in os.listdir(npy_folder) if f.endswith('.npy')]

#     # Lặp qua từng tệp .npy và tìm ảnh tương ứng
#     for npy_file in npy_files:
#         # Lấy tên tệp (bỏ phần mở rộng .npy)
#         file_name = os.path.splitext(npy_file)[0]
        
#         # Tên tệp ảnh tương ứng trong thư mục source_images_folder
#         image_file = f"{file_name}.jpg"  # Giả sử ảnh có định dạng .jpg (có thể thay đổi nếu cần)

#         # Đường dẫn đầy đủ đến tệp ảnh
#         source_image_path = os.path.join(source_images_folder, image_file)
#         destination_image_path = os.path.join(destination_folder, image_file)

#         # Kiểm tra nếu tệp ảnh tồn tại trong thư mục source_images_folder
#         if os.path.isfile(source_image_path):
#             # Sao chép tệp ảnh sang thư mục đích
#             shutil.copy(source_image_path, destination_image_path)
#             print(f"Đã sao chép {image_file} từ {source_images_folder} sang {destination_folder}")
#         else:
#             print(f"Tệp ảnh {image_file} không tồn tại trong {source_images_folder}")

# # Thực hiện sao chép cho cả thư mục vinvl và swintext
# copy_images_from_npy_folder(path_vinvl)
# copy_images_from_npy_folder(path_swintext)

import torch
print(torch.version.cuda)
print(torch.backends.cudnn.version())
