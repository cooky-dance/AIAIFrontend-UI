# AIAIFrontend UI

Local Streamlit frontend for testing AIAI Seedance2 video generation.

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
streamlit run aiai_seedance2_frontend.py
```

On Windows, you can also double-click `双击启动_aiai_seedance2_frontend.bat`.

## Notes

- The app reads the AIAI API key from the sidebar input or the `AIAI_API_KEY` environment variable.
- Seedance media inputs must be public `http://` or `https://` URLs.
- Local images can be uploaded to a public temporary host from the UI before submitting a video task.
