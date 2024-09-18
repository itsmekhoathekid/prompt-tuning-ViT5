from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.common.exceptions import NoSuchElementException
import os
import json 
import time
import re
import os
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

def Create_webdriver():
    options = webdriver.EdgeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument("--window-size=1500,1000")
    options.add_argument("--disable-notifications")

    # Khởi tạo WebDriver cho Microsoft Edge
    driver = webdriver.Edge(
        service=Service(EdgeChromiumDriverManager().install()),
        options=options
    )
    return driver

def Click_start_button(driver):
    try:
        # Tìm nút "Bắt đầu" bằng class
        start_button = driver.find_element(By.CSS_SELECTOR, 'a.text-white.btn-green.btn-action')
        start_button.click()
        print("Đã click vào nút 'Bắt đầu'")
        time.sleep(2)  # Chờ trang tải câu hỏi
    except NoSuchElementException:
        print("Không tìm thấy nút 'Bắt đầu'")

def Select_type_of_question(driver):
    try:
        # Tìm nút "Bắt đầu" bằng class
        _button = driver.find_element(By.CSS_SELECTOR, 'div.icon.iconKingHat')
        _button.click()
        print("Đã click vào nút 'Làm tất cả'")
        time.sleep(2)  # Chờ trang tải câu hỏi
    except NoSuchElementException:
        print("Không tìm thấy nút 'Làm tất cả'")

def Dump_contents_Json(id,question,img_src,difficulty,options,answer,explain,name_file):
    data = {
        "id":id,
        "question": question,
        "image_source":img_src,
        "difficulty":difficulty,
        "options": [options[i] for i in range(len(options))],
        "answer": answer,
        "explain":explain
    }
    file_path = os.path.join(f'D:\Code\Python\projects', name_file)
    with open(file_path, 'a', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def get_question(driver):
    question_text = driver.find_element(By.CSS_SELECTOR, 'div.content-quiz.mg-top-10').text
    question_text_cleaned = re.sub(r'\s+', ' ', question_text).strip()
    print(question_text_cleaned)

    return question_text_cleaned

def get_difficulty(driver):
    # difficulty_text = ''
    # try:
    #     difficulty_text = driver.find_element(By.CSS_SELECTOR,'span.clf.pull-right.bgblue1').text
    #     try: 
    #         difficulty_text = driver.find_element(By.CSS_SELECTOR,'span.clf.pull-right.bglogo2').text
    difficulty_text = driver.find_element(By.CSS_SELECTOR,'div.vn-tit-question span').text

    return difficulty_text

# Crawl Toan
# def get_options(driver):
#     options = []
#     options_elements = driver.find_elements(By.CSS_SELECTOR, 'div.cursor-pointer.mg-bottom-10.col-xs-6.col-md-6.col-sm-4')
                                                                    
#     for element in options_elements:
#         text = element.text
#         option_cleaned = re.sub(r'\s+', ' ', text).strip()
#         options.append(option_cleaned)
#         print(option_cleaned)

#     return options

# Crawl VatLi
def get_options(driver):
    options = []
    css_selectors = [
        'div.cursor-pointer.mg-bottom-10.col-xs-12.col-md-12.col-sm-4',
        'div.cursor-pointer.mg-bottom-10.col-xs-6.col-md-6.col-sm-4',
        'div.cursor-pointer.mg-bottom-10.col-xs-3.col-md-3.col-sm-4'
    ]

    options_elements = None

    for selector in css_selectors:
        try:
            options_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if options_elements:
                break  
        except:
            continue 

    if not options_elements:
        return options  

    for element in options_elements:
        text = element.text
        option_cleaned = re.sub(r'\s+', ' ', text).strip()
        options.append(option_cleaned)
        print(option_cleaned)

    return options

def select_key_and_get_answer_and_explain(driver):
    circle_select = driver.find_element(By.CSS_SELECTOR,'span.arround-select')
    circle_select.click()
    time.sleep(4)
    check_button = driver.find_element(By.CSS_SELECTOR,'a.false.cursor-pointer.text-white.btn-green.btn-action.visible')
    check_button.click()
    time.sleep(4)
    try:
        # status_ans = driver.find_element(By.CSS_SELECTOR,'span.font-roboto-b.font-size-18.color-green').text
        # if status_ans == 'Bạn đã chọn đúng':
            explain_button = driver.find_element(By.CSS_SELECTOR,'a.cursor-pointer.bg-grey.btn-action') 
            explain_button.click()
            time.sleep(3)
            explain_text = driver.find_elements(By.CSS_SELECTOR,'div.solution-item')
            explain_element = explain_text[-1]
    except:
        explain_text = driver.find_elements(By.CSS_SELECTOR,'div.solution-item')
        explain_element = explain_text[-1]
    driver.execute_script("arguments[0].scrollIntoView();", explain_element)
    # take_element_screenshot(driver,explain_element,folder_path,file_name,pdf=pdf)
    # explain_text = explain_text[-1].text
    # explain_text_cleaned = re.sub(r'\s+', ' ', explain_text).strip()
    # print(explain_text_cleaned)
    # key_answer = explain_text_cleaned[-1]
    # print(key_answer)
    return explain_element

def get_url_image(driver):
    try:
        element = driver.find_element(By.CSS_SELECTOR, 'div.content-quiz.mg-top-10 img')
        src = element.get_attribute('src')
        print(src)
        
        return src
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def Click_next_question(driver):
    next_question_button = driver.find_element(By.CSS_SELECTOR,'a.cursor-pointer.text-white.btn-green.btn-action.visible')
    next_question_button.click()
    time.sleep(5)

def get_QAs_element(driver):
    QAs_element = driver.find_element(By.CSS_SELECTOR, 'div.col-sm-11')
    return QAs_element

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
    
    
    
    # Thêm id vào ảnh
    if 'q_' in output_pdf_path:
        # Chọn font và kích thước chữ (bạn có thể tùy chỉnh)
        try:
            font = ImageFont.truetype("arial.ttf", 30)  # Thay thế đường dẫn tới file font nếu cần
        except IOError:
            font = ImageFont.load_default()  # Sử dụng font mặc định nếu không tìm thấy file font
        
        # Vị trí bên trái trên cùng để chèn id
        text_position = (15, 15)
        
        # Màu của văn bản (ở đây là màu đen)
        text_color = (0, 0, 0)
        draw.text(text_position, id, fill=text_color, font=font)
    
    # Chuyển đổi ảnh sang RGB (bắt buộc cho PDF)
    cropped_image_rgb = cropped_image.convert('RGB')
    
    # Lưu ảnh đã cắt dưới dạng PDF
    cropped_image_rgb.save(output_pdf_path)

    print(f"Ảnh đã cắt và lưu thành PDF với id '{id}' được thêm vào.")


import os
from pypdf import PdfMerger

def merge_pdfs(pdf_list, output_pdf):
    merger = PdfMerger()
    
    # Thêm từng file PDF vào đối tượng merger
    for pdf in pdf_list:
        merger.append(pdf)
    
    # Lưu kết quả gộp thành file mới
    merger.write(output_pdf)
    merger.close()
    print(f"Đã gộp các file PDF thành: {output_pdf}")

def take_element_screenshot(driver, element, folder_path, pdf_file_name, pdf, id): 
    # Kiểm tra nếu thư mục tồn tại, nếu không thì tạo mới
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Tạo một trang mới cho file PDF
    pdf.add_page()
    
    time.sleep(4)
    # Chụp ảnh màn hình của phần tử câu hỏi và lưu tạm thời dưới dạng PNG
    screenshot_file_path = os.path.join(folder_path, f'q_{id}.png')
    element.screenshot(screenshot_file_path)
    
    # Chụp ảnh phần tử câu trả lời
    element2 = select_key_and_get_answer_and_explain(driver)  # Giả sử hàm này trả về phần tử web
    screenshot_file_path_answer = os.path.join(folder_path, f'a_{id}.png')
    time.sleep(4)
    element2.screenshot(screenshot_file_path_answer)

    # Loại bỏ phần mở rộng .png trước khi thêm .pdf
    qa_pdf = os.path.splitext(screenshot_file_path)[0] + '.pdf'
    qa_pdf_answer = os.path.splitext(screenshot_file_path_answer)[0] + '.pdf'

    # Chuyển đổi ảnh PNG sang PDF
    crop_and_convert_image_to_pdf(screenshot_file_path, qa_pdf, id, pixels_to_cut=165)
    crop_and_convert_image_to_pdf(screenshot_file_path_answer, qa_pdf_answer, id, pixels_to_cut=165)
    
    # Gộp 2 file PDF lại với nhau
    merged_pdf_path = os.path.join(folder_path, f'{id}.pdf')
    merge_pdfs([qa_pdf, qa_pdf_answer], merged_pdf_path)

    # Xóa các file tạm
    os.remove(screenshot_file_path_answer)
    os.remove(screenshot_file_path)
    os.remove(qa_pdf)
    os.remove(qa_pdf_answer)
    



file_path = 'Link_Maths.json'
with open(file_path, 'r', encoding='utf-8') as file:
    links_physics = json.load(file)


for chapter in range(1,8):
    j = 0
    for link in links_physics[str(chapter)].keys():
        
        driver = Create_webdriver()
        driver.get(link)

        Click_start_button(driver)
        Select_type_of_question(driver)
        
        
        try:
            for i in range(1,10):



                j+=1
                with open('Link_Maths.json', 'r', encoding='utf-8') as file:
                    links_physics = json.load(file)
                    dic1 = links_physics[str(chapter)]
                    lesson = int(dic1[link])
                    
                lesson_str = '{:02}'.format(lesson)
                suffix = '{}{:03}'.format(lesson_str, j)
                prefix = f'T{str(chapter).zfill(2)}'
                id = f"{prefix}{suffix}"
                try:
                    QAs = get_QAs_element(driver)
                    pdf = FPDF()
                    take_element_screenshot(driver, element=QAs, folder_path=f'pictures//Math//chap_{chapter}',
                                            pdf_file_name=f'qa_{id}',pdf=pdf, id = id)
                    time.sleep(4)
                    question = get_question(driver)
                    difficulty = get_difficulty(driver)
                    options = get_options(driver)
                    src = get_url_image(driver)
                    
                    
                    Click_next_question(driver)
                    
                    # Dump_contents_Json(id, question, src, difficulty, options, answer, explain ,'Chemistry_C1.NO1.json')

                    print(f"==================Question {i} processed and saved.=====================")
                except NoSuchElementException as e:
                    try:
                        time.sleep(4)
                        go_head_button = driver.find_element(By.CSS_SELECTOR,'a.cursor-pointer.text-white.bg-green.btn-action')
                        go_head_button.click()
                        time.sleep(4)
                    except:
                        continue
        
                
        finally:
            # print("==============xong==================")
            driver.quit()    


