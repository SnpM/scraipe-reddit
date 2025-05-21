# scraipe-reddit

This is the Streamlit GUI demo for the Scraipe library.

## Quickstart

The app works out of the box. With Docker, you can pull the image from Docker Hub and run it as follows:

```bash
docker pull nibsbin/scraipe-reddit:latest
docker run -p 8051:8051 nibsbin/scraipe-reddit:latest
```

Or install the repository requirements (with poetry) and start Streamlit:

```bash
poetry install
streamlit run scraipe_reddit/app.py
```

## Preconfigure Credentials
Set the following environment variables to pre-configure scraper and analyzer credentials. You can configure these by copying [`secrets.env.template`](https://github.com/SnpM/scraipe-st/blob/main/secrets.env.template) into `secrets.env` and filling it out.


```bash
REDDIT_CLIENT_ID
REDDIT_CLIENT_SECRET
OPENAI_API_KEY
```

Then run the demo in Docker:

```bash
docker run --env-file secrets.env -p 8051:8051 scraipe-reddit:latest
```

Or from the repository:

```bash
source secrets.env
streamlit run scraipe_reddit/app.py
```