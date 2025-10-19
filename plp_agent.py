# plp_agent.py
from langchain.agents import Tool, create_react_agent, AgentExecutor
from langchain import hub
from plp_engine import PLPSystem

def create_agent_executor():
    """
    Creates a ReAct agent with access to the RAG retriever as a tool.
    """
    # Load your existing PLP system to access its components
    plp = PLPSystem()
    retriever = plp.vectordb.as_retriever()
    llm = plp.llm # Use the same LLM from your main system

    # 1. Define a Tool
    retriever_tool = Tool(
        name="Weight_Loss_Science_Knowledge_Base",
        func=retriever.invoke, # Use invoke for the latest LangChain versions
        description="Searches and returns relevant documents about the science of weight loss, nutrition, and exercise."
    )
    tools = [retriever_tool]

    # 2. Get the Agent Prompt
    prompt = hub.pull("hwchase17/react")

    # 3. Create the Agent
    agent = create_react_agent(llm, tools, prompt)

    # 4. Create the Agent Executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return agent_executor