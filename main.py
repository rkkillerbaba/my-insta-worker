from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import instaloader
import re

app = FastAPI()
L = instaloader.Instaloader(download_pictures=False, download_videos=False)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Downloader</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { background: #1e1e1e; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); text-align: center; max-width: 400px; width: 90%; }
        h2 { color: #E1306C; margin-bottom: 20px; }
        input[type="text"] { width: 90%; padding: 12px; margin: 15px 0; border: 1px solid #333; border-radius: 6px; font-size: 16px; background: #333; color: white; }
        button { background-color: #E1306C; color: white; border: none; padding: 12px 25px; font-size: 16px; border-radius: 6px; cursor: pointer; transition: 0.3s; font-weight: bold; }
        button:hover { background-color: #C13584; }
        .result { margin-top: 25px; }
        .download-btn { display: inline-block; background-color: #4CAF50; color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 15px; }
        .download-btn:hover { background-color: #45a049; }
        .loader { display: none; margin-top: 20px; color: #aaa; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Insta Downloader</h2>
        <p>Paste Reel or Post link below:</p>
        <input type="text" id="ig-url" placeholder="https://www.instagram.com/reel/...">
        <br>
        <button onclick="fetchDownloadLink()">Get Download Link</button>
        
        <div id="loader" class="loader">Fetching data... Please wait.</div>
        <div id="result" class="result"></div>
    </div>

    <script>
        async function fetchDownloadLink() {
            const url = document.getElementById('ig-url').value;
            const resultDiv = document.getElementById('result');
            const loader = document.getElementById('loader');
            
            if(!url) {
                alert("Please enter a valid URL!");
                return;
            }

            resultDiv.innerHTML = "";
            loader.style.display = "block";

            try {
                const response = await fetch(`/api/download?url=${encodeURIComponent(url)}`);
                const data = await response.json();

                loader.style.display = "none";

                if(data.success) {
                    resultDiv.innerHTML = `
                        <p style="color: #4CAF50;">Success! Your ${data.type} is ready.</p>
                        <a href="${data.download_url}" target="_blank" class="download-btn">⬇ Download Media</a>
                    `;
                } else {
                    resultDiv.innerHTML = `<p style="color: #f44336;">Error: ${data.error}</p>`;
                }
            } catch (error) {
                loader.style.display = "none";
                resultDiv.innerHTML = `<p style="color: #f44336;">Failed to connect to server.</p>`;
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    return HTML_PAGE

@app.get("/api/download")
async def fetch_media(url: str):
    match = re.search(r"(?:p|reel|tv)/([^/?#&]+)", url)
    if not match:
        return {"success": False, "error": "Invalid URL. Use a valid Instagram Reel or Post link."}
    
    shortcode = match.group(1)
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        return {
            "success": True,
            "type": "Video/Reel" if post.is_video else "Image",
            "download_url": post.video_url if post.is_video else post.url
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
