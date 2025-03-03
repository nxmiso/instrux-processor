import re
import json
import base64

if __name__ == "__main__":
    with open("./tmp/guide.json", "r") as f:
        guide = json.load(f)["guide"]
        
    content = ""
    
    # Introduction
    content += f"<h1>{guide['title']}</h1>\n"
    content += f"<h2>Introduction</h2>\n"
    content += f"<p>{guide['intro']}</p>\n"
    
    # Chapters
    for chapter in guide["chapters"]:
        content += f"<h2>{chapter['title']}</h2>\n"
        for element in chapter["elements"]:
            if "screenshot" in element:
                out_ts = re.sub(f"[:.]", "_", element["screenshot"])
                # Convert images to base64 to embed directly in the HTML file
                with open(f"./tmp/screenshots/{out_ts}.jpeg", "rb") as f:
                    img_data = f.read()
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                    content += f"<img src=\"data:image/jpeg;base64,{img_base64}\" />\n"
                
                # content += f"<img src=\"./screenshots/{out_ts}.jpeg\" />\n"
            elif "step" in element:
                content += f"<p class=\"step\">{element['step']}</p>\n"
            elif "tip" in element:
                tip = f"info-{element['type'].lower()}"
                content += f"<div class=\"{tip}\">{element['tip']}</div>\n"
    
    # Conclusion
    content += f"<br />\n"
    content += f"<p>{guide['conclusion']}</p>\n"
    
    with open("./tmp/guide.html", "w") as f:
        f.write(content)