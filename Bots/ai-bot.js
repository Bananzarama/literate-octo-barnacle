const { Client, Events, GatewayIntentBits } = require("discord.js");
const { Configuration, OpenAIApi } = require("openai");
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
const prefix = '*';

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

// Set up OpenAI API credentials
const configuration = new Configuration({
    apiKey: OPENAI_API_KEY,
  });
const openai = new OpenAIApi(configuration);

client.once("ready", async () => {
    logger.info(`Logged in as ${client.user.tag}!`);
    client.user.setActivity(`Current Model: text-davinci-003`);
});


// Set up a conversation state object to store context
const conversationState = {};

client.on("messageCreate", async (message) => {
  // Ignore messages from bots and messages that don't start with the prefix
  if (message.author.bot || !message.content.startsWith(prefix)) {
    return;
  }

  // Parse the user's message and extract the text
  const userMessage = message.content.slice(prefix.length);
  logger.info(`User: ${userMessage}`);

  try {
    // Get the conversation state for this user
    const context = conversationState[message.author.id] || [];
    const initPrompt = "You are a normal human being interacting with your peers:\n"

    // Call the OpenAI API to generate a response (text-davinci-003, text-curie-001, text-babbage-001, text-ada-001) (code-davinci-002, code-cushman-001)
    const response = await openai.createCompletion({
      model: "text-davinci-003",
      prompt: initPrompt + context.slice(-3).join('\n') + (context.length > 0 ? '\n' : '') + userMessage + "\n",
      temperature: 0.5,
      top_p: 0.3,
      max_tokens: 2048,
      n: 1,
      best_of: 1,
      presence_penalty: 0,
      frequency_penalty: 0.5,
    });

    // Extract the response text from the API response
    const botMessage = response.data.choices[0].text.trim();

    // Send the response to the user
    logger.info(`Bot: ${botMessage}`);
    message.channel.send(botMessage);

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

// Handle errors gracefully
client.on('error', error => {
  logger.error(error);
  client.destroy();
  logger.warn('Bot Destroyed!');
  client.login(DISCORD_BOT_TOKEN);
  logger.warn('Bot Rebuilt!');
});

client.login(DISCORD_BOT_TOKEN);
