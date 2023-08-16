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
print(FPT_API_KEY)
def fetch_mp3_url(phrase, voice):
    url = 'https://api.fpt.ai/hmi/tts/v5'
    headers = {
        'api-key': FPT_API_KEY,
        'speed': '-2',
        'voice': voice
    }
    phrase_payload = phrase if len(phrase) >= 3 else f'{phrase}  '
    phrase_mp3_url=requests.request('POST', url, data=phrase_payload.encode('utf-8'), headers=headers).json()['async']
    print('here')
    return phrase_mp3_url

def get_cached_mp3_url_getter(phrase_url_map):
    cachefile_name = 'mp3_url_cachefile.csv'
    with open(cachefile_name, 'r') as cachefile:
        for line in cachefile:
            segments = line.split(';')
            if len(segments)>2:
                phrase_url_map[segments[0]] = [segments[1].strip(),segments[2].strip()]
            else:
                phrase_url_map[segments[0]] = [segments[1].strip()]
    def get_mp3_url(phrase):
        new_cachefile_name = 'boygirl_mp3_url_cachefile.csv'
        with open(new_cachefile_name,'a') as cachefile:
            if phrase in phrase_url_map:
                if len(phrase_url_map[phrase])>1:
                    return phrase_url_map[phrase]
                else:#in this case we need to add female voice to cache file which hasanain says is not possible....so we can create a new cachefile to use for this usecase?
                    girl_mp3_url=fetch_mp3_url(phrase, girlVoice)
                    phrase_url_map[phrase].append(girl_mp3_url)
                    phrase_mp3_url_girl = girl_mp3_url
                    cachefile.write(f'{phrase};{phrase_url_map[phrase][0]};{girl_mp3_url}\n')
                    return [phrase_url_map[phrase][0],phrase_mp3_url_girl]
        phrase_mp3_url_girl = fetch_mp3_url(phrase, girlVoice)
        phrase_mp3_url_boy= fetch_mp3_url(phrase, boyVoice)
        phrase_url_map[phrase]=[phrase_mp3_url_boy,phrase_mp3_url_girl]
        with open(cachefile_name, 'a') as cachefile:
            cachefile.write(f'{phrase};{phrase_mp3_url_boy};{phrase_mp3_url_girl}\n')
        return [phrase_mp3_url_boy,phrase_mp3_url_girl]
        

    return get_mp3_url

def download_mp3_file(url, phrase):#need to download from 327-365 i think
    local_filename = f'mp3s/{url.split("/")[-1]}'
    if os.path.exists(local_filename):
        return
    try:
        urllib.request.urlretrieve(url, local_filename)
    except Exception as e:
        print(f'errored on `{phrase}` with {e}')



def get_new_anki_segment(word_url_map, segment):
    mp3_url_girl = word_url_map[segment][1]
    mp3_url_boy = word_url_map[segment][0]
    mp3_file_name_girl = mp3_url_girl.split('/')[-1]
    mp3_file_name_boy = mp3_url_boy.split('/')[-1]
    if ankiUseCase:
        copy_command = f'cp mp3s/{mp3_file_name_boy} /Users/hasanain/Library/Application\\ Support/Anki2/User\\ 1/collection.media/{mp3_file_name}'
        os.system(copy_command)
        return f'{segment} [sound:{mp3_file_name_boy}]'
    else:
        return f'{segment};{mp3_file_name_boy};{mp3_file_name_girl}'#idfk what s going on with mp3 file name where is it coming from i dk 


def main():
    word_url_map = {}
    get_mp3_url = get_cached_mp3_url_getter(word_url_map)
    
    with open('notes/anki_sample_word_upfront.txt', 'r') as f:
        lines = f.readlines()
    
    # get mp3 urls
    for line in lines:
        segments = line.split(';')
        vn_word = segments[0] 
        vn_sentence = segments[2]
        get_mp3_url(vn_word)
        get_mp3_url(vn_sentence)

    # download all mp3
    for phrase, arr in word_url_map.items():
        boy_url = arr[0]
        girl_url = arr[1]
        download_mp3_file(boy_url, phrase)
        download_mp3_file(girl_url, phrase)
    
    # write new file
    with open('notes/anki_sample_word_upfront_with_audio.txt', 'w') as output:
        for line in lines:
            line = line.strip()
            segments = line.split(';')
            # vn word
            vn_word_segment = get_new_anki_segment(word_url_map, segments[0])
            # vn sentence
            vn_sentence_segment = get_new_anki_segment(word_url_map, segments[2])
            new_line = ';'.join([segments[5], vn_word_segment, segments[1], vn_sentence_segment, segments[3], segments[4]])
            output.write(f'{new_line}\n')

if __name__ == '__main__':
    add_id()
    main()
