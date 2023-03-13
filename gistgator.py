import re
import nltk
import torch
from pydub.utils import make_chunks
from transformers import Wav2Vec2Tokenizer, Wav2Vec2ForCTC
from tkinter import *
from tkinter import filedialog
import moviepy.editor as mp
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
import librosa

nltk.download("punkt")


# Loading the model and the tokenizer for ASR
model_name = "facebook/wav2vec2-base-960h"
tokenizer = Wav2Vec2Tokenizer.from_pretrained(model_name)
model = Wav2Vec2ForCTC.from_pretrained(model_name)


# Loading the model and the tokenizer for Summarization
from transformers import BartTokenizer, AutoModelForSeq2SeqLM

tokenizer_2 = BartTokenizer.from_pretrained("Salesforce/bart-large-xsum-samsum")
model_2 = AutoModelForSeq2SeqLM.from_pretrained("Salesforce/bart-large-xsum-samsum")


# Creating global variables
filename = ""
# transcript = []
fo = ""


# Video to Audio
def browseFiles():
    global filename
    filename = filedialog.askopenfilename(
        initialdir="/", title="Select a File", filetypes=([("all files", "*.*")])
    )
    # Change label contents
    filename = filename.replace("/", "\\")
    # label_file_explorer.configure(text="File Opened: " + filename.split("/")[-1])


def convert_video_to_audio_moviepy(video_file, output_ext="wav"):
    filename, ext = os.path.splitext(video_file)
    clip = mp.VideoFileClip(video_file)
    clip.audio.write_audiofile(f"{filename}.{output_ext}")


# Audio preprocessing
def load_data(input_file):
    """Function for resampling to ensure that the speech input is sampled at 16KHz."""
    # read the file
    speech, sample_rate = librosa.load(input_file)
    # make it 1-D
    if len(speech.shape) > 1:
        speech = speech[:, 0] + speech[:, 1]
    # Resampling at 16KHz since wav2vec2-base-960h is pretrained and fine-tuned on speech audio sampled at 16 KHz.
    if sample_rate != 16000:
        speech = librosa.resample(speech, orig_sr=sample_rate, target_sr=16000)
    return speech


def correct_casing(input_sentence):
    """This function is for correcting the casing of the generated transcribed text"""
    sentences = nltk.sent_tokenize(input_sentence)
    return " ".join([s.replace(s[0], s[0].capitalize(), 1) for s in sentences])


# Define a function to normalize a chunk to a target amplitude.
def match_target_amplitude(aChunk, target_dBFS):
    """Normalize given audio chunk"""
    change_in_dBFS = target_dBFS - aChunk.dBFS
    return aChunk.apply_gain(change_in_dBFS)


def asr_transcript(input_file):
    """This function generates transcripts for the provided audio input"""
    speech = load_data(input_file)
    # Tokenize
    input_values = tokenizer(speech, return_tensors="pt").input_values
    # Take logits
    logits = model(input_values).logits
    # Take argmax
    predicted_ids = torch.argmax(logits, dim=-1)
    # Get the words from predicted word ids
    transcription = tokenizer.decode(predicted_ids[0])
    # Output is all upper case
    transcription = correct_casing(transcription.lower())
    return transcription


# Silence Detection and Creating Chunks
def splitFunction(audio):
    transcript = []
    myaudio = AudioSegment.from_file(audio, "wav")

    # Split track where the silence is 2 seconds or more and get chunks using
    # the imported function.
    chunks = split_on_silence(
        # Use the loaded audio.
        myaudio,
        # Specify that a silent chunk must be at least 2 seconds or 2000 ms long.
        min_silence_len=2000,
        silence_thresh=-50,
    )

    # Process each chunk with your parameters
    for i, chunk in enumerate(chunks):
        # Create a silence chunk that's 0.5 seconds (or 500 ms) long for padding.
        silence_chunk = AudioSegment.silent(duration=500)

        # Add the padding chunk to beginning and end of the entire chunk.
        audio_chunk = silence_chunk + chunk + silence_chunk

        # Normalize the entire chunk.
        normalized_chunk = match_target_amplitude(audio_chunk, -20.0)
        chunk_name = "chunk{0}.wav".format(i + 1)
        # Export the audio chunk with new bitrate.

        normalized_chunk.export(chunk_name, bitrate="192k", format="wav")
        length = librosa.get_duration(filename=chunk_name)
        if length < 2:
            os.remove(chunk_name)
        elif length > 60:
            chunk_length_ms = 60000
            myaudio = AudioSegment.from_file(chunk_name, "wav")
            chunks = make_chunks(myaudio, chunk_length_ms)
            for i, chunk in enumerate(chunks):
                chunk_name_sub = "{0}.wav".format(i + 1)
                chunk.export(chunk_name_sub, format="wav")
                length_sub = librosa.get_duration(filename=chunk_name_sub)
                print(
                    "Exporting "
                    + chunk_name
                    + " "
                    + chunk_name_sub
                    + " "
                    + str(length_sub)
                )
                transcript.append(asr_transcript(chunk_name_sub))
                os.remove(chunk_name_sub)
            os.remove(chunk_name)
        else:
            print("Exporting " + chunk_name + " " + str(length))
            transcript.append(asr_transcript(chunk_name))
            os.remove(chunk_name)

        return transcript


# Speech-To-Text
def STT_run(filename):
    if filename.endswith(".mp4") or filename.endswith(".avi"):
        convert_video_to_audio_moviepy(filename)
    audio = filename
    audio = audio.replace(filename.split(".")[-1], "wav")

    transcript = splitFunction(audio)
    transcriptStr = str(transcript)
    transcriptStr = transcriptStr[2:-2]

    INPUT = []
    global fo
    for i in transcript:
        if len(i) > 0:
            INPUT.append(i + ". ")
    fo = re.sub(r"[^.\w\s]", "", "".join(INPUT))
    return transcriptStr


# Text Summarization
def inputOutput():

    # tokenize without truncation
    inputs_no_trunc = tokenizer_2(
        fo, max_length=None, return_tensors="pt", truncation=False
    )

    # get batches of tokens corresponding to the exact model_max_length
    chunk_start = 0
    chunk_end = tokenizer_2.model_max_length  # == 1024 for Bart
    inputs_batch_lst = []
    while chunk_start <= len(inputs_no_trunc["input_ids"][0]):
        inputs_batch = inputs_no_trunc["input_ids"][0][
            chunk_start:chunk_end
        ]  # get batch of n tokens
        inputs_batch = torch.unsqueeze(inputs_batch, 0)
        inputs_batch_lst.append(inputs_batch)
        chunk_start += tokenizer_2.model_max_length  # == 1024 for Bart
        chunk_end += tokenizer_2.model_max_length  # == 1024 for Bart

    # generate a summary on each batch
    summary_ids_lst = [
        model_2.generate(inputs, num_beams=4, max_length=100, early_stopping=True)
        for inputs in inputs_batch_lst
    ]

    # decode the output and join into one string with one paragraph per summary batch
    summary_batch_lst = []
    for summary_id in summary_ids_lst:
        summary_batch = [
            tokenizer_2.decode(
                g, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )
            for g in summary_id
        ]
        summary_batch_lst.append(summary_batch[0])
    summary_all = "\n".join(summary_batch_lst)
    summaryStr = str(summary_all)
    return summaryStr
