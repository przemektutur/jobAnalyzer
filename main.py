"""main.py - main project file."""
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import data_processing as dp
import visualization as vz
import whole

# Urls definitions for different job offers
urls = {
    "JavaScript": "https://justjoin.it/all-locations/javascript",
    "HTML": "https://justjoin.it/all-locations/html",
    "PHP": "https://justjoin.it/all-locations/php",
    "Ruby": "https://justjoin.it/all-locations/ruby",
    "Python": "https://justjoin.it/all-locations/python",
    "Java": "https://justjoin.it/all-locations/java",
    ".NET": "https://justjoin.it/all-locations/net",
    "Scala": "https://justjoin.it/all-locations/scala",
    "C": "https://justjoin.it/all-locations/c",
    "Mobile": "https://justjoin.it/all-locations/mobile",
    "Testing": "https://justjoin.it/all-locations/testing",
    "DevOps": "https://justjoin.it/all-locations/devops",
    "Admin": "https://justjoin.it/all-locations/admin",
    "UX": "https://justjoin.it/all-locations/ux",
    "PM": "https://justjoin.it/all-locations/pm",
    "Game": "https://justjoin.it/all-locations/game",
    "Analytics": "https://justjoin.it/all-locations/analytics",
    "Security": "https://justjoin.it/all-locations/security",
    "Data": "https://justjoin.it/all-locations/data",
    "Go": "https://justjoin.it/all-locations/go",
    "Support": "https://justjoin.it/all-locations/support",
    "ERP": "https://justjoin.it/all-locations/erp",
    "Architecture": "https://justjoin.it/all-locations/architecture",
    "Other": "https://justjoin.it/all-locations/other",
}

# Working directory global settings
working_dir = ""
current_skills = []


def load_skills(file_path: str) -> None:
    """
    Load skills from a file and update the global current_skills list.

    Parameters
    ----------
    file_path: Path to the file containing skills.

    Return:
    -------
    None
    """
    global current_skills
    with open(file_path, "r") as file:
        current_skills = [line.strip() for line in file.readlines()]
    messagebox.showinfo("Info", "Skills loaded successfully.")


def analyze_data(df: pd.DataFrame) -> None:
    """
    Perform data analysis on the given DataFrame.

    Parameters
    ----------
    df: DataFrame containing job data.

    Return:
    -------
    None
    """
    model_from, model_to = vz.analyze_data(df)
    messagebox.showinfo("Info", "Data analysis completed.")


def visualize_data(df: pd.DataFrame) -> None:
    """
    Visualize data from the given DataFrame.

    Parameters
    ----------
    df: DataFrame containing job data.

    Return:
    -------
    None
    """
    most_common_skills, high_salary_skills = vz.visualize_data(df)
    most_common_skills_str = most_common_skills.to_string()
    high_salary_skills_str = high_salary_skills.to_string()

    messagebox.showinfo("Most Common Skills", most_common_skills_str)
    messagebox.showinfo("High Salary Skills", high_salary_skills_str)
    messagebox.showinfo("Info", "Data visualization completed.")


class App(tk.Tk):
    def __init__(self) -> None:
        """
        Initialize the App window.
        __init__ - Application constructor

        This method does not take any parameters.

        Return:
        --------
        None
        """
        super().__init__()
        self.title("Job Scraper")
        self.geometry("540x220")
        self.url_var = tk.StringVar(self)
        self.url_var.set(next(iter(urls)))
        self.experience_level_var = tk.StringVar(self)
        self.experience_level_var.set("junior")
        self.remote_var = tk.BooleanVar(self)
        self.create_widgets()

    def create_widgets(self) -> None:
        """
        Create and arrange widgets in the app window.

        This method does not take any parameters.

        Return:
        -------
        None
        """
        tk.Label(self, text="Select Job Type", width=20).grid(
            row=0, column=0, padx=10, pady=5
        )
        tk.OptionMenu(self, self.url_var, *urls.keys()).grid(
            row=1, column=0, padx=10, pady=5, sticky="ew"
        )

        tk.Label(self, text="Experience Level", width=20).grid(
            row=2, column=0, padx=10, pady=5
        )
        tk.OptionMenu(
            self,
            self.experience_level_var,
            "junior",
            "mid",
            "senior",
            "c-level",
        ).grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        tk.Checkbutton(
            self, text="Remote", variable=self.remote_var, width=20
        ).grid(
            row=4, column=0, padx=10, pady=5, sticky="ew"
        )

        tk.Button(
            self,
            text="Set Working Directory",
            command=self.set_working_directory,
            width=20,
        ).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(
            self, text="Load Skills", command=self.load_skills, width=20
        ).grid(
            row=1, column=1, padx=10, pady=5
        )
        tk.Button(
            self, text="Scrape Jobs", command=self.scrape_jobs, width=20
        ).grid(
            row=2, column=1, padx=10, pady=5
        )

        analyze_button = tk.Button(
            self,
            text="Analyze Data",
            command=self.analyze_data,
            bg="lightgreen",
            width=20
        )
        analyze_button.grid(row=0, column=2, padx=10, pady=5)
        visualize_button = tk.Button(
            self,
            text="Visualize Data",
            command=self.visualize_data,
            bg="lightgreen",
            width=20,
        )
        visualize_button.grid(row=1, column=2, padx=10, pady=5)
        whole_analysis_button = tk.Button(
            self,
            text="Whole Analyze",
            command=self.run_whole_analysis,
            bg="lightcoral",
            width=20,
        )
        whole_analysis_button.grid(row=2, column=2, padx=10, pady=5)

    def set_working_directory(self) -> None:
        """
        Set the working directory for saving job data.

        This method does not take any parameters.

        Return:
        -------
        None
        """
        global working_dir
        working_dir = filedialog.askdirectory()
        if working_dir:
            messagebox.showinfo(
                "Info", f"Working directory set to {working_dir}"
            )
        else:
            messagebox.showerror("Error", "No directory selected.")

    def load_skills(self) -> None:
        """
        Load skills from a selected file.

        This method does not take any parameters.

        Return:
        -------
        None
        """
        file_path = filedialog.askopenfilename()
        if file_path:
            load_skills(file_path)

    def scrape_jobs(self) -> None:
        """
        Scrape jobs based on the selected criteria and save the data.

        This method does not take any parameters.

        Return:
        -------
        None
        """
        url_key = self.url_var.get()
        experience_level = self.experience_level_var.get()
        is_remote = self.remote_var.get()

        if url_key:
            url = urls[url_key]
            if experience_level:
                url += f"/experience-level_{experience_level}"
            if is_remote:
                url += "/remote_yes"

            if working_dir:
                # Clear the output file before scraping
                output_file_path = os.path.join(working_dir, "output_data.csv")
                if os.path.exists(output_file_path):
                    os.remove(output_file_path)

                # df = dp.request(working_dir, current_skills, url)
                df = dp.request(working_dir, current_skills, url, url_key)
                dp.generate_summary(working_dir, df,
                                    os.path.join(working_dir, "skills.txt"))

                # Append to the output_whole.csv file
                output_whole_file_path = os.path.join(working_dir, "output_whole.csv")
                if os.path.exists(output_whole_file_path):
                    df.to_csv(
                        output_whole_file_path, mode="a", header=False, index=False
                    )
                else:
                    df.to_csv(
                        output_whole_file_path, mode="w", header=True, index=False
                    )

                messagebox.showinfo(
                    "Info", "Jobs scraped successfully."
                )
            else:
                messagebox.showerror(
                    "Error", "Please set the working directory first."
                )
        else:
            messagebox.showerror(
                "Error", "Please select a job type."
            )

    def analyze_data(self) -> None:
        """
        Analyze the scraped job data.

        This method does not take any parameters.

        Return:
        -------
        None
        """
        file_path = os.path.join(working_dir, "output_data.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, on_bad_lines="skip")
            analyze_data(df)
        else:
            messagebox.showerror(
                "Error", "CSV file not found. Please scrape jobs first."
            )

    def visualize_data(self) -> None:
        """
        Visualize the scraped job data.

        This method does not take any parameters.

        Return:
        -------
        None
        """
        file_path = os.path.join(working_dir, "output_data.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, on_bad_lines="skip")
            visualize_data(df)
        else:
            messagebox.showerror(
                "Error", "CSV file not found. Please scrape jobs first."
            )

    def run_whole_analysis(self) -> None:
        """
        Run the complete analysis using the whole module.

        This method does not take any parameters.

        Return:
        -------
        None
        """
        whole.main()
        messagebox.showinfo("Info", "Whole analysis completed.")


if __name__ == "__main__":
    app = App()
    app.mainloop()

