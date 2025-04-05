# Instrux

Instrux is a tool designed to process screen recordings and generate step-by-step guides with screenshots. It leverages the Deepgram API for transcription and GPT-4 for generating detailed instructions.

## Features

- Transcribes audio from video files.
- Generates a structured guide with chapters and steps.
- Captures screenshots at specified timestamps.
- Outputs the guide in HTML format.

## Requirements

- Python 3.9+
- Deepgram API Key
- OpenAI API Key
- FFmpeg

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/nxmiso/instrux-processor.git
    cd instrux-processor
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Set up your Deepgram and OpenAI API keys in a `.env` file:
    ```sh
    echo "DEEPGRAM_KEY={your_deepgram_api_key}" > .env
    echo "OPENAI_KEY={your_openai_api_key}" > .env
    ```

5. Ensure FFmpeg is installed and available in your system's PATH.

## Usage

1. Place your video file in the `tmp` directory and name it `video.mp4`.

2. Set the `context` variable in `main.py` line 11 to describe the video and any specific requirements.

3. Run the main script:
    ```sh
    python main.py
    ```

4. The script will process the video, transcribe the audio, generate a guide, and save the output in the `tmp` directory:
    - `transcript.json`: The transcribed text.
    - `guide.json`: The generated guide in JSON format.
    - `screenshots/`: Directory containing captured screenshots.

## Project Structure

- `main.py`: Main script for processing the video and generating the guide.
- `html.py`: Script for converting the guide JSON to HTML format.
- `gpt.py`: Contains the inference function for generating the guide using GPT-4.
- `requirements.txt`: List of required Python packages.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

- [Deepgram](https://deepgram.com) for their transcription API.
- [OpenAI](https://openai.com) for GPT-4.