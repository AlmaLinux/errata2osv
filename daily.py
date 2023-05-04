import argparse
import gzip
import os
import shutil
import sys
from datetime import date
from typing import Optional

import requests
import wget
import yaml
from bs4 import BeautifulSoup
from git import Repo

from errata2osv import errata_to_osv

tmpfile_name = 'updateinfo.xml'
excluded_repos = ["isos/", "cloud/", "live/", "metadata/", "raspberrypi/"]


def get_repos(url):
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Request failed with status code {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    repos = []

    for link in soup.find_all("a"):
        href = link.get("href")
        if href not in excluded_repos and href != '../' and href.endswith("/"):
            repos.append(url + href)

    return repos


def find_updateinfo_link(repo_link: str) -> Optional[str]:
    response = requests.get(repo_link)

    if response.status_code != 200:
        raise Exception(f'Request failed with status code {response.status_code}')

    soup = BeautifulSoup(response.text, "html.parser")

    for link in soup.find_all("a"):
        href = link.get("href")
        if href.endswith("updateinfo.xml.gz"):
            return repo_link + href

    return None


def process_database(database_name, repo_rootdir, repo_link, ecosystem, commit_msg):
    links = []
    repo_datadir = os.path.join(repo_rootdir, 'advisories', database_name)

    # get list of repositories
    repos = get_repos(repo_link)

    for repo in repos:
        repo_url = f"{repo}/x86_64/os/repodata/"
        updateinfo_link = find_updateinfo_link(repo_url)

        if updateinfo_link is None:
            print(f'updateinfo.xml.gz not found in {repo_link}')

        links.append(updateinfo_link)
        archive = wget.download(updateinfo_link)
        # unpack gz archive
        with gzip.open(archive, 'rb') as f_in:
            with open(tmpfile_name, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        errata_to_osv(tmpfile_name,
                      repo_datadir,
                      ecosystem)

        # remove downloaded archive and tmpfile
        os.remove(archive)
        os.remove(tmpfile_name)

    # workaround for current known issues in AlmaLinux 9 errata
    # remove osv entries with ids mentioned in almalinux8 database
    if os.path.basename(database_name) == 'almalinux9':
        # list files in almalinux8 database
        almalinux8_datadir = os.path.join(repo_rootdir, 'advisories', 'almalinux8')
        almalinux8_files = os.listdir(almalinux8_datadir)
        # remove osv entries with ids mentioned in almalinux8 database
        for almalinux8_file in almalinux8_files:
            if os.path.isfile(os.path.join(repo_datadir, almalinux8_file)):
                os.remove(os.path.join(repo_datadir, almalinux8_file))

    repo = Repo(repo_rootdir)
    repo.git.add(repo_datadir)
    if commit_msg is None:
        database_name = os.path.basename(repo_datadir)
        # Evaluate current date
        today = date.today()
        commit_msg = f'Sync {database_name} database from {today}\n\nUpdateinfo links:\n'
        for updateinfo_link in links:
            commit_msg += f'{updateinfo_link}\n'
    else:
        commit_msg = commit_msg
    repo.index.commit(commit_msg)


def main(vargs):
    parser = argparse.ArgumentParser(description='update osv-database repository',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('repo_rootdir', help='path to osv-database repository')
    parser.add_argument('--repos-file', default='sync_repos.yaml', help='yaml file with repositories to sync')
    parser.add_argument('--commit-msg', help='commit message', default=None)
    args = parser.parse_args(vargs)

    # Parse repos_file with the following structure:
    # database_name:
    #  repo_link: https://repo.link/
    #  ecosystem: ecosystem
    with open(args.repos_file) as f:
        yaml_data = yaml.safe_load(f)
        for key in yaml_data.keys():
            process_database(key,
                             args.repo_rootdir,
                             yaml_data[key]['repo_link'],
                             yaml_data[key]['ecosystem'],
                             args.commit_msg)


if __name__ == '__main__':
    main(sys.argv[1:])
