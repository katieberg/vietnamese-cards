import requests
import urllib.request
import os
import os.path
import uuid

# Script will do the following
# Will take the file of notes
# get the audio files for the phrases
# associate each phrase with an mp3 file

# put all mp3 files in anki's vault
# create a new file with all the sounds that have been downloaded
# user will take the file and import it to anki

FPT_API_KEY=os.environ.get("FPT_API_KEY")
def get_cached_mp3_url_getter(phrase_url_map):
    cachefile_name = 'mp3_url_cachefile.csv'
    with open(cachefile_name, 'r') as cachefile:
        for line in cachefile:
            segments = line.split(';')
            phrase_url_map[segments[0]] = segments[1].strip()
    url = 'https://api.fpt.ai/hmi/tts/v5'
    headers = {
        'api-key': FPT_API_KEY,
        'speed': '-2',
        'voice': 'minhquangace'
    }
    def get_mp3_url(phrase):
        if phrase in phrase_url_map:
            return phrase_url_map[phrase]
        phrase_payload = phrase if len(phrase) >= 3 else f'{phrase}  '
        phrase_mp3_url = requests.request('POST', url, data=phrase_payload.encode('utf-8'), headers=headers).json()['async']
        phrase_url_map[phrase] = phrase_mp3_url
        with open(cachefile_name, 'a') as cachefile:
            cachefile.write(f'{phrase};{phrase_mp3_url}\n')
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
    mp3_url = word_url_map[segment]
    mp3_file_name = mp3_url.split('/')[-1]
    copy_command = f'cp mp3s/{mp3_file_name} /Users/hasanain/Library/Application\\ Support/Anki2/User\\ 1/collection.media/{mp3_file_name}'
    os.system(copy_command)
    return f'{segment} [sound:{mp3_file_name}]'


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
    for phrase, url in word_url_map.items():
        download_mp3_file(url, phrase)
    
    # write new file
    with open('notes/anki_sample_word_upfront_with_audio.txt', 'w') as output:
        for line in lines:
            file_uuid = uuid.UUID('e1ed723d-62ad-4c5c-9dfc-c5e6c4ff945d') # random uuid for the namespace
            line_id = uuid.uuid5(file_uuid, line)
            segments = line.split(';')
            # vn word
            vn_word_segment = get_new_anki_segment(word_url_map, segments[0])
            # vn sentence
            vn_sentence_segment = get_new_anki_segment(word_url_map, segments[2])
            new_line = ';'.join([str(line_id), vn_word_segment, segments[1], vn_sentence_segment, segments[3], segments[4]])
            output.write(f'{new_line}')

if __name__ == '__main__':
    main()
