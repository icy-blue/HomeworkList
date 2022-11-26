import requests
import yaml
import os
from datetime import datetime
import json

limit = os.getenv('ENV_HOMEWORK_LIMIT', default=200)
owner = os.getenv('ENV_OWNER', default='SDUOJ-Team')
token = os.getenv('ENV_GITHUB_TOKEN')
period = os.getenv('ENV_FETCH_PERIOD')
pagesize = os.getenv('ENV_PAGE_SIZE', default=50)

with open('homeworks.yml', 'r') as file:
    homeworks = yaml.safe_load(file)


def setup_request(homework, page=1):
    repo_name = homework['name']
    url = f'https://api.github.com/repos/{owner}/{repo_name}/issues'
    headers = {}
    headers['Accept'] = 'application/vnd.github+json'
    if token is not None:
        headers['Authorization']: token
        print('token-length: ', len(token))
    params = {
        'state': 'all',
        'page': page,
        'per_page': pagesize,
    }
    if period is not None:
        now = datetime.now()
        start = now - datetime.timedelta(days=period)
        params['since'] = start.isoformat()
    print(params)
    r = requests.get(url=url, headers=headers, params=params)
    return json.loads(r.text)


def collect_issues(homework):
    issues = []
    page = 1
    data = setup_request(homework, page)
    while len(data) != 0 and len(issues) <= limit:
        # print(type(data), data)
        page = page + 1
        issues = issues + data
        data = setup_request(homework, page)
    return issues


def check_valid(issue, homework):
    if homework['type'] == 'pr' and 'pull_request' in issue:
        return None, False
    finished = issue['state'] == 'closed'
    if 'tag' in homework:
        is_answer = False
        for label in issue['labels']:
            is_answer = is_answer | (label['name'] == homework['tag'])
        finished = finished & is_answer
    if 'title' in homework and not issue['title'] in homework['title']:
        return None, False
    return issue['title'], finished


if __name__ == '__main__':
    for homework in homeworks['Homeworks']:
        issues = collect_issues(homework)
        for issue in issues:
            title, finished = check_valid(issue, homework)
            print(issue['state'], issue['labels'], title, finished)
