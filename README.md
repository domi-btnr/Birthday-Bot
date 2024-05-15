# Birthday Bot

Birthday Bot is a Discord bot that helps users manage and celebrate birthdays within Discord servers.

## Table of Contents

- [Usage](#usage)
- [Commands](#commands)
- [Installation](#installation)
- [Contributing](#contributing)
- [License](#license)

## Usage

Birthday Bot allows users to manage and celebrate birthdays within Discord servers. Once the bot is invited to your Discord server, users can interact with it using various commands. These commands enable users to set their birthdays, delete them if necessary, view their saved birthday information, and see upcoming birthdays in the server.

> [!TIP]
> If you prefer not to host the bot yourself, you can use my bot directly: [Birthday Bot](https://discord.com/api/oauth2/authorize?client_id=1239671141556162580&permissions=18432&scope=bot%20applications.commands)

## Commands

The bot provides the following commands:

- `/birthday set`: Set your birthday and timezone.
- `/birthday delete`: Delete your birthday from the database.
- `/birthday show`: Show your saved birthday information.
- `/birthday upcoming`: Show upcoming birthdays in the server.

> [!IMPORTANT]
> There needs to be a `#birthdays` channel to which the bot sends the birthday messages.

## Installation

If you prefer to host the bot yourself, follow these steps:

1. Clone this repository to your local machine.
2. Set up your Discord bot on the Discord Developer Portal and obtain your bot token.
3. Create a `.env` file in the root directory of the project and add your bot token along with MongoDB connection details:

   ```
   TOKEN=<your_bot_token_here>
   MONGO_HOST=<your_mongodb_host>
   MONGO_PORT=<your_mongodb_port>
   MONGO_USER=<your_mongodb_username>
   MONGO_PASS=<your_mongodb_password>
   MONGO_DB=<your_mongodb_database>
   ```
> [!NOTE]
> If you don't specify a port, the bot will default to port 27017. Similarly, if no database is specified, it will default to using the "BirthdayBot" database

4. Run the bot using Docker Compose:

   ```bash
   docker-compose up -d
   ```

## Contributing

If you'd like to contribute to this project, feel free to fork the repository, make your changes, and submit a pull request.

Some features that will be added later include:

- Selecting a specific channel for birthday messages.
- Changing the birthday message format.

## License

This project is licensed under the [MIT License](LICENSE).

**Note:** If you prefer not to host the bot yourself, you can use my bot directly: [Birthday Bot](https://discord.com/api/oauth2/authorize?client_id=1239671141556162580&permissions=18432&scope=bot%20applications.commands)