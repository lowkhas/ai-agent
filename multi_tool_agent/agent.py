from datetime import datetime, timezone
from json import loads
from google.adk.agents import Agent
import requests
import urllib

GITLAB_ACCESS_KEY="YOUR_GITLAB_ACCESS TOKEN"
GITLAB_API_URL="https://gitlab.com/api/v4"

headers = {
  "PRIVATE-TOKEN": f"{GITLAB_ACCESS_KEY}"
}

def get_latest_pipeline_id(project_id: int) -> dict:
  """Retrieves the latest gitlab pipeline ID.

  Returns:
    dict: A dictionary containing the latest pipeline id with a 'status' key ('success' or 'error') and a 'id' key with the pipeline id if successful, or an 'error_message' if an error occurred.
  """

  response = requests.get(f"{GITLAB_API_URL}/projects/{project_id}/pipelines", headers=headers)
  pipelines = response.json()
  pipeline_id = -1
  if pipelines:
    pipeline_id = pipelines[0]['id']
    return {"status": "success",
            "id": f"{pipeline_id}"}
  else:
    return {"status": "error",
            "error_message": f"Latest pipeline id for project '{project_id}' is not available."}

def get_pipeline_job_failed(project_id: int, pipeline_id: int) -> dict:
  """Retrieves the job which failed based on a project ID and a pipeline ID.

  Returns:
    dict: A dictionary containing the failed job id with a 'status' key ('success' or 'error') and a 'id' key with the job id if successful, or an 'error_message' if an error occurred.
  """

  response = requests.get(f"{GITLAB_API_URL}/projects/{project_id}/pipelines/{pipeline_id}/jobs", headers=headers)
  jobs = response.json()
  failed_jobs_id = str(next(
    (job['id'] for job in jobs if job.get('status') == 'failed' and job.get('allow_failure') is False),
    None
  ))

  if failed_jobs_id:
    return {"status": "success",
            "id": f"{failed_jobs_id}"}
  else:
    return {"status": "error",
            "error_message": f"Failed job id for project id : '{project_id}' and pipeline id: '{pipeline_id}' is not available."}

def get_logs_job_failed(project_id: int, job_id: int) -> dict:
  """Retrieves the logs from the jobs which failed based on a project ID and a job ID.

  Returns:
    dict: A dictionary containing the latest pipeline id with a 'status' key ('success' or 'error') and a 'id' key with the pipeline id if successful, or an 'error_message' if an error occurred.
  """

  response = requests.get(f"{GITLAB_API_URL}/projects/{project_id}/jobs/{job_id}/trace", headers=headers)

  if response:
    return {"status": "success",
            "job_logs": f"{response.text}"}
  else:
    return {"status": "error",
            "error_message": f"Failed getting job logs for project id : '{project_id}' and job id: '{job_id}' is not available."}

def create_issue(project_id: int, issue_title: str, issue_content: str) -> dict:
  """Create an issue after identify the problem in a job in a pipeline based on a project ID and a debug.
  This issue contain a Title and a description respecting Markdown format ONLY. Propose a solution to fix it.

  Returns:
    dict: A dictionary containing the latest pipeline id with a 'status' key ('success' or 'error') and a 'id' key with the pipeline id if successful, or an 'error_message' if an error occurred.
  """

  safe_issue_title=f"{urllib.parse.quote(issue_title, safe='')}"
  gitlab_issue_request = f"{GITLAB_API_URL}/projects/{project_id}/issues?title={safe_issue_title}&labels=fix,gitlab-ai-agent&description={issue_content}&created_at={datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}"

  response = requests.post(f"{gitlab_issue_request}", headers=headers)
  issue: dict = loads(response.content)

  if issue:
    issue_id = issue.get("id", None)
    if issue_id is None:
      raise BaseException(f"Id has not been found : {issue}")
    return {"status": "success",
            "issue_id": f"{issue_id}"}
  else:
    return {"status": "error",
            "error_message": f"Failed creating issue to fix {issue_title} for project id : '{project_id}'."}

root_agent = Agent(
    name="gitlab_pipeline_error_identifier",
    model="gemini-2.0-flash",
    description="Agent to identify gitlab pipeline error.",
    instruction="I can help you to identify error in a Gitlab pipeline and propose a fix to it.",
    tools=[get_latest_pipeline_id, get_pipeline_job_failed, get_logs_job_failed, create_issue]
)
