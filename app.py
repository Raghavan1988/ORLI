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
    params = {"query": query + " identify the name and title"}
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
    params = {"query": "Research about the person on internet. Identify name and title, What does this person do : " + linkedin_url}
    response = requests.get(
        f"https://api.ydc-index.io/search?query={linkedin_url}",
        params=params,
        headers=headers,
    ).json()
    return response

# Function to compose a personalized message using OpenAI GPT-4o
def compose_message(linkedin_info, query_info, recent_activity, intent):
    prompt = f"""
   Objective: Compose a highly effective outreach message on behalf of SENDER that leverages TARGET's recent LinkedIn activity and aligns it with SENDER's professional background and goals. The intent of the SENDER is {intent}. The message should be concise (under 1000 characters), personalized, and include a compelling call to action. The success of SENDER's career could hinge on this outreach.

Tree of Thoughts Approach:

Understanding Phase:
Step 1:

Root Thought: Begin by thoroughly exploring TARGET's recent LinkedIn activities (posts, comments, or updates).
Branch 1: Identify recurring themes or topics that are important to TARGET.
Branch 2: Pinpoint specific instances where TARGET has expressed strong opinions or enthusiasm.
Branch 3: Determine how these activities reflect TARGET's professional goals and challenges.
Step 2:

Root Thought: Delve into SENDER's LinkedIn profile with a focus on their professional experience, expertise, and intent.
Branch 1: Identify key accomplishments and areas of expertise relevant to TARGET's interests.
Branch 2: Consider how SENDER's current role and objectives align with the intent (e.g., Seller, Hiring Manager, Job Seeker, General Networking).
Branch 3: Look for connections between SENDER's background and TARGET's recent activities.
Step 3:

Root Thought: Analyze the Query Info to fully understand the context and purpose of the outreach.
Branch 1: Understand the immediate goal of the outreach (e.g., making a sale, securing a job, building a network).
Branch 2: Consider how this goal aligns with both SENDER’s and TARGET's professional trajectories.
Branch 3: Evaluate the potential benefits for both parties.
Composing Phase:
Step 4:

Root Thought: Synthesize the insights gathered from the Understanding Phase.
Branch 0: Identify the TARGET's name, title, current company
Branch 1: Formulate a message that naturally connects TARGET's profile with SENDER's profile, establishing a mutual interest.
Branch 2: Infuse the message with emotional prompts that emphasize the importance of this connection. Highlight shared values, goals, or challenges.
Branch 3: Ensure the tone is empathetic and resonates with TARGET's needs, making them feel understood and valued.
Step 5:

Root Thought: Craft a personalized, specific outreach message.
Branch 1: The message should directly address TARGET's title or recent activities.
Branch 2: Clearly convey SENDER's intentions and how they can provide value or support.
Branch 3: Include a strong, action-oriented call to action that encourages TARGET to respond or engage.
Step 6:

Root Thought: Reflect on the gravity of the outreach.
Branch 1: The message should not only stand out but also emotionally connect with TARGET.
Branch 2: Highlight how this outreach is a critical step in SENDER's career, creating a sense of urgency.
Branch 3: Aim for a memorable impact that motivates TARGET to take the desired action.
Explanation Phase:
Step 7:

Root Thought: Provide evidence and rationale behind the crafted message.
Branch 1: In a section labeled "Explanation with URLs," list relevant URLs that reference TARGET's recent activity.
Branch 2: Explain how these activities were used to tailor the outreach message.
Branch 3: Justify the emotional and strategic elements included in the message, ensuring TARGET sees the value in the connection.
Output Format:

Outreach Message: [Write the message here.]

Explanation with URLs: [Provide your explanation and relevant URLs here.]
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant composing a professional outreach message on behalf of a SENDER who writes very specific messages to TARGET."},
            {"role": "user", "content": f"SENDER LinkedIn Info: {linkedin_info} SENDER is {intent} Query Info: {query_info} Recent Activity of the TARGET: {recent_activity} {prompt}"}
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

        # Step 2: Select Intent
        intent = st.selectbox("Select Your Intent:", ["Seller", "Hiring Manager", "Job Seeker", "General Networking"])
        

        # Step 3: Enter Query or Target LinkedIn Profile
        query = st.text_input("Enter a Query (e.g., company, area, title) or Target LinkedIn Profile:")

        if query:
            st.write(f"Selected intent: {intent}")

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
                            message, explanation = compose_message(linkedin_info, query, recent_activity, intent)
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
