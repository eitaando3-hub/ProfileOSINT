"""Project README and setup guide."""
# ProfileOSINT

ProfileOSINT は、オープンソースを使用して個人プロファイルの検索と管理を行うデスクトップアプリケーションです。

## 機能

- **Sherlock統合**: ユーザーネームをもとに複数のプラットフォームを検索
- **Web検索統合**: 外部 API を使用した補完的な検索
- **監査ログ**: すべての操作を記録し、CSV エクスポート可能
- **プロフィール管理**: ハッシュ化されたユーザー名と検索結果の保存
- **ロールベースアクセス制御**: viewer, operator, auditor, admin の 4 ロール
- **重要イベント通知**: メール通知オプション

## インストール

```bash
pip install -r requirements.txt
```

## 実行

```bash
python -m app.main
```

## 環境変数

```bash
# ロール設定
export PROFILEOSINT_ROLE=admin
export PROFILEOSINT_USER=your-username

# メール通知設定
export PROFILEOSINT_SMTP_HOST=smtp.gmail.com
export PROFILEOSINT_SMTP_PORT=587
export PROFILEOSINT_SMTP_USER=your-email@example.com
export PROFILEOSINT_SMTP_PASSWORD=your-password
export PROFILEOSINT_ALERT_FROM=alerts@example.com
export PROFILEOSINT_ALERT_TO=admin@example.com
```

## 監査ログ

- **Audit Log タブ**: リアルタイムで操作を監視
- **Search History タブ**: Sherlock検索履歴を確認
- **CSV エクスポート**: ログをフィルタリングして出力

## セキュリティ

- ユーザー名と名前は SHA-256 でハッシュ化
- 監査ログは SQLite に記録
- RBAC によって操作権限を制御
- 重要操作は メール通知可能

## ライセンス

MIT License
