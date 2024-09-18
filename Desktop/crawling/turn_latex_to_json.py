import json
import re



def extract_questions_from_latex(latex):
    # Tìm tất cả các block câu hỏi và lời giải (tìm theo ID câu hỏi và chia khối)
    blocks = re.split(r"(\\section\*\{T\d+\})", latex)  # Tìm tất cả các phần ID câu hỏi

    questions_data = []
    
    # Xử lý trường hợp nếu đoạn đầu tiên của tài liệu không bắt đầu bằng \section*{T...}
    if not latex.startswith("\\section*{T"):
        # Nếu không có \section*{T...} ở đầu tài liệu, lấy nội dung trước phần đầu tiên của \section*{T...}
        pre_block = re.split(r"(\\section\*\{T\d+\})", latex, maxsplit=1)
        if len(pre_block) > 1:
            # Lấy phần câu hỏi trước \section*{T...} đầu tiên
            questions_data.extend(process_question_block("T0101001", pre_block[0]))  # ID giả định cho câu hỏi đầu

    for i in range(1, len(blocks), 2):  # Lặp qua các cặp (ID và nội dung)
        question_id_block = blocks[i]
        block = blocks[i + 1]

        # Trích xuất ID câu hỏi (ID đi kèm với \section*{T...})
        id_match = re.search(r"\\section\*\{(T\d+)\}", question_id_block)
        question_id = id_match.group(1) if id_match else None

        # Trích xuất và xử lý câu hỏi
        questions_data.extend(process_question_block(question_id, block))
    
    return questions_data


def process_question_block(question_id, block):
    # Loại bỏ các phần bảng biểu hoặc hình ảnh trong block, nhưng giữ lại câu hỏi
    block_cleaned = re.sub(r"\\begin\{tabular\}.*?\\end\{tabular\}", "", block, flags=re.DOTALL)  # Loại bỏ bảng
    block_cleaned = re.sub(r"\\includegraphics\[.*?\]\{.*?\}", "", block_cleaned, flags=re.DOTALL)  # Loại bỏ hình ảnh
    block_cleaned = re.sub(r"\\begin\{center\}.*?\\end\{center\}", "", block_cleaned, flags=re.DOTALL)  # Loại bỏ phần center


    # Trích xuất câu hỏi chính (loại bỏ tất cả các lựa chọn)
    question_match = re.search(r"Câu \d+\\\\\s*(.*?)(?=[A-D]\.\s)", block_cleaned, re.DOTALL)
    if question_match is None:
        question_match = re.search(r"\\section\*\{Câu \d+\}(.*?)(?=[A-D]\.\s)", block_cleaned, re.DOTALL)
    question = question_match.group(1).strip() if question_match else None

    # Nếu không tìm thấy câu hỏi, bỏ qua
    if not question:
        print(f"Không tìm thấy câu hỏi cho ID: {question_id}")
        return []

    # Trích xuất các lựa chọn (A, B, C, D)
    options = re.findall(r"([A-D])\.\s*(.*?)\s*(?=\\\\|\n|$)", block_cleaned)

    # Trích xuất lời giải
    explanation_match = re.search(r"\\section\*\{Lời giải.*?\}(.*?)(?=(Đáp án cần chọn là|\\section\*\{T\d+\}))", block_cleaned, re.DOTALL)
    explanation = explanation_match.group(1).strip() if explanation_match else None

    # Tạo đối tượng JSON
    question_data = {
        "id": question_id,
        "question": question,  # Chỉ chứa phần câu hỏi
        "options": [f"{opt[0]}. {opt[1]}" for opt in options],
        "explain": explanation
    }

    return [question_data]

# Đọc file LaTeX
path_r = r"C:\Users\VIET HOANG - VTS\Downloads\merged_output2\2024_09_17_b028d14ae51ffffc165dg\2024_09_17_b028d14ae51ffffc165dg.tex"
path_f = "test.tex"
with open(path_r, 'r', encoding='utf-8') as file:
    latex_text = file.read()

# Chuyển đổi LaTeX thành danh sách JSON format
questions_json = extract_questions_from_latex(latex_text)

# Chuyển đổi kết quả thành JSON (giữ nguyên LaTeX trong chuỗi)
json_output = json.dumps(questions_json, ensure_ascii=False, indent=4)
json_output = json_output.replace("\\\\", '\\')
print(json_output)


# problem 1 : xóa các bảng biểu, cột, hình ()
# problem 2 : có những câu ko lấy dc explain (lấy dc hết r)
# problem 3 : tại sao lại khi có \ thì lại hiện tận 2 cái \\ vậy (có vẻ là solve được)

