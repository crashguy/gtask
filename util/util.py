import base64
import logging
import os

import requests


def get_config(repo, branch, path):
    if repo.startswith('github.com/'):
        repo = repo[11:]
    url = "https://{username}:{password}@api.github.com/repos/" \
          "{repo}/contents/{path}?ref={branch}".format(
            username=os.environ['GITHUB_USERNAME'],
            password=os.environ['GITHUB_PASSWORD'],
            repo=repo, path=path, branch=branch)
    try:
        r = base64.b64decode(requests.get(url, timeout=10).json()['content']).decode()
    except Exception as e:
        logging.error('get config error', str(e))
        r = ""
    return r


def get_commit_id(repo, branch):
    if repo.startswith('github.com/'):
        repo = repo[11:]
    url = "https://{username}:{password}@api.github.com/repos/" \
          "{repo}/commits/{branch}".format(
            username=os.environ['GITHUB_USERNAME'],
            password=os.environ['GITHUB_PASSWORD'],
            repo=repo, branch=branch)
    try:
        r = requests.get(url, timeout=10).json()
        commit_id = r['sha']
        logging.info('%s commit_id is %s' % (branch, commit_id))
    except Exception as e:
        logging.error('get %s commit_id error. ', branch)
        logging.error(str(e))
        commit_id = ""
    return commit_id


if __name__ == '__main__':
    # test get_config
    # print(get_config("github.com/naturali/dnn", "master", "speech/config.py"))
    # test get_commit_id
    print(get_commit_id("github.com/naturali/dnn", "test_nan_gpu"))
    pass
