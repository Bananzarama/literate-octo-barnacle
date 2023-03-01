const { Client, Events, GatewayIntentBits, Collection } = require("discord.js");
const { Configuration, OpenAIApi } = require("openai");
const fs = require('node:fs');
const path = require('node:path');
const winston = require('winston');
const { combine, timestamp, printf, colorize, align } = winston.format;
const { DISCORD_BOT_CLIENTID, DISCORD_BOT_TOKEN, DISCORD_BOT_AUTHOR, OPENAI_API_KEY } = require('./config.json');
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.GuildPresences,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildMessageReactions,
    GatewayIntentBits.DirectMessages,
    GatewayIntentBits.DirectMessageReactions,
  ],
});

//AI chat prefix
const prefix = '*';

//vars for model and prompt
global.ai_model = "text-davinci-003"
global.init_prompt = "You are a normal human being.";

// Set up a conversation state object to store context
const conversationState = {};

// Winston Logger (error, combined(info), and CLI)
const logger = winston.createLogger({
  level: 'info',
  format: combine(
    colorize({ all: true }),
    timestamp({
      format: 'YYYY-MM-DD hh:mm:ss.SSS A',
    }),
    align(),
    printf((info) => `[${info.timestamp}] ${info.level}: ${info.message}`)
  ),
  defaultMeta: { service: 'AI-Bot-Discord' },
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
    new winston.transports.Console(),
  ],
});

// Slash Command Handler
client.commands = new Collection();
const commandsPath = path.join(__dirname, 'commands');
const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));
for (const file of commandFiles) {
  const filePath = path.join(commandsPath, file);
  const command = require(filePath);
  // Set a new item in the Collection with the key as the command name and the value as the exported module
  if ('data' in command && 'execute' in command) {
    client.commands.set(command.data.name, command);
  } else {
    logger.warn(`[WARNING] The command at ${filePath} is missing a required "data" or "execute" property.`);
  }
}

// Set up OpenAI API credentials
const configuration = new Configuration({
  apiKey: OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

// Initial code
client.once("ready", async () => {
  logger.info(`Logged in as ${client.user.tag}!`);
  client.user.setActivity(`Current Model: ${ai_model}`);
});

// Checks all new chat messages for messages directed at bot
client.on("messageCreate", async (message) => {
  // Ignore messages from bots and messages that don't start with the prefix
  if (message.author.bot || !message.content.startsWith(prefix)) {
    return;
  }

  // Parse the user's message and extract the text
  const userMessage = message.content.slice(prefix.length);
  logger.info(`${message.author.username}#${message.author.discriminator}: ${userMessage}`);

  try {
    // Get the conversation state for this user
    const context = conversationState[message.author.id] || [];

    // Call the OpenAI API to generate a response
    var tokens = 1750;
    if (ai_model == "text-davinci-003" || ai_model == "code-davinci-002") tokens = 3500;
    var whole_prompt = init_prompt + "\n" + context.slice(-3).join('\n') + (context.length > 0 ? '\n' : '') + userMessage + "\n";
    if (ai_model.includes("code-")) whole_prompt = userMessage + "\n";
    const response = await openai.createCompletion({
      model: ai_model,
      prompt: whole_prompt,
      temperature: 0.75,
      top_p: 1,
      max_tokens: 1500,
      n: 1,
      best_of: 1,
      presence_penalty: 0.5,
      frequency_penalty: 0.5,
    });

    // Extract the response text from the API response
    const botMessage = response.data.choices[0].text.trim();
    const promptTokens = response.data.usage.prompt_tokens;
    const responseTokens = response.data.usage.completion_tokens;

    // Send the response to the user
    if (botMessage !== "") {
      try {
        logger.info(`AI => ${message.author.username}#${message.author.discriminator}: ${botMessage}\n   Tokens: ${promptTokens}+${responseTokens}`);
        message.channel.send(botMessage);
      } catch (e) {
        logger.error(e);
      }
    }

    // Update the conversation state with any new context
    conversationState[message.author.id] = [...context.slice(-2), userMessage, botMessage];
  } catch (error) {
    message.channel.send('An error occurred while processing your request. Please try again later.');
    if (error.response) {
      logger.error(`Error Code: ${error.response.status}`);
      logger.error(JSON.stringify(error.response.data, null, 4));
    } else {
      logger.error(error.message);
    }
  }
});

// Slash Command Event Listener
client.on(Events.InteractionCreate, async interaction => {
  if (!interaction.isChatInputCommand()) return;
  const command = interaction.client.commands.get(interaction.commandName);
  if (!command) {
    logger.error(`No command matching ${interaction.commandName} was found.`);
    return;
  }
  try {
    await command.execute(interaction);
    const interactionUser = await interaction.guild.members.fetch(interaction.user.id)
    logger.info(`Slash command used: ${interaction.commandName} by user: ${interaction.member.nickname}(${interactionUser.user.tag})`)
    // Individual logging for the time being. FIX: winston transports maybe
    if (interaction.commandName == "swap-ai") {
      client.user.setActivity(`Current Model: ${ai_model}`);
      logger.warn(`Ai model changed to: ${ai_model}`)
    }
    if (interaction.commandName == "prompt") {
      client.user.setActivity(`Current Model: ${ai_model}`);
      logger.warn(`Ai prompt changed to: ${init_prompt}`)
    }
  } catch (error) {
    logger.error(error);
    await interaction.reply({ content: 'There was an error while executing this command!', ephemeral: true });
  }
});

// Handle errors gracefully
client.on('error', error => {
  logger.error(error);
  client.destroy();
  logger.warn('Bot Destroyed!');
  try {
    client.login(DISCORD_BOT_TOKEN);
    logger.info(`Logged in as ${client.user.tag}!`);
    client.user.setActivity(`Current Model: ${ai_model}`);
    logger.warn('Bot Rebuilt!');
  } catch (error) {
    logger.error(error);
  }
});

client.login(DISCORD_BOT_TOKEN);