# data_processing.py

import os
import pandas as pd
import datetime
import shutil
import docx
from docx.shared import Pt
import requests
from bs4 import BeautifulSoup
import json
from typing import List


def create_working_dir(working_dir: str, name: str) -> str:
    """
    Create a working directory with a timestamp and sanitized name.

    Parameters
    ----------
    working_dir : str
        The base directory where the new directory will be created.
    name : str
        The name to be sanitized and included in the directory name.

    Returns
    -------
    str
        The path to the newly created directory.
    """
    date = (
        str(datetime.datetime.now())
        .split(".")[0]
        .replace(" ", "_")
        .replace("-", "_")
        .replace(":", "_")
    )
    name = (
        name.replace("-", "_")
        .replace(":", "_")
        .replace("(", "_")
        .replace(")", "_")
    )
    dir_name = os.path.join(working_dir, f"{date}_{name}")
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    return dir_name


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by replacing or removing invalid characters.

    Parameters
    ----------
    filename : str
        The filename to sanitize.

    Returns
    -------
    str
        The sanitized filename.
    """
    return (
        filename.replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace("*", "")
        .replace("|", "")
        .replace(":", "")
        .replace("?", "")
        .replace("<", "")
        .replace(">", "")
        .replace(":", "_")
        .replace("(", "_")
        .replace(")", "_")
    )


def word_cv_prepare(
    working_dir: str, dir: str, skills: List[str], position: str,
    current_skills: List[str]
) -> None:
    """
    Prepare and save a CV document in a specified directory.

    Parameters
    ----------
    working_dir : str
        The base working directory.
    dir : str
        The directory where the CV will be saved.
    skills : List[str]
        List of skills to include in the CV.
    position : str
        The job position to include in the CV.
    current_skills : List[str]
        List of current skills to include in the CV.
    """
    all_skills = list(set(current_skills + skills))
    all_skills.sort(key=str.lower)

    source = os.path.join(working_dir, "PT.docx")
    if not os.path.exists(source):
        print(f"Source CV file not found: {source}")
        return

    destination = os.path.join(dir, "PrzemyslawTuturCV.docx")
    shutil.copy(source, destination)
    doc_name_position = sanitize_filename(position)
    doc = docx.Document(destination)
    paragraph = doc.add_paragraph(", ".join(all_skills).upper())
    run = paragraph.runs[0]
    run.font.name = "Times New Roman"

    section = doc.sections[0]
    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_para_run = footer_para.add_run(
        f"This CV document was automatically generated and submitted for the "
        f"{position} position based on skill matching. If you contact me with "
        f"a response, I might be momentarily confused :)... Apologies for the "
        f"Monty Python 'spam, spam, spam' scenario if you have received "
        f"multiple CVs."
    )
    footer_para_run.font.name = "Times New Roman"
    footer_para_run.font.bold = True
    footer_para_run.font.size = Pt(10)

    try:
        doc.save(os.path.join(dir, f"Przemyslaw_Tutur_{doc_name_position}.docx"))
    except OSError as e:
        print(f"Error saving document: {e}")


def generate_cover_letter(
    working_dir: str, job_title: str, company_name: str, job_url: str
) -> None:
    """
    Generate and save a cover letter for a job application.

    Parameters
    ----------
    working_dir : str
        The base working directory.
    job_title : str
        The job title to include in the cover letter.
    company_name : str
        The company name to include in the cover letter.
    job_url : str
        The job URL to include in the cover letter.
    """
    doc = docx.Document()
    doc.add_heading("Cover Letter", 0)
    doc.add_paragraph(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
    doc.add_paragraph("Dear Hiring Manager,")
    doc.add_paragraph(
        f"I am writing to express my interest in the {job_title} position at "
        f"{company_name}. I found this job listing on {job_url} and believe "
        f"that my skills and experience make me a strong candidate for this "
        f"role."
    )
    doc.add_paragraph(
        "I have extensive experience in the required skills mentioned in the "
        "job description, including [mention some key skills]. I am confident "
        "that my background and knowledge will enable me to contribute "
        "effectively to your team."
    )
    doc.add_paragraph(
        "I look forward to the opportunity to discuss how my skills and "
        "experiences align with the needs of your team. Thank you for "
        "considering my application."
    )
    doc.add_paragraph("Sincerely,")
    doc.add_paragraph("[Your Name]")

    cover_letter_path = os.path.join(
        working_dir, f"Cover_Letter_{sanitize_filename(job_title)}.docx"
    )
    doc.save(cover_letter_path)
    print(f"Cover letter saved to {cover_letter_path}")


def take_job_description(dir: str, url: str) -> None:
    """
    Retrieve and save the job description from a given URL.

    Parameters
    ----------
    dir : str
        The directory where the job description will be saved.
    url : str
        The URL of the job description.
    """
    try:
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        target_div_content = soup.find("div", class_="css-6sm4q6")
        if target_div_content:
            with open(
                os.path.join(dir, "job_description.txt"), "w", encoding="utf-8"
            ) as fdescriptor:
                fdescriptor.write(target_div_content.text)
        else:
            print("The specified div was not found.")
    except Exception as e:
        print(f"Error taking job description: {e}")


def request(
    working_dir: str, current_skills: List[str], url: str
) -> pd.DataFrame:
    """
    Send a request to a job listing URL, process the data, and save it.

    Parameters
    ----------
    working_dir : str
        The base working directory.
    current_skills : List[str]
        List of current skills to match against job listings.
    url : str
        The URL of the job listings.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the processed job data.
    """
    try:
        # Clear the current output data CSV file
        file_path = os.path.join(working_dir, "output_data.csv")
        if os.path.exists(file_path):
            os.remove(file_path)

        resp = requests.get(url)
        int_resp = requests.get(url)
        json_string = str(
            int_resp.text.split('{"pages":')[1].split('"meta":')[0].rstrip(",")
            + "}]"
        )
        data_set = json.loads(json_string)
        data_list = []
        for data in data_set[0]["data"]:
            sub_url = "https://justjoin.it/offers/" + data["slug"]
            row = {
                "TITLE": data["title"],
                "REQUIRED_SKILLS": str(data["requiredSkills"]),
                "ADDITIONAL_SKILLS": str(data["niceToHaveSkills"]),
                "WORKPLACE_TYPE": data["workplaceType"],
                "REMOTE_INTERVIEW": data["remoteInterview"],
                "URL": sub_url,
                "PAYMENT_FROM": str(data["employmentTypes"][0]["fromPln"]),
                "PAYMENT_TO": str(data["employmentTypes"][0]["toPln"]),
                "LOCATION": data.get("city", "Unknown"),
                "COMPANY": data.get("companyName", "Unknown"),
                "DATE": datetime.datetime.now().strftime("%Y-%m-%d"),
            }
            data_list.append(row)
            directory = create_working_dir(working_dir, data["slug"])
            take_job_description(directory, sub_url)
            word_cv_prepare(
                working_dir,
                directory,
                data["requiredSkills"],
                data["title"],
                current_skills,
            )
            generate_cover_letter(
                directory,
                data["title"],
                data.get("companyName", "Unknown"),
                sub_url,
            )
            print("Processed:", data["title"])
        df = pd.DataFrame(data_list)
        write_header = not os.path.exists(file_path)
        df.to_csv(file_path, mode="a", index=False, header=write_header)

        # Append to the output_whole.csv
        whole_file_path = os.path.join(working_dir, "output_whole.csv")
        df.to_csv(
            whole_file_path, mode="a", index=False,
            header=not os.path.exists(whole_file_path)
        )

        print("Data appended to CSV.")
        return df
    except Exception as e:
        print(f"Error processing request: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

