import calendar
from collections import Counter
import logging
import os
import time

from github import Github, GithubException, RateLimitExceededException
from typing import Dict

from tqdm import tqdm

logger = logging.getLogger(__name__)


def get_time_to_limit_reset(github: Github) -> float:
    """
    A method that calculates how much time until GitHub api limit breaks
    Args:
        github: GitHub instance
    Returns: estimated time to api reset in seconds
    """
    search_rate_limit = github.get_rate_limit().search
    reset_timestamp = calendar.timegm(search_rate_limit.reset.timetuple())
    return max(reset_timestamp - calendar.timegm(time.gmtime()), 0)


def process_stargazers(repo_name: str,
                       max_user_stars: int = 100,
                       n_top_repos: int = 100,
                       requests_per_page: int = 100,
                       access_token: str = None,
                       token_env_key: str = None) -> Dict[str, int]:
    """
    A method that does following:
    1. get all GitHub repo stargazers (list)
    2. for each stargazer get all of his starred repos
    3. for each visited repo during previous step saves its stargazers count
    4. returns mapping "repo" - "how much stars from our list repo has"
    Args:
        repo_name: name of GitHub repo like "scikit-learn/scikit-learn"
        max_user_stars: only max_user_stars starred repo from each user counts
        n_top_repos: returns this number of most popular repos
        requests_per_page: number of recordings in one api call
        access_token: GitHub api token
        token_env_key: env key where GitHub api token stored

    Returns: {repo_url: n_stargazers}
    """
    def handle_rate_limit_exception(exception: RateLimitExceededException):
        logger.exception(f"limit when tried to call GitHub api - {exception}")
        time.sleep(get_time_to_limit_reset(g) + 10)

    token = access_token or os.getenv(token_env_key)

    # make sure user pass access_token or $token_env_key exists
    if token is None:
        raise ValueError("you should specify access_token or token_env_key")

    repo_to_stars = Counter()
    g = Github(token)

    repo = None
    while repo is None:
        try:
            repo = g.get_repo(repo_name)
        except RateLimitExceededException as e:
            handle_rate_limit_exception(e)

    repo._requester.per_page = requests_per_page

    for user in tqdm(repo.get_stargazers()):
        try:
            for i, starred_repo in enumerate(user.get_starred()):
                if i >= max_user_stars:
                    break
                repo_to_stars[starred_repo.full_name] += 1
        except RateLimitExceededException as e:
            handle_rate_limit_exception(e)
        except GithubException as e:
            logger.exception(f"github exception - {e}")

    return dict(repo_to_stars.most_common(n_top_repos))
