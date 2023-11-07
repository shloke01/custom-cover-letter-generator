import os
from flask import Flask, render_template, request
import openai
import requests
from bs4 import BeautifulSoup as bs
import PyPDF2
from dotenv import load_dotenv

app = Flask(__name__)

## Configure
def configure():
    load_dotenv()

## Get job description from url
def extract_text_from_webpage(url):
    response = requests.get(url)
    soup = bs(response.content, 'html.parser')
    job_description = soup.get_text()
    return job_description

## Get data from resume
def extract_text_from_pdf(file):
    file = PyPDF2.PdfReader(file)
    text = ""
    num_pages = len(file.pages)

    for page_number in range(num_pages):
        page = file.pages[page_number]
        text += page.extract_text()

    return text

@app.route('/')
def index():
    configure()
    return render_template('index.html')

@app.route('/generate_cover_letter', methods=['POST'])
def generate_cover_letter():

    resume_file = request.files['resume']
    resume_text = extract_text_from_pdf(resume_file)

    job_description_url = request.form['job_description']
    job_description_text = extract_text_from_webpage(job_description_url)

    openai.api_key = os.getenv('api_key')

    # Generate the custom cover letter using OpenAI API
    MODEL = "gpt-4-1106-preview"
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Please omit the header/letterhead and fill in all remaining placeholders yourself based on the information in the resume."},
            {"role": "user", "content": f"Write a ready-to-go cover letter, no less than 500 words, based on the following job description:\n\n{job_description_text}\n\n tailored to the following resume:\n\n{resume_text}\n\n"}
        ],
        max_tokens=600,
        temperature=0.7,
        n=1,
        stop=None,
    )

    generated_cover_letter = response.choices[0].message.content.strip()

    return render_template('index.html', cover_letter=generated_cover_letter)


if __name__ == '__main__':
    app.run(debug=True)