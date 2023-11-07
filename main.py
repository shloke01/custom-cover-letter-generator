import openai
import requests
from bs4 import BeautifulSoup as bs
import PyPDF2
import io
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import tiktoken
from tokenizers import ByteLevelBPETokenizer

# nltk.download('punkt')
# nltk.download('stopwords')

# API Key
openai.api_key = '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'

def generate_cover_letter(job_description_url, pdf_filepath):
    # Fetch the job description webpage and extract the relevant text
    job_description_text = extract_text_from_webpage(job_description_url)
    jd_text_tokens = word_tokenize(job_description_text)
    jd_without_sw = [word for word in jd_text_tokens if not word in stopwords.words()]

    # print(jd_without_sw)

    resume_text = extract_text_from_pdf(pdf_filepath)
    resume_text_tokens = word_tokenize(resume_text)
    resume_without_sw = [word for word in resume_text_tokens if not word in stopwords.words()]

    # print(resume_without_sw)

    # Generate the custom cover letter using OpenAI API
    response = openai.Completion.create(
        engine='text-ada-001',
        prompt=f"Write a cover letter, no less than 500 words, based on the following job description:\n\n{jd_without_sw}\n\n tailored to the following resume:\n\n{resume_without_sw}\n\n",
        max_tokens=600,
        temperature=0.6,
        n=1,
        stop=None,
        timeout=120
    )

    # Extract the generated cover letter from the API response
    generated_cover_letter = response.choices[0].text.strip()

    # Print the custom cover letter
    print(generated_cover_letter)

## Get job description from url
def extract_text_from_webpage(url):
    response = requests.get(url)
    soup = bs(response.content, 'html.parser')
    job_description = soup.get_text()
    return job_description

## Get data from resume
def extract_text_from_pdf(file_path):
    response = requests.get(file_path)
    file = io.BytesIO(response.content)
    file = PyPDF2.PdfReader(file)
    text = ""
    num_pages = len(file.pages)

    for page_number in range(num_pages):
        page = file.pages[page_number]
        text += page.extract_text()

    return text


job_description_url = 'https://jobs.lever.co/hive/1da02246-e15e-48ee-8c99-8d813dcbf1a0'
pdf_filepath = 'https://shloke01.github.io/res/resume_w:o_number.pdf'

generate_cover_letter(job_description_url, pdf_filepath)

# print(extract_text_from_webpage(job_description_url))


