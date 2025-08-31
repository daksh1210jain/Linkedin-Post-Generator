import uuid
import re
import base64
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

# Load API key securely from Streamlit Secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -------------------------------
# Helper Functions
# -------------------------------

def generate_outlines(topic, tone, audience, n_posts=3):
    prompt = f"""
    You are an AI content strategist. Generate {n_posts} distinct outlines
    for LinkedIn posts about "{topic}".

    Each outline must include:
    - A hook/opening idea
    - 2-3 key talking points
    - A suggested call-to-action for engagement

    Output format:
    OUTLINE 1:
    ...
    OUTLINE 2:
    ...
    and so on.

    Target audience: {audience}
    Writing style/tone: {tone}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful LinkedIn post writing assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )
    return response.choices[0].message.content


def expand_outlines_to_posts(outlines, tone, audience, n_posts=3):
    prompt = f"""
    You are a professional LinkedIn ghostwriter. Convert the outlines below
    into exactly {n_posts} full LinkedIn posts. 

    Rules:
    - Each post must be complete and self-contained.
    - Start each post with "POST {{i}}:" (e.g., POST 1:, POST 2:).
    - Use short paragraphs, emojis where relevant, and end with a call-to-action. 
    - No splitting of one post into multiple outputs.
    - Tone: {tone}
    - Audience: {audience}

    Outlines:
    {outlines}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional LinkedIn ghostwriter."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9
    )
    return response.choices[0].message.content


def download_button(content, filename, label="Download"):
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{label}</a>'
    return href


def copy_button(content, key):
    button_id = f"copy-btn-{key}"
    textarea_id = f"copy-text-{key}"
    html_code = f"""
    <textarea id="{textarea_id}" style="display:none;">{content}</textarea>
    <button id="{button_id}" style="
        background-color:#0073b1;
        color:white;
        border:none;
        padding:8px 12px;
        border-radius:6px;
        cursor:pointer;
        margin-top:6px;">
        📋 Copy to Clipboard
    </button>
    <script>
    const btn{key} = document.getElementById("{button_id}");
    btn{key}.onclick = function() {{
        const text = document.getElementById("{textarea_id}").value;
        navigator.clipboard.writeText(text);
        btn{key}.innerText = "✅ Copied!";
        setTimeout(() => btn{key}.innerText = "📋 Copy to Clipboard", 2000);
    }}
    </script>
    """
    return components.html(html_code, height=80)

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="LinkedIn Post Agent", layout="centered")

st.title("🤖 LinkedIn Post Generator (Agentic AI)")
st.write("Generate engaging, audience-focused LinkedIn posts in seconds.")

topic = st.text_input("💡 Topic", placeholder="e.g., AI in Healthcare")
tone = st.selectbox("🎭 Tone", ["Professional", "Conversational", "Inspirational", "Storytelling"])
audience = st.text_input("🎯 Target Audience", placeholder="e.g., startup founders, data scientists")
n_posts = st.slider("📌 Number of Posts", 1, 5, 3)

if st.button("🚀 Generate Posts"):
    with st.spinner("Crafting LinkedIn posts..."):
        outlines = generate_outlines(topic, tone, audience, n_posts)
        posts = expand_outlines_to_posts(outlines, tone, audience, n_posts)

        st.subheader("✨ Generated LinkedIn Posts")

        # Split cleanly on "POST {i}:" markers
        posts_list = re.split(r"POST\s+\d+:", posts.strip(), flags=re.IGNORECASE)
        posts_list = [p.strip() for p in posts_list if p.strip()]

        for i, post in enumerate(posts_list, start=1):
            st.markdown(f"---\n\n### Post {i}\n\n{post}")
            st.markdown(download_button(post, f"linkedin_post_{i}.txt", "💾 Download"), unsafe_allow_html=True)
            copy_button(post, key=str(uuid.uuid4()))
