from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
import instaloader
import re
import requests

app = FastAPI()
L = instaloader.Instaloader(download_pictures=False, download_videos=False)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Premium Insta Downloader</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        body { 
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); 
            color: #fff; 
            min-height: 100vh; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            padding: 20px;
        }
        
        .glass-panel {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 40px 30px;
            max-width: 450px;
            width: 100%;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            text-align: center;
        }
        
        h2 {
            font-size: 28px;
            margin-bottom: 5px;
            background: -webkit-linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 600;
        }
        p.subtitle { color: #bbb; font-size: 13px; margin-bottom: 25px; }
        
        .input-group { position: relative; margin-bottom: 20px; }
        .input-group i { position: absolute; left: 15px; top: 50%; transform: translateY(-50%); color: #aaa; }
        
        input[type="text"] {
            width: 100%;
            padding: 15px 15px 15px 45px;
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            color: white;
            font-size: 14px;
            outline: none;
            transition: all 0.3s ease;
        }
        input[type="text"]:focus { border-color: #dc2743; box-shadow: 0 0 10px rgba(220, 39, 67, 0.3); }
        
        .action-btn {
            background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
            color: white;
            border: none;
            padding: 15px 20px;
            border-radius: 12px;
            width: 100%;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
        }
        .action-btn:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(220, 39, 67, 0.4); }
        
        .spinner {
            display: none; width: 40px; height: 40px; margin: 20px auto;
            border: 4px solid rgba(255,255,255,0.1); border-top-color: #dc2743;
            border-radius: 50%; animation: spin 1s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        
        .result-card {
            display: none; margin-top: 25px; background: rgba(0,0,0,0.3);
            border-radius: 15px; padding: 15px; border: 1px solid rgba(255,255,255,0.05);
            animation: fadeIn 0.5s ease;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        
        .media-preview-container {
            width: 100%; border-radius: 10px; overflow: hidden; margin-bottom: 15px; background: #000;
        }
        video, img { width: 100%; max-height: 300px; display: block; object-fit: contain; }
        
        .btn-group { display: flex; gap: 10px; }
        .btn-group a {
            flex: 1; text-decoration: none; padding: 12px; border-radius: 8px; font-size: 14px;
            font-weight: 600; display: flex; justify-content: center; align-items: center; gap: 8px; transition: 0.3s;
        }
        .btn-download { background: linear-gradient(to right, #00b09b, #96c93d); color: white; }
        .btn-download:hover { box-shadow: 0 5px 15px rgba(150, 201, 61, 0.4); }
        
        .error-msg { color: #ff4d4d; font-size: 14px; margin-top: 15px; display: none; }
    </style>
</head>
<body>

    <div class="glass-panel">
        <h2>InstaGrab Pro</h2>
        <p class="subtitle">Fast, secure & direct downloads</p>
        
        <div class="input-group">
            <i class="fa-solid fa-link"></i>
            <input type="text" id="ig-url" placeholder="Paste Instagram Reel or Post link here...">
        </div>
        
        <button class="action-btn" onclick="fetchData()">
            <i class="fa-solid fa-bolt"></i> Generate Link
        </button>
        
        <div id="loader" class="spinner"></div>
        <div id="error" class="error-msg"></div>
        
        <div id="result" class="result-card">
            <div class="media-preview-container" id="media-container"></div>
            
            <div class="btn-group">
                <a href="#" id="download-btn" class="btn-download">
                    <i class="fa-solid fa-download"></i> Download File
                </a>
            </div>
        </div>
    </div>

    <script>
        async function fetchData() {
            const url = document.getElementById('ig-url').value;
            const resultCard = document.getElementById('result');
            const loader = document.getElementById('loader');
            const errorMsg = document.getElementById('error');
            const mediaContainer = document.getElementById('media-container');
            const downloadBtn = document.getElementById('download-btn');
            
            if(!url) {
                errorMsg.style.display = "block"; errorMsg.innerHTML = "Please enter a valid Instagram URL!"; return;
            }

            resultCard.style.display = "none"; errorMsg.style.display = "none";
            loader.style.display = "block"; mediaContainer.innerHTML = "";

            try {
                const response = await fetch(`/api/download?url=${encodeURIComponent(url)}`);
                const data = await response.json();

                loader.style.display = "none";

                if(data.success) {
                    resultCard.style.display = "block";
                    
                    if(data.type === "Video/Reel") {
                        mediaContainer.innerHTML = `<video controls autoplay loop playsinline src="${data.download_url}"></video>`;
                    } else {
                        mediaContainer.innerHTML = `<img src="${data.download_url}" alt="Instagram Image">`;
                    }
                    
                    // Yahan humne naye proxy route par link bheja hai
                    downloadBtn.href = `/api/force_download?link=${encodeURIComponent(data.download_url)}`;
                } else {
                    errorMsg.style.display = "block"; errorMsg.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> ${data.error}`;
                }
            } catch (error) {
                loader.style.display = "none"; errorMsg.style.display = "block";
                errorMsg.innerHTML = `<i class="fa-solid fa-wifi"></i> Failed to connect to server.`;
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return HTML_PAGE

@app.get("/api/download")
def fetch_media(url: str):
    match = re.search(r"(?:p|reel|tv)/([^/?#&]+)", url)
    if not match:
        return {"success": False, "error": "Invalid URL."}
    
    shortcode = match.group(1)
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        return {
            "success": True,
            "type": "Video/Reel" if post.is_video else "Image",
            "download_url": post.video_url if post.is_video else post.url
        }
    except Exception as e:
        return {"success": False, "error": "Could not fetch media. Account might be private."}

# ==========================================
# NAYA ROUTE: FORCE DOWNLOAD PROXY
# ==========================================
@app.get("/api/force_download")
def force_download(link: str):
    try:
        # Instagram se direct file stream karna
        req = requests.get(link, stream=True)
        content_type = req.headers.get("content-type", "")
        
        # Extension decide karna (video ya image)
        ext = "mp4" if "video" in content_type else "jpg"
        
        # Browser ko batana ki ye attachment hai (download ke liye)
        headers = {
            "Content-Disposition": f'attachment; filename="InstaGrab_Pro_{ext}"'
        }
        
        return StreamingResponse(
            req.iter_content(chunk_size=1024*1024), 
            media_type=content_type, 
            headers=headers
        )
    except Exception as e:
        return {"error": "Failed to download the file."}
