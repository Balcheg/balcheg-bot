import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1VWZ2xopHzGYUjo2zaX4uvdIW73Wy_pweiQ9Sjo2_QK4'

def get_sheets_service():
    creds_json = os.getenv("GOOGLE_CREDENTIALS")
    creds_dict = json.loads(creds_json)
    credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)
    return service

def add_article(article_text, username):
    service = get_sheets_service()
    values = [[datetime.now().strftime('%Y-%m-%d %H:%M:%S'), article_text, username]]
    body = {'values': values}
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='Articles!A:C',
        valueInputOption='RAW',
        body=body
    ).execute()

def add_goal(goal_text, username):
    service = get_sheets_service()
    values = [[datetime.now().strftime('%Y-%m-%d %H:%M:%S'), goal_text, username]]
    body = {'values': values}
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='Goals!A:C',
        valueInputOption='RAW',
        body=body
    ).execute()

def get_articles():
    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='Articles!A:C'
    ).execute()
    return result.get('values', [])

def get_goals():
    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='Goals!A:C'
    ).execute()
    return result.get('values', [])

def clear_sheet(sheet_name):
    service = get_sheets_service()
    service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=f'{sheet_name}!A:C'
    ).execute()