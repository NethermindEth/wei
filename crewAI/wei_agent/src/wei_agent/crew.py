import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our custom tools
from wei_agent.tools import SerperSearchTool
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class WeiAgent():
    """WeiAgent crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def planner(self) -> Agent:
        return Agent(
            config=self.agents_config['planner'], # type: ignore[index]
            verbose=True
        )

    @agent
    def proposal_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['proposal_researcher'], # type: ignore[index]
            verbose=True
        )

    @agent
    def protocol_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['protocol_researcher'], # type: ignore[index]
            verbose=True
        )

    @agent
    def report_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['report_analyzer'], # type: ignore[index]
            verbose=True
        )

    @agent
    def investigator(self) -> Agent:
        return Agent(
            config=self.agents_config['investigator'], # type: ignore[index]
            verbose=True
        )

    @agent
    def evaluator(self) -> Agent:
        return Agent(
            config=self.agents_config['evaluator'], # type: ignore[index]
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['planning_task'], # type: ignore[index]
        )

    @task
    def proposal_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['proposal_research_task'], # type: ignore[index]
        )

    @task
    def protocol_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['protocol_research_task'], # type: ignore[index]
        )

    @task
    def report_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['report_analysis_task'], # type: ignore[index]
        )

    @task
    def investigation_task(self) -> Task:
        return Task(
            config=self.tasks_config['investigation_task'], # type: ignore[index]
        )

    @task
    def evaluation_task(self) -> Task:
        return Task(
            config=self.tasks_config['evaluation_task'], # type: ignore[index]
            output_file='governance_evaluation.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the WeiAgent crew for Ethereum governance proposal analysis"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        # Get the model from environment variables or use a default
        model = os.environ.get("MODEL", "claude-3-5-sonnet-20240620")
        
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.hierarchical, # Using hierarchical process for complex governance analysis
            verbose=True,
            manager_llm=model, # Using the model specified in environment variables
        )
