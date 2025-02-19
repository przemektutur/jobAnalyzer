# visualization.py

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
from sklearn.cluster import KMeans
from typing import Tuple


def analyze_data(df: pd.DataFrame) -> Tuple[LinearRegression, LinearRegression]:
    """
    Analyze data to fit linear regression models.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing job data.

    Returns
    -------
    Tuple[LinearRegression, LinearRegression]
        Fitted linear regression models for payment from and to.
    """
    df["REQUIRED_SKILLS_LEN"] = df["REQUIRED_SKILLS"].apply(
        lambda x: len(eval(x)) if isinstance(x, str) else 0
    )
    df["ADDITIONAL_SKILLS_LEN"] = df["ADDITIONAL_SKILLS"].apply(
        lambda x: len(eval(x)) if isinstance(x, str) and x != "None" else 0
    )
    X = df[["REQUIRED_SKILLS_LEN", "ADDITIONAL_SKILLS_LEN"]].fillna(0)
    y_from = df["PAYMENT_FROM"].astype(float).fillna(
        df["PAYMENT_FROM"].astype(float).median()
    )
    y_to = df["PAYMENT_TO"].astype(float).fillna(
        df["PAYMENT_TO"].astype(float).median()
    )

    model_from = LinearRegression()
    model_to = LinearRegression()
    model_from.fit(X, y_from)
    model_to.fit(X, y_to)

    return model_from, model_to


def visualize_data(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """
    Visualize data from the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing job data.

    Returns
    -------
    Tuple[pd.Series, pd.Series]
        Most common skills and high salary skills.
    """
    most_common_skills, high_salary_skills = analyze_most_desirable_skills(df)
    plot_required_skills_pie_chart(df)
    plot_salary_ranges(df)
    plot_job_locations(df)
    plot_salary_trends(df)
    cluster_job_offers(df)
    return most_common_skills, high_salary_skills


def plot_required_skills_pie_chart(
    df: pd.DataFrame, ax: plt.Axes = None, job_type: str = None
) -> None:
    """
    Plot a pie chart of the required skills distribution.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing job data.
    ax : plt.Axes, optional
        Matplotlib axes object to draw the plot onto.
    job_type : str, optional
        Job type for the title.
    """
    skills = df["REQUIRED_SKILLS"].apply(lambda x: eval(x) if isinstance(x, str) else [])
    if skills.apply(len).sum() == 0:
        return  # Skip plotting if there are no skills to plot
    skills_counts = pd.Series(np.concatenate(skills.values)).value_counts()
    skills_counts.head(20).plot(kind="pie", autopct="%1.1f%%", ax=ax)
    if ax:
        ax.set_title(f"Required Skills Distribution - {job_type}")
        ax.set_ylabel("")  # Remove y-axis label
    else:
        plt.title("Required Skills Distribution")
        plt.ylabel("")  # Remove y-axis label
        plt.show()


def plot_salary_ranges(df: pd.DataFrame) -> None:
    """
    Plot box plots of salary ranges.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing job data.
    """
    # plt.figure(figsize=(6, 4))
    df[["PAYMENT_FROM", "PAYMENT_TO"]].astype(float).plot(kind="box")
    plt.title("Salary Ranges")
    plt.ylabel("Salary (PLN)")
    plt.show()


def analyze_most_desirable_skills(
    df: pd.DataFrame
) -> Tuple[pd.Series, pd.Series]:
    """
    Analyze and return the most desirable skills and high salary skills.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing job data.

    Returns
    -------
    Tuple[pd.Series, pd.Series]
        Most common skills and high salary skills.
    """
    skills = df["REQUIRED_SKILLS"].apply(lambda x: eval(x) if isinstance(x, str) else [])
    if skills.apply(len).sum() == 0:
        return pd.Series(dtype="int"), pd.Series(dtype="int")
    skills_counts = pd.Series(np.concatenate(skills.values)).value_counts()
    high_salary_skills = pd.Series(
        np.concatenate(
            df[df["PAYMENT_TO"].astype(float) > df["PAYMENT_TO"].astype(float).quantile(0.75)][
                "REQUIRED_SKILLS"
            ].apply(lambda x: eval(x) if isinstance(x, str) else []).values
        )
    ).value_counts()

    return skills_counts.head(20), high_salary_skills.head(20)


def plot_job_locations(
    df: pd.DataFrame, ax: plt.Axes = None, job_type: str = None
) -> None:
    """
    Plot a bar chart of the top 10 job locations.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing job data.
    ax : plt.Axes, optional
        Matplotlib axes object to draw the plot onto.
    job_type : str, optional
        Job type for the title.
    """
    location_counts = df["LOCATION"].value_counts().head(10)
    if location_counts.empty:
        return  # Skip plotting if there are no locations to plot
    location_counts.plot(kind="bar", ax=ax)
    if ax:
        ax.set_title(f"Job Locations (Top 10) - {job_type}")
        ax.set_xlabel("")
        ax.set_ylabel("Number of Jobs")
    else:
        plt.title(f"Job Locations (Top 10) - {job_type}")
        plt.xlabel("")
        plt.ylabel("Number of Jobs")
        plt.show()


def plot_salary_trends(df: pd.DataFrame) -> None:
    """
    Plot salary trends over time.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing job data.
    """
    df["DATE"] = pd.to_datetime(df["DATE"])
    df = df.sort_values("DATE")
    plt.figure(figsize=(8, 5))
    plt.plot(df["DATE"], df["PAYMENT_FROM"].astype(float), label="Payment From")
    plt.plot(df["DATE"], df["PAYMENT_TO"].astype(float), label="Payment To")
    plt.title("Salary Trends Over Time")
    plt.xlabel("Date")
    plt.ylabel("Salary (PLN)")
    plt.legend()
    plt.show()


def elbow_method(X: np.ndarray, ax: plt.Axes = None) -> int:
    """
    Use the elbow method to determine the optimal number of clusters.

    Parameters
    ----------
    X : np.ndarray
        Data for clustering.
    ax : plt.Axes, optional
        Matplotlib axes object to draw the plot onto.

    Returns
    -------
    int
        Optimal number of clusters.
    """
    distortions = []
    K = range(1, min(11, len(X) + 1))
    for k in K:
        kmeans = KMeans(n_clusters=k, random_state=0)
        kmeans.fit(X)
        distortions.append(kmeans.inertia_)

    angles = []
    for i in range(1, len(K) - 1):
        p1 = np.array([K[i - 1], distortions[i - 1]])
        p2 = np.array([K[i], distortions[i]])
        p3 = np.array([K[i + 1], distortions[i + 1]])
        v1 = p1 - p2
        v2 = p3 - p2
        dot_product = np.dot(v1, v2)
        norms_product = np.linalg.norm(v1) * np.linalg.norm(v2)
        cos_angle = dot_product / norms_product
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle = np.arccos(cos_angle)
        angles.append(angle)

    if angles:
        optimal_k = K[np.argmax(angles) + 1]
        optimal_k = max(optimal_k - 2, 2)
    else:
        optimal_k = 2

    if ax:
        ax.plot(K, distortions, "bx-")
        ax.set_xlabel("k")
        ax.set_ylabel("Distortion")
        ax.set_title(f"Elbow Method For Optimal k = {optimal_k}")
    else:
        plt.plot(K, distortions, "bx-")
        plt.xlabel("k")
        plt.ylabel("Distortion")
        plt.title(f"Elbow Method For Optimal k = {optimal_k}")
        plt.show()

    return optimal_k


def cluster_job_offers(df: pd.DataFrame) -> None:
    """
    Cluster job offers based on required and additional skills.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing job data.
    """
    df["REQUIRED_SKILLS_LEN"] = df["REQUIRED_SKILLS"].apply(
        lambda x: len(eval(x)) if isinstance(x, str) else 0
    )
    df["ADDITIONAL_SKILLS_LEN"] = df["ADDITIONAL_SKILLS"].apply(
        lambda x: len(eval(x)) if isinstance(x, str) and x != "None" else 0
    )

    df = df.dropna(subset=["REQUIRED_SKILLS_LEN", "PAYMENT_FROM", "PAYMENT_TO"])

    plot_clusters(df)


def plot_clusters(df: pd.DataFrame) -> None:
    """
    Plot clusters of job offers based on required skills and payment.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing job data.
    """
    job_types = df["JOB_TYPE"].unique()
    num_plots = len(job_types)
    num_per_page = 3
    num_pages = (num_plots + num_per_page - 1) // num_per_page

    for page in range(num_pages):
        fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(12, 18))
        axes = axes.flatten()

        for i in range(num_per_page):
            index = page * num_per_page + i
            if index >= num_plots:
                axes[2 * i].axis("off")
                axes[2 * i + 1].axis("off")
                continue

            job_type = job_types[index]
            subset = df[df["JOB_TYPE"] == job_type]
            X = subset[
                ["REQUIRED_SKILLS_LEN", "PAYMENT_FROM", "PAYMENT_TO"]
            ].dropna()

            if X.empty or len(X) < 2:
                axes[2 * i].axis("off")
                axes[2 * i + 1].axis("off")
                continue

            optimal_clusters = elbow_method(X, ax=axes[2 * i])

            kmeans = KMeans(n_clusters=optimal_clusters, random_state=0).fit(X)
            subset = subset.copy()  # Avoid SettingWithCopyWarning
            subset.loc[:, "CLUSTER"] = kmeans.labels_

            axes[2 * i + 1].scatter(
                subset["REQUIRED_SKILLS_LEN"],
                subset["PAYMENT_FROM"].astype(float),
                c=subset["CLUSTER"],
                cmap="viridis",
            )
            axes[2 * i + 1].set_title(f"Clustering for {job_type}")
            axes[2 * i + 1].set_xlabel("Required Skills Length")
            axes[2 * i + 1].set_ylabel("Payment From")

        plt.tight_layout()
        plt.show()


def analyze_job_types(df: pd.DataFrame) -> None:
    """
    Analyze job types for salary ranges and skill distribution.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing job data.
    """
    job_types = df["JOB_TYPE"].unique()
    num_plots = len(job_types)
    num_per_page = 4
    num_pages = (num_plots + num_per_page - 1) // num_per_page

    for page in range(num_pages):
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(8, 8))
        axes = axes.flatten()

        for i in range(num_per_page):
            index = page * num_per_page + i
            if index >= num_plots:
                axes[i].axis("off")
                continue

            job_type = job_types[index]
            subset = df[df["JOB_TYPE"] == job_type]
            subset[["PAYMENT_FROM", "PAYMENT_TO"]].astype(float).plot(
                kind="box", ax=axes[i]
            )
            axes[i].set_title(f"Salary Ranges for {job_type}")
            axes[i].set_ylabel("Salary (PLN)")

        plt.tight_layout()
        plt.show()

    for page in range(num_pages):
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(8, 8))
        axes = axes.flatten()

        for i in range(num_per_page):
            index = page * num_per_page + i
            if index >= num_plots:
                axes[i].axis("off")
                continue

            job_type = job_types[index]
            subset = df[df["JOB_TYPE"] == job_type]
            plot_required_skills_pie_chart(subset, ax=axes[i], job_type=job_type)

        plt.tight_layout()
        plt.show()

    for page in range(num_pages):
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(8, 8))
        axes = axes.flatten()

        for i in range(num_per_page):
            index = page * num_per_page + i
            if index >= num_plots:
                axes[i].axis("off")
                continue

            job_type = job_types[index]
            subset = df[df["JOB_TYPE"] == job_type]
            plot_job_locations(subset, ax=axes[i], job_type=job_type)

        plt.tight_layout()
        plt.show()


def analyze_skill_salary_relationship(df: pd.DataFrame) -> None:
    """
    Analyze the relationship between skills and salary.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing job data.
    """
    skills = df["REQUIRED_SKILLS"].apply(lambda x: eval(x) if isinstance(x, str) else [])
    skill_counts = pd.Series(np.concatenate(skills.values)).value_counts(
        normalize=True
    ).head(20)

    skills_repeated = np.concatenate(skills.values)
    payment_repeated = np.repeat(df["PAYMENT_FROM"].values, [len(s) for s in skills])

    skill_salary = pd.DataFrame(
        {"SKILL": skills_repeated, "PAYMENT_FROM": payment_repeated}
    )
    avg_salary_per_skill = skill_salary.groupby("SKILL")["PAYMENT_FROM"].mean().loc[
        skill_counts.index
    ]

    plt.figure(figsize=(10, 6))
    avg_salary_per_skill.plot(kind="bar")
    plt.title("Average Salary by Top 20 Skills")
    plt.xlabel("Skills")
    plt.ylabel("Average Salary (PLN)")
    plt.xticks(rotation=45)
    plt.show()

    print("\nAverage Salary by Top 20 Skills:\n", avg_salary_per_skill)

def plot_salary_trends(df: pd.DataFrame) -> None:
    """
    Plot salary trends over time with future approximation.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing job data.
    """
    df["DATE"] = pd.to_datetime(df["DATE"])
    df = df.sort_values("DATE")

    # Fill NaN values with the median of the respective columns
    df["PAYMENT_FROM"] = df["PAYMENT_FROM"].astype(float).fillna(df["PAYMENT_FROM"].astype(float).median())
    df["PAYMENT_TO"] = df["PAYMENT_TO"].astype(float).fillna(df["PAYMENT_TO"].astype(float).median())

    # Adding future dates for approximation
    future_dates = pd.date_range(df["DATE"].max(), periods=10, freq='D')[1:]
    future_df = pd.DataFrame(future_dates, columns=["DATE"])

    model_from = LinearRegression()
    model_to = LinearRegression()

    X = np.array(df.index).reshape(-1, 1)
    y_from = df["PAYMENT_FROM"].astype(float)
    y_to = df["PAYMENT_TO"].astype(float)

    model_from.fit(X, y_from)
    model_to.fit(X, y_to)

    future_X = np.array(range(len(df), len(df) + len(future_dates))).reshape(-1, 1)
    future_df["PAYMENT_FROM"] = model_from.predict(future_X)
    future_df["PAYMENT_TO"] = model_to.predict(future_X)

    plt.figure(figsize=(8, 5))
    plt.plot(df["DATE"], df["PAYMENT_FROM"].astype(float), label="Payment From")
    plt.plot(df["DATE"], df["PAYMENT_TO"].astype(float), label="Payment To")
    plt.plot(future_df["DATE"], future_df["PAYMENT_FROM"], linestyle='--', color='blue', label="Predicted Payment From")
    plt.plot(future_df["DATE"], future_df["PAYMENT_TO"], linestyle='--', color='orange', label="Predicted Payment To")
    plt.title("Salary Trends Over Time")
    plt.xlabel("Date")
    plt.ylabel("Salary (PLN)")
    plt.legend()
    plt.show()
