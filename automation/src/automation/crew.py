import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task, LLM # Import LLM from crewai
from crewai.project import CrewBase, agent, crew, task

# Import custom tools
from automation.tools import PDFContentReaderTool, PDFModifyAndSaveTool

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

# Configure the Gemini LLM using crewai.LLM
gemini_api_key = os.getenv("GEMINI_API_KEY")
# Use the model name specified in the .env file or the user's last request
model_name = os.getenv("MODEL", "gemini/gemini-2.5-pro-exp-03-25") # Use the specific model requested

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Instantiate crewai.LLM for Gemini
llm = LLM(
    model=model_name,
    temperature=0.7, # As requested in feedback
    api_key=gemini_api_key # Use the API key directly
)


# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


@CrewBase
class Automation():
    """Automation crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def pdf_analyzer(self) -> Agent:
        """Agent responsible for analyzing the PDF content and user request."""
        return Agent(
            config=self.agents_config['pdf_analyzer'], # Will update this in agents.yaml
            tools=[PDFContentReaderTool()], # This agent reads the PDF
            llm=llm,
            verbose=True,
            allow_delegation=False # Analyzer focuses on reading and planning
        )

    @agent
    def pdf_modifier(self) -> Agent:
        """Agent responsible for applying modifications to the PDF."""
        return Agent(
            config=self.agents_config['pdf_modifier'], # Will update this in agents.yaml
            tools=[PDFModifyAndSaveTool()], # This agent modifies the PDF
            llm=llm,
            verbose=True,
            allow_delegation=False # Modifier focuses on executing the plan
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def analyze_pdf_task(self) -> Task:
        """Task to analyze the PDF and the user's modification request."""
        return Task(
            config=self.tasks_config['analyze_pdf_task'], # Will update this in tasks.yaml
            agent=self.pdf_analyzer() # Assign to the analyzer agent
        )

    @task
    def modify_pdf_task(self) -> Task:
        """Task to perform the modification based on the analysis."""
        # Define the output path for the modified PDF
        output_pdf_filename = "modified_output.pdf"
        # Save the output file in the same directory as this script (src/automation/)
        output_pdf_path = os.path.join(os.path.dirname(__file__), output_pdf_filename)

        return Task(
            config=self.tasks_config['modify_pdf_task'], # Will update this in tasks.yaml
            agent=self.pdf_modifier(), # Assign to the modifier agent
            context=[self.analyze_pdf_task()] # Depends on the analysis task
            # Removed output_file parameter, tool handles saving based on input path now
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Automation crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
