def notify_in_app(user_ids, message: str) -> None:
    print(f"[notify] to={list(user_ids)}: {message}")
def notify_email(emails, subject: str, body: str) -> None:
    print(f"[email] to={list(emails)}: {subject}")
