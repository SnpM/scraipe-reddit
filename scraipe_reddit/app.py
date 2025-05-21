import streamlit as st
from streamlit_scroll_navigation import scroll_navbar
import pandas as pd
import CONFIG
import asyncio
import logging
import utils

from scraipe import Workflow
from scraipe.extended import RedditLinkCollector, RedditSubmissionScraper, OpenAiAnalyzer
from scraipe.defaults import TextStatsAnalyzer


class App:
    def __init__(self, title: str ="scraipe-reddit", version: str = "demo v0.1.0",
                 reddit_client_id: str = CONFIG.REDDIT_CLIENT_ID, reddit_client_secret: str = CONFIG.REDDIT_CLIENT_SECRET,
                 openai_api_key: str = CONFIG.OPENAI_API_KEY, instruction: str = CONFIG.INSTRUCTION):
        # Initialize app configuration and credentials
        self.title = title
        self.version = version
        
        self.initial_reddit_client_id = reddit_client_id
        self.initial_reddit_client_secret = reddit_client_secret
        self.initial_openai_api_key = openai_api_key
        self.initial_instruction = instruction
        
        # Validate Reddit credentials and cache result in session state
        if "initial_reddit_valid" in  st.session_state:
            self.initial_reddit_valid = st.session_state.initial_creds_valid
        else:
            self.initial_reddit_valid = utils.test_reddit_creds(reddit_client_id, reddit_client_secret)
            st.session_state.initial_creds_valid = self.initial_reddit_valid       
        
        # Validate OpenAI credentials and cache result in session state
        if "initial_openai_valid" in  st.session_state:
            self.initial_openai_valid = st.session_state.initial_creds_valid
        else:
            self.initial_openai_valid = utils.test_openai_creds(openai_api_key)
            st.session_state.initial_creds_valid = self.initial_openai_valid

    
    def main(self):
        # Set up Streamlit page
        st.set_page_config(page_title=self.title, page_icon=":guardsman:")
        
        st.title(self.title)
        
        #===App configuration
        reddit_client_id = ""
        reddit_client_secret = ""
        openai_api_key = ""

        # Credentials input section
        with st.expander("Credentials", expanded=not (self.initial_reddit_valid and self.initial_openai_valid)):
            # Feedback on Reddit credentials
            feedback_container = st.empty()
                
            st.markdown("You can find your Reddit API credentials [here](https://www.reddit.com/prefs/apps).")
            
            # Configuration and test
            reddit_client_id = st.text_input("Reddit Client ID", type="password", placeholder="Leave blank to use default")
            reddit_client_secret = st.text_input("Reddit Client Secret", type="password", placeholder="Leave blank to use default")
            
            # Use default credentials if none provided
            if reddit_client_id == "":
                reddit_client_id = self.initial_reddit_client_id
            if reddit_client_secret == "":
                reddit_client_secret = self.initial_reddit_client_secret
            
            # Button to test and save Reddit credentials
            if st.button("Save", key="reddit_test"):
                st.session_state.reddit_valid = utils.test_reddit_creds(reddit_client_id, reddit_client_secret)
                st.session_state.reddit_client_id = reddit_client_id
                st.session_state.reddit_client_secret = reddit_client_secret
                
            # Render feedback for Reddit credentials
            if "reddit_valid" in st.session_state:
                reddit_valid = st.session_state.reddit_valid
            else:
                reddit_valid = self.initial_reddit_valid
                                
            if reddit_valid:
                feedback_container.success("Reddit credentials are valid.")
            else:
                feedback_container.error("Reddit credentials are invalid.")
            st.divider()
            #===OpenAI configuration
            # Feedback on OpenAI credentials
            feedback_container = st.empty()
                
            st.markdown("You can find your OpenAI API key [here](https://platform.openai.com/api-keys).")
            
            # Configuration and test
            openai_api_key = st.text_input("OpenAI API Key", type="password", placeholder="Leave blank to use default")
            
            # Use default OpenAI key if none provided
            if openai_api_key == "":
                openai_api_key = self.initial_openai_api_key
            
            # Button to test and save OpenAI credentials
            if st.button("Save", key="openai_test"):
                st.session_state.openai_valid = utils.test_openai_creds(openai_api_key)
                st.session_state.openai_api_key = openai_api_key
                
            # Render feedback for OpenAI credentials
            if "openai_valid" in st.session_state:
                openai_valid = st.session_state.openai_valid
            else:
                openai_valid = self.initial_openai_valid                
            if openai_valid:
                feedback_container.success("OpenAI credentials are valid.")
            else:
                feedback_container.error("OpenAI credentials are invalid.")
                
        #===Workflow configuration
        cols = st.columns([.55,.25,.2])
        # Input for subreddit names
        subreddit_names = cols[0].text_input("Subreddits", key="subreddit_names", placeholder="Enter subreddit names (e.g. r/bjj)")
        # Select sorting type for Reddit posts
        sort_types = ["hot", "new", "top"," controversial", "rising"]
        sort_type = cols[1].selectbox("Sort Type", options=sort_types, index=0)
        # Set post limit
        post_limit = cols[2].number_input("Limit", min_value=1, max_value=100, value=10, step=1)
        
        # LLM instruction input
        instruction_help = "Instruction for LLM analysis. Ensure a JSON schema is included."
        instruction = st.text_area("Instruction", key="instruction", value=self.initial_instruction, help=instruction_help)
        
        # Time filter for 'top' sort type
        top_time_filter = ""
        if sort_type == "top":
            top_time_filter = st.selectbox("Time Filter", options=["all", "day", "hour", "month", "week"], index=0)
        
        #===Scrape===
        st.divider()
        cols = st.columns([.15,.85])

        # Run workflow when button is pressed
        if cols[0].button("Run",use_container_width=True):
            def run_workflow():
                __subreddit_names = subreddit_names
                # Prep subreddit names
                if __subreddit_names == "":
                    __subreddit_names = "r/bjj"
                    st.toast("No subreddit specified. Defaulting to r/bjj", icon="⚠️")
                def clean_subreddit_name(subreddit_name):
                    # remove 'r/' from subreddit names and strip
                    return subreddit_name.strip().replace("r/", "")
                subreddits_names_parsed = [clean_subreddit_name(item) for item in __subreddit_names.split(",")]
                
                # Check reddit credentials
                if "reddit_valid" in st.session_state:
                    # get saved credentials
                    reddit_valid = st.session_state.reddit_valid
                    reddit_client_id = st.session_state.reddit_client_id
                    reddit_client_secret = st.session_state.reddit_client_secret
                else:
                    # get initial credentials
                    reddit_valid = self.initial_reddit_valid
                    reddit_client_id = self.initial_reddit_client_id
                    reddit_client_secret = self.initial_reddit_client_secret
                    
                if not reddit_valid:
                    st.error("Reddit credentials are invalid. Please check your credentials.")
                    return
                
                # Setup Reddit link collector
                link_collector = RedditLinkCollector(
                    client_id=reddit_client_id,
                    client_secret=reddit_client_secret,
                    subreddits=subreddits_names_parsed,
                    sorts=sort_type,
                    limit=post_limit,
                    top_time_filter=top_time_filter
                )
                
                # Setup Reddit submission scraper
                scraper = RedditSubmissionScraper(
                    client_id=reddit_client_id,
                    client_secret=reddit_client_secret
                )
                
                # Setup analyzer (OpenAI or fallback to TextStats)
                if "openai_valid" in st.session_state:
                    openai_valid = st.session_state.openai_valid
                    openai_api_key = st.session_state.openai_api_key
                else:
                    openai_valid = self.initial_openai_valid
                    openai_api_key = self.initial_openai_api_key
                    
                if not openai_valid:
                    st.warning("OpenAI credentials are invalid. Defaulting to TextStatsAnalyzer.")
                    analyzer = TextStatsAnalyzer()
                else:
                    analyzer = OpenAiAnalyzer(
                        api_key=openai_api_key,
                        instruction=instruction,
                        max_content_size=5000
                    )
                
                # Create workflow with collector, scraper, and analyzer
                workflow = Workflow(scraper,analyzer,link_collector=link_collector)
                
                with cols[1].status("running workflow..."):
                    st.write("collecting links...")
                    workflow.clear_store()
                    workflow.collect_links()
                
                    # Scrape posts and show progress
                    scraping_bar = st.progress(0.0, text="Scraping...")
                    acc = 0
                    links = workflow.get_links().get("link",[]).tolist()
                    for result in workflow.get_scrape_generator(links, overwrite=True):
                        acc += 1
                        scraping_bar.progress(acc/len(links), text=f"Scraping {len(links)} links...")
                        
                    
                    # Analyze posts and show progress
                    analyzing_bar = st.progress(0.0, text="Analyzing...")
                    scrapes_df = workflow.get_scrapes()
                    scrapes_length = len(scrapes_df) if scrapes_df is not None else 0
                    acc = 0
                    for result in workflow.get_analyze_generator(overwrite=True):
                        acc += 1
                        analyzing_bar.progress(acc/scrapes_length, text=f"Analyzing {scrapes_length} content items....")
                
                    # Export results to DataFrame and store in session state
                    export_df = workflow.export()
                    st.session_state.export_df = export_df
            run_workflow()
                    
        # Display results if available
        if "export_df" in st.session_state:
            export_df = st.session_state.export_df
            other_cols = [col for col in export_df.columns if col not in ["links"]]
            col_conf = {
                "link": st.column_config.LinkColumn(width="small",),
            }
            st.dataframe(export_df,column_config=col_conf)
            


        
def serve():
    # Entrypoint for running the app
    app = App()
    app.main()
    
if __name__ == "__main__":
    serve()