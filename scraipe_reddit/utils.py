import asyncio
import logging
import streamlit as st
from asyncpraw import Reddit

USER_AGENT = "scraipe_reddit (by /u/petertigerr)"
    
def test_reddit_creds(reddit_client_id, reddit_client_secret):
    async def run_test():
        try:
            async with Reddit(client_id=reddit_client_id, client_secret=reddit_client_secret, user_agent=USER_AGENT) as reddit:
                async for subreddit in reddit.subreddits.popular(limit=1):
                    pass
                return True
        except Exception as e:
            logging.error(f"Reddit creds test failed: {e}")
            return False
    return asyncio.run(run_test())

from openai import OpenAI

def test_openai_creds(openai_api_key):
    client = OpenAI(api_key=openai_api_key)
    try:
        client.models.list()
        return True
    except Exception as e:
        logging.error(f"OpenAI creds test failed: {e}")
        return False