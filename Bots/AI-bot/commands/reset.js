const { SlashCommandBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('reset')
        .setDescription('Reset your chat history. (may fix errors)'),
    async execute(interaction) {
        await interaction.reply(`Hi your AI chat history has been reset`);
    },
};