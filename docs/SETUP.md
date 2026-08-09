# セットアップ手順（PC で一度だけやる作業）

ゴール：スマホ・Web の Claude Code（クラウド環境）から `scripts/append_entry.py` で
スプレッドシート「スタジオ会計_入出金管理」に追記できるようにする。

Claude への頼み方：この手順を一緒に進めて。ブラウザでやる操作は 1 ステップずつ案内して、
コマンドで済むものは代わりに実行して。

## 1. Google Cloud の準備

1. https://console.cloud.google.com でプロジェクトを作る（既存のものでも可）
2. 「API とサービス」→「ライブラリ」で **Google Sheets API** を有効化する
3. 「IAM と管理」→「サービスアカウント」→ サービスアカウントを作成する
   - 名前は例：`studio-kaikei-writer` 。ロールは付けなくてよい
4. 作ったサービスアカウントの「キー」タブ →「鍵を追加」→「新しい鍵を作成」→ **JSON**
   - ダウンロードした JSON キーは**リポジトリの外**に置く。絶対にコミットしない

※ gcloud CLI が使える環境なら 2〜4 はコマンドでもできる（Claude に頼む）。

## 2. スプレッドシートの共有

1. 「スタジオ会計_入出金管理」を開く
2. 共有に、サービスアカウントのメールアドレス（`...@....iam.gserviceaccount.com`）を
   **編集者**として追加する

## 3. claude.ai/code の環境設定

1. https://claude.ai/code → 設定 → Environments で、このリポジトリに使っている環境を開く
2. 環境変数（シークレット）を 2 つ登録する
   - `SHEET_ID`：スプレッドシートの URL の `/d/` と `/edit` の間の文字列
   - `GOOGLE_SERVICE_ACCOUNT_JSON`：JSON キーファイルの**中身全部**を貼り付け
3. セットアップスクリプトに以下を入れる

   ```
   pip install google-api-python-client google-auth cffi
   ```

## 4. 動作確認

1. **新しいセッション**を開始する（環境変数はセッション開始時に読み込まれるため）
2. dry-run で行の組み立てを確認：

   ```
   python scripts/append_entry.py --date 2026/01/01 --account "雑収入" \
     --partner "テスト" --memo "動作確認" --income 1 --method "現金" --dry-run
   ```

3. 問題なければ `--dry-run` を外して 1 行追記し、シートに入ったのを確認してから
   その行をシート上で手で削除する

これが済めば、スマホから「◯◯さん、△△円、現金でもらった」と言うだけで
復唱→OK→追記まで完結する。
