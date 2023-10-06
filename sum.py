import math
from nltk import sent_tokenize, word_tokenize, PorterStemmer
from nltk.corpus import stopwords
import tkinter as tk
from tkinter import messagebox

def create_frequency_table(text_string):
    stopWords = set(stopwords.words("english"))
    words = word_tokenize(text_string)
    ps = PorterStemmer()

    freqTable = dict()
    for word in words:
        word = ps.stem(word)
        if word in stopWords:
            continue
        if word in freqTable:
            freqTable[word] += 1
        else:
            freqTable[word] = 1

    return freqTable

def create_tf_idf_summary(text):
    sentences = sent_tokenize(text)
    total_documents = len(sentences)
    freq_matrix = create_frequency_matrix(sentences)
    tf_matrix = create_tf_matrix(freq_matrix)
    count_doc_per_words = create_documents_per_words(freq_matrix)
    idf_matrix = create_idf_matrix(freq_matrix, count_doc_per_words, total_documents)
    tf_idf_matrix = create_tf_idf_matrix(tf_matrix, idf_matrix)
    sentence_scores = score_sentences(tf_idf_matrix)
    threshold = find_average_score(sentence_scores)
    summary = generate_summary(sentences, sentence_scores, 1.3 * threshold)
    return summary

def create_frequency_matrix(sentences):
    frequency_matrix = {}
    stopWords = set(stopwords.words("english"))
    ps = PorterStemmer()

    for sent in sentences:
        freq_table = {}
        words = word_tokenize(sent)
        for word in words:
            word = word.lower()
            word = ps.stem(word)
            if word in stopWords:
                continue
            if word in freq_table:
                freq_table[word] += 1
            else:
                freq_table[word] = 1
        frequency_matrix[sent[:15]] = freq_table

    return frequency_matrix

def create_tf_matrix(freq_matrix):
    tf_matrix = {}

    for sent, f_table in freq_matrix.items():
        tf_table = {}

        count_words_in_sentence = len(f_table)
        for word, count in f_table.items():
            tf_table[word] = count / count_words_in_sentence

        tf_matrix[sent] = tf_table

    return tf_matrix

def create_documents_per_words(freq_matrix):
    word_per_doc_table = {}

    for sent, f_table in freq_matrix.items():
        for word, count in f_table.items():
            if word in word_per_doc_table:
                word_per_doc_table[word] += 1
            else:
                word_per_doc_table[word] = 1

    return word_per_doc_table

def create_idf_matrix(freq_matrix, count_doc_per_words, total_documents):
    idf_matrix = {}

    for sent, f_table in freq_matrix.items():
        idf_table = {}

        for word in f_table.keys():
            idf_table[word] = math.log10(total_documents / float(count_doc_per_words[word]))

        idf_matrix[sent] = idf_table

    return idf_matrix

def create_tf_idf_matrix(tf_matrix, idf_matrix):
    tf_idf_matrix = {}

    for (sent1, f_table1), (sent2, f_table2) in zip(tf_matrix.items(), idf_matrix.items()):
        tf_idf_table = {}

        for (word1, value1), (word2, value2) in zip(f_table1.items(), f_table2.items()):
            tf_idf_table[word1] = float(value1 * value2)

        tf_idf_matrix[sent1] = tf_idf_table

    return tf_idf_matrix

def score_sentences(tf_idf_matrix):
    sentenceValue = {}

    for sent, f_table in tf_idf_matrix.items():
        total_score_per_sentence = 0

        count_words_in_sentence = len(f_table)
        for word, score in f_table.items():
            total_score_per_sentence += score

        sentenceValue[sent] = total_score_per_sentence / count_words_in_sentence

    return sentenceValue

def find_average_score(sentenceValue):
    sumValues = 0
    for entry in sentenceValue:
        sumValues += sentenceValue[entry]

    average = (sumValues / len(sentenceValue))

    return average

def generate_summary(sentences, sentenceValue, threshold):
    sentence_count = 0
    summary = ''

    for sentence in sentences:
        if sentence[:15] in sentenceValue and sentenceValue[sentence[:15]] >= threshold:
            summary += " " + sentence
            sentence_count += 1

    return summary

def copy_to_clipboard():
    output_text = output_text_box.get("1.0", "end-1c")
    window.clipboard_clear()
    window.clipboard_append(output_text)
    window.update()
    messagebox.showinfo("Text Copied", "Text copied to clipboard!")

def clear_input_box():
    input_text_box.delete("1.0", "end")
    output_text_box.config(state="normal")
    output_text_box.delete("1.0", "end")
    output_text_box.config(state="disabled")

def paste_from_clipboard():
    clipboard_text = window.clipboard_get()
    input_text_box.insert("1.0", clipboard_text)

def summarize_text():
    input_text = input_text_box.get("1.0", "end-1c")
    summary = create_tf_idf_summary(input_text)
    output_text_box.config(state="normal")
    output_text_box.delete("1.0", "end")
    output_text_box.insert("1.0", summary)
    output_text_box.config(state="disabled")

# Create the Tkinter window
window = tk.Tk()
window.title("Text Summarizer")

# Increase the default UI size
window.geometry("800x600")

# Create input box with a title
input_label = tk.Label(window, text="Input Text")
input_label.pack()

input_text_box = tk.Text(window, height=10, width=80, padx=10, pady=10)
input_text_box.pack()
input_text_box.focus()

# Create a frame for buttons under the input box
button_frame = tk.Frame(window)
button_frame.pack()

# Create the "Clear" button for input text box
clear_button = tk.Button(button_frame, text="Clear", command=clear_input_box, padx=20, pady=10)
clear_button.pack(side=tk.LEFT, padx=20, pady=(10, 10))

# Create the "Paste" button for input text box
paste_button = tk.Button(button_frame, text="Paste", command=paste_from_clipboard, padx=20, pady=10)
paste_button.pack(side=tk.LEFT, padx=20, pady=(10, 10))

# Create output box with a title
output_label = tk.Label(window, text="Output Text")
output_label.pack()

output_text_box = tk.Text(window, height=10, width=80, state="disabled", padx=10, pady=10)
output_text_box.pack()

# Create a frame for buttons under the output box
output_button_frame = tk.Frame(window)
output_button_frame.pack()

# Create the "Summarize" button
summarize_button = tk.Button(output_button_frame, text="Summarize", command=summarize_text, padx=20, pady=10)
summarize_button.pack(side=tk.LEFT, padx=20, pady=(10, 10))

# Create the "Copy" button for output text box
copy_button = tk.Button(output_button_frame, text="Copy", command=copy_to_clipboard, padx=20, pady=10)
copy_button.pack(side=tk.LEFT, padx=20, pady=(10, 10))

# Allow right-click for paste in the input text box
input_text_box.bind("<Button-3>", lambda e: input_text_box.event_generate("<Control-v>"))


# Start the Tkinter main loop
window.mainloop()