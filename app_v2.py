from mcp import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
import asyncio
import streamlit as st
import urllib3
import logging
from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from mcp.client.sse import sse_client
from dotenv import load_dotenv
import httpx
from langchain_mcp_adapters.client import MultiServerMCPClient
# Configure logging
logging.basicConfig(level=logging.INFO)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()




async def get_final_answer(agent_response: str) -> str:
    ai_messages = [message for message in agent_response.get("messages", []) if "AIMessage" in str(type(message))]
    result = ai_messages[-1]
    return result.content

async def chat_page():
    client = MultiServerMCPClient(
        {
            "netbox": {
                "url": "http://192.168.221.45:8002/sse",
                "transport": "sse",
            },
            "checkmk": {
                "url": "http://192.168.221.45:8000/sse",
                "transport": "sse",
            }
        }
    )
    tools = await client.get_tools()
    # Fetch a specific prompt from MCP
    
    prompt_netbox = await client.get_prompt("netbox" , "netbox-mcp")
    prompt_checkmk = await client.get_prompt("checkmk" , "checkmk_prompt")


    prompt_netbox_str = prompt_netbox[0].content
    prompt_checkmk_str = prompt_checkmk[0].content
    agent = create_react_agent(
        model=llm_model,
        tools=tools,
        prompt= prompt_netbox_str + prompt_checkmk_str,
    )
    
    # streamlit
    st.title("Trợ lý CNTT")
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
    asyncio.run(chat_page())