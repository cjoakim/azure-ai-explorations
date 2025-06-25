from azure.ai.projects import AIFoundryClient, PromptTemplate
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

# This class is used to invoke Azure AI Foundry.
# Chris Joakim, 2025

class AIFoundryUtil:
    def __init__(self, endpoint: str, credential: AzureKeyCredential):
        self.client = AIFoundryClient(endpoint=endpoint, credential=credential)
        self.api_version = '2024-10-21'
        self.embedding_deployment_name = None
        self.completion_deployment_name = None

    def create_project(self, resource_group_name: str, account_name: str, project_name: str) -> bool:
        try:
            self.client.projects.create(resource_group_name, account_name, project_name)
            return True
        except Exception as e:
            print(f"Error creating project: {e}")
            return False

    def set_api_version(self, api_version: str = '2024-10-21') -> bool:
        try:
            self.api_version = api_version
            return True
        except Exception as e:
            print(f"Error setting API version: {e}")
            return False

    def set_embedding_deployment_name(self, name: str) -> bool:
        try:
            self.embedding_deployment_name = name
            return True
        except Exception as e:
            print(f"Error setting embedding deployment name: {e}")
            return False

    def set_completion_deployment_name(self, name: str) -> bool:
        try:
            self.completion_deployment_name = name
            return True
        except Exception as e:
            print(f"Error setting completion deployment name: {e}")
            return False

    def create_and_run_agent(self, agent_definition):
        try:
            agent = self.client.agents.create(agent_definition)
            self.client.agents.run(agent.id)
            return True
        except Exception as e:
            print(f"Error creating or running agent: {e}")
            return False

    def get_azure_openai_client(self):
        try:
            return self.client.inference.get_azure_openai_client()
        except Exception as e:
            print(f"Error getting Azure OpenAI client: {e}")
            return None

    def list_deployed_models(self):
        try:
            return list(self.client.deployments.list())
        except Exception as e:
            print(f"Error listing deployed models: {e}")
            return []

    def list_connected_resources(self):
        try:
            return list(self.client.connections.list())
        except Exception as e:
            print(f"Error listing connected resources: {e}")
            return []

    def upload_document_and_create_dataset(self, document_path: str, dataset_name: str):
        try:
            with open(document_path, 'rb') as f:
                document_data = f.read()
            dataset = self.client.datasets.create(dataset_name, documents=[document_data])
            return dataset
        except Exception as e:
            print(f"Error uploading document or creating dataset: {e}")
            return None

    def create_and_list_search_indexes(self, index_definition):
        try:
            self.client.indexes.create(index_definition)
            return list(self.client.indexes.list())
        except Exception as e:
            print(f"Error creating or listing search indexes: {e}")
            return []

    def get_ai_inference_client(self):
        try:
            return self.client.inference.get_inference_client()
        except Exception as e:
            print(f"Error getting AI Inference client: {e}")
            return None

    def read_prompt_and_render(self, prompt_content: str):
        try:
            prompt_template = PromptTemplate(prompt_content)
            return prompt_template.render()
        except Exception as e:
            print(f"Error reading prompt or rendering: {e}")
            return None

    def run_evaluations(self, evaluation_definition):
        try:
            evaluation = self.client.evaluations.create(evaluation_definition)
            return evaluation
        except Exception as e:
            print(f"Error running evaluations: {e}")
            return None

    def enable_telemetry(self):
        try:
            self.client.enable_telemetry()
            return True
        except Exception as e:
            print(f"Error enabling telemetry: {e}")
            return False

# Example usage:
# credential = DefaultAzureCredential()
# ai_foundry_util = AIFoundryUtil(endpoint="https://your-aifoundry-endpoint.azure.com", credential=credential)
# project_created = ai_foundry_util.create_project("your-resource-group", "your-account-name", "your-new-project")
