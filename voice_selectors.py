from __future__ import print_function
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
import boto3
polly = boto3.client('polly',region_name='us-west-2')


def get_languages():
    languages = [(x['LanguageName'],x['LanguageCode']) for x in polly.describe_voices()['Voices']]
    languages = list(set(languages))
    languages.sort(key=lambda x: x[0])
    return languages

def get_voices_for_language(language_code):
    voices = [(x['Name'],x['Id']) for x in polly.describe_voices(LanguageCode=language_code)['Voices']]
    voices.sort(key=lambda x: x[0])
    return voices

def get_lang():
    return languages_W.value

def get_voice():
    return voices_W.value
    

languages_W = widgets.Dropdown(
    options=get_languages(),
    selection='US English'
)

voices_W = widgets.Dropdown(
    options=get_voices_for_language(languages_W.value))


@interact(languages = languages_W, voices = voices_W)
def print_city(languages, voices):
    voices_W.options = get_voices_for_language(languages_W.value)
