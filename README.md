# Ecommerce Chatbot

## Project Overview
This project implements an **Ecommerce chatbot** using the Rasa framework. The bot is capable of:
- Placing orders
- Returning orders
- Checking order status
- Checking payment or refund status
It features robust intent recognition, order management capabilities, and support for integration via REST, Facebook, Slack, and Socket.IO.

## Folder Structure
- config.yml: Pipeline and policies configuration for intent/entity recognition
- domain.yml: Bot intents, entities, slots, responses, actions
- endpoints.yml: Action server endpoint definitions
- credentials.yml: Channel credentials for supported platforms

## Features
- Supports order management through defined actions
- Handles user greetings, goodbyes, mood, and bot identity queries
- Designed for error handling and fallback intent classification
- Easy integration with messaging channels

## Setup Instructions

### Requirements
- Python 3.10
- Rasa (latest version recommended)

### Getting Started
1. Open a terminal and navigate to your project directory:
cd ./-comchatbot

2. Set the execution policy (for Windows users):
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

3. Activate your Python environment (replace as needed):
.\path\to\python.exe

4. Train the model:
rasa train

5. In the first terminal, start the bot server with:
rasa run -m models --enable-api --cors "*" --debug --endpoints endpoints.yml

6. In a second terminal, run the action server:
rasa run actions


**Tip:** Close all related CSV files before running these commands to avoid file access issues.

### Usage
- Open the Rasa UI (from the 'ui' folder provided) after the bot server is running to interact with the chatbot.
- Test functionalities such as order placement, returns, status queries, and general conversation.

## Integrations
- REST, Facebook, Slack, and Socket.IO channels are supported out-of-the-box.
- Configure `credentials.yml` to set up messaging platform access.

## Customization
- Update `domain.yml` to add or edit intents, responses, and actions.
- Adjust `config.yml` for custom pipeline and policies.

## Troubleshooting
- If the server stops at coroutine debugging, proceed to open the UI and interact with the chatbot.
- Ensure all CSV files used by custom actions or the bot are closed before running the servers.

## Credits
Developed using the Rasa open-source framework for advanced conversational AI.

---

For additional help, refer to the official Rasa documentation at: https://rasa.com/docs/
