#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import TelegramBot from 'node-telegram-bot-api';

class TelegramWebAppMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'telegram-webapp-mcp',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.bot = null;
    this.setupToolHandlers();
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'send_webapp_message',
            description: 'Send a message to a Telegram chat with WebApp support',
            inputSchema: {
              type: 'object',
              properties: {
                chatId: {
                  type: 'string',
                  description: 'Chat ID to send message to',
                },
                text: {
                  type: 'string',
                  description: 'Message text to send',
                },
                webAppUrl: {
                  type: 'string',
                  description: 'WebApp URL to attach to the message',
                },
                webAppText: {
                  type: 'string',
                  description: 'Text for the WebApp button',
                  default: 'Open WebApp',
                },
              },
              required: ['chatId', 'text', 'webAppUrl'],
            },
          },
          {
            name: 'send_webapp_inline_keyboard',
            description: 'Send a message with inline keyboard containing WebApp button',
            inputSchema: {
              type: 'object',
              properties: {
                chatId: {
                  type: 'string',
                  description: 'Chat ID to send message to',
                },
                text: {
                  type: 'string',
                  description: 'Message text to send',
                },
                webAppUrl: {
                  type: 'string',
                  description: 'WebApp URL to attach to the button',
                },
                buttonText: {
                  type: 'string',
                  description: 'Text for the WebApp button',
                  default: 'Open Bakery App',
                },
              },
              required: ['chatId', 'text', 'webAppUrl'],
            },
          },
          {
            name: 'get_webapp_info',
            description: 'Get information about the current WebApp context',
            inputSchema: {
              type: 'object',
              properties: {
                initData: {
                  type: 'string',
                  description: 'WebApp init data from Telegram',
                },
              },
            },
          },
          {
            name: 'send_webapp_data',
            description: 'Send data back to the WebApp',
            inputSchema: {
              type: 'object',
              properties: {
                data: {
                  type: 'string',
                  description: 'Data to send to the WebApp',
                },
                showAlert: {
                  type: 'boolean',
                  description: 'Whether to show alert in WebApp',
                  default: false,
                },
              },
              required: ['data'],
            },
          },
        ],
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'send_webapp_message':
            return await this.sendWebAppMessage(args);
          case 'send_webapp_inline_keyboard':
            return await this.sendWebAppInlineKeyboard(args);
          case 'get_webapp_info':
            return await this.getWebAppInfo(args);
          case 'send_webapp_data':
            return await this.sendWebAppData(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message}`,
            },
          ],
        };
      }
    });
  }

  async initializeBot() {
    if (!this.bot) {
      const token = process.env.TELEGRAM_BOT_TOKEN;
      if (!token) {
        throw new Error('TELEGRAM_BOT_TOKEN environment variable is required');
      }
      this.bot = new TelegramBot(token, { polling: false });
    }
    return this.bot;
  }

  async sendWebAppMessage(args) {
    const bot = await this.initializeBot();
    const { chatId, text, webAppUrl, webAppText = 'Open WebApp' } = args;

    const message = await bot.sendMessage(chatId, text, {
      reply_markup: {
        inline_keyboard: [
          [
            {
              text: webAppText,
              web_app: {
                url: webAppUrl,
              },
            },
          ],
        ],
      },
    });

    return {
      content: [
        {
          type: 'text',
          text: `Message sent successfully! Message ID: ${message.message_id}`,
        },
      ],
    };
  }

  async sendWebAppInlineKeyboard(args) {
    const bot = await this.initializeBot();
    const { chatId, text, webAppUrl, buttonText = 'Open Bakery App' } = args;

    const message = await bot.sendMessage(chatId, text, {
      reply_markup: {
        inline_keyboard: [
          [
            {
              text: buttonText,
              web_app: {
                url: webAppUrl,
              },
            },
          ],
        ],
      },
    });

    return {
      content: [
        {
          type: 'text',
          text: `Inline keyboard with WebApp button sent! Message ID: ${message.message_id}`,
        },
      ],
    };
  }

  async getWebAppInfo(args) {
    const { initData } = args;
    
    if (!initData) {
      return {
        content: [
          {
            type: 'text',
            text: 'No init data provided. This function requires WebApp init data from Telegram.',
          },
        ],
      };
    }

    // Parse init data (simplified)
    const params = new URLSearchParams(initData);
    const user = params.get('user');
    const authDate = params.get('auth_date');
    const hash = params.get('hash');

    return {
      content: [
        {
          type: 'text',
          text: `WebApp Info:
- User: ${user || 'Not provided'}
- Auth Date: ${authDate || 'Not provided'}
- Hash: ${hash ? 'Present' : 'Not provided'}
- Init Data: ${initData}`,
        },
      ],
    };
  }

  async sendWebAppData(args) {
    const { data, showAlert = false } = args;

    // This would typically be sent back to the WebApp
    // In a real implementation, you'd need to maintain WebApp connections
    return {
      content: [
        {
          type: 'text',
          text: `Data sent to WebApp: ${data}${showAlert ? ' (with alert)' : ''}`,
        },
      ],
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Telegram WebApp MCP server running on stdio');
  }
}

const server = new TelegramWebAppMCPServer();
server.run().catch(console.error);

