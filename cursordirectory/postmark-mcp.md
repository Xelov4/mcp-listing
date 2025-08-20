# Postmark MCP

## Description
The Postmark MCP server exposes these Postmark capabilities as tools:

- **sendEmail**: Send individual transactional emails with full control
- **sendEmailWithTemplate**: Use your existing Postmark templates
- **listTemplates**: Browse available email templates
- **getDeliveryStats**: Analyze your sending performance

## GitHub Repository
*No direct GitHub repository link found*

## Installation
Use the Cursor deep link to install:
```
cursor://anysphere.cursor-deeplink/mcp/install?name=postmark&config=eyJlbnYiOnsiREVGQVVMVF9TRU5ERVJfRU1BSUwiOiJ5b3VyLXNlbmRlci1lbWFpbEBleGFtcGxlLmNvbSIsIlBPU1RNQVJLX1NFUlZFUl9UT0tFTiI6InlvdXItcG9zdG1hcmstc2VydmVyLXRva2VuIiwiREVGQVVMVF9NRVNTQUdFX1NUUkVBTSI6InlvdXItbWVzc2FnZS1zdHJlYW0ifSwiY29tbWFuZCI6Im5vZGUgcGF0aC90by9wb3N0bWFyay1tY3AvaW5kZXguanMifQ%3D%3D
```

## Environment Variables Required
- `DEFAULT_SENDER_EMAIL`: Your sender email address
- `POSTMARK_SERVER_TOKEN`: Your Postmark server token
- `DEFAULT_MESSAGE_STREAM`: Your message stream

## Source
- **Page**: https://cursor.directory/mcp/postmark-mcp
- **Last Updated**: 2025-01-18
