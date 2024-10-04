#!/bin/bash

# Check if number of rounds is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <number_of_rounds> [output_filename]"
    exit 1
fi

# Set the number of rounds
rounds=$1

# Set the output filename (default or provided)
output_file=${2:-full_debate.mp3}

# Set the duration of silence in seconds
silence_duration=1

# Create a temporary directory
temp_dir=$(mktemp -d)

# Function to add silence to the end of a file
add_silence() {
    local input_file=$1
    local output_file=$2
    ffmpeg -i "$input_file" -af "apad=pad_dur=$silence_duration" -c:a libmp3lame "$output_file"
}

# Process each file
for i in $(seq 1 $rounds); do
    # aaa
    add_silence "speech_${i}_aaa.mp3" "${temp_dir}/silenced_${i}_aaa.mp3"
    echo "file '${temp_dir}/silenced_${i}_aaa.mp3'" >> concat_list.txt

    # For position
    add_silence "speech_${i}_for.mp3" "${temp_dir}/silenced_${i}_for.mp3"
    echo "file '${temp_dir}/silenced_${i}_for.mp3'" >> concat_list.txt

    # Against position
    add_silence "speech_${i}_against.mp3" "${temp_dir}/silenced_${i}_against.mp3"
    echo "file '${temp_dir}/silenced_${i}_against.mp3'" >> concat_list.txt
done

# Add the final aaa speech (without added silence)
echo "file 'speech_$((rounds+1))_aaa.mp3'" >> concat_list.txt

# Concatenate the files
ffmpeg -f concat -safe 0 -i concat_list.txt -c copy "$output_file"

# Clean up
rm concat_list.txt
rm -r "$temp_dir"

echo "Concatenation complete. Output file: $output_file"