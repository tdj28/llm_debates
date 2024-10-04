# LLM Debates

![alt text](image.png)

LLM Debates is a sophisticated project that leverages Large Language Models to generate and analyze debates on various topics. This tool is designed to create structured, multi-round debates with arguments for and against a given topic, complete with audio generation capabilities.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Audio Processing](#audio-processing)
- [License](#license)

## Installation

To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/llm_debates.git
   cd llm_debates
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install Playwright:
   ```
   playwright install
   ```

## Usage

The project includes several scripts for generating debates and processing audio. Here are the main components:

1. Debate Generation (not shown in the provided code snippets)
2. Audio Processing

To run the audio processing script:

```bash
./make_full_speech.sh <number_of_rounds> [output_filename]
```

This script will concatenate the debate audio files with added silence between segments.

## Features

- Multi-round debate generation
- Argument creation for and against a given topic
- Web search integration for sourcing relevant information
- Audio generation for debate speeches
- Structured data management for debate rounds and arguments

## Audio Processing

The `make_full_speech.sh` script (lines 1-53) provides a comprehensive solution for concatenating debate audio files with added silence between segments.


## License

This project is licensed under the Apache License 2.0. For more details, see the [LICENSE](LICENSE) file in the repository.
