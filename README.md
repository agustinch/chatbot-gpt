# Food Chatbot `beta`

Chatbot example with text-davinci-003. The goal is to move all business logic to the OpenAI model. The chatbot can manage your food and give you recipe recommendations.
Chatbot can remember what you have in your fridge. You can add, update, delete and read refrigerator items. Then, based on the items in your fridge, you can ask for dish recommendations.

## Technology
- Python: We create an API with FastApi
- Redis: To store each chat session.
- React / Next.js: To build our front
- OpenAI: We use text-davinci-003 model to build business logic


## Next steps
- Improve prompt to resolve some errors and deviations in chat conversations.
- Add database to store food
- Add logic to remember user conversations
- Improve logic to reduce OpenAI API calls
