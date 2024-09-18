import os
from PIL import Image, ImageDraw, ImageFont

output_dir = './PDFs'
source_dir = './pictures/Math/chap_1'

# Kiểm tra nếu thư mục lưu PDF không tồn tại thì tạo mới
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Hàm để cắt và chuyển ảnh thành PDF
def crop_and_convert_image_to_pdf(source_image_path, output_pdf_path, id, pixels_to_cut=165):
    # Mở ảnh gốc
    image = Image.open(source_image_path)
    x2, y2 = image.size
    print(x2, y2)
    # Xác định vùng cần cắt (giữ từ trên đến (height - pixels_to_cut))
    if 'q' in output_pdf_path:
        crop_box = (0, 0, x2, y2 - pixels_to_cut)
    else:   
        crop_box = (0, 0, x2, y2)
    
    # Cắt ảnh theo tọa độ crop_box (giữ phần trên của ảnh)
    cropped_image = image.crop(crop_box)
    
    # Tạo đối tượng ImageDraw để vẽ lên ảnh
    draw = ImageDraw.Draw(cropped_image)
    
    # Chọn font và kích thước chữ (bạn có thể tùy chỉnh)
    try:
        font = ImageFont.truetype("arial.ttf", 20)  # Thay thế đường dẫn tới file font nếu cần
    except IOError:
        font = ImageFont.load_default()  # Sử dụng font mặc định nếu không tìm thấy file font

    # Vị trí bên trái trên cùng để chèn id
    text_position = (5, 5)
    
    # Màu của văn bản (ở đây là màu đen)
    text_color = (0, 0, 0)
    
    # Thêm id vào ảnh
    draw.text(text_position, id, fill=text_color, font=font)
    
    # Chuyển đổi ảnh sang RGB (bắt buộc cho PDF)
    cropped_image_rgb = cropped_image.convert('RGB')
    
    # Lưu ảnh đã cắt dưới dạng PDF
    cropped_image_rgb.save(output_pdf_path)

    print(f"Ảnh đã cắt và lưu thành PDF với id '{id}' được thêm vào.")

# Duyệt qua tất cả các file trong thư mục source_dir
for file in os.listdir(source_dir):
    if file.split('.')[-1].lower() in ('png', 'jpg', 'jpeg'):
        # Đường dẫn file ảnh gốc
        source_image_path = os.path.join(source_dir, file)

        # Đường dẫn file PDF đầu ra
        output_pdf_path = os.path.join(output_dir, f'{file.split(".")[-2]}.pdf')

        id = file.split('.')[0].split('_')[-1]
        # Gọi hàm cắt và chuyển đổi ảnh thành PDF
        crop_and_convert_image_to_pdf(source_image_path, output_pdf_path, id)

        print(f'Đã cắt và lưu file PDF: {output_pdf_path}')
        


# còn 1 vài vấn đề 
# Ví dụ như cách để lấy
