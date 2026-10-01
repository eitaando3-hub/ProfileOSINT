# ProfileOSINT

ProfileOSINT is a desktop application for searching and managing personal profiles using open-source tools.

## Features

- **Sherlock Integration**: Search across multiple platforms using a username
- **Web Search Integration**: Supplementary searches via external APIs
- **Audit Logging**: Log all operations with CSV export capability
- **Profile Management**: Store hashed usernames and search results
- **Role-Based Access Control**: Four roles—viewer, operator, auditor, admin
- **Event Notifications**: Optional email alerts for critical operations

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m app.main
```

## Environment Variables

```bash
# Role configuration
export PROFILEOSINT_ROLE=admin
export PROFILEOSINT_USER=your-username

# Email notifications
export PROFILEOSINT_SMTP_HOST=smtp.gmail.com
export PROFILEOSINT_SMTP_PORT=587
export PROFILEOSINT_SMTP_USER=your-email@example.com
export PROFILEOSINT_SMTP_PASSWORD=your-password
export PROFILEOSINT_ALERT_FROM=alerts@example.com
export PROFILEOSINT_ALERT_TO=admin@example.com
```

## Audit Logging

- **Audit Log Tab**: Monitor operations in real-time
- **Search History Tab**: Review Sherlock search history
- **CSV Export**: Filter and export logs

## Security

- Usernames and names are hashed with SHA-256
- Audit logs stored in SQLite
- Operations controlled via RBAC
- Critical operations can trigger email alerts

## License

MIT License
