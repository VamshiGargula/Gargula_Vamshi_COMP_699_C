# Task Automator Lab

A comprehensive low-code/no-code automation platform designed to streamline scripting and workflow management for developers, IT professionals, and DevOps teams. This system transforms plain English task descriptions or visual drag-and-drop designs into production-ready Python scripts, complete with visualization, simulation, optimization, and collaboration features.

## Project Overview

Task Automator Lab addresses the need for an integrated tool that bridges business process modeling and executable automation. It enables users to:

- Define tasks via natural language or a visual step-builder interface.
- Visualize workflows as interactive flowcharts with conditional logic, loops, and branching.
- Simulate executions using mock datasets, local files, or configuration files in a safe, isolated environment.
- Generate robust Python scripts with built-in logging, error handling, retries, and modular structure.
- Optimize workflows with best-practice suggestions, bottleneck analysis, and alternative script variants.
- Support team collaboration through version tracking, comments, documentation, and Git integration.

The platform is built with Streamlit for a responsive UI, ensuring seamless interaction between task parsing, visualization, simulation, and code export modules.

## Business Value

- **Time Savings**: Reduces repetitive scripting by 20–50 hours per developer per month.
- **Error Reduction**: Minimizes runtime errors in automations by 30–60%.
- **Efficiency Gains**: Improves workflow performance by 20–40% through simulation and optimization.
- **Collaboration**: Enhances maintainability and team productivity by 50–70% with visual aids and version control.

## Key Features

### Task Input & Design
- Plain English task entry with automatic script drafting.
- Drag-and-drop visual builder for workflow construction.
- Support for conditional logic, loops (for/while), retries, and decision points.

### Visualization
- Real-time interactive flowcharts reflecting workflow structure.
- Dynamic updates for step reordering, branching, and annotations.

### Simulation & Testing
- Upload mock data (CSV, Excel, JSON, TXT) for scenario testing.
- Isolated execution environment with detailed logs, success/failure tracking, and step-level debugging.
- Rerun failed steps and export structured test reports.

### Script Generation & Optimization
- Auto-generated Python scripts compliant with PEP8, including try/except, logging, and comments.
- Embedded code editor for customizations, reusable functions, and parameter definitions.
- Recommendation engine for missing steps, optimizations, and best practices.
- Safe mutation to propose alternative versions with performance comparisons.

### Collaboration & Management
- User roles: Developer, Analyst, Tester, Team Lead with tailored permissions.
- Version history, diff comparisons, and rollback capabilities.
- Git integration for direct script export with commit messages.
- Project grouping, task assignment, deadlines, and activity tracking.
- Secure authentication with session management and password recovery.

### Data Handling
- Multi-format support: CSV, Excel, JSON, TXT, folder/file operations.
- Variable management with typed inputs/outputs (string, integer, JSON).

## System Requirements

### Functional Requirements
Detailed in the project proposal under Section 3.1 (User Requirements). Covers capabilities for each role:
- **Developer**: Script customization, loops, retries, exceptions, templates, Git export.
- **Analyst**: Visual design, conditional paths, config-based simulation, grouping.
- **Tester**: Mock data upload, isolated runs, logging, result exports.
- **Team Lead**: Version control, user management, reviews, reporting.

### Non-Functional Requirements
- **Performance**: Responsive UI with real-time updates; simulation completion in <5 seconds for average workflows.
- **Usability**: Intuitive interfaces; syntax checking; PEP8 compliance.
- **Security**: Sandboxed testing; secure auth; no data corruption in simulations.
- **Reliability**: Error handling in generated code; audit logs for all actions.
- **Scalability**: Handle complex workflows with branching/loops; support team-scale usage.

## Use Cases & Models
Refer to the full proposal for:
- Use Case Descriptions (Section 4)
- Diagrams: Use Case, Activity, Sequence, Class, Object (Section 5)

## Technical Constraints
- Complex logic parsing for branching, loops, and conditions.
- Dynamic visualization and real-time optimization scoring.
- Seamless module integration within Streamlit.
- Safe dynamic code execution without risking mock data integrity.

## Getting Started
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt` (includes Streamlit, necessary libraries for data handling, visualization, and code generation).
3. Run the app: `streamlit run app.py`.
4. Create an account via the login interface to access role-based features.

## Development Status
This repository contains the system proposal document and initial implementation scaffolding. Core modules (task parser, flowchart generator, simulator, optimizer) are under active development.

## Contributing
Contributions welcome via pull requests. Focus areas:
- Enhance natural language processing for task input.
- Improve visualization library integration.
- Add more data format handlers.
- Expand recommendation engine algorithms.

Follow the code style guidelines and include tests for new features.


For issues or feature requests, open a GitHub issue.
