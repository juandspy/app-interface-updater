from pprint import pprint
from PyInquirer import prompt, Separator
from rich import print as pprint
from datetime import datetime
import subprocess
import os


from app_interface import (
    read_yaml,
    get_services,
    get_namespaces,
    get_sha,
    update_sha,
    replace_sha,
)
from git_helpers import get_sha_date, init_repo
from config import REPOSITORIES_FOLDER, PATH_TO_DEPLOY_YML


def to_date(ts):
    if type(ts) == str:
        return ts
    return datetime.fromtimestamp(ts)


def build_question_get_answer(type, message, choices=[], qmark="❓"):
    question = [
        {
            "type": type,
            "qmark": qmark,
            "message": message,
            "name": "answer",
        }
    ]
    if len(choices) > 0:
        question[0]["choices"] = [{"name": choice} for choice in choices]

    ans = prompt(question)["answer"]
    if type == "checkbox":
        if len(ans) != 1:
            pprint(":cross_mark: You can only chose one answer")
            exit(1)
        ans = ans[0]
    return ans

def run_and_fail_if_exit_code(args, cwd):
    p = subprocess.run(args, cwd=cwd)
    if p.returncode != 0:
        raise Exception( f'Invalid exit code: { p.returncode }' )

if __name__ == "__main__":
    pprint(":book: Reading", PATH_TO_DEPLOY_YML)
    y = read_yaml(PATH_TO_DEPLOY_YML)

    service = build_question_get_answer(
        "checkbox", "Select the service you want to update", get_services(y)
    )

    namespace = build_question_get_answer(
        "checkbox",
        "Select the namespace you want to update",
        get_namespaces(y, service),
    )

    repo = init_repo(f"{REPOSITORIES_FOLDER}/{service.replace('.yml', '')}")

    new_sha = build_question_get_answer("input", "Write the new SHA value")
    try:
        new_sha_date = get_sha_date(repo, new_sha)
    except Exception as e:
        pprint(f"    :warning: Could not find {new_sha}'s date:\n{e}\n")
        new_sha_date = "Unknown"

    current_sha = get_sha(y, service, namespace)
    try:
        current_sha_date = get_sha_date(repo, current_sha)
    except Exception as e:
        pprint(f"    :warning: Could not find {current_sha}'s date:\n{e}\n")
        current_sha_date = "Unknown"
    pprint(
        f"    The current SHA in app-interface is [bold cyan]{current_sha} (date: {to_date(current_sha_date)})[/bold cyan]",
    )
    pprint(
        f"    The new SHA for {service} is [bold cyan]{new_sha} (date: {to_date(new_sha_date)})[/bold cyan]",
    )

    if not build_question_get_answer(
        "confirm",
        "Do you want to continue?",
    ):
        exit(0)

    pprint(f"    :car: Replacing the SHA")
    replace_sha(y, service, new_sha, namespace, PATH_TO_DEPLOY_YML)

    if build_question_get_answer(
        "confirm",
        "Do you want to see the git diff?",
    ):
        run_and_fail_if_exit_code(["git", "diff"], cwd=os.path.dirname(PATH_TO_DEPLOY_YML))

    commit_branch = f"update-{service}-{namespace}-{new_sha}"
    commit_msg = f'"update {service} in {namespace} to SHA {new_sha}"'

    if build_question_get_answer(
        "confirm",
        "Do you want to commit the changes?",
    ):
        pprint(f"    :keycap_1: Switching to branch [bold cyan]{commit_branch}[/bold cyan]")
        run_and_fail_if_exit_code(["git", "checkout", "-b", commit_branch], cwd=os.path.dirname(PATH_TO_DEPLOY_YML))

        pprint(f"    :keycap_2: Commiting the changes with message: [bold cyan]{commit_msg}[/bold cyan]")
        run_and_fail_if_exit_code(["git", "add", "deploy.yml"], cwd=os.path.dirname(PATH_TO_DEPLOY_YML))
        run_and_fail_if_exit_code(["git", "commit", "-m", commit_msg], cwd=os.path.dirname(PATH_TO_DEPLOY_YML))

    if build_question_get_answer(
        "confirm",
        "Do you want to push the changes?",
    ):
        run_and_fail_if_exit_code(["git", "push", "-u", "fork", commit_branch], cwd=os.path.dirname(PATH_TO_DEPLOY_YML))

    pprint(f"    :backhand_index_pointing_up: Click on the link above to create the MR")
