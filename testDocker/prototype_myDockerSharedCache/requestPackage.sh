read -p "Enter server url: " url
uv run --with requests python requestPackage.py "$url"