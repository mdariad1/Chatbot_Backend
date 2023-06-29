from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
import random
import json

from chat import get_tag

app = Flask(__name__)
CORS(app)

db_name = "chatbot"
username = "root"
password = "mama2001"
server = "localhost"
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{username}:{password}@{server}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # silence the deprecation warning
db = SQLAlchemy(app)


def pick_response(tag):
    with open('intents.json', 'r') as json_data:
        intents = json.load(json_data)

    for intent in intents['intents']:
        if tag == intent["tag"]:
            return random.choice(intent['responses'])

    return "I don't understand the question..."


@app.post("/dialogue")
def dialogue():
    user_msg = request.get_json().get("message")
    dialogue_tag = request.get_json().get("dialogue_tag")
    response_counter = request.get_json().get("response_counter")

    if dialogue_tag == 'none':
        dialogue_tag = get_tag(user_msg)

    print(dialogue_tag)

    # TODO: check if text is valid

    if dialogue_tag == "unclear":
        response = "I don't understand the question..."
        message = {"answer": response, "dialogue_tag": "none", "response_counter": 1}
        return jsonify(message)

    if dialogue_tag == "greeting" or dialogue_tag == "goodbye" or dialogue_tag == "thanks":
        response = pick_response(dialogue_tag)
        message = {"answer": response, "dialogue_tag": "none", "response_counter": 1}
        return jsonify(message)

    response, end_dialogue = parse_message(user_msg, dialogue_tag, response_counter)
    if end_dialogue:
        dialogue_tag = "none"
        response_counter = 1
    else:
        response_counter += 1
    message = {"answer": response, "dialogue_tag": dialogue_tag, "response_counter": response_counter}
    return jsonify(message)


def parse_message(user_msg, tag, response_counter):
    if tag == "funny":
        response = pick_response(tag)
        return response, True

    if tag == "courses":
        statement = 'SELECT * FROM courses'

        response = pick_response(tag) + "\n"

        courses = execute_statement(statement)
        counter = 1
        for course in courses:
            response = response + str(counter) + '. ' + course[1] + '\n'
            counter += 1

        return response, True

    if tag == "contact":
        if response_counter == 1:
            response = pick_response(tag) + "\n"

            phone = "0256 592 155 | 0256 592 364"
            email = "secretariat.mateinfo@e-uvt.ro"
            response += "1. Our phone numbers - " + phone + "\n"
            response += "2. Our email address - " + email + "\n"


            response += "Would you like me to redirect you to our contact page?\n"

            return response, False
        elif response_counter == 2:
            response = ''

            affirmative_forms = ['Yes', 'Yeah', 'Sure', 'Of course', 'Certainly', 'Definitely', 'Absolutely']
            affirmative = False

            for form in affirmative_forms:
                if form in user_msg or form.lower() in user_msg:
                    affirmative = True

            if affirmative:
                response += 'redirect_to_contact'
            else:
                response += "Alright. If you have any other questions, please let me know."

            return response, True
    if tag == "exams":
        statement = ''
        if response_counter == 1:
            question_forms = ['Please select the level of study you are interested in:\n',
                              'What level of study are you interested in?\n',
                              'Tell me the level of study you are interested in\n']
            response = random.choice(question_forms)
            return response, False

        elif response_counter == 2:
            response = pick_response(tag) + "\n"
            # PROGRAMMES DIALOGUE
            category1 = ["bachelor", "Bachelor", "undergraduate", "Undergraduate", "bachelor's", "Bachelor's"]
            category2 = ["master", "Master", "postgraduate", "Postgraduate", "master's", "Master's"]

            if user_msg in category1:
                statement = 'SELECT * FROM exams WHERE programme = "bachelor"'
            elif user_msg in category2:
                statement = 'SELECT * FROM exams WHERE programme = "master"'

            data = execute_statement(statement)
            link = data.first()[2]

            str_link = f"<a href='{link}' target='_blank' style='text-decoration: underline;'>{link}</a>"
            response += str_link + "\n\n"
            response += "Would you like me to give you a link to the academic structure of the year?\n"

            return response, False

        elif response_counter == 3:
            response = ''

            affirmative_forms = ['Yes', 'Yeah', 'Sure', 'Of course', 'Certainly', 'Definitely', 'Absolutely']
            affirmative = False

            for form in affirmative_forms:
                if form in user_msg or form.lower() in user_msg:
                    affirmative = True

            if affirmative:
                response_forms = ['Sure thing. Please check this link below:\n',
                                  'Certainly. Take a look at this link below:\n',
                                  'Great. Please examine the link provided below:\n']

                response += random.choice(response_forms)

                statement = 'SELECT * FROM admission WHERE admName = "master"'
                data = execute_statement(statement)
                structure = data.first()[2]

                link1 = f"<a href={structure} target='_blank text' style='text-decoration: underline;'>{structure}</a>\n"
                response += link1
            else:
                response += "Alright. If you have any other questions, please let me know."

            return response, True
    if tag == "scholarship":
        statement = 'SELECT * FROM scholarships'

        if response_counter == 1:
            response = pick_response(tag) + "\n"
            scholarships = execute_statement(statement)

            counter = 1
            for scholarship in scholarships:
                response = response + str(counter) + '. ' + scholarship[1] + ' - ' + str(scholarship[2]) + ' lei' + '\n'
                counter += 1

            question_forms = ['Would you like me to provide you with an additional link for more informations?\n',
                              'Would you be interested in receiving an extra link that offers more information?\n',
                              'Can I offer you an additional link that provides further details?\n',
                              'Do you want me to share an extra link that can give you more information?\n']

            response += random.choice(question_forms)

            return response, False

        elif response_counter == 2:
            response = ''

            affirmative_forms = ['Yes', 'Yeah', 'Sure', 'Of course', 'Certainly', 'Definitely', 'Absolutely']
            affirmative = False

            for form in affirmative_forms:
                if form in user_msg or form.lower() in user_msg:
                    affirmative = True

            if affirmative:
                response_forms = ['Sure thing. Please check these links below:\n',
                                  'Certainly. Take a look at these links below:\n',
                                  'Of course. Please examine the links provided below:\n']

                response += random.choice(response_forms)

                details = "https://goo.gl/maps/MWEMzUPnVPSPnCKq7"
                ongoing = "https://orar.uvt.ro/universitatea-de-vest-din-timisoara-parter/"
                link1 = f"<a href={details} target='_blank text' style='text-decoration: underline;'>{details}</a>\n"
                link2 = f"<a href={ongoing} target='_blank text' style='text-decoration: underline;'>{ongoing}</a>\n"
                response += "1. Scholarships' details - " + link1
                response += "2. General notice board - " + link2
            else:
                response += "Alright. If you have any other questions, please let me know."

            return response, True

    if tag == "location":
        response = pick_response(tag) + "\n"
        uvt_location = "https://goo.gl/maps/MWEMzUPnVPSPnCKq7"
        halls_map = "https://orar.uvt.ro/universitatea-de-vest-din-timisoara-parter/"
        link1 = f"<a href={uvt_location} target='_blank text' style='text-decoration: underline;'>{uvt_location}</a>\n"
        link2 = f"<a href={halls_map} target='_blank text' style='text-decoration: underline;'>{halls_map}</a>\n"
        response += "1. University location - " + link1
        response += "2. University halls' map - " + link2
        return response, True

    if tag == "payments":
        response = pick_response(tag) + "\n"
        return response, True

    if tag == "admission":
        statement = 'SELECT * FROM specials'

        if response_counter == 1:
            question_forms = ['Please select the programme you are interested in:\n',
                              'What level of study are you interested in?\n',
                              'What level of study do you want to apply for?\n']
            response = random.choice(question_forms)
            return response, False

        elif response_counter == 2:
            response = pick_response(tag) + "\n"
            # PROGRAMMES DIALOGUE
            category1 = ["bachelor", "Bachelor", "undergraduate", "Undergraduate", "bachelor's", "Bachelor's"]
            category2 = ["master", "Master", "postgraduate", "Postgraduate", "master's", "Master's"]

            if user_msg in category1:
                statement = 'SELECT * FROM admission WHERE admName = "bachelor"'
            elif user_msg in category2:
                statement = 'SELECT * FROM admission WHERE admName = "master"'

            specializations = execute_statement(statement)
            link = specializations.first()[2]
            response += f"<a href='{link}' target='_blank' style='text-decoration: underline;'>{link}</a>"

            return response, True

    if tag == "programmes":
        statement = ''

        if response_counter == 1:
            question_forms = ['Please select the level of study you are interested in:\n',
                              'What level of study are you interested in?\n',
                              'What level of study do you want to apply for?\n']
            response = random.choice(question_forms)
            return response, False
        elif response_counter == 2:
            response = pick_response(tag) + "\n"
            # PROGRAMMES DIALOGUE
            category1 = ["bachelor", "Bachelor", "undergraduate", "Undergraduate", "bachelor's", "Bachelor's"]
            category2 = ["master", "Master", "postgraduate", "Postgraduate", "master's", "Master's"]

            if user_msg in category1:
                statement = 'SELECT * FROM specials WHERE details = "bachelor"'
            elif user_msg in category2:
                statement = 'SELECT * FROM specials WHERE details = "master"'

            programmes = execute_statement(statement)
            counter = 1
            for programme in programmes:
                response = response + str(counter) + '. ' + programme[1] + '\n'
                counter += 1

            response += '\n'
            response += "Would you like me to redirect you to the Programmes' page for more details?\n"

            return response, False

        elif response_counter == 3:
            response = ''

            affirmative_forms = ['Yes', 'Yeah', 'Sure', 'Of course', 'Certainly', 'Definitely', 'Absolutely']
            affirmative = False

            for form in affirmative_forms:
                if form in user_msg or form.lower() in user_msg:
                    affirmative = True

            if affirmative:
                response += 'redirect_to_programmes'
            else:
                response += "Alright. If you have any other questions, please let me know."

            return response, True


def execute_statement(statement):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    connection = engine.connect()
    result = connection.execute(text(statement))
    connection.close()
    return result


if __name__ == "__main__":
    app.run(debug=True)
