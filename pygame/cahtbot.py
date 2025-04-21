import random
import re
import datetime

GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up", "hey")
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]

def greeting(sentence):
    """If user's input is a greeting, return a greeting response"""
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)

RESPONSES = {
    r'.*your name.*': ["My name is ChatBot. You can call me CB.", "I'm ChatBot, but friends call me CB."],
    r'.*how are you.*': ["I'm functioning within normal parameters.", "All systems operational!"],
    r'.*what can you do.*': ["I can chat with you, tell you the time, and respond to basic questions.", 
                            "I'm a simple chatbot. Try asking me about myself or say hello!"],
    r'.*time.*': [f"The current time is {datetime.datetime.now().strftime('%H:%M')}"],
    r'.*date.*': [f"Today's date is {datetime.datetime.now().strftime('%Y-%m-%d')}"],
    r'.*quit.*': ["Goodbye! It was nice talking to you.", "See you later!"]
}

def respond(user_input):
    """Generate a response to the user's input"""
    greeting_response = greeting(user_input)
    if greeting_response:
        return greeting_response
    
    for pattern, responses in RESPONSES.items():
        if re.match(pattern, user_input, re.IGNORECASE):
            return random.choice(responses)
    
    return "I didn't understand that. Could you try rephrasing?"

def chat():
    """Main chat function"""
    print("ChatBot: Hello! I'm a simple chatbot. Type 'quit' to exit.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            print("ChatBot: " + random.choice(RESPONSES['.*quit.*']))
            break
        
        response = respond(user_input)
        print("ChatBot: " + response)

if __name__ == "__main__":
    chat()