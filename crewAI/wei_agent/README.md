# WeiAgent Crew

Welcome to the WeiAgent Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your API keys into the `.env` file**

```
ANTHROPIC_API_KEY=your_anthropic_api_key
MODEL=claude-3-5-sonnet-20240620
SERPER_API_KEY=your_serper_api_key
```

- Modify `src/wei_agent/config/agents.yaml` to define your agents
- Modify `src/wei_agent/config/tasks.yaml` to define your tasks
- Modify `src/wei_agent/crew.py` to add your own logic, tools and specific args
- Modify `src/wei_agent/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the wei-agent Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The wei-agent Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Available Tools

### SerperSearchTool

The SerperSearchTool enables agents to search the internet for up-to-date information using the Serper API. This tool is particularly useful for research tasks that require current information about topics, news, events, or any other online data.

#### Usage

The tool is already configured for the following agents:
- Proposal Research Specialist
- Ethereum Protocol Expert
- Proposal Intent Investigator

#### Testing the Search Tool

You can test the SerperSearchTool directly using the provided example script:

```bash
python -m wei_agent.examples.serper_search_example "your search query"
```

Make sure your `SERPER_API_KEY` is set in the `.env` file before running the example.

## Support

For support, questions, or feedback regarding the WeiAgent Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
