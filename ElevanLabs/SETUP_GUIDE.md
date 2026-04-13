# Setup Instructions

## 1. Get your API Key
1.  On the ElevenLabs page you are looking at:
    -   **Name**: You can leave it as "Voracious Giant Forest Hog" or name it "My App".
    -   **Permissions**: Ensure **Text to Speech** is set to **Access** (it might be the default, but double check).
    -   Click the **Create Key** button.
2.  A new popup will appear with your API Key (it starts with `sk_...`).
3.  **Copy this key immediately.** You won't be able to see it again.

## 2. Configure the App
1.  Open the `.env` file in your editor (it should be open).
2.  Paste your key:
    ```env
    ELEVENLABS_API_KEY=sk_your_actual_key_here
    ```
3.  Save the file.

## 3. Run the App
Open two terminal windows:

**Terminal 1 (Backend):**
```bash
uv run python server/app.py
```

**Terminal 2 (Frontend):**
```bash
uv run streamlit run client/app.py
```
