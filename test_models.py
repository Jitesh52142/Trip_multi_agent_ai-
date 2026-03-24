import os
from crewai import Agent, Task, Crew, Process



def test_model(model_name):
    print(f"\n--- Testing model: {model_name} ---")
    try:
        agent = Agent(
            role="Test",
            goal="Test",
            backstory="Test",
            llm=model_name,
            verbose=False
        )
        task = Task(description="Say exactly 'hello'", expected_output="The word hello", agent=agent)
        crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
        result = crew.kickoff()
        print("SUCCESS:", str(result))
    except Exception as e:
        print("FAILED:", str(e))

models = [
    "gemini/gemini-1.5-flash-latest",
    "gemini/gemini-pro",
    "gemini/gemini-2.0-flash",
    "gemini/gemini-1.5-pro-latest",
]

for m in models:
    test_model(m)
