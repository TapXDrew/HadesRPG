import json
import os
import traceback
import random

import discord
from discord.ext import commands

from utils.characters import Angel, Demon
import utils.userInfo

initial_extensions = [
    "cogs.commands"
]


class HadesBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=self._get_prefix, case_insensitive=True)
        self.config = json.load(open(os.getcwd() + '/configs/config.json'))
        # self.remove_command('help')
        self._load_commands()

    # noinspection PyBroadException
    def _load_commands(self):
        for extension in initial_extensions:
            try:
                self.load_extension(extension)  # Loads in the extension
            except Exception:
                print(f"Failed to load extension {extension}.")  # If it fails, we print the traceback error
                traceback.print_exc()
        self.load_extension("jishaku")

    async def _get_prefix(self, bot, message):
        self.prefix = "&"
        return commands.when_mentioned_or(self.prefix)(self, message)

    async def on_ready(self):
        print("------------------------------------")
        print("Bot Name: " + self.user.name)
        print("Bot ID: " + str(self.user.id))
        print("Discord Version: " + discord.__version__)
        print("------------------------------------")

    async def on_message(self, message):
        if message.channel.id == 735415970872557588 and message.author != self.user:
            if not message.content.startswith("&suggest"):
                await message.author.send("Hey! You tried to post into the suggestion channel! Rather than doing that, how about you use the `&suggest <message>` command instead? (P.S. You can submit an anonymous post by doing `&suggest -a <message>`) Here is the message you sent so you can re-submit it with the command!")
                await message.author.send(message.content)
            await message.delete()
        user = utils.userInfo.User(self, message)

        if user.active_character:

            character_dump = user.active_character

            character_class_name = character_dump.split(";")[1]
            character = eval(character_class_name)(character_dump)

            locations = [735005737364881470, 734672426172153887, 734672182549938197, 734996665773064335,
                         734999518357094442, 734998914872246362, 734676284097036349, 735005811897532486,
                         734675140184637521, 734680519173734430, 734680875039719496, 734685825513816065,
                         734710207220940821, 735016272345170010, 734709942514221056, 735017543965605908,
                         734683106677751818, 734682946497413130, 734682763109728297, 734996724266827786, ]

            if message.channel.id in locations:
                message_value = 0
                for _ in message.content.split(" "):
                    message_value += random.randint(1, 5)
                if message_value > 100:
                    message_value = 100
                if user.character_1 == user.active_character:
                    column = 'character_1'
                elif user.character_2 == user.active_character:
                    column = 'character_2'
                elif user.character_3 == user.active_character:
                    column = 'character_3'
                else:
                    return await self.process_commands(message)
                character.xp += message_value
                user.update_value(column, character.char_dump)
                user.update_value('active_character', character.char_dump)
                level_info = await self.get_level_info(message, column)
                if level_info['Leveled Up']:
                    await message.channel.send(f"{message.author.name} has leveled up to level {level_info['Current Level']}!")

        await self.process_commands(message)

    async def get_level_info(self, ctx, column):
        user = utils.userInfo.User(self, ctx)
        character_dump = user.active_character
        character_class_name = character_dump.split(";")[1]
        character = eval(character_class_name)(character_dump)

        needed_xp = -1
        character_level = 0

        while needed_xp < character.xp:
            needed_xp += pow((character_level + 1), 3) + 30 * pow((character_level + 1), 2) + 30 * (character_level + 1) - 50
            character_level += 1

        if character_level > character.level:
            character.level = character_level
            character.xp = 0
            leveled_up = True
        else:
            leveled_up = False

        return_dict = {
            "Current XP": character.xp,
            "Current Level": character.level,
            "Needed XP": needed_xp,
            "Next Level": character.level + 1,
            "Leveled Up": leveled_up
        }
        user.update_value(column, character.char_dump)
        user.update_value('active_character', character.char_dump)

        return return_dict

    def run(self):
        super().run(self.config['Bot']['Token'], reconnect=True)


if __name__ == "__main__":
    Hades = HadesBot()
    Hades.run()
