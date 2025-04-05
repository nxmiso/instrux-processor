import os
import re
import json
import time
import shutil
from tqdm import tqdm
from gpt import inference
from deepgram import Deepgram

# Context
context = "The video is for the Stax.ai CX product and demonstrates how users can configure custom data views for projects, plans, and client data fields - allowing for users to be more organized in how they approach projects."

# This service transcribes audio from a screen recording/walkthrough to create step-by-step instructions.
dg = Deepgram(os.getenv("DEEPGRAM_KEY"))

if __name__ == "__main__":
    # Clear working directory
    shutil.rmtree("./tmp/screenshots", ignore_errors=True)
    os.makedirs("./tmp/screenshots", exist_ok=True)
    
    # Split audio from video for transcription
    os.system("ffmpeg -i ./tmp/video.mp4 -vn -ab 128k -ar 44100 -y ./tmp/audio.mp3")
    
    # Transcript audio
    transcription = dg.transcription.sync_prerecorded({
        "buffer": open("./tmp/audio.mp3", "rb"),
        "mimetype": "audio/mp3",
    }, {
        "smart_format": True,
        "model": "nova",
        "punctuate": True
    })
    
    transcript = []
    new_segment = True
    for w in transcription["results"]["channels"][0]["alternatives"][0]["words"]:
        text = w["punctuated_word"].strip()
        transcript.append({
            "text": text,
            "start": w["start"],
            "end": w["end"],
            "confidence": w["confidence"],
            "new": new_segment
        })
        new_segment = text[-1] == "."
        
    with open("./tmp/transcript.json", "w") as f:
        f.write(json.dumps(transcript, indent=2))
        
    # with open("./tmp/transcript.json", "r") as f:
    #     transcript = json.load(f)
        
    # Prepare the transcript for the prompt: [MM:SS] Text\n[MM:SS] Text\n...
    transcript_text = ""
    for w in transcript:
        if w.get("new", False):
            # w['start'] is in seconds, format it to [MM:SS]
            timestamp = time.strftime("%M:%S", time.gmtime(w["start"]))
            transcript_text += f"\n[{timestamp}]"
        transcript_text += f" {w['text']}"
        
    # Clean up unnecessary spaces
    transcript_text = transcript_text.strip()
        
    # Use GenAI to generate step-by-step instructions
    prompt = f"Here is the transcript of a screen recording of a process walkthrough. Each segment has the timestamp of the start of the segment, followed by the text spoken in the segment.\n\n\"\"\"\n{transcript_text}\n\"\"\"\n\nHere is some additional context about the product and video to make sure the guide is accurate:\n\n\"\"\"\n{context}\n\"\"\"\n\nThe output is used to create a step-by-step guide with screeshots. Come up with a helpful and clear title for the guide along with an introduction/overview, and conclusion. The guide consists of chapters-each chapter demonstrating a particular function. Use the transcript to determine the best way to break down the process into chapters. Within each chapter, there must be clear steps that are easy to follow. The steps may also be accompanie by screenshots (recommended, but don't overdo it). For the screenshots, provide the timestamp (it can be the start of the segment or in between if appropriate) so we can create a screenshot from the video at this timestamp. In between steps, we can also include helpful tips (shown in info/notice boxes). The output should be in JSON format. The root JSON object must contain the key 'guide' which is an object with the following keys: 'title' (string), 'chapters' (array of objects), 'intro' (string), and 'conclusion' (string). Each chapter object must contain the keys 'title' (string) and 'elements' (array of objects). Don't say 'Title' or 'Chapter' or 'Step' in any of the outputs - go straight to the names/text. Each element is a screenshot, step, or tip. If it is a screenshot, it must have the key 'screenshot' with the value being the timestmap string ('mm:ss' format - same as the transcript). If it is a step, it must have the key 'step' with the value being the text/html of the step. If it is a tip, it must have the key 'tip' with the value being the text/html of the tip, and also have the key 'type' with the value being a string representing the type of tip. Type options for tips are: 'Info' for information, 'Error' for errors, warnings, and troubleshooting, and 'Success' to indicate when something is done. The guide should be clear, concise, and easy to follow. The screenshots should be relevant and helpful. The tips should provide additional context or information that is useful but not necessary for the main steps. All strings (title, intro, conclusion, steps, tips) are going to be passed in as 'innerHTML' to the appropriate divs, so they can include <strong>, <i>, and <u> tags. The screenshots must be relevant and helpful. Think about this and analyze the results to make sure they are accurate and that this is a good and useful guide.\n\nPlease generate the comprehensive step-by-step guide."
    
    guide = inference(prompt, model="gpt-4o")
    
    with open("./tmp/guide.json", "w") as f:
        f.write(json.dumps(guide, indent=2))
        
    # with open("./tmp/guide.json", "r") as f:
    #     guide = json.load(f)
        
    # Capture screenshots
    timestamps = []
    for chapter in guide["guide"]["chapters"]:
        for element in chapter["elements"]:
            if "screenshot" in element:
                timestamp = element["screenshot"]
                # Remove everything that's not a digit or colon
                timestamp = re.sub(r"[^\d:]", "", timestamp)
                
                # Convert MM:SS to seconds
                seconds = int(timestamp.split(":")[0]) * 60 + int(timestamp.split(":")[1])
                timestamps.append(seconds)
                
    # Get the framerate of the video
    os.system("ffmpeg -i ./tmp/video.mp4 2> ./tmp/video_info.log")
    with open("./tmp/video_info.log", "r") as f:
        lines = f.read()
    
    m = re.search(r"(\d+\.?\d*) fps", lines)
    fps = float(m.group(1))
    
    # Find the nearest frame for each timestamp (using the framerate)            
    screenshots = []
    for t in timestamps:
        frame = round(t * fps)
        screenshots.append((t, frame))
                
    # Generate screenshots
    selector = "+".join([f"eq(n,{s[1]})" for s in screenshots])
    os.system(f"ffmpeg -i ./tmp/video.mp4 -vf \"select='{selector}',scale=iw:ih\" -vsync vfr -pix_fmt rgb24 -q:v 1 ./tmp/screenshots/%04d.jpeg")
    
    # Rename the files to be MM_SS.jpeg
    for i, s in enumerate(screenshots):
        out_ts = time.strftime("%M_%S", time.gmtime(s[0]))
        fn = i+1
        os.rename(f"./tmp/screenshots/{fn:04d}.jpeg", f"./tmp/screenshots/{out_ts}.jpeg")