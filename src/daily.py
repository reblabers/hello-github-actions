import json
import os
import time
from datetime import datetime
from pathlib import Path
from github import Github


# daily.jsonのパスを定義
daily_json_path = os.path.join(
    os.path.dirname(__file__), '../mnemonic/daily.json')

# daily.jsonを読み込む関数


def read_daily_json(path: Path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

# 今日の日付を取得する関数


def get_today_date():
    return datetime.now().strftime('%Y-%m-%d')

# daily.jsonに今日の日付を書き出す関数


def write_daily_json(path: Path, date):
    data = {'date': date}
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def save(path: Path, data: str, metadata: dict):
    os.makedirs(path.parent, exist_ok=True)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)
    
    with open(f"{path}.metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f)


def timestamp(dt: datetime) -> int:
    return int(dt.timestamp())


def save_pr(repo, pr, pr_dir: Path):
    file_dir = pr_dir / "files"

    # https://pygithub.readthedocs.io/en/latest/github_objects/PullRequest.html

    status = 'merged' if pr.merged else 'closed'
    metadata = {
        "repo": repo.full_name,
        "status": status,
        "created_at": timestamp(pr.created_at),
        "updated_at": timestamp(pr.updated_at),
    }

    descriptions = [
        f"<title>{pr.title}</title>",
        f"<repository>{repo.full_name}</repository>",
        f"<head>{pr.head.ref}</head>",
        f"<base>{pr.base.ref}</base>",
        f"<created_at>{pr.created_at}</created_at>",
        f"<closed_at>{pr.closed_at}</closed_at>",
        f"<merged_at>{pr.merged_at if pr.merged else "null"}</merged_at>",
        f"<description>{pr.body}</description>",
    ]
    content = "\n".join(descriptions)
    save(pr_dir / "abstract.xml", content, metadata)

    # review comments
    review_comments = {}
    for review_comment in pr.get_review_comments():
        body = review_comment.body
        user_id = review_comment.user.id
        path = review_comment.path
        # created_at = timestamp(review_comment.created_at)

        if path not in review_comments:
            review_comments[path] = ["<comments>"]
   
        review_comments[path].append("<comment>")
        review_comments[path].append(f"### user: {user_id}")
        review_comments[path].append("")
        review_comments[path].append(f"{body}")
        review_comments[path].append("</comment>")
    
    for path in review_comments:
        content = "\n".join(review_comments[path] + ["</comments>"])
        save(file_dir / path / "comments.xml", content, metadata)
    
    # issue comments
    issue_comments = ["<comments>"]
    for issue_comment in pr.get_issue_comments():
        body = issue_comment.body
        user_id = issue_comment.user.id
        # created_at = timestamp(issue_comment.created_at)

        issue_comments.append("<comment>")
        issue_comments.append(f"### user: {user_id}")
        issue_comments.append("")
        issue_comments.append(f"{body}")
        issue_comments.append("</comment>")

    content = "\n".join(issue_comments + ["</comments>"])
    save(pr_dir / "comments.xml", content, metadata)

     # diffs
    for file in pr.get_files():
        if file.patch:
            save(file_dir / file.filename / "diffs.patch", file.patch, metadata)


def main():
    # daily.jsonを読み込む
    # daily_data = read_daily_json(daily_json_path)
    # print('Current daily.json:', daily_data)

    # # 今日の日付を取得
    # today_date = get_today_date()
    # print('Today\'s date:', today_date)

    # daily.jsonに今日の日付を書き出す
    # write_daily_json(daily_json_path, today_date)
    # print('Updated daily.json with today\'s date.')

    # GitHub PR情報を取得
    # print('\nFetching GitHub PRs...')
    # get_github_prs("spring-projects/spring-boot", daily_data['date'])

    # https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html
    g = Github()
    repo = g.get_repo("spring-projects/spring-boot")
    pr = repo.get_pull(43086)

    pr_dir = Path(f"repos/{repo.full_name}/pulls")
    since = timestamp(datetime(2025, 1, 24))

    prs = repo.get_pulls(state='closed', sort='updated', direction='desc')
    for pr in prs:
        if timestamp(pr.updated_at) > since:
            print(pr.number, pr.title, pr.updated_at)

            save_pr(repo, pr, pr_dir / str(pr.number))

            print(f"Saved PR {pr.number} to {pr_dir}")
            time.sleep(5)
        else:
            break


# メイン処理を実行
if __name__ == '__main__':
    main()
