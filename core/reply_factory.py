
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id):
    '''
    Validates and stores the answer for the current question to session.
    '''
    if isinstance(current_question_id, str): 
        if not current_question_id.isnumeric():
            return False, "Question id must be a number"
        current_question_id = int(current_question_id)
    if not isinstance(current_question_id, int):
        return False, "Question id must be a positive integer"
    if current_question_id < 0 or current_question_id > len(PYTHON_QUESTION_LIST):
        return False, "Question id is invalid"
    if PYTHON_QUESTION_LIST[current_question_id]["answer"] != answer:
        return False, "Incorrect answer passed"
    return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    if current_question_id!=len(PYTHON_QUESTION_LIST)-1:
        return PYTHON_QUESTION_LIST[current_question_id+1], current_question_id+1
    return None


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    matched_answers = set(map(lambda q_dict: q_dict["answer"], PYTHON_QUESTION_LIST)).intersection(
        map(lambda message: message.text,
            filter(
                lambda message: message["is_user"],
                session["message_history"]
            )
        )
    )
    return f"Thank you for playing, you score is {len(matched_answers)}"
