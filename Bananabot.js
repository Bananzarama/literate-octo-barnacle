const { Client, Events, GatewayIntentBits } = require("discord.js");
const winston = require('winston');
const { combine, timestamp, printf, colorize, align } = winston.format;
const { clientId, token, author } = require('./config.json');
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
const MongoClient = require("mongodb").MongoClient;
const uri = "mongodb://127.0.0.1:27017/bananabot";
let db;

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
  defaultMeta: { service: 'Bananabot-Discord' },
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
    new winston.transports.Console(),
  ],
});

const connectToDb = async () => {
  const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });
  try {
    await client.connect();
    logger.info('Connected to MongoDB');
    db = client.db('bananabot');
  } catch (error) {
    logger.error(`Failed to connect to MongoDB: ${error}`);
    process.exit(1);
  }
};

const updateCounter = async (value) => {
  try {
    const counters = db.collection('counters');
    const { value: count } = await counters.findOneAndUpdate(
      { type: 'banana_count' },
      { $inc: { value } },
      { upsert: true, returnOriginal: false }
    );
    return count;
  } catch (error) {
    logger.error(`Failed to update counter: ${error}`);
    process.exit(1);
  }
};

client.once("ready", async () => {
  logger.info(`Logged in as ${client.user.tag}!`);
  await connectToDb();
  const count = await updateCounter(0)
    .then((count) => {
      logger.info(`Current banana count: ${count.value}`);
      client.user.setActivity(`Current banana count: ${count.value}`);
    })
    .catch((err) => {
      logger.error(err);
      process.exit(1);
    });
});

client.on("messageCreate", async (message) => {
  if (message.author.bot || !message.system) {
    return;
  }
  if (message.content.includes("banana")) {
    const count = await updateCounter(1)
      .then((count) => {
        logger.info(`Current banana count: ${count.value}`);
        message.react('861110914103377930');
        client.user.setActivity(`Current banana count: ${count.value}`);
      })
      .catch((err) => {
        logger.error(err);
        process.exit(1);
      });
    }
});

client.login(token);