#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import threading
import os

from starting_gait import PetBotCommander
from starting_gait import POSE_SIT,POSE_CROUCH,POSE_STAND

from langchain.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


def make_tools(node):
    @tool
    def llm_Sit():
        """make the quadrupped bot sit"""
        node.smooth_move("SIT",POSE_SIT)
        return "Bot is sitting"
    
    @tool
    def llm_Stand():
        """make the quadrupped bot stand"""
        node.smooth_move("STAND",POSE_STAND)
        return "Bot is standing"
    
    @tool
    def llm_Crouch():
        """make the quadrupped bot crouch"""
        node.smooth_move("CROUCH",POSE_CROUCH)
        return "Bot is crouching"
    
    return [llm_Crouch,llm_Sit,llm_Stand]

def run_llm(node):

    tools = make_tools(node)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an AI controller for a quadruped robot.\n"
            "The robot can perform three actions using tools:\n"
            "- sit\n"
            "- stand\n"
            "- crouch\n\n"
            "If the user asks for one of these actions, call the correct tool.\n"
            "If the request is unrelated to robot movement or impossible, explain politely that the robot cannot perform that action."
        ),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True
    )

    print("\n Quadruped LLM Controller Ready\n")

    while True:

        user_input = input(">> ")

        if user_input.lower() in ["exit", "quit"]:
            break

        result = agent_executor.invoke({
            "input": user_input
        })
        print(result["output"])


def main():
    rclpy.init()
    node = PetBotCommander()

    spin_thread = threading.Thread(
        target=rclpy.spin,
        args=(node,),
        daemon=True
    )
    spin_thread.start()

    try:
        run_llm(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()



if __name__=='__main__':
    main()