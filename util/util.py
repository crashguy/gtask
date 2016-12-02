import requests
import base64
import logging


def get_config(repo, branch, path):
    if repo.startswith('github.com/'):
        repo = repo[11:]
    url = "https://crashguy:cc860808@api.github.com/repos/{repo}/contents/{path}?ref={branch}".format(repo=repo, path=path, branch=branch)
    try:
        r = base64.b64decode(requests.get(url).json()['content']).decode()
    except Exception as e:
        logging.error('get config error', str(e))
        r = ""
    return r

if __name__ == '__main__':
    # test get_config
    print(get_config("github.com/alphaf52/dnn", "for_platform", "speech/config.py"))
