import os
print(os.getcwd())

import nltk
import streamlit as st
import joblib
import time
import matplotlib.pyplot as plt
import pandas as pd
from lime.lime_text import LimeTextExplainer

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Load the trained machine learning pipeline
pipeline = joblib.load('C:/Users/Cecily/Desktop/final_project/models/sentiments_pipeline.pkl')


# Streamlit app configuration
st.set_page_config(page_title="Mental Well-Being Screening", page_icon="🧠", layout="wide")

# Custom CSS for background and buttons
st.markdown(
    """
    <style>
    .stApp {
        background-color: #e0f7fa;
    }
    .css-1d391kg {
        background-color: #CBE3EF;
        color: black;
    }
    .custom-button {
        background-color: #007BFF;
        color: white;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
    }
    .custom-button:hover {
        background-color: #0056b3;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state for input history
if 'input_history' not in st.session_state:
    st.session_state.input_history = []

# Title and description
st.title("Mental Well-Being Screening Tool 🧠")
st.write("This application analyzes social media posts from Reddit to predict whether a user is likely experiencing mental health concerns.")

# User input section
user_input = st.text_area(
    "Paste your text here for analysis:",
    placeholder="Enter text for analysis...",
    height=100
)

# Button for sentiment analysis
if st.button("Analyze Sentiment"):
    if user_input.strip():
        # Save input to history
        st.session_state.input_history.append(user_input)

        # Display loading spinner
        with st.spinner("Analyzing... Please wait..."):
            time.sleep(2)  # Simulate processing delay
            prediction = pipeline.predict([user_input])[0]
            probability = pipeline.predict_proba([user_input])[0]
            result = "Signs of emotional difficulty" if prediction == 1 else "No significant signs of emotional difficulty"
            confidence = probability[int(prediction)] * 100

        # Customizable prediction threshold
        threshold = st.slider("Set Confidence Threshold", 0.0, 1.0, 0.5)
        if confidence / 100 >= threshold:
            st.subheader("Prediction Result")
            st.write(f"**Prediction:** {result}")
            st.write(f"**Confidence:** {confidence:.2f}%")
        else:
            st.write(f"The model's confidence ({confidence:.2f}%) is below the threshold of {threshold * 100:.1f}%.")

    else:
        st.error("Please enter some text for analysis.")

# Display user input history
st.header("User Input History")
if st.session_state.input_history:
    for i, input_text in enumerate(reversed(st.session_state.input_history), 1):
        st.write(f"{i}. {input_text}")

# Feature importance visualization
def plot_feature_importance(model):
    if hasattr(model.named_steps['classifier'], 'feature_importances_'):
        feature_importances = model.named_steps['classifier'].feature_importances_
        feature_names = model.named_steps['preprocessor'].transformers_[0][1].get_feature_names_out()
        numerical_feature_names = ['upvotes', 'num_comments', 'year', 'month', 'day', 'hour', 'upvotes_per_comment', 'has_body']
        all_feature_names = list(feature_names) + numerical_feature_names
        importance_df = pd.DataFrame({
            'Feature': all_feature_names,
            'Importance': feature_importances
        }).sort_values(by='Importance', ascending=False)

        plt.figure(figsize=(10, 6))
        plt.barh(importance_df['Feature'], importance_df['Importance'], color='skyblue')
        plt.xlabel('Importance')
        plt.ylabel('Feature')
        plt.title('Feature Importance for Random Forest Model')
        plt.gca().invert_yaxis()
        st.pyplot(plt)
    else:
        st.write("Model does not support feature importances.")

if st.button("Show Feature Importance"):
    plot_feature_importance(pipeline)

# Sidebar
st.sidebar.header("About the App")
st.sidebar.write("This tool predicts mental wellness from Reddit posts using a pre-trained ML model with TF-IDF vectorization and logistic regression.")
st.sidebar.write("Disclaimer: This tool is not a diagnostic instrument.")

st.write("---")
st.write("Developed by Group_11. Powered by Streamlit and Scikit-learn.")


# Add LIME explanation button and logic
if st.button("Explain Prediction with LIME"):
    # Create an explainer for text data
    explainer = LimeTextExplainer(class_names=['No significant signs of emotional difficulty', 'Signs of emotional difficulty'])
    
    # Generate explanation for the current input text
    explanation = explainer.explain_instance(
        user_input,  # Input text
        pipeline.predict_proba,  # Function that returns prediction probabilities
        num_features=10  # Number of features (words) to show
    )
    
    # Display LIME explanation as text
    st.write("LIME Explanation (Top Influential Words):")
    st.write(explanation.as_list())
    
    # Display visualization 
    fig = explanation.as_pyplot_figure()
    st.pyplot(fig)

