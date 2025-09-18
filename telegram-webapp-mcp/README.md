# Telegram WebApp MCP Server

MCP (Model Context Protocol) server for Telegram WebApp integration. This server provides tools for interacting with Telegram WebApps through AI assistants.

## Features

- **Send WebApp Messages**: Send messages with WebApp buttons to Telegram chats
- **Inline Keyboards**: Create inline keyboards with WebApp buttons
- **WebApp Info**: Parse and display WebApp initialization data
- **Data Exchange**: Send data back to WebApp instances

## Installation

```bash
npm install
```

## Configuration

Set the following environment variables:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

## Usage

### As MCP Server

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "telegram-webapp": {
      "command": "node",
      "args": ["/path/to/telegram-webapp-mcp/server.js"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "your_bot_token_here"
      }
    }
  }
}
```

### Available Tools

1. **send_webapp_message**: Send a message with WebApp button
2. **send_webapp_inline_keyboard**: Send message with inline keyboard containing WebApp button
3. **get_webapp_info**: Parse WebApp initialization data
4. **send_webapp_data**: Send data back to WebApp

## Example Usage

```javascript
// Send a message with WebApp button
await callTool('send_webapp_message', {
  chatId: '123456789',
  text: 'Welcome to our bakery!',
  webAppUrl: 'https://your-webapp.com',
  webAppText: 'Open Bakery App'
});
```

## License

MIT

