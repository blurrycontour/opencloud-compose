""" Script to download and install web extensions for OpenCloud. """

import argparse
import os
import xml.etree.ElementTree as ET
import shutil
import subprocess

import requests


extensions = [
    "calculator",
    "progress-bars",
    "draw-io",
    "json-viewer",
    "maps",
    "pastebin",
    "unzip",
]
feed_url = "https://github.com/opencloud-eu/web-extensions/releases.atom"

def find_latest_release(extension, feed):
    """ Get the latest release for a given extension from the feed XML. """
    root = ET.fromstring(feed)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall("atom:entry", ns):
        title = entry.find("atom:title", ns).text
        semver = title.split()[-1]  # Assuming version is the last word in the title
        if extension in title:
            link = entry.find("atom:link", ns).attrib["href"]
            asset_link = link.replace("/tag/", "/download/") + f"/{extension}-{semver}.zip"
            return asset_link, semver
    return None, None


def download_asset(url:str, target_path:str):
    """ Download the asset from the given URL and save it to the target path. """
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "wb") as f:
            f.write(response.content)
        print(f"  Downloaded to {target_path}")
    else:
        print(f"  Failed to download from {url}. HTTP status code: {response.status_code}")


def extract_asset(zip_path, target_dir):
    """ Extract the downloaded zip file to the target directory. """
    try:
        subprocess.run(["unzip", "-o", zip_path, "-d", target_dir], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"  Extracted {zip_path} to {target_dir}")
        os.remove(zip_path)
        print(f"  Removed {zip_path}")
    except subprocess.CalledProcessError as e:
        print(f"  Failed to extract {zip_path}. Error: {e}")


if __name__ == "__main__":
    # parse args
    ap = argparse.ArgumentParser(description="Download and install web extensions for OpenCloud.")
    ap.add_argument("--extensions", "-e", nargs="+", default=extensions, help=f"List of extensions to download (default: {extensions})")
    ap.add_argument("--target-dir", "-t", required=True, help="Directory to save downloaded extensions")
    ap.add_argument("--clear", "-c", action="store_true", help="Clear existing extensions before downloading new ones")
    args = ap.parse_args()

    os.makedirs(args.target_dir, exist_ok=True)
    # Clear existing extensions
    if args.clear:
        shutil.rmtree(args.target_dir, ignore_errors=True)

    feed = requests.get(feed_url, timeout=10).text
    for extension in args.extensions:
        print(f"{extension}:")
        asset_url, version = find_latest_release(extension, feed)
        if asset_url:
            print(f"  Version: {version}")
            print(f"  Link: {asset_url}")
            # download the asset
            target_path = f"{args.target_dir}/{extension}-{version}.zip"
            download_asset(asset_url, target_path)
            extract_asset(target_path, args.target_dir)
        else:
            print(f"  Failed to find latest release for {extension}.")
