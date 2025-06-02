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
import json
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
# Configure logging
logging.basicConfig(level=logging.INFO)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

llm_model = AzureAIChatCompletionsModel(
    )

async def get_final_answer(agent_response: str) -> str:
    ai_messages = [message for message in agent_response.get("messages", []) if "AIMessage" in str(type(message))]
    result = ai_messages[-1]
    return result.content

async def get_custom_fields():
    try:
        async with sse_client(url="http://192.168.221.54:8000/sse") as (read, wirte):
            async with  ClientSession(read, wirte) as session:
                await session.initialize()
                result = await session.call_tool("get_custom_fields", {"object_type": "custom-fields", "filters": {}  })
                return result
    except Exception as e:
        print(f"Error calling tool get_custom_fields: {str(e)}")
        return None
    
def build_prompt_custom_feild(custom_feilds):
    """
    Prompt mô tả các custom field của Netbox từ danh sách dict.
    custom_feilds: list các dict custom field.
    """
    if not custom_feilds:
        return "Không có custom field nào trong Netbox."

    prompt = "Dưới đây là danh sách các custom field hiện có trong Netbox:\n"
    for idx, field in enumerate(custom_feilds, 1):
        name = field.get("name", "Không rõ tên")
        description = field.get("description", "")
        object_types = ", ".join(field.get("object_types", []))
        prompt += f"{idx}. Tên: {name}\n"
        if object_types:
            prompt += f"   Áp dụng cho: {object_types}\n"
        if description:
            prompt += f"   Mô tả: {description}\n"
    return prompt

async def chat_page():
    client = MultiServerMCPClient(
        {
            "netbox": {
                "url": "http://192.168.221.54:8000/sse",
                "transport": "sse",
            },
            "checkmk": {
                "url": "http://192.168.221.54:8002/sse",
                "transport": "sse",
            }
        }
    )
    tools = await client.get_tools()
    
    # get all custom fields from netbox
    custom_fields = await get_custom_fields()
    custom_fields_json = []
    for item in custom_fields.content:
        try:
            # Parse the text content as JSON
            json_obj = json.loads(item.text)
            # Select only the required fields
            filtered = {
                "id": json_obj["id"],
                "name": json_obj["name"],
                "object_types": json_obj["object_types"],
                "description": json_obj["description"]
            }
            custom_fields_json.append(filtered)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")

    prompt_custom_field = build_prompt_custom_feild(custom_fields_json)

    # get netbox_prompt_get_count_objects from MCP
    netbox_prompt_get_count_objects = await client.get_prompt("netbox", "netbox_prompt_get_count_objects")
    # Fetch a specific prompt from MCP
    prompt_netbox = await client.get_prompt("netbox" , "netbox-mcp")
    prompt_checkmk = await client.get_prompt("checkmk" , "checkmk_prompt")

    # get content of prompt
    prompt_netbox_str = prompt_netbox[0].content
    prompt_checkmk_str = prompt_checkmk[0].content
    prompt_netbox_count_objects = netbox_prompt_get_count_objects[0].content 

    # create agent
    agent = create_react_agent(
        model=llm_model,
        tools=tools,
        prompt= prompt_custom_field + prompt_netbox_str + prompt_checkmk_str + prompt_netbox_count_objects,
    )
    
    # streamlit
    st.title("Trợ lý CNTT")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Hiển thị lại toàn bộ lịch sử chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    if user_input := st.chat_input("Trợ lý Công nghệ thông tin tại MB sẽ giải đáp thắc mắc của bạn! Hãy gõ câu hỏi vào đây."):
        # Add user input to chat history
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        try:
            logging.info(f"📝 User input: {user_input}")
            user_question = [user_input] + st.session_state.messages[-8:]
            # ✅ Use agent_executor to process user input
            response = await agent.ainvoke({
                "messages": user_question,
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