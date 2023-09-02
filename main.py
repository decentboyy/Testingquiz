import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackContext

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# States for the conversation
QUIZ_TITLE, QUIZ_QUESTION, QUIZ_OPTIONS, QUIZ_CORRECT_ANSWER = range(4)

# Dictionary to store quizzes
quizzes = {}

# Start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to the Quiz Bot! Use /newquiz to create a new quiz.")

# Function to start creating a new quiz
def new_quiz(update: Update, context: CallbackContext):
    update.message.reply_text("Let's create a new quiz. Please enter the title of your quiz:")
    return QUIZ_TITLE

# Function to handle quiz title
def set_quiz_title(update: Update, context: CallbackContext):
    context.user_data['quiz_title'] = update.message.text
    update.message.reply_text(f"Great! Your quiz title is: {context.user_data['quiz_title']}\n"
                              "Now, enter the first question:")
    return QUIZ_QUESTION

# Function to handle quiz questions
def set_quiz_question(update: Update, context: CallbackContext):
    context.user_data['quiz_question'] = update.message.text
    update.message.reply_text("Enter options for the question (separated by commas):")
    return QUIZ_OPTIONS

# Function to handle quiz options
def set_quiz_options(update: Update, context: CallbackContext):
    context.user_data['quiz_options'] = update.message.text.split(',')
    update.message.reply_text("Which option is the correct answer (e.g., A, B, C)?")
    return QUIZ_CORRECT_ANSWER

# Function to handle correct answer
def set_correct_answer(update: Update, context: CallbackContext):
    correct_answer = update.message.text.upper()
    if correct_answer in context.user_data['quiz_options']:
        quiz = {
            'title': context.user_data['quiz_title'],
            'questions': [
                {
                    'question': context.user_data['quiz_question'],
                    'options': context.user_data['quiz_options'],
                    'correct_answer': correct_answer
                }
            ],
            'leaderboard': {}
        }
        chat_id = update.message.chat_id
        if chat_id not in quizzes:
            quizzes[chat_id] = []
        quizzes[chat_id].append(quiz)
        update.message.reply_text("Quiz created successfully!")
    else:
        update.message.reply_text("Invalid answer option. Please enter a valid option.")
    return ConversationHandler.END

# Main function to handle user messages
def quiz_bot(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    user_answer = update.message.text.upper()

    if chat_id in quizzes:
        for quiz in quizzes[chat_id]:
            for question in quiz['questions']:
                if user_answer == question['correct_answer']:
                    # Update the user's score
                    if user_id not in quiz['leaderboard']:
                        quiz['leaderboard'][user_id] = 0
                    quiz['leaderboard'][user_id] += 1

        # Generate the leaderboard
        leaderboard = sorted(quiz['leaderboard'].items(), key=lambda x: x[1], reverse=True)
        leaderboard_text = "Leaderboard:\n"
        for rank, (user_id, score) in enumerate(leaderboard, start=1):
            user = context.bot.get_chat_member(chat_id, user_id)
            leaderboard_text += f"{rank}. {user.user.first_name} - {score} points\n"

        update.message.reply_text(leaderboard_text)

# Create an Updater and pass in your bot's API token
updater = Updater("5058249365:AAEQ7-6sDQh3HrpU23fEMvjARKa95RKVJfU", use_context=True)

# Get the dispatcher to register handlers
dp = updater.dispatcher

# Define a conversation handler for creating quizzes
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('newquiz', new_quiz)],
    states={
        QUIZ_TITLE: MessageHandler(filters=Filters.text & ~Filters.command, callback=set_quiz_title),
        QUIZ_QUESTION: [MessageHandler(Filters.text & ~Filters.command, set_quiz_question)],
        QUIZ_OPTIONS: [MessageHandler(Filters.text & ~Filters.command, set_quiz_options)],
        QUIZ_CORRECT_ANSWER: [MessageHandler(Filters.text & ~Filters.command, set_correct_answer)],
    },
    fallbacks=[],
)

# Register the conversation handler
dp.add_handler(conv_handler)

# Register a message handler for all other messages
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, quiz_bot))

# Register a command handler for the /start command
dp.add_handler(CommandHandler("start", start))

# Start the Bot
updater.start_polling()

# Run the bot until you send a signal to stop (e.g., Ctrl+C)
updater.idle()
