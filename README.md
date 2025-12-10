# MedMiner

MedMiner leverages large language models (LLMs) and Langchain/Langgraph workflows to extract and analyze data from medical documents efficiently.

## Getting Started

> [!NOTE]
> Use the included dev container to automatically install all the necessary dev tools and dependencies.

1. **Clone the repository:**
    ```sh
    git clone https://github.com/aidh-ms/MedMiner.git
    cd MedMiner
    ```

2. **Open the project in Visual Studio Code:**
    ```sh
    code .
    ```

3. **(Optionally) Enable Snowstorm server**

to enable the snowstorm server for snomedct go to the `.env` file in the `.devcontainer` folder and add the following line.

```bash
COMPOSE_PROFILES=dev
```

4. **Reopen in Container:**
    - Press `F1` to open the command palette.
    - Type `Remote-Containers: Reopen in Container` and select it.
    - VS Code will build the Docker container defined in the `.devcontainer` folder and open the project inside the container.

## ToDo's

- [ ] more workflows
    - [ ] procedures
    - [ ] diagnoses
- [ ] ui
- [ ] cli
- [ ] logging & metrics
- [ ] unit tests & pre commit
