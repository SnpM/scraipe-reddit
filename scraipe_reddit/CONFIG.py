import os
import logging
# LLM secrets
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Reddit secrets
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")

unconfigured = []
required = ["OPENAI_API_KEY", "REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET"]
for var_name in required:
    if not globals()[var_name]:
        unconfigured.append(var_name)
if len(unconfigured) > 0:
    logging.warning(f"The following credentials are not configured in the environment. They must be configured in the GUI.\n {', '.join(unconfigured)}")
    
INSTRUCTION = """
Extract funny jokes from the attached reddit post.
JSON: {"jokes": ["joke"]}
""".strip()