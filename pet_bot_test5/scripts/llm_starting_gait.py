#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor
from std_msgs.msg import Float64MultiArray
import threading
import os

from starting_gait import PetBotCommander
from starting_gait import POSE_SIT,POSE_CROUCH,POSE_STAND

from forward_gait import HybridIKTrot

from backward_gait import HybridIKTrot_Backward

from sideward_gait import SideWalk

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
    
    @tool 
    def llm_Forward(steps:int):
        """make the quadruped bot move forward"""

        steps = max(1, min(steps, 15))

        gait_forward = HybridIKTrot(steps)

        executor = SingleThreadedExecutor()
        executor.add_node(gait_forward)

        while rclpy.ok() and not gait_forward.timer.is_canceled():
            executor.spin_once(timeout_sec=0.1)

        executor.remove_node(gait_forward)
        gait_forward.destroy_node()

        return f"Robot moved forward {steps} steps"

    @tool 
    def llm_Backward(steps:int):
        """make the quadruped bot move backward"""

        steps = max(1, min(steps, 15))

        gait_backward = HybridIKTrot_Backward(steps)

        executor = SingleThreadedExecutor()
        executor.add_node(gait_backward)

        while rclpy.ok() and not gait_backward.timer.is_canceled():
            executor.spin_once(timeout_sec=0.1)

        executor.remove_node(gait_backward)
        gait_backward.destroy_node()

        return f"Robot moved backward {steps} steps"


    @tool 
    def llm_Sideward(steps:int):
        """make the quadruped bot move sideward"""

        steps = max(1, min(steps, 15))

        gait_sideward = SideWalk(steps)

        executor = SingleThreadedExecutor()
        executor.add_node(gait_sideward)

        while rclpy.ok() and not gait_sideward.timer.is_canceled():
            executor.spin_once(timeout_sec=0.1)

        executor.remove_node(gait_sideward)
        gait_sideward.destroy_node()

        return f"Robot moved sideward {steps} steps"
    
    return [llm_Crouch,llm_Sit,llm_Stand,llm_Forward,llm_Backward,llm_Sideward]

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
        """You control a quadruped robot.

        Available actions:
        - sit
        - stand
        - crouch
        - move forward
        - move backward
        - move sideways

        When moving the robot, you must decide how many steps are required
        to achieve the user's request and pass that number to the tool.

        Remember the right ward motion in sideward gait is not working so you can execute only the leftward motion
        Remember that the sideward motion actually makes the bot turn in left or right direction.

        You are intelligent. Use your intelligence to the task.

        If told to move in a specific shape do that using all the appropriate command available to you.

        If given a command out of your capability politely explain the user about it.

        Guidelines:
        - small movement → 2 steps
        - medium movement → 5 steps
        - long movement → 10 steps

        Remember steps must not be greater than 15

        Example:
        User: move forward a little
        Action: llm_Forward
        Action Input: 2

        User: move forward a long distance
        Action Input: 10"""
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

    print("Quadruped LLM locomotion controller started")

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