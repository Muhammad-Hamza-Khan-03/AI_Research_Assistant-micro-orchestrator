# AI Research Assistant — LLM Research & Analysis Orchestration

An experimental **FastAPI** service that connects web search, LLM summarisation, stored knowledge retrieval, and a **LangGraph** analysis workflow.

The project explores how an AI application can coordinate an API, relational metadata, embeddings, artifact storage, and caching. It is a prototype for technical review; the repository does not establish a production deployment or benchmark.

[Author portfolio](https://hamza-khan-portfolio.hamzakhan102003.chatgpt.site/) · [LinkedIn](https://www.linkedin.com/in/muhammadhamzakhan/)

## Implemented structure

| Component | Role |
|---|---|
| FastAPI routes | Research and analysis request/response schemas |
| LangChain + OpenAI | Research summaries and structured analysis |
| LangGraph | Validation, normalisation, embedding, retrieval, and synthesis stages |
| PostgreSQL + SQLAlchemy | Research metadata and summaries |
| MongoDB | Stored embedding records |
| Redis | Cached research and analysis responses |
| S3 | Raw research text artifacts |
| Tavily integration | Web search input for the research pipeline |

## Request paths

| Method | Route | Purpose |
|---|---|---|
| GET | / | Service identification response |
| POST | /chain/research | Search for a topic, summarise it, and store research artifacts |
| POST | /graph/analyze | Compare submitted text with stored related research |
| GET | /docs | FastAPI interactive API documentation |

Research input:

```json
{"topic": "Retrieval augmented generation evaluation"}
```

Analysis input:

```json
{"text": "The research text to compare with previously stored knowledge."}
```

These are request examples, not recorded successful responses.

## Repository map

- `main.py`: application setup and route registration.
- `routers/`: HTTP adapters.
- `schemas/`: request and response models.
- `services/research_service.py`: search → summary → persistence workflow.
- `services/analyze_service.py`: LangGraph analysis stages.
- `tools/`: search, embeddings, retrieval, caching, and S3 helpers.
- `models/`: research and embedding models.
- `test/database_test/`: service connectivity scripts.

## Local setup

Create a Python virtual environment and install the repository dependencies:

```bash
git clone https://github.com/Muhammad-Hamza-Khan-03/AI_Research_Assistant-micro-orchestrator.git
cd AI_Research_Assistant-micro-orchestrator
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configure local environment values in an uncommitted `.env` file:

| Variable | Purpose |
|---|---|
| POSTGRES_URI | SQLAlchemy PostgreSQL connection |
| MONGO_URI | MongoDB connection |
| MONGO_DB_NAME | Database containing embedding records |
| REDIS_URI | Redis connection |
| OPENAI_API_KEY | OpenAI model and embedding requests |
| TAVILY_API_KEY | Tavily web search |
| AWS_ACCESS_KEY / AWS_SECRET_KEY | S3 credentials expected by the configuration |
| AWS_S3_BUCKET | Research artifact bucket |

Review `config.py` and the tool modules for defaults and required service configuration. Use your own development services; never commit real credentials.

After configuring PostgreSQL and MongoDB, initialise the project collections and tables:

```bash
python init_db.py
uvicorn main:app --reload
```

Visit http://127.0.0.1:8000/docs. Startup requires the configured dependencies. Model, search, and storage calls may incur provider costs.

## Current limitations

- The analysis route adapter currently accesses the service result through attributes, while the service formats a dictionary. That adapter needs correction and an integration check before the route can be described as working end to end.
- LangGraph state handling and response schemas require validation with the installed dependency versions.
- The repository contains connectivity scripts rather than evidence of a complete automated test suite.
- This snapshot does not include CI/CD configuration or a production monitoring stack.
- Output quality, latency, retrieval accuracy, and operational behaviour have not been benchmarked here.

The useful engineering focus is the orchestration and data flow. Claims about deployment and reliability should follow measured validation.

## Contact

[Portfolio](https://hamza-khan-portfolio.hamzakhan102003.chatgpt.site/) · [LinkedIn](https://www.linkedin.com/in/muhammadhamzakhan/) · [Email](mailto:hamzakhan102003@gmail.com)
