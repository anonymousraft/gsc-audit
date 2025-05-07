import os
import pickle
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from rich.console import Console

console = Console()

def get_oauth_credentials(oauth_secrets_file: str, scopes: list, token_path: str = 'token.pickle'):
    """
    Obtain OAuth2 credentials using google-auth-oauthlib.
    Supports 'installed', 'web', or flat JSON formats.
    """
    creds = None
    if os.path.exists(token_path):
        with open(token_path, 'rb') as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            console.log("[green]Refreshed expired credentials[/green]")
        else:
            console.print("[yellow]Opening browser for authentication...[/yellow]")
            conf = json.load(open(oauth_secrets_file))
            if 'installed' in conf:
                client_conf = {'installed': conf['installed']}
            elif 'web' in conf:
                client_conf = {'installed': conf['web']}
            elif 'client_id' in conf and 'client_secret' in conf:
                client_conf = {
                    'installed': {
                        'client_id': conf['client_id'],
                        'client_secret': conf['client_secret'],
                        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                        'token_uri': 'https://oauth2.googleapis.com/token'
                    }
                }
            else:
                console.print("[bold red]Invalid OAuth JSON format.[/]")
                raise ValueError("Invalid OAuth credentials file format.")
            flow = InstalledAppFlow.from_client_config(client_conf, scopes=scopes)
            creds = flow.run_local_server(port=0)
            console.log("[green]Authentication successful[/green]")
        with open(token_path, 'wb') as f:
            pickle.dump(creds, f)
            console.log(f"[green]Saved token to {token_path}[/green]")
    return creds


def build_oauth_service(creds):
    from googleapiclient.discovery import build
    return build('searchconsole', 'v1', credentials=creds)