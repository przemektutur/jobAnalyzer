# whole.py

import os
import requests
import json
import datetime
import pandas as pd
from visualization import (
    visualize_data,
    analyze_job_types,
    analyze_skill_salary_relationship,
)
from main import urls  # Import URLs from main.py


def request(working_dir: str, current_skills: list, url: str) -> pd.DataFrame:
    """
    Request job data from a given URL and save it to a CSV file.

    Parameters
    ----------
    working_dir : str
        The working directory to save the data.
    current_skills : list
        List of current skills to include in the request.
    url : str
        The URL to request job data from.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the job data.
    """
    try:
        file_path = os.path.join(working_dir, "output_data.csv")
        if os.path.exists(file_path):
            os.remove(file_path)

        resp = requests.get(url)
        if resp.status_code == 200:
            json_string = str(
                resp.text.split('{"pages":')[1].split('"meta":')[0].rstrip(",")
                + "}]"
            )
            data_set = json.loads(json_string)
            data_list = []
            for data in data_set[0]["data"]:
                sub_url = "https://justjoin.it/offers/" + data["slug"]
                required_skills = data.get("requiredSkills", [])
                additional_skills = data.get("niceToHaveSkills", [])
                employment_info = (
                    data["employmentTypes"][0] if data["employmentTypes"] else {}
                )

                row = {
                    "TITLE": data.get("title", ""),
                    "REQUIRED_SKILLS": str(required_skills),
                    "ADDITIONAL_SKILLS": str(additional_skills),
                    "WORKPLACE_TYPE": data.get("workplaceType", ""),
                    "REMOTE_INTERVIEW": data.get("remoteInterview", ""),
                    "URL": sub_url,
                    "PAYMENT_FROM": str(employment_info.get("fromPln", "")),
                    "PAYMENT_TO": str(employment_info.get("toPln", "")),
                    "LOCATION": data.get("city", "Unknown"),
                    "COMPANY": data.get("companyName", "Unknown"),
                    "DATE": datetime.datetime.now().strftime("%Y-%m-%d"),
                }
                data_list.append(row)
                print("Processed:", data["title"])
            df = pd.DataFrame(data_list)
            write_header = not os.path.exists(file_path)
            df.to_csv(file_path, mode="a", index=False, header=write_header)

            whole_file_path = os.path.join(working_dir, "output_whole.csv")
            df.to_csv(
                whole_file_path,
                mode="a",
                index=False,
                header=not os.path.exists(whole_file_path),
            )

            print("Data appended to CSV.")
            return df
        else:
            print(f"Failed to fetch data for {url}: HTTP {resp.status_code}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error processing request: {e}")
        return pd.DataFrame()


def fetch_job_data(working_dir: str, current_skills: list) -> list:
    """
    Fetch job data for all job types from URLs.

    Parameters
    ----------
    working_dir : str
        The working directory to save the data.
    current_skills : list
        List of current skills to include in the request.

    Returns
    -------
    list
        List of dictionaries containing job data.
    """
    all_data = []
    for job_type, url in urls.items():
        print(f"Fetching data for {job_type} from {url}")
        data = request(working_dir, current_skills, url)
        if not data.empty:
            data["JOB_TYPE"] = job_type
            all_data.extend(data.to_dict("records"))
    return all_data


def save_to_csv(data: list, file_path: str) -> None:
    """
    Save job data to a CSV file.

    Parameters
    ----------
    data : list
        List of dictionaries containing job data.
    file_path : str
        Path to the CSV file to save the data.
    """
    df = pd.DataFrame(data)
    if not df.empty:
        df.columns = [col.strip() for col in df.columns]
        if os.path.exists(file_path):
            existing_df = pd.read_csv(file_path)
            combined_df = pd.concat([existing_df, df]).drop_duplicates(
                subset=["TITLE", "PAYMENT_FROM", "PAYMENT_TO"]
            )
        else:
            combined_df = df.drop_duplicates(
                subset=["TITLE", "PAYMENT_FROM", "PAYMENT_TO"]
            )
        required_columns = [
            "TITLE",
            "REQUIRED_SKILLS",
            "ADDITIONAL_SKILLS",
            "WORKPLACE_TYPE",
            "REMOTE_INTERVIEW",
            "URL",
            "PAYMENT_FROM",
            "PAYMENT_TO",
            "LOCATION",
            "COMPANY",
            "DATE",
            "JOB_TYPE",
        ]
        for col in required_columns:
            if col not in combined_df.columns:
                combined_df[col] = ""
        combined_df = combined_df[required_columns]
        combined_df.to_csv(file_path, index=False)
    else:
        print("No data to save.")


def analyze_and_visualize(file_path: str) -> None:
    """
    Analyze and visualize job data from a CSV file.

    Parameters
    ----------
    file_path : str
        Path to the CSV file containing job data.
    """
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        visualize_data(df)
        analyze_job_types(df)
        analyze_skill_salary_relationship(df)
    else:
        print(f"No file found at {file_path} to analyze and visualize.")


def main() -> None:
    """
    Main function to fetch, save, analyze, and visualize job data.
    """
    working_dir = os.getcwd()
    current_skills = []  # Load current skills from the file or user input if necessary
    file_path = os.path.join(working_dir, "output_whole.csv")
    all_data = fetch_job_data(working_dir, current_skills)
    save_to_csv(all_data, file_path)
    analyze_and_visualize(file_path)


if __name__ == "__main__":
    main()

