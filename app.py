from mcp import ClientSession, StdioServerParameters
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
import asyncio
import streamlit as st
import urllib3
import logging
from mcp.client.sse import sse_client
import os
from langchain_openai import ChatOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def get_final_answer(agent_response: str) -> str:
    ai_messages = [message for message in agent_response.get("messages", []) if "AIMessage" in str(type(message))]
    result = ai_messages[-1]
    return result.content

def configure_page():
    st.title("NetBox Configuration")
    openai_key = st.text_input("OpenAI API Key", type="password", placeholder="Your OpenAI API Key")
    mcp_server_url = st.text_input("MCP Server URL", placeholder="http://localhost:8000/sse")

    if st.button("Save and Continue"):
        if not mcp_server_url or not openai_key:
            st.error("All fields are required.")
        else:
            st.session_state['OPENAI_API_KEY'] = openai_key
            st.session_state['MCP_SERVER_URL'] = mcp_server_url

            os.environ['OPENAI_API_KEY'] = openai_key
            os.environ['MCP_SERVER_URL'] = mcp_server_url
            st.success("Configuration saved! Redirecting to chat...")
            st.session_state['page'] = "chat"

async def chat_page():
    mcp_server_url = st.session_state['MCP_SERVER_URL']
    openai_api_key = st.session_state['OPENAI_API_KEY']
    async with sse_client(url=mcp_server_url) as (read, wirte):
        async with  ClientSession(read, wirte) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)

            llm_model = ChatOpenAI(model_name="gpt-4o", openai_api_key=openai_api_key)
            # Fetch a specific prompt from MCP
            prompt_name = "netbox_mcp" 
            fetched_prompt = await session.get_prompt(prompt_name)
            prompt = fetched_prompt.messages[0].content.text
            agent = create_react_agent(
                model=llm_model,
                tools=tools,
                prompt=prompt,
            )
            
            # streamlit
            st.title("Chat with AI Agent")
            if "messages" not in st.session_state:
                st.session_state.messages = []
            
            # Hiển thị lại toàn bộ lịch sử chat
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    
            if user_input := st.chat_input("Ask AI Agent a question"):
                # Add user input to chat history
                with st.chat_message("user"):
                    st.markdown(user_input)
                st.session_state.messages.append({"role": "user", "content": user_input})

                try:
                    logging.info(f"📝 User input: {user_input}")

                    # ✅ Use agent_executor to process user input
                    response = await agent.ainvoke({
                        "messages": user_input,
                    })

                    logging.info(f"🤖 Agent response: {response}")
                    
                    # Extract and display the final answer
                    final_answer = await get_final_answer(response)

                    with st.chat_message("assistant"):
                        st.markdown(final_answer)
                    # Update chat history
                    st.session_state.messages.append({"role": "assistant", "content": final_answer})

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if 'page' not in st.session_state:
        st.session_state['page'] = "configure"

    if st.session_state['page'] == "configure":
        configure_page()
    elif st.session_state['page'] == "chat":
        asyncio.run(chat_page())