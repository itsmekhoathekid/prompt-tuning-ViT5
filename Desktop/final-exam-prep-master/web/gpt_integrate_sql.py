from openai import OpenAI
from dotenv import load_dotenv 
import json
import requests
import os
from data_retriever_sql import DrawTotal, DrawChap
from predict_threshold_sql import PrepThreshold, PredictThreshold
import csv
from datetime import datetime
import time 
import pandas as pd
from app import create_app, db, login_manager, bcrypt
from models import User, Progress, Test, Universities, QAs, Subject, SubjectCategory

load_dotenv()


# prompt creation
class promptCreation:
    def __init__(self, type_test, num_test, subject, num_chap = None):
        self.type_test = type_test
        self.num_test = num_test
        self.num_chap = num_chap
        self.prompt = "Bạn là một gia sư dạy kèm"
        self.final_exam_date = "2025-06-27"
        self.subject = subject
        self.aim_score = 9
        self.data = DrawTotal(self.subject, None, self.type_test, self.num_test) if self.type_test == 1 else DrawChap(self.subject, self.num_chap, self.type_test, self.num_test)
        self.test_intro = self.get_test_intro()
        self.subject_intro = f"Đây là kết quả môn {self.return_subject_name()}"
        self.detail_analyze_prompt = (f"Lưu ý là thêm số liệu cụ thể để phân tích cho kĩ lưỡng nha, Từ đó đưa ra nhận xét về kết quả vừa thực hiện (mạnh phần nào, yếu phần nào, "
        f"phần nào cần được cải thiện, so sánh với các kết quả trước để khen thưởng, nhắc nhở\n"
        f"Đưa ra lời khuyên cụ thể cho user để cải thiện kết quả hơn\n")
        # Correctly instantiate the data object based on type_test
        self.functions_prompt = f"Biết rằng app có 1 số chức năng như: practice test recommendation (đây là 1 bài test gồm những kiến thức đã sai từ {self.num_chap} chương trước), Analytic review (review phần analysis của {self.num_test} bài test, tìm ra được điểm mạnh yếu trong kiến thức và đánh giá chung bài test), Wrong question searching (chức năng xem lại tất cả các bài đã sai)\n"
        self.prompt_score = "(cho biết kết quả ở hệ số 10)"
    def return_subject_name(self):
        name = {
            "T": "Toán",
            "L": "Lý",
            "H": "Hóa",
            "S": "Sinh",
            "V": "Văn",
            "A": "Anh",
        }
        return name.get(self.subject, "Unknown Subject")

    def get_test_intro(self):
        if self.type_test == 1:
            return f"Đây là kết quả của total test, là bài test tất cả các chương đã học tính đến hiện tại là {self.data.num_chap}."
        elif self.type_test == 0:
            return f"Đây là kết quả của test chương, là bài test chương {self.data.num_chap}."

    def previous_result(self):
        data_prompt = self.test_intro
        data_prompt += (
            f"{self.prompt}, Đây là kết quả môn {self.subject}, từ đó hãy Phân tích kết quả kiểm tra {self.prompt_score} và thời gian thực hiện chúng. "
            f"Từ đó cho ra nhận xét nó có kịp tiến độ hay không, "
            f"biết rằng thời gian tối ưu 2 bài test cách là {self.data.time_to_do_test} ngày, "
            f"với aim điểm là {self.aim_score} thì user có kịp tiến độ ko, với "
            f"dữ liệu được đưa vào như sau:\n"
        )
        results, _, exact_time, nums = self.data.previous_results()
        for i in range(len(results)):
            data_prompt += f"{results[i]/nums[i]*10} at {exact_time[i]}\n"
        data_prompt += self.analyze_only_prompt
        return data_prompt
    def diff_prompt(self):
        return "\nChú thích cho loại câu hỏi: 0 là Nhận biết, 1 là Thông hiểu, 2 là vận dụng, 3 là vận dụng cao\n" 
    def date_time_test(self):
        query = db.session.query(Test).filter_by(test_type=self.type_test).all()
        date = query[-1].time
        if self.type_test == 1:
            test_name = "total"
        else:
            test_name = "chương"
        
        return f"Thời điểm làm bài test {test_name} cuối cùng là {date}"
    
    def next_test_date(self):
        query = db.session.query(Test).filter_by(test_type=self.type_test).all()
        date = query[-1].time
        
        date = pd.to_datetime(date)  
        print(self.data.time_to_do_test)
        return date + self.data.time_to_do_test


class promptTotal(promptCreation):
    def __init__(self, type_test, num_test, subject):
        super().__init__(type_test, num_test, subject)
        self.analyze_only_prompt = "Chỉ phân tích và đánh giá, không cần đưa ra kế hoạch cải thiện và khuyến nghị "

    def fast_analysis(self):
        data_prompt = self.test_intro
        data_prompt += (
            f"{self.prompt} {self.subject_intro} và với lượng dữ liệu được đưa vào như sau ({self.prompt_score} và thời gian thực hiện chúng), "
            f"hãy phân tích và đánh giá kết quả của bài test vừa thực hiện so với các lần làm test total trước đó, "
            f"để xác định các xu hướng học tập và đánh giá sự tiến bộ của học sinh theo thời gian. "
            f"Dữ liệu được đưa vào như sau:\n"
        )

        results, durations, exact_time, nums = self.data.previous_results()
        for i in range(len(results)):
            data_prompt += f"Điểm: {results[i]/nums[i]*10} Thời gian thực hiện: {durations[i]} giây, Thời điểm thực hiện: {exact_time[i]}\n"

        data_prompt += (
            "Vui lòng so sánh các kết quả này để xác định sự tiến bộ của học sinh qua thời gian. "
            "Những lần nào học sinh có sự cải thiện về điểm số và thời gian làm bài, và những lần nào không? "
            "Những yếu tố nào có thể đã ảnh hưởng đến kết quả, chẳng hạn như thời gian làm bài, số lượng bài tập ôn luyện, hoặc các yếu tố bên ngoài? "
        )
        data_prompt += self.analyze_only_prompt
        return data_prompt

    def deep_analysis(self):

        data_prompt = (
            f"{self.test_intro} {self.prompt} {self.subject_intro} và tất cả lượng dữ liệu sau được lấy trung bình từ {self.num_test} bài test total trước đó\n"
            "Dưới đây là tỉ lệ % đúng và thời gian làm bài của từng chương:\n"
        )
        acuc_chaps, time_chaps = self.data.short_total_analysis()
        for key, value in acuc_chaps.items():
            data_prompt += f"Chương {key}: {value}% - {time_chaps[key]} giây\n"

        data_prompt += self.diff_prompt()
        data_prompt += "Tỉ lệ % đúng của từng loại câu hỏi:\n"
        accu_diff, dic_ques, dic_total = self.data.cal_accu_diff()
        for type1, accu in accu_diff.items():
            data_prompt += f"Loại câu hỏi {type1}: {accu}%\n"

        data_prompt += "Tỉ lệ % đúng của các loại câu hỏi từng chương:\n"
        chap_difficulty_percentile = self.data.difficult_percentile_per_chap()
        for chap, dic_diff in chap_difficulty_percentile.items():
            data_prompt += f"Chương {chap}:\n"
            for type1, acuc in dic_diff.items():
                data_prompt += f"- Loại câu hỏi {type1}: {acuc}%\n"

        data_prompt += "So sánh với kì vọng % đúng của các loại câu hỏi từng chương (để nhắc nhở học sinh chú ý loại câu hỏi sai nhiều trong to do list):\n"
        predict = PredictThreshold(self.type_test, self.subject)
        data = predict.predicted_data()
        for row in data.itertuples(index=False):
            # Access columns using row indices (chapter, difficulty, accuracy)
            data_prompt += f"Chương {row.chapter} có loại câu hỏi {row.difficulty} với kì vọng là {row.accuracy}%\n"
            
        data_prompt += "Dưới đây là trung bình các bài hay sai của các chương (đây dùng để nhắc nhở học sinh chú ý các bài sai nhiều):\n"
        lessons_review_dict = self.data.lessons_id_to_review()
        for chap, value in lessons_review_dict.items():
            data_prompt += f"Chương {chap}:"
            for lesson, count in value['lesson'].items():
                data_prompt += f" bài {lesson} sai {count} lần \n"
        # tìm ra điểm mạnh điểm yếu
        # Điểm số, tgian làm bài cải thiện hay giảm, so sánh với aim score để đánh giá
        # nhận xét về phần làm tốt, phần cần cải thiện
        # nhắc nhở học sinh ôn các bài hay sai trong chương, xem lại các chương sai nhiều
        # đề xuất chiến lược học tập, sử dụng các functions của ứng dụng
        data_prompt += (
            "\nHãy phân tích kỹ lưỡng để tìm ra điểm mạnh và điểm yếu của học sinh, càng chi tiết càng tốt:\n"
            "- So sánh kết quả với aim score để đánh giá hiệu quả học tập.\n"
            "- Nhận xét về những phần làm tốt và chỉ ra các phần cần cải thiện.\n"
            "- Nhắc nhở học sinh ôn tập lại các bài thường hay sai, đặc biệt chú ý những chương có tỉ lệ sai cao.\n"
            "- Đề xuất chiến lược học tập để cải thiện các điểm yếu (Chỉ tập trung phân tích, không cần ghi ngày giờ cụ thể), bao gồm việc sử dụng các chức năng của ứng dụng như 'Wrong question searching', 'Analytic review', và 'Practice test recommendation' để hỗ trợ ôn tập.\n"
        )
        return data_prompt
    def return_max_chap(self):
        return self.data.return_max_chap()


class promptChap(promptCreation):
    def __init__(self, type_test,num_test,subject,num_chap):
        super().__init__(type_test, num_test,subject,num_chap)
    def chap_analysis(self):
        data_prompt = (
            f"{self.test_intro} {self.prompt} {self.subject_intro}. "
            f"Tất cả các dữ liệu dưới đây được lấy trung bình từ {self.num_test} bài test chương {self.num_chap} trước đó.\n"
            "Dưới đây là tỷ lệ % đúng và thời gian làm bài của từng lần làm bài trước đó. Dòng dữ liệu cuối cùng là kết quả của lần thực hiện gần đây nhất:\n"
        )

        results, durations, exact_time, nums = self.data.previous_results()
        for i in range(len(results)):
            data_prompt += f"- Điểm: {results[i]/nums[i]*10} | Thời gian thực hiện: {durations[i]} giây | Thời điểm thực hiện: {exact_time[i]}\n"

        data_prompt += "\nPhân tích tỉ lệ % đúng của từng loại câu hỏi trong chương:\n"
        data_prompt += self.diff_prompt()
        accu_diff, dic_ques, dic_total = self.data.cal_accu_diff()
        for type1, accu in accu_diff.items():
            data_prompt += f"- Loại câu hỏi {type1}: {accu}%\n"

        data_prompt += "\nSo sánh tỉ lệ % đúng hiện tại với kỳ vọng của từng loại câu hỏi trong chương:\n"
        predict = PredictThreshold(self.type_test, self.subject, self.num_chap)

        data = predict.predicted_data()
        print(data)
        for row in data.itertuples(index=False):
            # Access columns using row indices (chapter, difficulty, accuracy)
            data_prompt += f"Chương {row.chapter} có loại câu hỏi {row.difficulty} với kì vọng là {row.accuracy}%\n"

        data_prompt += (
            "\nPhân tích chi tiết kết quả trên để tìm ra điểm mạnh và điểm yếu của học sinh:\n"
            "- Xác định các phần kiến thức mà học sinh đã nắm vững (điểm số cao, thời gian ngắn).\n"
            "- Nhận diện các phần cần cải thiện (điểm số thấp, thời gian dài).\n"
            "- So sánh kết quả với kỳ vọng để xác định liệu học sinh có đạt được mục tiêu đã đề ra không.\n"
            "- Chú ý đến những chương hoặc loại câu hỏi có tỉ lệ sai cao để tập trung ôn tập.\n"
        )

        data_prompt += (
            "Đưa ra các nhận xét và lời khuyên cụ thể cho học sinh:\n"
            "- Tập trung ôn lại các loại câu hỏi có tỉ lệ đúng thấp.\n"
            "- Chuẩn bị kỹ lưỡng cho bài kiểm tra tiếp theo bằng cách ôn tập các chương có tỉ lệ sai cao.\n"
            "- Đặt mục tiêu cụ thể cho mỗi buổi học, ví dụ: cải thiện điểm số trong các câu hỏi 'Nhận biết' và 'Thông hiểu'. (Chỉ tập trung phân tích, không cần ghi ngày giờ cụ thể)\n"
        )

        data_prompt += self.detail_analyze_prompt
        return data_prompt


class generateAnalysis:
    def __init__(self, subject, num_chap, num_test):
        self.configuration = {
            "temperature": 0.8,
            "max_tokens": 4096,
            "top_p": 0.8,
        }
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
        self.num_test = num_test
        self.subject = subject
        self.num_chap = num_chap
        self.next_test_date = promptTotal(1, self.num_test, self.subject).next_test_date()

    def return_subject_name(self):
        name = {
            "M": "Toán",
            "L": "Lý",
            "H": "Hóa",
            "S": "Sinh",
            "V": "Văn",
            "A": "Anh",
        }
        return name.get(self.subject, "Unknown Subject")

    def return_prompt(self, analyze_type):
        if analyze_type == "fast":
            prompt = promptTotal(1, self.num_test, self.subject).fast_analysis()
        elif analyze_type == "deep":
            prompt = promptTotal(1, self.num_test, self.subject).deep_analysis()
        elif analyze_type == "progress":
            prompt = promptTotal(1, self.num_test, self.subject).previous_result()
        elif analyze_type == "chapter":
            prompt = promptChap(0, self.num_test, self.subject, self.num_chap).chap_analysis()
        else:
            return "Invalid analyze type. Please choose between 'fast', 'deep', 'progress', or 'chapter'."
        return prompt

    def call_gpt(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # ft:gpt-4o-2024-08-06:personal:study-planning-v1:A3hYPnEP
            messages=[
                {"role": "system", "content": "bạn là 1 gia sư, bạn giỏi trong việc đánh giá những số liệu của X bài test total (bài test tổng hợp khi user học đến chương N) hoặc số liệu của X bài test chương (bài test chương N của user), biết N và X là số dương bất kỳ. Nhiệm vụ của bạn là theo prompt được hướng dẫn, bạn hãy generate các phân tích cũng như đánh giá. Và khi cần sẽ là 1 kế hoạch rõ ràng dựa vào đánh giá được cho, kế hoạch này sẽ như 1 to do list và từng ngày sẽ có từng tác vụ cụ thể được hướng dẫn trong prompt. Nếu đang phân tích thì chỉ tập trung phân tích, đừng ghi kế hoạch cụ thể."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.configuration['temperature'],
            max_tokens=self.configuration['max_tokens'],
            top_p=self.configuration['top_p'],
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message.content

    def analyze(self, analyze_type):
        prompt = self.return_prompt(analyze_type)
        response = self.call_gpt(prompt)
        return response

    def detail_plan_and_timeline(self):
        # Xác định ngày tiếp theo cho test tổng và test chương
        self.num_chap = promptTotal(1, self.num_test, self.subject).return_max_chap()
        date_total = promptCreation(1, self.num_test, self.subject, self.num_chap).next_test_date()
        date_chap = promptCreation(0, self.num_test, self.subject, self.num_chap).next_test_date()
        diff = promptCreation(1, self.num_test, self.subject, self.num_chap).diff_prompt()
        current_date = datetime.now()
        functions = promptCreation(1, self.num_test, self.subject, self.num_chap).functions_prompt
        
        # Bắt đầu xây dựng chuỗi prompt
        prompt = "1. **từ dữ liệu test tổng:**\n"
        prompt += self.return_prompt("deep")
        
        prompt += (
            f"\n Lập kế hoạch chi tiết ôn tập dựa vào các yếu tố sau  : \n"
            f"1. Nhắc nhở ôn lại kiến thức cũ từ dữ liệu test tổng , đặc biệt là những phần còn yếu.\n"
            f"2. Chuẩn bị học chương {self.num_chap + 1} để sẵn sàng cho bài test chương tiếp theo.\n"
            f"3. Từ dữ liệu test tổng, tập trung cải thiện điểm yếu đã chỉ ra ({diff}) của từng chương, sử dụng các chức năng của ứng dụng ({functions}), nhắc nhở ôn tập cụ thể tên bài nào chương nào\n"
            f"4. Lưu ý không bỏ sót việc nhắc học sinh làm bài test chương {self.num_chap + 1} vào ngày {str(date_chap.strftime('%d/%m/%Y'))[:10]}, bài test tổng vào ngày {str(date_total)[:10]}\n"
            f"5. Ôn tập chương kèm với cụ thể các loại câu hỏi hay sai nhất từ dữ liệu test tổng (0, 1, 2, 3) từ dữ liệu test tổng, và cụ thể bài học sai nhiều của chương đó (cùng từ dữ liệu test tổng luôn)\n"
        )
        # {str(current_date.strftime('%d/%m/%Y'))[:10]}
        prompt += (
            f"Đặc biệt tập trung vào các yếu tố 3,4,5 (đặc biệt yếu tố 5) vừa rồi, lập kế hoạch từ ngày {str(current_date.strftime('%d/%m/%Y'))[:10]}  đến ngày {str(date_total.strftime('%d/%m/%Y'))[:10]}\n"
            f"Tác vụ trong 1 ngày càng chi tiết càng tốt\n "
            "ôn tập từ chương đầu đến hiện tại,  các loại câu hỏi hay bài học cần chú ý thì phải cụ thể\n"
            "Hãy viết theo format sau: \n"
            "'ngày xx/tháng xx/năm xxxx : làm gì đó'\n"
        )

        # # Gọi GPT với prompt ban đầu
        response = self.call_gpt(prompt)
        
        # # Kiểm tra và bổ sung nếu cần
        required_factors = [
            "Mỗi ngày ôn tập chương sẽ gồm cả việc ôn lại **các loại câu hỏi hay sai** và **bài học sai nhiều** từ dữ liệu test tổng của chương đó. Hãy làm rõ ra là nên xem lại loại câu hỏi nào và bài học nào của từng chương"
        ]

        credit = self.return_prompt("deep")
        # Vòng lặp kiểm tra các yếu tố trong response
        for factor in required_factors:
            # Nếu thiếu yếu tố, yêu cầu GPT bổ sung
            additional_prompt = "Có dữ liệu test total sau : \n"
            additional_prompt += credit
            additional_prompt += "\nĐây là kế hoạch học tập hiện tại : \n"
            additional_prompt += response
            additional_prompt += f"\nVui lòng bổ sung yếu tố sau vào kế hoạch học tập nếu thiếu: {factor}"
            print(additional_prompt)
            response = self.call_gpt(additional_prompt)

        return response

    def format_data(self): 
        data = self.detail_plan_and_timeline() # try except
        data += (
            f"Hãy viết theo format sau, chắc chắn rằng nó đúng format json"
            f"ngày xx/tháng xx/năm xxxx : làm gì đó' ,từ prompt đầu vào sau, hãy làm file json sau để chứa to do list với format sau : {{'date': '24/08/2024', 'action': 'Phân tích kết quả bài test', 'done': 'false'}} và chú ý đến các tiêu chí : ôn tập đầy đủ các chương , sử dụng chính xác các functions trong app để ôn tập, nhắc nhở làm bài kiểm tra, học bài mới, to do list đa dạng với sáng tạo"
        )
        response = self.call_gpt(data)
        return response
    
    def turning_into_json(self):
        json_string = self.format_data()

        
        
        with open("test.txt", "w", encoding="utf-8") as f:
            f.write(json_string)
        try: 
            start_pos = json_string.find("[")
            end_pos = json_string.find("]")
            json_string = json_string[start_pos:end_pos+1]
            json_data = json.loads(json_string)
        except json.decoder.JSONDecodeError: 
            prompt = "format json không đúng, hãy thử lại"
            prompt += json_string
            json_string = self.call_gpt(prompt)
            start_pos = json_string.find("[")
            end_pos = json_string.find("]")
            json_string = json_string[start_pos:end_pos+1]
            json_data = json.loads(json_string)
        return json_data




# app = create_app()
# with app.app_context(): # type , num , subject, num_chap
#     a = promptTotal(1, 15, "L")
#     print(a.deep_analysis())
    # a = generateAnalysis("L", 3)
    # print(a.analyze("chapter"))
    # print(a.next_test_date())
#     test = generateAnalysis("T",3)
#     # # "deep", "fast", "progress", "chapter"
#     # # print(test.analyze("deep"))
#     # # print(test.detail_plan_and_timeline())
#     # # # test.format_data()
#     abc = test.format_data()
#     with open("todo.txt", "w", encoding="utf-8") as f:
#         f.write(abc)
#     json_str = test.turning_into_json()
#     with open("todo_T.json", "w", encoding="utf-8") as f:
#         try:
#             json.dump(json_str, f, ensure_ascii=False, indent=4)
#         except json.decoder.JSONDecodeError:
#             print("Error")
    
    # print(test.analyze("deep"))
