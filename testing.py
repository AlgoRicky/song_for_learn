import streamlit as st
from gtts import gTTS
from io import BytesIO
import base64


import jaconv
import streamlit as st
from sudachipy import Dictionary

from kanji_reading_with_level import add_reading as add_reading_with_level


from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
import json


tokenizer = Dictionary().create()


def make_ruby(text: str, rt: str) -> str:
    """Generater Ruby tagged text"""
    return f"<ruby>{text}<rt>{rt}</rt></ruby>"


def kana_with_romaji_ruby(text: str) -> str:
    hiragana = jaconv.kata2hira(text)
    romaji = jaconv.kana2alphabet(hiragana)
    return make_ruby(text, romaji)


def kana_to_romaji():
    st.write("""## Hiragana and Katakana to Romaji

    パイコン あめりか
    """)

    text = st.text_input("Hiragana and Katakana texts:")
    if text:
        result = kana_with_romaji_ruby(text)
        st.write(f"#### {result}", unsafe_allow_html=True)

def add_reading(text: str) -> tuple[str, str]:
    """Add Hiranaga ruby to text"""
    hiragana = ""
    romaji = ""
    for token in tokenizer.tokenize(text):
        ruby_kana = jaconv.kata2hira(token.reading_form())
        hiragana += make_ruby(token, ruby_kana) + "/ "
        ruby_romaji = jaconv.kata2alphabet(token.reading_form())
        romaji += make_ruby(token, ruby_romaji) + " "
    return hiragana, romaji


def word_segmentation():
    st.write("""## Word segmentation

    すもももももももものうち
    """)

    text = st.text_input("Text for Word segmentation:")
    if text:
        words = []
        for token in tokenizer.tokenize(text):
            words.append(kana_with_romaji_ruby(str(token)))
        result = " / ".join(words)
        st.write(f"#### {result}", unsafe_allow_html=True)

def get_transcript(video_id: str, languages: list = None) -> dict:
    """Fetches the transcript for a given video ID and languages."""
    if languages is None:
        languages = ['ja']
    
    xyz = YouTubeTranscriptApi().fetch(video_id, languages=languages)
    json_formatted = json.loads(JSONFormatter().format_transcript(xyz)) 
    return [x['text'].split('\n')[0] for x in json_formatted ]

# xyz = YouTubeTranscriptApi().fetch('8iuLXODzL04', languages=['ja'])
# json_formatted = json.loads(JSONFormatter().format_transcript(xyz))


def make_audio(text: str):
                      
    sound_file = BytesIO()
    tts = gTTS(f'{text}', lang='ja')
    tts.write_to_fp(sound_file)
    return sound_file 

def main():
    import pandas as pd
    import os
    st.set_page_config(layout="wide")
    st.write("""## Please input the video ID to get the transcript from YouTube
        8iuLXODzL04
        """)
    text = st.text_input("Text:")

    if text != '':
        st.markdown("""
                <style>
                img
                {
                    display:block;
                    float:none;
                    margin-left:auto;
                    margin-right:auto;
                    width:30%;
                }
                </style>
                """,
        unsafe_allow_html=True)
        # st.markdown(
        #     f""" 
        #       [![Watch the video](https://img.youtube.com/vi/{text}/default.jpg)](https://youtu.be/{text}) 
        #       """,
        # unsafe_allow_html=True)
        st.markdown(
            f""" 
              [![data-testid="img"](https://img.youtube.com/vi/{text}/default.jpg)](https://youtu.be/{text}) 
              """,
        unsafe_allow_html=True)
        
        if  os.path.exists(f"./history/{text}.json"):
            with open(f"./history/{text}.json", 'r', encoding='utf8') as fp:
                # json.dump(trsancript, fp, ensure_ascii=False)
                trsancript=json.load(fp)
        else:
            trsancript = get_transcript(text, languages=['ja'])
            with open(f"./history/{text}.json", 'w', encoding='utf8') as fp:
                json.dump(trsancript, fp, ensure_ascii=False)
        

        for x in trsancript:
            left, center, right = st.columns(3, vertical_alignment="bottom")
            with left:
                st.write(x)
            with center:
                st.write("""## """+add_reading(x)[0], unsafe_allow_html=True)
            with right:
                st.audio(make_audio(x))

        # y = pd.DataFrame({
        #     "lyrics":trsancript,
        #     "ruby":[add_reading(x) for x in trsancript],
        #     "voice":[make_audio(x) for x in trsancript]
        # })
        # st.write(y)

    # col1, col2, col3 = st.columns(3)






#     with col1:
#         st.write("""## Please input the video ID to get the transcript from YouTube
#     8iuLXODzL04
#     """)
#         text = st.text_input("Text:")
#         if text != '':
#             trsancript = get_transcript(text, languages=['ja'])
#             st.write(f"#### Transcript: {"\n".join(trsancript)}", unsafe_allow_html=True)
    
#             with col2:
#                 st.write("""## Hiragana and Katakana to Romaji """)
#                 for x in trsancript:
#                     st.write(f"#### {add_reading(x)}", unsafe_allow_html=True)
#                 # st.write(f"""{add_reading("\n".join(trsancript))[0]}""")

#             with col3:
#                 for x in trsancript:
#                    st.audio(make_audio("\n".join(x)))
# #       audio_base64 = base64.b64encode(make_audio(text)).decode('utf-8')
# #        audio_tag = f'<audio autoplay="true" src="data:audio/wav,{make_audio(text)}">'
# #        st.markdown(audio_tag, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

