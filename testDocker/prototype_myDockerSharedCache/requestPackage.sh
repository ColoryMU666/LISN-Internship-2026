read -p "Enter server url: " url
uv run --with requests --with fastapi main.py "$url"
