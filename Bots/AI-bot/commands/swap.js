const { SlashCommandBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('swap-ai')
        .setDescription('Swap the current AI model for another!')
        .addStringOption(option =>
            option.setName('ai_model')
                .setDescription('Options for AI Models')
                .setRequired(true)
                .addChoices(
                    { name: "text-davinci-003", value: "text-davinci-003" },
                    { name: "text-curie-001", value: "text-curie-001" },
                    { name: "text-babbage-001", value: "text-babbage-001" },
                    { name: "text-ada-001", value: "text-ada-001" },
                    { name: "code-davinci-002", value: "code-davinci-002" },
                    { name: "code-cushman-001", value: "code-cushman-001" },
                )),
    async execute(interaction) {
        ai_model = interaction.options.getString('ai_model');
        await interaction.reply(`AI model swapped to: ${ai_model}`);
    },
};