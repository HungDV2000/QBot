import cst
from enum import Enum

spreadsheetId = cst.spreadsheet_id

tab_list_all_ma = "100 mã (50 tăng và 50 giảm)"
tab_cho_va_khop = "Chờ và khớp"
tab_white_list = "list"

tab_dat_lenh = cst.tab_dat_lenh

import os.path
import numpy as np

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = None
service = None

def init_sheet_api():
  creds = None
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    
    with open("token.json", "w") as token:
      token.write(creds.to_json())
  try:
    global service
    service = build("sheets", "v4", credentials=creds)
  except HttpError as err:
    print(err)

def get_dat_lenh(range):
  RANGE_NAME = f"'{tab_dat_lenh}'!{range}"
  init_sheet_api()
  try:
      result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheetId, range=RANGE_NAME)
        .execute()
      )
      rows = result.get("values", [])
      return rows
  except HttpError as error:
      print(f"An error occurred: {error}")
      return error

def get_cho_va_khop(range):
  RANGE_NAME = f"'{tab_cho_va_khop}'!{range}"
  init_sheet_api()
  try:
      result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheetId, range=RANGE_NAME)
        .execute()
      )
      rows = result.get("values", [])
      return rows
  except HttpError as error:
      print(f"An error occurred: {error}")
      return error
  
def get_100_ma(range):
  RANGE_NAME = f"'{tab_list_all_ma}'!{range}"
  init_sheet_api()
  try:
      result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheetId, range=RANGE_NAME)
        .execute()
      )
      rows = result.get("values", [])
      return rows
  except HttpError as error:
      print(f"An error occurred: {error}")
      return error
  
def get_white_list():
    RANGE_NAME = f"'{tab_white_list}'!A1:A1000"
    init_sheet_api()
    try:
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheetId, range=RANGE_NAME)
            .execute()
        )
        rows = result.get("values", [])
        whitelist = []
        for row in rows:
            if not row or not row[0].strip():
                continue
            symbol = row[0].strip().upper()
            # Fix: Chuyển đổi format đúng
            # Từ sheet: "BTC/USDT" → "BTC/USDT:USDT" (format Binance futures)
            if symbol.endswith("/USDT"):
                whitelist.append(symbol + ":USDT")
            elif not symbol.endswith(":USDT"):
                # Nếu chỉ có tên mã (không có /USDT), thêm /USDT:USDT
                whitelist.append(symbol + "/USDT:USDT")
            else:
                whitelist.append(symbol)
        return whitelist
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []




def update(tab_name, array_index, value_array):
  index = 2 + array_index
  RANGE_NAME = f"'{tab_name}'!B{index}:P1000"
  init_sheet_api()
  try:
      values = [
              value_array
      ]
      body = {"values": values}
      print(body)
      result = (
          service.spreadsheets()
          .values()
          .update(
              spreadsheetId=spreadsheetId ,
              range=RANGE_NAME,
              valueInputOption="USER_ENTERED",
              body=body,
          )
          .execute()
      )
      print(f"{result.get('updatedCells')} cells updated.")
      return result
  except HttpError as error:
      print(f"An error occurred: {error}")
      return error
  
def update_single_value(tab_name, range, value):
  RANGE_NAME = f"'{tab_name}'!{range}"
  init_sheet_api()
  try:
      values = [
              [value]
      ]
      body = {"values": values}
      print(body)
      result = (
          service.spreadsheets()
          .values()
          .update(
              spreadsheetId=spreadsheetId ,
              range=RANGE_NAME,
              valueInputOption="USER_ENTERED",
              body=body,
          )
          .execute()
      )
      print(f"{result.get('updatedCells')} cells updated.")
      return result
  except HttpError as error:
      print(f"An error occurred: {error}")
      return error

def replace_nan(array, replace_value):
    nan_indices = np.isnan(array)
    array[nan_indices] = replace_value
    return array

def update_multi(tab_name, array_index, array_2d, from_column_alphabet_name):
  # Fix: Nếu array_index < 0, dùng abs để ghi từ hàng đó trực tiếp
  # Nếu array_index >= 0, dùng công thức 2 + array_index (giữ backward compatibility)
  if array_index < 0:
      index = abs(array_index)
  else:
      index = 2 + array_index
  
  # Fix: Mở rộng range đến cột AZ để đủ chứa tất cả data (52 cột)
  RANGE_NAME = f"'{tab_name}'!{from_column_alphabet_name}{index}:AZ1000"
  
  
  print("----------------------------")
  print(array_2d)
  init_sheet_api()

  try:
      values = array_2d
      body = {"values": values}
      print(body)
      result = (
          service.spreadsheets()
          .values()
          .update(
              spreadsheetId=spreadsheetId ,
              range=RANGE_NAME,
              valueInputOption="USER_ENTERED",
              body=body,
          )
          .execute()
      )
      print(f"{result.get('updatedCells')} cells updated.")
      return result
  except HttpError as error:
      print(f"An error occurred: {error}")
      return error

def clear_multi(tab_name, array_index,  from_column_alphabet_name, end_row=1000, end_column="AZ"):
  """
  Clear dữ liệu trong sheet
  Args:
    tab_name: Tên tab
    array_index: Index (sẽ được convert thành row = 2 + array_index, hoặc nếu < 0 thì dùng abs)
    from_column_alphabet_name: Cột bắt đầu (VD: "A")
    end_row: Hàng kết thúc (default: 1000)
    end_column: Cột kết thúc (default: "AZ")
  """
  # Fix: Nếu array_index < 0, dùng abs để clear từ hàng đó trực tiếp
  # Nếu array_index >= 0, dùng công thức 2 + array_index (giữ backward compatibility)
  if array_index < 0:
      index = abs(array_index)
  else:
      index = 2 + array_index
  
  RANGE_NAME = f"'{tab_name}'!{from_column_alphabet_name}{index}:{end_column}{end_row}"
  print(f"Clear range: {RANGE_NAME}")
  init_sheet_api()

  try:
      result =  service.spreadsheets().values().clear(
            spreadsheetId=spreadsheetId,
            range=RANGE_NAME,
        ).execute()
      return result
  except HttpError as error:
      print(f"An error occurred: {error}")
      return error


