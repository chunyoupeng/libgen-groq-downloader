import sys,os
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libgen_groq_downloader')))

# Import the class from libgen_groq_downloader.py
from libgen_groq_downloader import LibgenGroqDownloader

if __name__ == '__main__':
	log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	file_handler = logging.FileHandler('app.log')
	file_handler.setFormatter(log_formatter)
	file_handler.setLevel(logging.INFO)

	# Create a console handler
	console_handler = logging.StreamHandler()
	console_handler.setFormatter(log_formatter)
	console_handler.setLevel(logging.INFO)

	# Get the root logger and set its level
	root_logger = logging.getLogger()
	root_logger.setLevel(logging.INFO)

	# Add handlers to the root logger
	root_logger.addHandler(file_handler)
	root_logger.addHandler(console_handler)

	raw_text = """我想下载《Pride and Prejudice》这本书，文件格式是pdf。"""
	text2 = """《高效能人士的七个习惯》 - 史蒂芬·柯维 (The 7 Habits of Highly Effective People by Stephen R. Covey format epub, english)
	•	尽管不仅仅是关于领导力，这本书提供了领导者在个人和职业生活中提高效能的基本习惯。
	8.	《领导梯队：全面打造领导力驱动型公司》 - 拉姆·查兰 (The Leadership Pipeline by Ram Charan, Stephen Drotter, and James Noel)
	•	探讨了如何在公司内部建立和发展领导力梯队。
	9.	《变革的力量》 - 约翰·科特 (Leading Change by John P. Kotter)
	•	提供了在组织中推动变革的八步流程，以及成功变革的关键因素。
	10.	《韧性》 - 埃里克·格雷滕斯 (Resilience by Eric Greitens)
	•	通过实际案例和经验教训，讨论了在面对挑战时如何保持韧性和领导力。"""
	downloader1 = LibgenGroqDownloader(raw_text)
	d2 = LibgenGroqDownloader(text2)
	downloader1.download()
	d2.download()