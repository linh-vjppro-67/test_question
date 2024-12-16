import streamlit as st
import json
import os
import time
from openai import AzureOpenAI

# Set up Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],  # Lấy endpoint từ secrets
    api_key=st.secrets["AZURE_OPENAI_API_KEY"],         # Lấy API key từ secrets
    api_version="2024-05-01-preview"
)

# Function to generate questions based on the selected job title, categories, skills, level, type, and number of questions
def generate_questions(job_title, categories, skills, level, question_type, num_questions):
    assistant = client.beta.assistants.create(
        model="gpt-4o-mini",  # Replace with model deployment name.
        instructions="""
        For each question, only include the skills that are directly mentioned or implied in the question. The skills listed should strictly correspond to the category provided and should be relevant to the context of the question. If the question mentions specific technologies or tools, only those technologies or tools should appear in the 'skills' field. Do not add skills from the category that are not directly mentioned or related to the question. For example, if the question is about container orchestration, only skills like 'Kubernetes' and 'Docker' should appear, and not other skills from the 'Microservices' category like 'Spring Cloud'. Question difficulty and length should be appropriate for the level (Senior, Junior). Senior questions should be more difficult and longer, while Junior questions should be easier and simpler. With multiple-select questions, there are 5 or more options and 2 or more true answers.
        Output format like json:
            "questions": [
            {
                "id": 1,
                "level": "Senior",
                "type": "single-choice",
                "job_title": [
                "Java Software Engineer"
                ],
                "category": [
                "Microservices"
                ],
                "skills": [
                "Kubernetes",
                "Docker"
                ],
                "question": "Which platform is widely used for container orchestration?",
                "options": [
                { "description": "Docker", "isAnswerKey": false },
                { "description": "Kubernetes", "isAnswerKey": true },
                { "description": "Git", "isAnswerKey": false },
                { "description": "Jenkins", "isAnswerKey": false }
                ]
            },
            {
                "id": 2,
                "level": "Junior",
                "type": "multiple-select",
                "job_title": [
                "Java Software Engineer"
                ],
                "category": [
                "Microservices"
                ],
                "skills": [
                "Kubernetes",
                "Docker"
                ],
                "question": "Which of the following are used for container orchestration?",
                "options": [
                { "description": "Docker", "isAnswerKey": true },
                { "description": "Kubernetes", "isAnswerKey": true },
                { "description": "Git", "isAnswerKey": false },
                { "description": "Jenkins", "isAnswerKey": false },
                { "description": "OpenShift", "isAnswerKey": false },
                { "description": "Ansible", "isAnswerKey": false }
                ]
            }
            ]
        }
        """,
        temperature=1,
        top_p=1
    )

    # Create a thread for generating questions
    thread = client.beta.threads.create()

    # Prepare the input content for the assistant
    input_value = f"Based on file search AssistantVectorStore_29761, with the role {level} {job_title} for focused categories: {', '.join(categories)} with skills: {', '.join(skills)}. Generate {num_questions} {question_type} questions in real context. Remove ```json"
    # st.write(f"Input to API: {input_value}")  # Debugging: Show the input message

    # Add a user question to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=input_value
    )

    # Run the thread to generate the responses
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    # Loop to wait for the completion of the task
    while run.status in ['queued', 'in_progress', 'cancelling']:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

    # Fetch the messages (questions generated) after completion
    if run.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread.id)

        # Convert SyncCursorPage to a list to check the number of messages
        messages_list = list(messages)
        results = []
        for message in messages_list:
            if hasattr(message, "content") and isinstance(message.content, list):
                for block in message.content:
                    if hasattr(block, "text") and hasattr(block.text, "value"):
                        value = block.text.value
                        results.append(value)
        return results

    else:
        return f"Run status: {run.status}"

# Streamlit App
def app():
    # Read data from file 'data.json'
    with open('data.json', 'r') as file:
        data = json.load(file)

    st.title('FPT Software Assessment')

    # Extract the job title from the data
    job_title = data['job_title']
    st.write(f"Job Title: {job_title}")

    # Prepare the categories and skills based on the loaded data
    categories = [item['category'] for item in data['value']]
    all_skills = {item['category']: item['skills'] for item in data['value']}

    # Multiselect for Categories
    selected_categories = st.multiselect('Select Categories', categories)

    # Collect skills for the selected categories
    available_skills = []
    for category in selected_categories:
        available_skills.extend(all_skills.get(category, []))
    available_skills = list(set(available_skills))  # Remove duplicates

    # Multiselect for Skills
    selected_skills = st.multiselect('Select Skills', available_skills)

    # Dropdown for Question Level
    selected_level = st.selectbox('Select Level', ['Senior', 'Junior'])

    # Dropdown for Question Type
    selected_type = st.selectbox('Select Question Type', ['single-choice', 'multiple-select'])

    # Dropdown for Number of Questions
    num_questions = st.selectbox('Select Number of Questions', [5, 10, 15, 20])

    # Display the selected options
    st.write(f'Selected Categories: {selected_categories}')
    st.write(f'Selected Skills: {selected_skills}')
    st.write(f'Selected Level: {selected_level}')
    st.write(f'Selected Type: {selected_type}')
    st.write(f'Selected Number of Questions: {num_questions}')

    # Generate dynamic input message
    if selected_categories and selected_skills:
        # Add a button to perform an action
        if st.button('Submit'):
            st.write("Your request has been submitted successfully!")
            st.write("Wait a minute...")

            # Call the function to generate questions using OpenAI
            result = generate_questions(job_title, selected_categories, selected_skills, selected_level, selected_type, num_questions)

            # Process the result if it's in the correct format
            if isinstance(result, list):
                for question in result:
                    try:
                        question_data = json.loads(question)  # Try parsing as JSON
                        if 'questions' in question_data:
                            for q in question_data['questions']:
                                if isinstance(q, dict) and 'question' in q:
                                    st.subheader(q['question'])
                                    for option in q.get('options', []):
                                        # Check if the option is the correct answer
                                        if option.get('isAnswerKey', False):
                                            # Display the correct answer in bold and green
                                            st.markdown(f"<span style='color: green; font-weight: bold;'>{option['description']}</span>", unsafe_allow_html=True)
                                        else:
                                            st.write(option['description'])
                        else:
                            st.write("No questions found in the response.")
                    except Exception as e:
                        st.write(f"Error parsing question data: {e}")
            else:
                st.write("Error: Invalid data format received")

# Run the app
if __name__ == '__main__':
    app()
