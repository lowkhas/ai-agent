# Gitlab AI agent

This is a basic Gitlab AI agent. His goal is to detect based on a failed gitlab pipeline :

- The job which fail
- The job's log
- Create an issue based on these log

## Setup API key

In the agent folder create a '.env' file, containing
```conf
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=XXXXXX
```

## Run the Agent

```bash
# Setup the env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Make sure to NOT enter in the 
# Run Google ADK folder's agent but to stay on the root path of the project
adk web --host 0.0.0.0
# Then go to http://127.0.0.1:8000
# And start using the agent. You just need to tel him that you have a problem on a pipeline and give him the Gitlab project ID.
```

### Note

For now i only test the agent on basic error like typo. 