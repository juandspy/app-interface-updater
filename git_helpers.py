from git import Repo


def get_sha_date(repo, sha):
    commit = repo.commit(sha)
    return commit.committed_date


def init_repo(repo_path):
    return Repo(repo_path)


def add_new_tag(repo, tag):
    new_tag = repo.create_tag(tag)


def check_tag_exists(repo, tag):
    return tag in repo.tags


if __name__ == "__main__":
    MY_REPO = "../ccx-data-pipeline"

    repo = init_repo(MY_REPO)

    new_sha = "7245a0bcc22ca25c2f1a77f320f1f3544b521a6e"

    get_sha_date(repo, new_sha)
