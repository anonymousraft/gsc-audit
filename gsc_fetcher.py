import pandas as pd
from google.oauth2 import service_account
from utils import load_config, init_logger
from oauth_utils import get_oauth_credentials, build_oauth_service

def authenticate():
    """
    Authenticate to Google Search Console using OAuth2 or Service Account.
    """
    cfg = load_config()
    logger = init_logger(cfg['logging']['file'], cfg['logging']['level'])

    if cfg['auth']['type'] == 'oauth':
        creds = get_oauth_credentials(
            cfg['auth']['oauth_credentials_file'],
            cfg['auth']['oauth_scope'],
            cfg['auth']['credentials_file']
        )
        service = build_oauth_service(creds)
        logger.info('Authenticated via OAuth2')
    else:
        creds = service_account.Credentials.from_service_account_file(
            cfg['auth']['sa_keyfile'],
            scopes=cfg['auth']['sa_scopes']
        )
        from googleapiclient.discovery import build
        service = build('webmasters', 'v3', credentials=creds)
        logger.info('Authenticated via Service Account')

    return service, logger

def list_properties(service, logger) -> list:
    """
    Retrieve all verified properties (sites) in the user's GSC account.
    """
    resp = service.sites().list().execute()
    sites = [entry['siteUrl'] for entry in resp.get('siteEntry', [])]
    logger.info(f'Found {len(sites)} properties')
    return sites

def fetch_performance(service, logger, site_url,
                      start_date, end_date,
                      dimensions, filters=None) -> pd.DataFrame:
    """
    Fetch all available rows by paging through Search Console data.
    Breaks when fewer than page_size rows are returned.
    """
    page_size = 25000
    body = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': dimensions,
        'rowLimit': page_size
    }
    if filters:
        body['dimensionFilterGroups'] = [{'filters': filters}]

    all_data = []
    start_row = 0

    while True:
        body['startRow'] = start_row
        try:
            resp = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
        except Exception as e:
            logger.error(f"Fetch error at row {start_row}: {e}")
            break

        rows = resp.get('rows', [])
        fetched = len(rows)
        logger.info(f"Page fetched {fetched} rows (startRow={start_row})")

        if fetched == 0:
            # no data left
            break

        for row in rows:
            rec = {}
            keys = row.get('keys', [])
            for i, dim in enumerate(dimensions):
                rec[dim] = keys[i] if i < len(keys) else None
            rec['clicks']      = row.get('clicks', 0)
            rec['impressions'] = row.get('impressions', 0)
            rec['ctr']         = row.get('ctr', 0)
            rec['position']    = row.get('position', 0)
            all_data.append(rec)

        start_row += fetched

        # if we got fewer than page_size, that was the last page
        if fetched < page_size:
            logger.info("Last page detected, stopping pagination.")
            break

    df = pd.DataFrame(all_data)
    # Ensure all expected columns exist
    expected = [*dimensions, 'clicks', 'impressions', 'ctr', 'position']
    for col in expected:
        if col not in df.columns:
            df[col] = 0
    df = df[expected]

    logger.info(f"Total rows fetched: {len(df)} for dimensions={dimensions}")
    return df
