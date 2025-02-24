import requests

class Myworkspace:
    def __init__(self, access_token: str):
        self.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Origin': 'https://myworkspace.microsoft.com',
        'Referer': 'https://myworkspace.microsoft.com/',
        'Authorization': f'Bearer {access_token}'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_workspaces(self):
        try:
            response = self.session.get("https://myworkspace-prod.trafficmanager.net/azureworkspace/userworkspaces")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Failed to get workspace, error: {error}")
            return None
    
    def start_workspace(self, workplace_id: str):
        try:
            response = self.session.post(f"https://myworkspace-prod.trafficmanager.net/azureworkspace/start/{workplace_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Failed to start workspace, error: {error}")
            return None
    
    def extend_running_time(self, workplace_id: str, extend_hours: int):
        try:
            response = self.session.put(
                f"https://myworkspace-prod.trafficmanager.net/azureworkspace/extendruntime/{workplace_id}",
                data=str(extend_hours),
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json, text/plain, */*',
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Failed to extend running time, error: {error}")
            return None
    
    def get_nat_jit(self):
        try:
            response = self.session.get("https://myworkspace-prod.trafficmanager.net/natrule/jit")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Failed to get NAT JIT, error: {error}")
            return None

    def extend_jit(self, workplace_id: str, extend_hours: int):
        try:
            response = self.session.post(
                "https://myworkspace-prod.trafficmanager.net/natrule/jit",
                json={"WorkspaceID": workplace_id, "Hours": extend_hours}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Failed to extend NAT JIT, error: {error}")
            return None