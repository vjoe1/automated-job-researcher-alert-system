import os
from typing import Annotated
from dotenv import load_dotenv
from fastapi import Header, HTTPException

load_dotenv()

BOT_SECRET_KEY = os.environ.get("BOT_SECRET_KEY")
if not BOT_SECRET_KEY:
    raise RuntimeError("BOT_SECRET_KEY is not configured")

def verify_bot_key(x_api_key: Annotated[str, Header()]):
    if x_api_key != BOT_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")