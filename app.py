import os
from flask import Flask, render_template, request
from openai import OpenAI
import requests
from bs4 import BeautifulSoup as bs
import PyPDF2
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = OpenAI()

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
    return render_template('index.html')

@app.route('/generate_cover_letter', methods=['POST'])
def generate_cover_letter():

    resume_file = request.files['resume']
    resume_text = extract_text_from_pdf(resume_file)

    job_description_url = request.form['job_description']
    job_description_text = extract_text_from_webpage(job_description_url)

    # Generate the custom cover letter using OpenAI API
    MODEL = "gpt-4-0125-preview"
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Please omit the header/letterhead and fill in all placeholders yourself based on the information in the resume."},
            {"role": "user", "content": f"Write a ready-to-go cover letter, no less than 500 words, based on the following job description:\n\n{job_description_text}\n\n tailored to the following resume:\n\n{resume_text}\n\n"}
        ]
    )

    generated_cover_letter = response.choices[0].message.content.strip()
    return render_template('index.html', cover_letter=generated_cover_letter)


if __name__ == '__main__':
    app.run(debug=True)