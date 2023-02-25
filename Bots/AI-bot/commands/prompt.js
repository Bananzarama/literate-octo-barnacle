const { SlashCommandBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('prompt')
        .setDescription('Change the initial prompt for the AI!')
        .addStringOption(option =>
            option.setName('prompt')
                .setDescription('The AIs new initial prompt')
                .setRequired(true)),
    async execute(interaction) {
        init_prompt = interaction.options.getString('prompt') ?? 'You are a normal human being.';
        await interaction.reply(`AI prompt swapped to: ${init_prompt}`);
    },
};