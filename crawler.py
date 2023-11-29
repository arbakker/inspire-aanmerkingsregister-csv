import argparse
import sys
import urllib.parse

import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_text_without_children(soup, selector):
    return "".join(
        soup.select_one(selector).find_all(string=True, recursive=False)
    ).strip()


def get_dataset(soup):
    article_soup = soup.select_one(".node-dataset-full.node-dataset-full--promoted")
    title = article_soup.select_one(".node-dataset-full__title>span").text.strip()
    annex = article_soup.select_one(".node-dataset-full__annex-item").text.strip()
    thema = article_soup.select_one(".node-dataset-full__theme-item").text.strip()

    primary_dataprovider = article_soup.select_one(
        ".node-dataset-full__primary-provider>a"
    ).text.strip()

    extra_dataproviders = ",".join(
        [
            x.text.strip()
            for x in article_soup.select(".node-dataset-full__provider-item>a")
        ]
    )

    decision_policy_manager = get_text_without_children(
        article_soup, ".node-dataset-full__decision-policy-manager"
    )
    date_decision = article_soup.select_one(
        ".node-dataset-full__date-decision>time"
    ).text.strip()
    dataset_status = get_text_without_children(
        article_soup, ".node-dataset-full__status"
    )
    md_url_as_is = None
    try:
        md_url_as_is = article_soup.select_one(
            ".node-dataset-full__uuid-as-is-link", href=True
        )["href"]
    except TypeError:
        pass
    md_url_harmonized = None
    try:
        md_url_harmonized = article_soup.select_one(
            ".node-dataset-full__uuid-harmonized-link", href=True
        )["href"]
    except TypeError:
        pass

    return {
        "title": title,
        "annex": annex,
        "thema": thema,
        "primary_dataprovider": primary_dataprovider,
        "extra_dataprovider": extra_dataproviders,
        "decision_policy_manager": decision_policy_manager,
        "date_decision": date_decision,
        "dataset_status": dataset_status,
        "md_url_as_is": md_url_as_is,
        "md_url_harmonized": md_url_harmonized,
    }


def get_datasets(soup):
    datasets = []
    for s_dataset in soup.select(
        "article.node-dataset-card.node-dataset-card--promoted"
    ):
        url_dataset = s_dataset.select_one(
            "a.node-dataset-card__title-link", href=True
        )["href"]
        url_dataset = urllib.parse.urljoin(
            "https://www.inspireaanmerking.nl/aanmerkingsregister?page=", url_dataset
        )
        print(url_dataset, file=sys.stderr)
        ds_soup = BeautifulSoup(
            requests.get(url_dataset, timeout=10).text, features="html.parser"
        )
        dataset = get_dataset(ds_soup)
        datasets.append(dataset)
    return datasets


def main(output_file):
    base_url = "https://www.inspireaanmerking.nl/aanmerkingsregister?page="
    i = 0
    datasets = []
    while True:
        url = f"{base_url}{i}"
        print(f"crawling {url}", file=sys.stderr)
        soup = BeautifulSoup(requests.get(url, timeout=10).text, features="html.parser")
        page_datasets = get_datasets(soup)
        if len(page_datasets) == 0:
            break
        else:
            datasets.extend(page_datasets)
            i += 1

    df = pd.DataFrame(datasets)
    with open(output_file, "w") if output_file != "-" else sys.stdout as out_f:
        df.to_csv(out_f, sep="\t", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crawler for inspireaanmerking.nl",
    )
    parser.add_argument(
        "output_csv_file",
        type=str,
        help="Filepath of output CSV file - overwrites if already exists, if empty writes to stdout",
        default=["-"],
        nargs="*",
    )
    args = parser.parse_args()
    if len(args.output_csv_file) > 1:
        raise ValueError("ERROR: only one output_csv_file arg allowed")

    main(args.output_csv_file[0])
