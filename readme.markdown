# VoiceQuery-Hub System 
## Overview
This project implements a secure, voice-activated system for handling user queries and predictions. It integrates speaker verification, speech-to-text conversion, natural language processing, and database interactions to provide role-based dashboards and insights. The system is built using LangGraph for workflow orchestration, Gemini for LLM tasks, and PostgreSQL for data storage.

Key features include:
- **Voice Verification**: Ensures only authorized users can access the system.
- **Query Classification**: Distinguishes between standard queries and prediction requests.
- **Database Integration**: Translates natural language questions into PostgreSQL queries for efficient data retrieval.
- **Data Storage**: Saves sensor readings, user data (including voice embeddings), and query history.
- **Role-Based Dashboards**: Provides tailored insights based on user roles (e.g., Engineer, Admin, Operator).

The workflow is visualized in the following diagram:

![Workflow Diagram](workflow-diagram.png)  

## Technologies Used
- **Speech-to-Text**: Google Gemini for converting recorded audio to text.
- **Speaker Verification**: `nvidia/speakerverification_en_titanet_large` model from Hugging Face.
- **Workflow Orchestration**: LangGraph, with key nodes for verification, continuation (if verified), and dispatching.
- **LLM for Dispatching**: Google Gemini, responsible for splitting multiple questions and classifying them as "query" or "prediction".
- **Database Agent**: Custom agent that converts classified questions into PostgreSQL queries.
- **Database**: PostgreSQL for storing user data, voice embeddings, sensor readings, queries, and role-specific information.
- **Machine Learning Models**: Integrated for predictions (e.g., failure in 7 days, remaining useful life).
- **Dashboards**: Role-based access to insights, such as engineering-specific, admin-specific, or operator-specific views.

## Workflow Description
1. **Start**: User provides a voice record.
2. **Verification**: Verify the user from the recorded voice using speaker verification. If not verified, access is denied.
3. **Speech-to-Text**: Convert verified speech to text.
4. **Extract User Question**: Parse the text to identify the query.
5. **Classification**: Use the dispatcher LLM (Gemini) to classify the question as a "Query" or "Prediction". If multiple questions are present, split them accordingly.
   - **Query Path**:
     - DB Agent translates to PostgreSQL query.
     - Execute the query.
     - Provide answer to the user.
   - **Prediction Path**:
     - DB Agent retrieves data for ML models.
     - Run classification model (predict failure in 7 days).
     - Run regression model (predict remaining useful life).
     - Output predictions to the user.
6. **Dashboard Access**: Post-processing, users access role-based dashboards:
   - **Engineer**: Show engineering-specific insights.
   - **Admin**: Show admin-specific insights and manage users.
   - **Operator**: Show operator-specific insights.
7. **End**: Process completes.

All interactions, including sensor readings and voice embeddings, are stored in the PostgreSQL database for auditing and future reference.

## Installation
1. Clone the repository:
   ```
   https://github.com/raheemahmedd/VoiceQuery-Hub
   ```
2. Install dependencies (assuming Python environment):
   ```
   pip install -r requirements.txt
   ```
   *Note: Ensure you have access to Hugging Face models and Google Gemini API keys.*
3. Set up PostgreSQL database:
   
4. Download the speaker verification model from Hugging Face.
   ```
   https://huggingface.co/nvidia/speakerverification_en_titanet_large
   ```
5. Run the application:
   - Streamlit UI:
   ```
    cd streamlit_app
    streamlit run app.py
   ```
   - Bakend server:
   ```
    cd ..
    uvicorn app.main:app --reload

## Usage
- Record your voice query.
- The system verifies your identity, processes the query, and routes it to the appropriate path (query or prediction).
- Access your dashboard via the provided interface for role-specific insights.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

