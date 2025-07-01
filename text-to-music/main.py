import sys
from textblob import TextBlob
from midiutil import MIDIFile
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import spacy
from transformers import pipeline

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

# Simple mapping: sentiment polarity to scale
MAJOR_SCALE = [60, 62, 64, 65, 67, 69, 71, 72]  # C major
MINOR_SCALE = [60, 62, 63, 65, 67, 68, 70, 72]  # C minor

# Advanced sentiment analysis

def text_to_sentiment(text, model='vader'):
    if model == 'vader':
        analyzer = SentimentIntensityAnalyzer()
        return analyzer.polarity_scores(text)['compound']
    elif model == 'transformers':
        classifier = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')
        result = classifier(text)[0]
        return result['score'] if result['label'] == 'POSITIVE' else -result['score']
    elif model == 'textblob':
        blob = TextBlob(text)
        return blob.sentiment.polarity
    else:
        raise ValueError('Unknown sentiment model')

def sentiment_to_scale(sentiment, user_scale=None):
    if user_scale == 'major':
        return MAJOR_SCALE
    elif user_scale == 'minor':
        return MINOR_SCALE
    return MAJOR_SCALE if sentiment >= 0 else MINOR_SCALE

def text_to_melody(text, scale, mapping_mode='word', sentiment=0.0):
    doc = nlp(text)
    melody = []
    durations = []
    velocities = []
    for i, token in enumerate(doc):
        # Map part-of-speech to octave or note
        base_note = scale[i % len(scale)]
        if token.pos_ in ['NOUN', 'PROPN']:
            note = base_note + 12  # one octave up
        elif token.pos_ in ['VERB']:
            note = base_note + 7   # fifth up
        else:
            note = base_note
        # Rhythm: longer for longer words, shorter for short words
        duration = min(4, max(1, len(token.text) // 3))
        # Velocity: scale with sentiment intensity
        velocity = int(80 + 20 * abs(sentiment))
        melody.append(note)
        durations.append(duration)
        velocities.append(velocity)
    return melody, durations, velocities

def create_midi(melody, durations, velocities, filename="output.mid", tempo=120):
    midi = MIDIFile(1)
    track = 0
    time = 0
    midi.addTrackName(track, time, "TextToMusic")
    midi.addTempo(track, time, tempo)
    channel = 0
    for i, note in enumerate(melody):
        midi.addNote(track, channel, note, time, durations[i], velocities[i])
        time += durations[i]
    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)
    print(f"MIDI file saved as {filename}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Convert text to music (MIDI) with advanced options")
    parser.add_argument('--text', type=str, required=True, help='Text to convert to music')
    parser.add_argument('--output', type=str, default='output.mid', help='Output MIDI filename')
    parser.add_argument('--sentiment-model', type=str, choices=['vader', 'transformers', 'textblob'], default='vader', help='Sentiment analysis model')
    parser.add_argument('--scale', type=str, choices=['major', 'minor', 'auto'], default='auto', help='Scale to use')
    parser.add_argument('--tempo', type=int, default=120, help='Tempo (BPM)')
    parser.add_argument('--mapping-mode', type=str, choices=['word', 'sentence'], default='word', help='Map by word or sentence')
    args = parser.parse_args()

    sentiment = text_to_sentiment(args.text, model=args.sentiment_model)
    scale = sentiment_to_scale(sentiment, user_scale=None if args.scale == 'auto' else args.scale)
    melody, durations, velocities = text_to_melody(args.text, scale, mapping_mode=args.mapping_mode, sentiment=sentiment)
    create_midi(melody, durations, velocities, args.output, tempo=args.tempo)

if __name__ == "__main__":
    main() 