import requests
import urllib.request
import os
import os.path
from add_id import add_id

# Script will do the following
# Will take the file of notes
# get the audio files for the phrases
# associate each phrase with an mp3 file

# put all mp3 files in anki's vault
# create a new file with all the sounds that have been downloaded
# user will take the file and import it to anki

FPT_API_KEY=os.environ.get("FPT_API_KEY")
girlVoice='linhsan' #here
boyVoice='minhquangace' #here
ankiUseCase=False
def get_cached_mp3_url_getter(phrase_url_map,voice):#here
    cachefile_name = 'mp3_url_cachefile.csv'
    with open(cachefile_name, 'r') as cachefile:
        for line in cachefile:
            segments = line.split(';')
            phrase_url_map[segments[0]] = [segments[1].strip(),segments[2].strip()]#here and phrase url map should look like {phrase:[boymp3file,girlmp3file]}
    url = 'https://api.fpt.ai/hmi/tts/v5'
    headers = {
        'api-key': FPT_API_KEY,
        'speed': '-2',
        'voice': voice #here
    }
    def get_mp3_url(phrase):
        index=0#giving index depending on boy or girl voice
        if voice==girlVoice:
            index=1
        if phrase in phrase_url_map:#check if the selected genders mp3 file is already there
            if voice==boyVoice:
                if len(phrase_url_map[phrase][0])>0:
                    return phrase_url_map[phrase][0]
            else:
                if len(phrase_url_map[phrase][1])>0:
                    return phrase_url_map[phrase][1]
        phrase_payload = phrase if len(phrase) >= 3 else f'{phrase}  '#we are adding some whitespace?WHY
        phrase_mp3_url = requests.request('POST', url, data=phrase_payload.encode('utf-8'), headers=headers).json()['async']
        phrase_url_map[phrase][index] = phrase_mp3_url
        if index==0:
             with open(cachefile_name, 'a') as cachefile:
                cachefile.write(f'{phrase};{phrase_mp3_url}\n')#I am assuming that we will always have the boy mp3 before we are trying for girl MP3
        else:
            with open(cachefile_name, 'r+') as cachefile:#this is meant to add the girl MP3 at the end of the cachefile
                for line in cachefile:
                    segments = line.split(';')
                    if(segments[0])==phrase:
                        overWriteLine=f'{line};phrase_mp3_url'
                        # need to write something that will delete the existing line and replace with overWriteLine....... does this work or no
                        line.write(overWriteLine) # i am in over my head here. maybe it would be better to create 1 cache file for anki case (male voice only) and 1 cache file that adds the female voice?

       
        return phrase_mp3_url
        

    return get_mp3_url

def download_mp3_file(url, phrase):
    local_filename = f'mp3s/{url.split("/")[-1]}'
    if os.path.exists(local_filename):
        return
    try:
        urllib.request.urlretrieve(url, local_filename)
    except Exception as e:
        print(f'errored on `{phrase}` with {e}')



def get_new_anki_segment(word_url_map, segment):
   
    mp3_boy_url = word_url_map[segment][0]
    mp3_girl_url = word_url_map[segment][1]
    mp3_girl_file_name = mp3_girl_url.split('/')[-1]
    mp3_boy_file_name = mp3_boy_url.split('/')[-1]

    if ankiUseCase==True:
        copy_command = f'cp mp3s/{mp3_boy_file_name} /Users/hasanain/Library/Application\\ Support/Anki2/User\\ 1/collection.media/{mp3_boy_file_name}'
        os.system(copy_command)
        return f'{segment} [sound:{mp3_boy_file_name}]'    
    
    return f'{segment};{mp3_boy_file_name};{mp3_girl_file_name}]'


def main():
    word_url_map = {}
    get_mp3_boy_url = get_cached_mp3_url_getter(word_url_map, boyVoice)
    get_mp3_girl_url = get_cached_mp3_url_getter(word_url_map, girlVoice)
    
    with open('notes/anki_sample_word_upfront.txt', 'r') as f:
        lines = f.readlines()
    
    # get mp3 urls
    for line in lines:
        segments = line.split(';')
        vn_word = segments[0] 
        vn_sentence = segments[2]
        get_mp3_boy_url(vn_word)
        get_mp3_girl_url(vn_word)
        get_mp3_boy_url(vn_sentence)
        get_mp3_girl_url(vn_sentence)

    # download all mp3
    for phrase, url in word_url_map.items():
        download_mp3_file(url, phrase)
    
    # write new file
    if ankiUseCase:
        fileName='notes/anki_sample_word_upfront_with_audio.txt'
    else:
        fileName='notes/app_word_upfront_with_audio'

    with open(fileName, 'w') as output: 
        for line in lines:
            line = line.strip()
            segments = line.split(';')
            # vn word
            vn_word_segment = get_new_anki_segment(word_url_map, segments[0])
            #if anki usecase this will be 'phrase [mp3filename]' and if not, it will be phrase;mp3boy;mp3girl
            # vn sentence
            vn_sentence_segment = get_new_anki_segment(word_url_map, segments[2])
            new_line = ';'.join([segments[5], vn_word_segment, segments[1], vn_sentence_segment, segments[3], segments[4]])
            output.write(f'{new_line}\n')

if __name__ == '__main__':
    add_id()
    main()
