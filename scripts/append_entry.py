#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""取引入力シートに 1 行追記する。

使い方:
    python scripts/append_entry.py --date 2026/08/07 --account "売上高（レッスン）" --partner "◯◯様" --memo "マシン回数券 販売" --income 12000 --method "現金"

必要な環境変数:
    SHEET_ID                        スプレッドシート ID
    認証はどちらか一方:
    GOOGLE_SERVICE_ACCOUNT_JSON     サービスアカウント JSON キーの中身（クラウド環境向け）
    GOOGLE_APPLICATION_CREDENTIALS  サービスアカウント JSON キーのパス（手元の端末向け）

注意: I 列（残高）は数式なので A〜H の 8 列だけを書く。
"""

import argparse
import json
import os
import sys

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_NAME = "取引入力"

ACCOUNTS = [
    "売上高（スタジオレンタル）", "売上高（撮影）", "売上高（レッスン）",
    "売上高（物販）", "雑収入", "事業主借",
    "地代家賃", "水道光熱費", "通信費", "消耗品費", "広告宣伝費", "支払手数料",
    "旅費交通費", "業務委託費", "接待交際費", "修繕費", "保険料", "減価償却費",
    "租税公課", "新聞図書費", "研修費", "雑費", "事業主貸",
]

METHODS = ["現金", "銀行振込", "クレジットカード", "口座引落", "電子マネー・QR決済", "その他", ""]


def parse_args():
    p = argparse.ArgumentParser(description="取引を 1 行追記する")
    p.add_argument("--date", required=True, help="YYYY/MM/DD")
    p.add_argument("--account", required=True, help="勘定科目")
    p.add_argument("--partner", default="", help="取引先")
    p.add_argument("--memo", default="", help="摘要・内容")
    p.add_argument("--income", type=int, help="入金額")
    p.add_argument("--expense", type=int, help="出金額")
    p.add_argument("--method", default="", help="支払方法")
    p.add_argument("--receipt", default="", help="証憑ファイルの URL")
    p.add_argument("--dry-run", action="store_true", help="書き込まずに内容だけ表示")
    return p.parse_args()


def validate(a):
    if (a.income is None) == (a.expense is None):
        sys.exit("エラー: --income か --expense のどちらか一方だけを指定してください")
    if a.account not in ACCOUNTS:
        sys.exit("エラー: 未知の勘定科目です: " + a.account)
    if a.method not in METHODS:
        sys.exit("エラー: 未知の支払方法です: " + a.method)
    amount = a.income if a.income is not None else a.expense
    if amount <= 0:
        sys.exit("エラー: 金額は 1 以上にしてください")


def load_credentials():
    key_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if key_json:
        return Credentials.from_service_account_info(json.loads(key_json), scopes=SCOPES)
    key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if key_path:
        return Credentials.from_service_account_file(key_path, scopes=SCOPES)
    sys.exit(
        "エラー: GOOGLE_SERVICE_ACCOUNT_JSON（キーの中身）か "
        "GOOGLE_APPLICATION_CREDENTIALS（キーのパス）を環境変数に設定してください"
    )


def main():
    a = parse_args()
    validate(a)

    row = [
        a.date,
        a.account,
        a.partner,
        a.memo,
        a.income if a.income is not None else "",
        a.expense if a.expense is not None else "",
        a.method,
        a.receipt,
    ]

    if a.dry_run:
        print("[dry-run] 追記しない内容:", row)
        return

    sheet_id = os.environ.get("SHEET_ID")
    if not sheet_id:
        sys.exit("エラー: SHEET_ID を環境変数に設定してください")

    creds = load_credentials()
    values = build("sheets", "v4", credentials=creds).spreadsheets().values()

    result = values.append(
        spreadsheetId=sheet_id,
        range=SHEET_NAME + "!A:H",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()

    updated = result.get("updates", {}).get("updatedRange", "")
    print("追記しました:", updated)
    print(row)


if __name__ == "__main__":
    main()
