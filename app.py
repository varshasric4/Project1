
from flask import Flask, request, jsonify, render_template, url_for
from googletrans import Translator
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

app = Flask(__name__)

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

translator = Translator()
lemmatizer = WordNetLemmatizer()

# Mapping English words to ISL video filenames
word_to_animation = {
    '0': '0.mp4', '1': '1.mp4', '2': '2.mp4', '3': '3.mp4', '4': '4.mp4',
    '5': '5.mp4', '6': '6.mp4', '7': '7.mp4', '8': '8.mp4', '9': '9.mp4',
    'a': 'A.mp4', 'after': 'After.mp4', 'again': 'Again.mp4', 'against': 'Against.mp4',
    'age': 'Age.mp4', 'all': 'All.mp4', 'alone': 'Alone.mp4', 'also': 'Also.mp4',
    'and': 'And.mp4', 'ask': 'Ask.mp4', 'at': 'At.mp4', 'b': 'B.mp4', 'be': 'Be.mp4',
    'beautiful': 'Beautiful.mp4', 'before': 'Before.mp4', 'best': 'Best.mp4', 'better': 'Better.mp4',
    'busy': 'Busy.mp4', 'but': 'But.mp4', 'bye': 'Bye.mp4', 'c': 'C.mp4', 'can': 'Can.mp4',
    'computer': 'Computer.mp4', 'd': 'D.mp4', 'day': 'Day.mp4', 'distance': 'Distance.mp4',
    'cannot': 'Cannot.mp4', 'change': 'Change.mp4', 'college': 'College.mp4', 'come': 'Come.mp4',
    'do not': 'Do Not.mp4', 'do': 'Do.mp4', 'does not': 'Does Not.mp4', 'e': 'E.mp4', 'eat': 'Eat.mp4',
    'engineer': 'Engineer.mp4', 'f': 'F.mp4', 'fight': 'Fight.mp4', 'finish': 'Finish.mp4',
    'from': 'From.mp4', 'g': 'G.mp4', 'glitter': 'Glitter.mp4', 'go': 'Go.mp4', 'god': 'God.mp4',
    'gold': 'Gold.mp4', 'good': 'Good.mp4', 'great': 'Great.mp4', 'h': 'H.mp4', 'hand': 'Hand.mp4',
    'hands': 'Hands.mp4', 'happy': 'Happy.mp4', 'hello': 'Hello.mp4', 'help': 'Help.mp4',
    'her': 'Her.mp4', 'here': 'Here.mp4', 'his': 'His.mp4', 'home': 'Home.mp4', 'homepage': 'Homepage.mp4',
    'how': 'How.mp4', 'i': 'I.mp4', 'invent': 'Invent.mp4', 'it': 'It.mp4', 'j': 'J.mp4', 'k': 'K.mp4',
    'keep': 'Keep.mp4', 'l': 'L.mp4', 'language': 'Language.mp4', 'laugh': 'Laugh.mp4', 'learn': 'Learn.mp4',
    'm': 'M.mp4', 'me': 'ME.mp4', 'more': 'More.mp4', 'my': 'My.mp4', 'n': 'N.mp4', 'name': 'Name.mp4',
    'next': 'Next.mp4', 'not': 'Not.mp4', 'now': 'Now.mp4', 'o': 'O.mp4', 'of': 'Of.mp4', 'on': 'On.mp4',
    'our': 'Our.mp4', 'out': 'Out.mp4', 'p': 'P.mp4', 'pretty': 'Pretty.mp4', 'q': 'Q.mp4', 'r': 'R.mp4',
    'right': 'Right.mp4', 's': 'S.mp4', 'sad': 'Sad.mp4', 'safe': 'Safe.mp4', 'see': 'See.mp4',
    'self': 'Self.mp4', 'sign': 'Sign.mp4', 'sing': 'Sing.mp4', 'so': 'So.mp4', 'sound': 'Sound.mp4',
    'stay': 'Stay.mp4', 'study': 'Study.mp4', 't': 'T.mp4', 'talk': 'Talk.mp4', 'television': 'Television.mp4',
    'thank you': 'Thank You.mp4', 'thank': 'Thank.mp4', 'that': 'That.mp4', 'they': 'They.mp4',
    'this': 'This.mp4', 'those': 'Those.mp4', 'time': 'Time.mp4', 'to': 'To.mp4', 'type': 'Type.mp4',
    'u': 'U.mp4', 'us': 'Us.mp4', 'v': 'V.mp4', 'w': 'W.mp4', 'walk': 'Walk.mp4', 'wash': 'Wash.mp4',
    'way': 'Way.mp4', 'we': 'We.mp4', 'welcome': 'Welcome.mp4', 'what': 'What.mp4', 'when': 'When.mp4',
    'where': 'Where.mp4', 'which': 'Which.mp4', 'who': 'Who.mp4', 'whole': 'Whole.mp4', 'whose': 'Whose.mp4',
    'why': 'Why.mp4', 'will': 'Will.mp4', 'with': 'With.mp4', 'without': 'Without.mp4', 'words': 'Words.mp4',
    'work': 'Work.mp4', 'world': 'World.mp4', 'wrong': 'Wrong.mp4', 'x': 'X.mp4', 'y': 'Y.mp4',
    'you': 'You.mp4', 'your': 'Your.mp4', 'yourself': 'Yourself.mp4', 'z': 'Z.mp4'
}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    text = data.get('text', '').strip()

    # Detect if the text is in Telugu
    is_telugu = any('\u0C00' <= char <= '\u0C7F' for char in text)

    # If Telugu text, translate it to English
    translated_text = text
    if is_telugu:
        try:
            translated_text = translator.translate(text, src='te', dest='en').text
            print("Translated to English:", translated_text)
        except Exception as e:
            return jsonify({'error': 'Translation failed', 'details': str(e)})

    # Preprocess English text
    text = translated_text.lower()
    tokens = nltk.word_tokenize(text)
    tokens = [word for word in tokens if word.isalnum()]
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    tokens = [lemmatizer.lemmatize(word) for word in tokens]

    # Find matching ISL animation files for the processed tokens
    animation_urls = []
    for word in tokens:
        if word in word_to_animation:
            filename = word_to_animation[word]
            animation_urls.append(url_for('static', filename=f'assets/{filename}'))

    # Return the ISL animation URLs and the translated English text
    return jsonify({'animation_urls': animation_urls, 'translated_text': translated_text})

if __name__ == '__main__':
    app.run(debug=True)
