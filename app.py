import streamlit as st
from utils.rag_utils import retrieve_similar_documents
from models.llm import generate_llm
from utils.web_search import live_web_search, search_banking_news, get_current_repo_rate, search_banking_regulations
from utils.common_utils import cache

# Basic setup for the app
st.set_page_config(page_title="Banking Assistant Chatbot", page_icon="🏦", layout="wide")

st.markdown("""
    <h1 style='text-align: center; color: #2E4053;'>🏦 Banking Assistant Chatbot</h1>
    <p style='text-align: center; font-size: 18px;'>You can ask me questions about savings accounts, EMI, KYC, repo rate, NEFT/RTGS, CIBIL score and more – powered by Azure OpenAI + Banking Knowledge Base + Web Search</p>
""", unsafe_allow_html=True)

st.markdown("---")

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    mode = st.radio("📝 Response Style:", ["concise", "detailed"], horizontal=True)

with col2:
    enable_web_search = st.checkbox("🌐 Enable Web Search", value=False, help="Get real-time information from the web")

with col3:
    if st.button("🔄 Refresh Data"):
        try:
            with st.spinner("🔄 Updating banking data..."):
                # Import and run the scraper
                import subprocess
                import sys
                
                # Run the met_scraper.py script
                result = subprocess.run([sys.executable, "data/met_scraper.py"], 
                                      capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    st.success("✅ Banking data updated successfully!")
                    st.info("New data has been merged with existing knowledge base")
                    
                    # Ask user if they want to rebuild the index
                    if st.button("🔄 Rebuild Search Index (Recommended)"):
                        try:
                            with st.spinner("🔧 Rebuilding search index..."):
                                # Run the build_faiss_index.py script
                                index_result = subprocess.run([sys.executable, "build_faiss_index.py"], 
                                                           capture_output=True, text=True, timeout=120)
                                
                                if index_result.returncode == 0:
                                    st.success("✅ Search index rebuilt successfully!")
                                    st.info("Your assistant now has access to the latest data")
                                else:
                                    st.warning("⚠️ Index rebuild completed with some issues")
                                    st.text(f"Output: {index_result.stdout}")
                                    if index_result.stderr:
                                        st.text(f"Errors: {index_result.stderr}")
                        except subprocess.TimeoutExpired:
                            st.error("⏰ Index rebuild timed out. Please try again.")
                        except Exception as e:
                            st.error(f"❌ Error rebuilding index: {str(e)}")
                            st.info("You can also run manually: python3 build_faiss_index.py")
                else:
                    st.warning("⚠️ Data update completed with some issues")
                    st.text(f"Output: {result.stdout}")
                    if result.stderr:
                        st.text(f"Errors: {result.stderr}")
                        
        except subprocess.TimeoutExpired:
            st.error("⏰ Data update timed out. Please try again.")
        except Exception as e:
            st.error(f"❌ Error updating data: {str(e)}")
            st.info("You can also run manually: python3 data/met_scraper.py")

st.info("""\
**Try questions like:**
- How can I open a savings account?
- How can I check my CIBIL score?
- What is the current RBI repo rate?
- What's the process to apply for an education loan?

Use **Concise** for short answers or **Detailed** for in-depth explanations.
**Enable Web Search** for real-time information.
""")

st.markdown("---")

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for entry in st.session_state.chat_history:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])

# Chat input
if query := st.chat_input("🔍 Ask a banking question:"):
    st.session_state.chat_history.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.spinner("🔍 Searching knowledge base and generating reply..."):
        try:
            # Check cache first for improved performance
            cache_key = f"query_{hash(query)}"
            cached_response = cache.get(cache_key)
            if cached_response:
                st.info("📋 Retrieved response from cache for faster delivery")
                st.session_state.chat_history.append({"role": "assistant", "content": cached_response})
                with st.chat_message("assistant"):
                    st.markdown(cached_response)
            else:
                # Get context from knowledge base (only if not cached)
                context_chunks = retrieve_similar_documents(query, top_k=5)
                context = "\n---\n".join(context_chunks)
            
                # Add web search if enabled
                web_context = ""
                if enable_web_search:
                    with st.spinner("🌐 Searching web for current information..."):
                        st.info("🔍 **Web Search Active** - Fetching real-time information...")
                        
                        # Enhanced query type detection for maximum performance
                        query_lower = query.lower()
                        
                        # Repo rate queries
                        if any(term in query_lower for term in ["repo rate", "rbi rate", "monetary policy", "interest rate"]):
                            st.info("📊 Searching for current RBI repo rate...")
                            web_context = f"\n\nCurrent Information:\n{get_current_repo_rate()}"
                        
                        # News queries - expanded detection
                        elif any(term in query_lower for term in ["news", "latest", "recent", "update", "current", "today", "happening", "developments", "announcements"]):
                            st.info("📰 Searching for latest banking news...")
                            web_context = f"\n\nLatest News:\n{search_banking_news()}"
                        
                        # Regulation queries - expanded detection
                        elif any(term in query_lower for term in ["regulation", "policy", "guideline", "rule", "compliance", "requirement"]):
                            st.info("📋 Searching for banking regulations...")
                            web_context = f"\n\nRegulation Information:\n{search_banking_regulations(query)}"
                        
                        # Banking-specific queries that should use web search
                        elif any(term in query_lower for term in ["current", "today", "latest", "new", "recent", "what is", "how to", "where to", "when", "which bank"]):
                            st.info("🌐 Performing targeted web search...")
                            web_context = f"\n\nWeb Search Results:\n{live_web_search(query)}"
                        
                        # Default web search for all other queries
                        else:
                            st.info("🌐 Performing comprehensive web search...")
                            web_context = f"\n\nWeb Search Results:\n{live_web_search(query)}"
                        
                        if web_context and "error" not in web_context.lower():
                            st.success("✅ Web search completed successfully!")
                            # Debug: Show what was found
                            if len(web_context) > 100:
                                st.info(f"📊 Found {len(web_context)} characters of web search results")
                        else:
                            st.warning("⚠️ Web search completed with limited results")

                prompt = f"""
                You are an expert Indian banking assistant. Use the context below to answer the user's question.
                
                CRITICAL INSTRUCTIONS:
                - If web search results are provided, they are the PRIMARY and MOST IMPORTANT source
                - Web search results contain real-time, current information that should be prioritized
                - Always start your response with the most current information from web search
                - Combine web search results with knowledge base context when relevant
                - Provide specific, actionable information from the web search results
                - Always acknowledge the source of information when using web search results
                
                ---
                Knowledge Base Context (Historical/General Information):
                {context}
                
                {web_context}
                ---
                
                Question: {query}
                
                Response Guidelines:
                1. START with web search results if available - they contain current information
                2. Use specific details, numbers, and facts from web search results
                3. If web search found real-time news, rates, or updates, mention them prominently
                4. Combine with knowledge base context only when it adds value
                5. Always cite sources: "According to [source]..." or "Based on [source]..."
                6. If web search found current rates or news, lead with that information
                7. Provide actionable insights based on the current information found
                """

                response = generate_llm(prompt, mode=mode)

                # Cache the response for future use
                cache.set(cache_key, response)

                st.session_state.chat_history.append({"role": "assistant", "content": response})

                with st.chat_message("assistant"):
                    st.markdown(response)

        except Exception as e:
            st.error(f"Error: {str(e)}")
