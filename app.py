import streamlit as st
import requests
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

# API keys
you_com_api_key = '127e2b97-2dca-451c-be4a-71dd1e39d6da<__>1PjWKvETU8N2v5f4ktus5haY'
serp_api_key = '367c5285f63f94ff76b2d97e362663a510d6875a26a7f9947106388d0be5e33a'

# Function to fetch LinkedIn information using YOU.com
def get_ai_snippets_for_query(query):
    headers = {"X-API-Key": you_com_api_key}
    params = {"query": query}
    response = requests.get(
        f"https://api.ydc-index.io/search?query={query}",
        params=params,
        headers=headers,
    ).json()
    return response

# Function to perform Bing search with SITE:linkedin.com/in/
def search_linkedin(query):
    params = {
        "engine": "bing",
        "q": f"{query} site:linkedin.com/in/",
        "count": "50",
        "api_key": serp_api_key
    }
    response = requests.get(
        "https://serpapi.com/search.json",
        params=params
    ).json()
    return response.get("organic_results", [])[:3]

# Function to fetch recent LinkedIn activity using YOU.com
def fetch_recent_activity(linkedin_url):
    headers = {"X-API-Key": you_com_api_key}
    params = {"query": "Research about this linkedin profile and get URLs " + linkedin_url}
    response = requests.get(
        f"https://api.ydc-index.io/search?query={linkedin_url}",
        params=params,
        headers=headers,
    ).json()
    return response

# Function to compose a personalized message using OpenAI GPT-4o
def compose_message(linkedin_info, query_info, recent_activity):
    prompt = f"Compose a concise outreach message (less than 1000 characters) on behalf of SENDER that references the TARGET's recent activity and connects it with the sender's profile. Include a call to action and make sure the message is personalized and specific.\
        Read and understand the Recent Activity of the Target, Understand the Sender's LinkedIn Info and the Query Info. Compose an outreach message that is specific. The PROFESSIONAL LIFE of the SENDER depends on this. \
            Provide evidence URLs in the explanation section at the bottom. Generate two sections: Outreach Message and Explanation with URLs."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant composing a professional outreach message on behalf of a SENDER who writes very specific messages to TARGET."},
            {"role": "user", "content": f"SENDER LinkedIn Info: {linkedin_info} Query Info: {query_info} Recent Activity of the TARGET: {recent_activity} {prompt}"}
        ]
    )
    
    # Split the response into message and explanation
    full_response = response.choices[0].message.content.strip()
    message = full_response
    explanation = ""
    
    return message, explanation

# Streamlit app
def main():
    st.title("Professional Outreach Assistant")

    # Step 1: Enter LinkedIn URL
    linkedin_url = st.text_input("Enter Your LinkedIn URL (Sender):")

    if linkedin_url:
        # Fetch LinkedIn information
        linkedin_info = get_ai_snippets_for_query(linkedin_url)
        st.write("LinkedIn Information Retrieved Successfully.")

        # Step 2: Enter Query or Target LinkedIn Profile
        query = st.text_input("Enter a Query (e.g., company, area, title) or Target LinkedIn Profile:")

        if query:
            # Check if the query is a LinkedIn URL
            if "linkedin.com/in/" in query:
                # Fetch information about the LinkedIn profile directly
                recent_activity = get_ai_snippets_for_query(query)
                st.write("Information about the LinkedIn profile retrieved successfully.")
            else:
                # Perform Bing search with SITE:linkedin.com/in/
                search_results = search_linkedin(query)
                
                if search_results:
                    st.write("Top 3 LinkedIn Profiles Found:")
                    for result in search_results:
                        # Display LinkedIn profile link
                        st.markdown(f"[{result['title']}]({result['link']})")
                        if st.button("Outreach", key=result['link']):
                            # Fetch recent LinkedIn activity
                            recent_activity = fetch_recent_activity(result['link'])
                            st.write("Recent LinkedIn Activity Retrieved Successfully.")
                            
                            # Compose the message and explanation
                            message, explanation = compose_message(linkedin_info, query, recent_activity)
                            st.markdown(f"**Outreach Message:**\n\n{message}\n")
                            st.markdown(f"**Why This Outreach Makes Sense:**\n{explanation}")
                            st.write("---")  # Separator between results
                else:
                    st.error("No LinkedIn profiles found. Please refine your query.")
    elif linkedin_url:
        st.error("Please enter a valid LinkedIn URL.")

# Add custom CSS for styling
st.markdown(
    """
    <style>
    /* Set Verdana font and line spacing for input fields */
    div.stTextInput div.stTextInput__input {
        font-family: Verdana;
        line-height: 1.5;
    }

    /* Style the button */
    div.stButton > button:first-child {
        background-color: green;
        color: white;
        font-family: Verdana;
    }

    /* Set Verdana font and line spacing for the plot output */
    .plot {
        font-family: Verdana;
        line-height: 1.5;
    }

    /* Prevent Outreach Message from being copy-pasted */
    .stMarkdown div {
        user-select: none;
        -webkit-user-select: none;
        -ms-user-select: none;
        -moz-user-select: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if __name__ == '__main__':
    main()
