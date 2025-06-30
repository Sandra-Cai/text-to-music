import sys
from textblob import TextBlob
from midiutil import MIDIFile

# Simple mapping: sentiment polarity to scale
MAJOR_SCALE = [60, 62, 64, 65, 67, 69, 71, 72]  # C major
MINOR_SCALE = [60, 62, 63, 65, 67, 68, 70, 72]  # C minor

def text_to_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

def sentiment_to_scale(sentiment):
    return MAJOR_SCALE if sentiment >= 0 else MINOR_SCALE

def text_to_melody(text, scale):
    words = text.split()
    melody = []
    for i, word in enumerate(words):
        note = scale[i % len(scale)]
        melody.append(note)
    return melody

def create_midi(melody, filename="output.mid"):
    midi = MIDIFile(1)
    track = 0
    time = 0
    midi.addTrackName(track, time, "TextToMusic")
    midi.addTempo(track, time, 120)
    channel = 0
    volume = 100
    duration = 1
    for i, note in enumerate(melody):
        midi.addNote(track, channel, note, i, duration, volume)
    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)
    print(f"MIDI file saved as {filename}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Convert text to music (MIDI)")
    parser.add_argument('--text', type=str, required=True, help='Text to convert to music')
    parser.add_argument('--output', type=str, default='output.mid', help='Output MIDI filename')
    args = parser.parse_args()

    sentiment = text_to_sentiment(args.text)
    scale = sentiment_to_scale(sentiment)
    melody = text_to_melody(args.text, scale)
    create_midi(melody, args.output)

if __name__ == "__main__":
    main() 