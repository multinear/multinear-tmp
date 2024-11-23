# Multinear: A Platform for Developing and Testing GenAI Applications

Multinear is a platform designed to aid in the development of Generative AI applications by running experiments, measuring results, and providing insights. It allows developers to run their GenAI-powered workflows with various configurations, collect metadata, and analyze outcomes to build reliable and robust applications.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Project Initialization](#project-initialization)
  - [Running the Platform](#running-the-platform)
- [Usage](#usage)
  - [Defining Your Task Runner](#defining-your-task-runner)
  - [Configuring Tasks and Evaluations](#configuring-tasks-and-evaluations)
  - [Running Experiments](#running-experiments)
- [Analyzing Results](#analyzing-results)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Experiment Workflow**: Run experiments with different configurations of models, prompts, datasets, and business logic.
- **Result Tracking**: Automatically saves metadata and results of each experiment for analysis.
- **Regression Detection**: Identify regressions when new changes impact previously working cases.
- **Evaluation Framework**: Supports various evaluation methods including direct comparison, LLM-as-a-judge, and human evaluation.
- **Comprehensive Insights**: Compare results across runs, visualize performance trends, and understand the impact of changes.
- **Security Testing**: Evaluate your application against malicious inputs, guardrails, and safety measures.

## Getting Started

### Installation

To install Multinear and its dependencies, run:

```bash
git clone https://github.com/multinear/multinear.git
cd multinear
make install
```

This will install the required Python packages.

### Project Initialization

Initialize a new Multinear project in your desired directory:

```bash
multinear init
```

You will be prompted to enter your project details:

- **Project name**: The name of your project.
- **Project ID**: A URL-friendly identifier for your project (default provided).
- **Project description**: A brief description of your project.

This command creates a `.multinear` directory containing your project configuration.

### Running the Platform

Start the Multinear web server:

```bash
multinear web
```

By default, the server runs on `http://127.0.0.1:8000`. You can access the frontend interface in your browser to interact with the platform.

For development mode with auto-reload on file changes:

```bash
multinear web_dev
```

## Usage

### Defining Your Task Runner

Create a `task_runner.py` in the `.multinear` directory of your project. This file defines the `run_task(input)` function, which contains the logic for processing each task.

Example `task_runner.py`:

```python
def run_task(input):
    # Your GenAI-powered application logic here
    output = my_application.process(input)
    details = {'model': 'gpt-4o'}
    return {'output': output, 'details': details}
```

### Configuring Tasks and Evaluations

Define your tasks and evaluation criteria in `.multinear/config.yaml`.

Example `config.yaml`:

```yaml
project:
  id: my-genai-project
  name: My GenAI Project
  description: Experimenting with GenAI models

tasks:
  - id: task1
    input: "Input data for task 1"
    min_score: 0.8
    checklist:
      - "The output should be in English."
      - "The response should be polite."
  - id: task2
    input: "Input data for task 2"
    min_score: 1.0
    checklist:
      - "The output should include at least two examples."
      - "The response should be less than 500 words."
```

### Running Experiments

Start an experiment by running a new job:

```bash
curl -X POST http://127.0.0.1:8000/api/jobs/my-genai-project
```

Or use the frontend interface to initiate a run.

## Analyzing Results

Once the experiment run is complete, you can analyze the results via the frontend dashboard. The platform provides:

- **Run Summaries**: Overview of each experiment run, including total tasks, passed/failed counts, and overall score.
- **Detailed Reports**: Drill down into individual tasks to see input, output, logs, and evaluation details.
- **Trend Analysis**: Compare results across runs to identify improvements or regressions.
- **Filter and Search**: Find specific tasks or runs based on criteria such as challenge ID, date, or status.

## Architecture

Multinear consists of several components:

- **CLI Tool (`cli.py`)**: Command-line interface for initializing projects and starting the web server.
- **Web Server (`main.py`)**: A FastAPI application serving API endpoints and static frontend files.
- **Engine (`engine/` Directory)**:
  - **Run Management (`run.py`)**: Handles execution of tasks and evaluation.
  - **Storage (`storage.py`)**: Manages data models and database operations using SQLAlchemy.
  - **Evaluation (`evaluate.py`, `checklist.py`)**: Provides evaluation mechanisms for task outputs.
- **API (`api/` Directory)**: Defines API routes and schemas for interaction with the frontend and external tools.
- **Utilities (`utils/capture.py`)**: Captures task execution output and logs.
- **Frontend**: A Svelte-based interface for interacting with the platform (located in `multinear/frontend/`).

## Contributing

We welcome contributions to Multinear! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Make your changes with clear commit messages.
4. Submit a pull request to the `main` branch.

Please ensure that your code adheres to the project's coding standards and passes all tests.

## License

Multinear is released under the [MIT License](LICENSE). You are free to use, modify, and distribute this software as per the terms of the license.
