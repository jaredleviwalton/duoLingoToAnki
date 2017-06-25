import duolingo
import requests
import codecs
import os.path

def emptyStringIfNothing(string):
        if not string:
            return ""
        else:
            return string

# START 

if __name__ == '__main__':

    debug = True

    username = ""
    password = ""

    processWordsFilePath = "/Users/jawalking/Library/Application Support/Anki2/Jared/collection.media/processWords.txt"
    pronunciationSoundFilePath = "/UUsers/jawalking/Library/Application Support/Anki2/Jared/collection.media/"
    ankiImportFilePath = os.path.dirname(os.path.realpath(__file__)) + "/ankiDuolingoGermanCards.txt"
    cloudFrontBaseUrl = "https://d7mj4aqfscim2.cloudfront.net/tts/de/token/"

    # Instantiate duo class and login to duoLingo
    # duolingo = duolingo.Duolingo(username, password=password)
    lingo = duolingo.Duolingo(username, password=password)

    # If the file exists open a file that contains already known words
    knownWordsList=list()
    if os.path.isfile(processWordsFilePath):
        with codecs.open(processWordsFilePath, "r+", "utf-8") as knownWordsFile:
            knownWordsList = knownWordsFile.read().splitlines()

    # Remove a previous Anki import file if it exists
    if os.path.isfile(ankiImportFilePath):
        os.remove(ankiImportFilePath)

    # Get the vocabulary words from duoLingo
    rawVocabulary = lingo.get_vocabulary()
    words = rawVocabulary['vocab_overview']

    # for each vocabulary word in our language vocabulary...
    for word in words:
        rawWordString = word['word_string']
        if debug: print rawWordString + ":"

        # If there is no vocab word here, move on...
        if not rawWordString:
            if debug: print "\tWord \""+rawWordString+"\" is empty string, skipping..."
            continue
        
        # If we have processed this word already, move on...
        if rawWordString in knownWordsList: 
            if debug: print "\tWord \""+rawWordString+"\" is already known, skipping..."
            continue
        else:
            if debug: print "\tNew word, will continue to process..."
        
        partOfSpeach = emptyStringIfNothing(word['pos'])
        normalizedWordString = emptyStringIfNothing(word['normalized_string'])
        wordGender = emptyStringIfNothing(word['gender'])
        skillLearnedIn = emptyStringIfNothing(word['skill_url_title'])

        # If this word is a Noun we need to capitalize it... (only works for most latin based languages)
        if partOfSpeach == "Noun":
            WordString = rawWordString.title()
        else:
            WordString = rawWordString
        
        # Get the translation from our learning language to native language from duoLingo
        rawTanslations = lingo.get_translations([WordString]).values()
        translatedWordString = '\n'.join(rawTanslations[0])

        # the duoLingo API for getting the sound URL is broken, this is a supper hacky workaround
        if debug: print "\tGetting sound file..."
        if not os.path.isfile(pronunciationSoundFilePath + WordString + ".mp3"):
            # pronunciationSoundUrl = lingo.get_audio_url(rawWordString)
            pronunciationSoundUrl = cloudFrontBaseUrl + rawWordString
            r = requests.get(pronunciationSoundUrl)
            if r.status_code == 200:
                with open( pronunciationSoundFilePath + WordString + ".mp3", "wb") as f:
                    for chunk in r:
                        f.write(chunk)
            else:
                print "\t\tFailed to get audio file! " + WordString + ".mp3"
        else:
            if debug: print "\t\tSound file already exits, skipping..."

        # This is for generating the cards for Anki
        if debug: print "\tAdding " + rawWordString + " to Anki import deck..."
        ankiTags = skillLearnedIn + " " + wordGender + " " + partOfSpeach
        ankiImportCardInfo = "\""+WordString+"\""   +";"+   "\""+translatedWordString+"\""   +";"+   "\""+wordGender+"\""   +";"+   "\"[sound:"+WordString+".mp3]\""   +";"+   "\""+ankiTags+"\""   +"\n\n"

        # Write Anki card template to file...
        ankiTextFile = codecs.open(ankiImportFilePath, "a", "utf-8")
        ankiTextFile.write(ankiImportCardInfo)
        ankiTextFile.close()

        # Add this word to our known word list
        knownWordsList.append(rawWordString)
   
   # Add all new know-words to our known word list file for future use.
    processWordsFile = codecs.open(processWordsFilePath, "a", "utf-8")
    for word in knownWordsList:
        processWordsFile.write(word + "\n")
    processWordsFile.close()

    print "*****************************    Done!   *****************************"






