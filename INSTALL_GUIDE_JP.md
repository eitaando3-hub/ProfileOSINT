# ProfileOSINT Portable Installation Guide

## 概要 (Overview)

このパッケージは、Windows 10/11 (Home/Pro) で完全ポータブル環境として機能します。

---

## 🚀 クイックスタート (Quick Start)

### **Windows (10/11 Home/Pro)**

#### 方法1: 自動セットアップ (推奨)
```batch
1. USB メモリをプラグイン
2. setup_windows.bat をダブルクリック
3. インストール完了後、run_profileosint.bat をダブルクリック
```

#### 方法2: 手動実行
```batch
1. activate_venv.bat をダブルクリック
2. コマンドプロンプトで以下を入力:
   python -m app.main
```

### **macOS/Linux**

```bash
1. USB をマウント
2. ターミナルで以下を実行:
   bash setup_linux_mac.sh
3. インストール完了後:
   bash run_profileosint.sh
```

---

## 📋 USB メモリの構成

```
USB_ROOT/
├── setup_windows.bat          # Windows セットアップ
├── run_profileosint.bat       # Windows 起動
├── activate_venv.bat          # Windows 環境有効化
├── setup_linux_mac.sh         # Linux/macOS セットアップ
├── run_profileosint.sh        # Linux/macOS 起動
├── activate_venv.sh           # Linux/macOS 環境有効化
│
├── INSTALL_GUIDE.md           # このフ��イル
├── README.md                  # 日本語版
├── requirements.txt           # Python 依存パッケージ
│
├── app/                       # アプリケーション本体
│   ├── __init__.py
│   ├── main.py
│   ├── config/                # 設定モジュール
│   ├── core/                  # コアモジュール
│   ├── db/                    # データベース
│   ├── security/              # セキュリティ
│   ├── sources/               # 検索ソース
│   ├── ui/                    # UI
│   ├── utils/                 # ユーティリティ
│   └── notifications/         # 通知
│
├── venv/                      # Python 仮想環境 (セットアップ後に作成)
│   ├── Scripts/ (Windows) or bin/ (Linux/Mac)
│   ├── Lib/ (Windows) or lib/ (Linux/Mac)
│   └── ...
│
└── data/                      # ユーザーデータ (セットアップ後に作成)
    ├── profiles/              # プロフィール
    ├── logs/                  # ログ
    └── audit.db               # 監査ログ DB
```

---

## 🔧 トラブルシューティング

### Windows: "Python not found in system PATH"

**原���**: Python がシステムにインストールされていない

**解決方法**:
```
1. https://www.python.org/downloads/ にアクセス
2. Windows インストーラーをダウンロード
3. インストーラーを実行
4. [重要] "Add Python to PATH" をチェック
5. PC を再起動
6. setup_windows.bat を再度実行
```

### Windows: "Virtual environment activation failed"

**原因**: Windows Defender または他のセキュリティソフトが実行スクリプトをブロック

**解決方法**:
```powershell
# PowerShell を管理者モードで実行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# その後、setup_windows.bat を再実行
```

### macOS/Linux: "Permission denied"

**原因**: スクリプトに実行権限がない

**解決方法**:
```bash
chmod +x setup_linux_mac.sh
chmod +x run_profileosint.sh
chmod +x activate_venv.sh

bash setup_linux_mac.sh
```

### "Sherlock not found" エラー

**原因**: Sherlock がインストールされていない

**解決方法**:
```
仮想環境を有効化して、以下を実行:
pip install sherlock-project
```

---

## 🌍 環境変数設定 (Optional)

### メール通知を有効にする

#### Windows (PowerShell)
```powershell
$env:PROFILEOSINT_SMTP_HOST = "smtp.gmail.com"
$env:PROFILEOSINT_SMTP_PORT = "587"
$env:PROFILEOSINT_SMTP_USER = "your-email@gmail.com"
$env:PROFILEOSINT_SMTP_PASSWORD = "your-app-password"
$env:PROFILEOSINT_ALERT_FROM = "alerts@gmail.com"
$env:PROFILEOSINT_ALERT_TO = "admin@gmail.com"

python -m app.main
```

#### Windows (コマンドプロンプト)
```batch
set PROFILEOSINT_SMTP_HOST=smtp.gmail.com
set PROFILEOSINT_SMTP_PORT=587
set PROFILEOSINT_SMTP_USER=your-email@gmail.com
set PROFILEOSINT_SMTP_PASSWORD=your-app-password
set PROFILEOSINT_ALERT_FROM=alerts@gmail.com
set PROFILEOSINT_ALERT_TO=admin@gmail.com

python -m app.main
```

#### Linux/macOS
```bash
export PROFILEOSINT_SMTP_HOST="smtp.gmail.com"
export PROFILEOSINT_SMTP_PORT="587"
export PROFILEOSINT_SMTP_USER="your-email@gmail.com"
export PROFILEOSINT_SMTP_PASSWORD="your-app-password"
export PROFILEOSINT_ALERT_FROM="alerts@gmail.com"
export PROFILEOSINT_ALERT_TO="admin@gmail.com"

python -m app.main
```

---

## 📊 システム要件

### Windows
- **OS**: Windows 10 (1909以上) / Windows 11
- **Edition**: Home, Pro どちらでも可
- **Python**: 3.8 以上（システムにインストール必須）
- **USB メモリ**: 2GB 以上推奨

### macOS
- **OS**: macOS 10.14 以上
- **Python**: 3.8 以上
- **USB メモリ**: 2GB 以上推奨

### Linux
- **Distribution**: Ubuntu 18.04+, Debian 10+ など
- **Python**: 3.8 以上
- **USB メモリ**: 2GB 以上推奨

---

## 🔐 セキュリティに関する注意

1. **ユーザー名のハッシング**
   - すべてのユーザー名は SHA-256 でハッシング化
   - 復号不可能な一方向ハッシュです

2. **監査ログ**
   - すべての操作は SQLite に記録
   - CSV でエクスポート可能

3. **メール通知**
   - 重要操作時にメール通知（オプション）
   - SMTP 認証情報は環境変数で管理

---

## 💾 データのバックアップ

重要なデータは `data/` フォルダに保存されます：

```bash
# Windows: data フォルダをコピー
xcopy data data_backup /E /I

# Linux/macOS: data フォルダをコピー
cp -r data data_backup
```

---

## 🆘 さらにサポートが必要な場合

GitHub Issue を作成してください：
https://github.com/eitaando3-hub/ProfileOSINT/issues

---

## 📝 ライセンス

MIT License
