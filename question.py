from app import db, Question, CountAttempt, Attempt

def get_questions():
    return Question.query.all()


def check_answers(user_answers):  # depracated
    questions = get_questions()
    results = {}
    for question in questions:
        if question.QuestionID in user_answers:
            results[question.QuestionID] = (user_answers[question.QuestionID]==question.Answer)
    return results

def get_next_question(userid):
    questions = get_questions()
    # only select the QuestionID column in CountAttempt
    records = CountAttempt.query.filter_by(UserID=userid).with_entities(CountAttempt.QuestionID).all()
    records = set([record[0] for record in records])
    for question in questions:
        if question.QuestionID not in records:
            new_record = CountAttempt(userid, question.QuestionID, 0)
            db.session.add(new_record)
    db.session.commit()

    record = CountAttempt.query.filter_by(UserID=userid).order_by('NumAttempts').first()
    if record:
        next_question = Question.query.filter_by(QuestionID=record.QuestionID).first()

        return next_question
    return None


def check_one_answer(questionid, user_answer):
    try:
        question = Question.query.filter_by(QuestionID=questionid).first()
        return question.Answer==int(user_answer), question
    except error:
        return error, None


def update_attempts(userid, questionid, user_answer):
    count_attempt_record = CountAttempt.query.filter_by(
        UserID=userid, QuestionID=questionid
        ).first()
    if count_attempt_record:
        if count_attempt_record.Correct:
            count_attempt_record.PracticeAttempts+=1
        else:
            count_attempt_record.NumAttempts += 1
            attempt_record = Attempt(userid, questionid, user_answer)
            db.session.add(attempt_record)

            correct, _ = check_one_answer(questionid, user_answer)
            if correct:
                count_attempt_record.Correct = True

        db.session.commit()
    

if __name__ == "__main__":
    update_attempts("thepoppycat", 5)
    print(get_next_question("thepoppycat"))