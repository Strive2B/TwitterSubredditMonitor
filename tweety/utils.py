import os


def file_size_bytes(file_path: str):
    """Returns file size in bytes"""
    st = os.stat(file_path)
    return st.st_size


def tweet_url_to_id(tweet_url: str) -> int:
    return int(tweet_url.split("status/")[-1].split("/")[0])


def space_url_to_id(space_url: str) -> str:
    return space_url.split('spaces/')[-1].split("/")[0]
