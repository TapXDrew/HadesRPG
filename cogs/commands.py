import asyncio
import os
import random
import shutil

import requests

import discord
from discord.ext import commands

from utils.userInfo import User

from utils.characters import Angel, Demon
from utils.locations import *

import utils.monsters


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def store_excess_roles(self, ctx, character_type):
        user = User(self.bot, ctx)

        if user.active_character:
            character_dump = user.active_character
            character_class_name = character_dump.split(";")[1]
            character = eval(character_class_name)(character_dump)

            angel_roles = [734915182148714609, 734926170386202675, 734926359276552312, 734926495213944875, 734926685018783794, 734926821174280214]
            demon_roles = [734915359299076118, 734922024077492316, 734921783081304154, 734919595076616292, 734921343006670970, 734918991461613631]
            location_roles = [735321849591758858, 735325510787399730, 735325656086478989, 735332070359826475,
                              735331817070002176, 735331591559053627, 735332168816918528, 735325383829749850,
                              735325249134002256, 735325120519864340, 735324814989983744, 735324672517996548,
                              735324547062169751, 735324419362390029, 735323202057666602, 735322980334436443,
                              735322817327005748, 735322659189031024, 735322494302552145, 735322392796200961]

            removing_roles = []
            if character_type == 'Demon':
                for role in ctx.author.roles:
                    if role.id in angel_roles+location_roles:
                        removing_roles.append(role.id)
                        await ctx.author.remove_roles(role)
            elif character_type == "Angel":
                for role in ctx.author.roles:
                    if role.id in demon_roles+location_roles:
                        removing_roles.append(role.id)
                        await ctx.author.remove_roles(role)

            if user.character_1 == user.active_character:
                column = 'character_1'
            elif user.character_2 == user.active_character:
                column = 'character_2'
            elif user.character_3 == user.active_character:
                column = 'character_3'
            else:
                return

            character.roles = removing_roles

            user.update_value(column, character.char_dump)

    # noinspection PyBroadException
    @commands.command(name="setup", aliases=[])
    async def start_CMD(self, ctx):
        name_limit = 32

        url_image = None
        name_gen = None
        character_type = None
        location = None
        character_type_role = None
        character_role = None
        area_role = None

        dbuser = User(self.bot, ctx)

        if dbuser.character_1 and dbuser.character_2 and dbuser.character_3:
            return await ctx.send("You do not have any free character slots!")

        embed = discord.Embed(title="Character Creation", color=discord.Color.blue())

        message = await ctx.send("Please type your character name", embed=embed)
        while True:
            name = await self.bot.wait_for('message', check=lambda check: check.author.id == ctx.author.id)
            if len(name.content) > name_limit:
                await ctx.send(f"Character name length can not be longer than {name_limit} characters")
                continue
            else:
                break
        embed.add_field(name="Character Name", value=name.content)
        await name.delete()

        await message.edit(content="What character type do you want? Demon or Angel", embed=embed)
        await message.add_reaction('😈')
        await message.add_reaction('👼')

        while True:
            react, user = await self.bot.wait_for('reaction_add', check=lambda _, check: check.id == ctx.author.id)
            await react.remove(ctx.author)

            if react.emoji == '👼':
                character_type = "Angel"
                location = "Garden"

                character_role = discord.utils.get(self.bot.get_guild(734592074342727771).roles, id=734926170386202675)
                character_type_role = discord.utils.get(self.bot.get_guild(734592074342727771).roles, id=734915182148714609)
                area_role = discord.utils.get(self.bot.get_guild(734592074342727771).roles, id=735322494302552145)
                break
            elif react.emoji == '😈':
                character_type = "Demon"
                location = "Courtyard"

                character_role = discord.utils.get(self.bot.get_guild(734592074342727771).roles, id=734922024077492316)
                character_type_role = discord.utils.get(self.bot.get_guild(734592074342727771).roles, id=734915359299076118)
                area_role = discord.utils.get(self.bot.get_guild(734592074342727771).roles, id=735324419362390029)
                break
            else:
                continue
        await message.remove_reaction('😈', member=self.bot.user)
        await message.remove_reaction('👼', member=self.bot.user)

        embed.add_field(name="Character Type", value=character_type)
        await message.edit(
            content="Please share a picture of what your character looks like (Send 'Avatar' for your user avatar)",
            embed=embed)
        while True:
            avatar = await self.bot.wait_for('message', check=lambda check: check.author.id == ctx.author.id)
            if avatar.content.lower() == 'avatar':
                url = ctx.author.avatar_url
            elif avatar.attachments:
                url = avatar.attachments[0].url
            else:
                url = avatar.content
            try:
                name_gen = ''
                for _ in range(5):
                    name_gen += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                r = requests.get(url, stream=True)
                with open(f"{name_gen}.png", 'wb') as out_file:
                    shutil.copyfileobj(r.raw, out_file)

                url_image = await discord.utils.get(self.bot.get_guild(734592074342727771).channels, id=735154858092658758).send(file=discord.File(f"{name_gen}.png"))
                embed.set_image(url=url_image.attachments[0].url)

                break
            except Exception:
                await ctx.send("Please use either an image attachment or an image link", delete_after=10)
                continue

            finally:
                try:
                    os.remove(f"{name_gen}.png")
                except Exception:
                    pass

        await self.store_excess_roles(ctx, character_type)
        await ctx.author.add_roles(character_type_role)
        await ctx.author.add_roles(character_role)
        await ctx.author.add_roles(area_role)
        await ctx.author.add_roles(discord.utils.get(self.bot.get_guild(734592074342727771).roles, id=734915716528078848))

        character_dump = f"{name.content};{character_type};{location};{1};{1};{0};{0};{0};{10};{0};{'Empty'};{'Empty'};{None};{None};{[]};{[]};{[location]};{10};{0};{0};{0};{None};{[]};{False};{url_image.attachments[0].url};{[area_role.id, character_role.id, character_type_role.id]}"
        dbuser.create_character(character_type, character_dump)
        dbuser.update_value('active_character', character_dump)

        await ctx.author.edit(nick=name.content)
        await avatar.delete()
        await message.edit(content=None, embed=embed)

    @commands.command(name="Me", aliases=['Profile'])
    async def profile_CMD(self, ctx, member: discord.Member = None):
        user = User(self.bot, ctx, user=member if member else None)
        if not user.active_character:
            return await ctx.send(
                f"{user.user.name} does not have a character created yet!" if member is not None else f"You do not have a character created yet! Create one with {self.bot.prefix}setup")

        character_dump = user.active_character
        character_class_name = character_dump.split(";")[1]
        character = eval(character_class_name)(character_dump)

        level_info = await self.bot.get_level_info(ctx, 'active_character')

        embed = discord.Embed(title=f"{character.name} ({character.type})", color=discord.Color.green())
        embed.add_field(name="HP & Armor", value=f"{character.health} HP with {character.armor} armor", inline=False)
        embed.add_field(name="Level & XP", value=f"{character.level} ({character.display_xp}/{level_info['Needed XP']+1})", inline=False)
        embed.add_field(name="Location", value=character.location, inline=False)
        embed.add_field(name="Level Up Points and Stats",
                        value=f"Points Available --> {character.points}\nPower Level: {character.power}\nSpeed Level: {character.speed}\nKnowledge Level: {character.knowledge}",
                        inline=False)
        embed.add_field(name="Weapons",
                        value=f"Slot 1: {character.weapon_slot_one.capitalize()}\nSlot 2: {character.weapon_slot_two.capitalize()}", inline=False)
        embed.set_image(url=character.profile_image)
        await ctx.send(embed=embed)

    @commands.command(name='1', aliases=['P1'])
    async def profile_1_CMD(self, ctx):
        user = User(self.bot, ctx)
        if not user.character_1:
            return await ctx.send(f"You do not have a character created in character slot 1! Create on with the {self.bot.prefix}setup command!")

        character_dump = user.character_1
        await ctx.author.edit(nick=character_dump.split(";")[0])

        user.update_value('active_character', character_dump)
        character_class_name = character_dump.split(";")[1]
        character = eval(character_class_name)(character_dump)

        await self.store_excess_roles(ctx, character_class_name)

        for role_id in character.roles:
            role_to_add = discord.utils.get(self.bot.get_guild(734592074342727771).roles, id=role_id)
            await ctx.author.add_roles(role_to_add)

        level_info = await self.bot.get_level_info(ctx, 'active_character')

        embed = discord.Embed(title=f"{character.name} ({character.type})", color=discord.Color.green())
        embed.add_field(name="HP & Armor", value=f"{character.health} HP with {character.armor} armor", inline=False)
        embed.add_field(name="Level & XP", value=f"{character.level} ({character.display_xp}/{level_info['Needed XP'] + 1})",
                        inline=False)
        embed.add_field(name="Location", value=character.location, inline=False)
        embed.add_field(name="Level Up Points and Stats",
                        value=f"Points Available --> {character.points}\nPower Level: {character.power}\nSpeed Level: {character.speed}\nKnowledge Level: {character.knowledge}",
                        inline=False)
        embed.add_field(name="Weapons",
                        value=f"Slot 1: {character.weapon_slot_one.capitalize()}\nSlot 2: {character.weapon_slot_two.capitalize()}",
                        inline=False)
        embed.set_image(url=character.profile_image)
        await ctx.send(embed=embed)

    @commands.command(name='2', aliases=['P2'])
    async def profile_2_CMD(self, ctx):
        user = User(self.bot, ctx)
        if not user.character_2:
            return await ctx.send(
                f"You do not have a character created in character slot 2! Create on with the {self.bot.prefix}setup command!")

        character_dump = user.character_2
        user.update_value('active_character', character_dump)
        await ctx.author.edit(nick=character_dump.split(";")[0])

        character_class_name = character_dump.split(";")[1]
        character = eval(character_class_name)(character_dump)

        await self.store_excess_roles(ctx, character_class_name)

        level_info = await self.bot.get_level_info(ctx, 'active_character')

        for role_id in character.roles:
            role_to_add = discord.utils.get(self.bot.get_guild(734592074342727771).roles, id=role_id)
            await ctx.author.add_roles(role_to_add)

        embed = discord.Embed(title=f"{character.name} ({character.type})", color=discord.Color.green())
        embed.add_field(name="HP & Armor", value=f"{character.health} HP with {character.armor} armor", inline=False)
        embed.add_field(name="Level & XP", value=f"{character.level} ({character.display_xp}/{level_info['Needed XP'] + 1})",
                        inline=False)
        embed.add_field(name="Location", value=character.location, inline=False)
        embed.add_field(name="Level Up Points and Stats",
                        value=f"Points Available --> {character.points}\nPower Level: {character.power}\nSpeed Level: {character.speed}\nKnowledge Level: {character.knowledge}",
                        inline=False)
        embed.add_field(name="Weapons",
                        value=f"Slot 1: {character.weapon_slot_one.capitalize()}\nSlot 2: {character.weapon_slot_two.capitalize()}",
                        inline=False)
        embed.set_image(url=character.profile_image)
        await ctx.send(embed=embed)

    @commands.command(name='3', aliases=['P3'])
    async def profile_3_CMD(self, ctx):
        user = User(self.bot, ctx)
        if not user.character_3:
            return await ctx.send(f"You do not have a character created in character slot 3! Create on with the {self.bot.prefix}setup command!")

        character_dump = user.character_3
        user.update_value('active_character', character_dump)
        await ctx.author.edit(nick=character_dump.split(";")[0])

        character_class_name = character_dump.split(";")[1]
        character = eval(character_class_name)(character_dump)

        await self.store_excess_roles(ctx, character_class_name)

        level_info = await self.bot.get_level_info(ctx, 'active_character')

        for role_id in character.roles:
            role_to_add = discord.utils.get(self.bot.get_guild(734592074342727771).roles, id=role_id)
            await ctx.author.add_roles(role_to_add)

        embed = discord.Embed(title=f"{character.name} ({character.type})", color=discord.Color.green())
        embed.add_field(name="HP & Armor", value=f"{character.health} HP with {character.armor} armor", inline=False)
        embed.add_field(name="Level & XP", value=f"{character.level} ({character.display_xp}/{level_info['Needed XP'] + 1})",
                        inline=False)
        embed.add_field(name="Location", value=character.location, inline=False)
        embed.add_field(name="Level Up Points and Stats",
                        value=f"Points Available --> {character.points}\nPower Level: {character.power}\nSpeed Level: {character.speed}\nKnowledge Level: {character.knowledge}",
                        inline=False)
        embed.add_field(name="Weapons",
                        value=f"Slot 1: {character.weapon_slot_one.capitalize()}\nSlot 2: {character.weapon_slot_two.capitalize()}",
                        inline=False)
        embed.set_image(url=character.profile_image)
        await ctx.send(embed=embed)

    @commands.command(name="PF", alises=['PFP'])
    async def pf_CMD(self, ctx, member: discord.Member = None):
        user = User(self.bot, ctx, user=member if member else None)
        if not user.active_character:
            return await ctx.send(
                f"{user.user.name} does not have a character created yet!" if member is not None else f"You do not have a character created yet! Create one with {self.bot.prefix}setup")

        character_dump = user.active_character
        character_class_name = character_dump.split(";")[1]
        character = eval(character_class_name)(character_dump)
        await ctx.send(character.image)

    @commands.command(name='LevelUp', aliases=[])
    async def levelup_CMD(self, ctx):
        user = User(self.bot, ctx)

        if not user.active_character:
            return await ctx.send(f"You do not have a character created yet! Create one with {self.bot.prefix}setup")

        character_dump = user.active_character
        character_class_name = character_dump.split(";")[1]
        character = eval(character_class_name)(character_dump)

        if user.character_1 == user.active_character:
            column = 'character_1'
        elif user.character_2 == user.active_character:
            column = 'character_2'
        elif user.character_3 == user.active_character:
            column = 'character_3'
        else:
            return

        emojis = ['⚡', '☄️', '📖', '❌']

        embed = discord.Embed(color=discord.Color.orange())
        embed.add_field(name=f"🔸Skill Points: {character.points:,}", value=f"Power: {character.power} ⚡\nSpeed: {character.speed} ☄\nKnowledge: {character.knowledge} 📖", inline=False)
        message = await ctx.send("What skill do you want to level up?", embed=embed)
        for emoji in emojis:
            await message.add_reaction(emoji)

        while True:
            if character.points == 0:
                break
            react, _ = await self.bot.wait_for('reaction_add', check=lambda _, check: check.id == ctx.author.id)
            await react.remove(ctx.author)
            if react.emoji == '⚡':
                character.power += 1
            elif react.emoji == '☄️':
                character.speed += 1
            elif react.emoji == '📖':
                character.knowledge += 1
            elif react.emoji == '❌':
                break
            else:
                continue
            character.points -= 1
            newEmbed = discord.Embed(color=discord.Color.orange())
            newEmbed.add_field(name=f"🔸Skill Points: {character.points:,}", value=f"Power: {character.power} ⚡\nSpeed: {character.speed} ☄\nKnowledge: {character.knowledge} 📖", inline=False)
            await message.edit(embed=newEmbed)

        user.update_value(column, character.char_dump)
        user.update_value('active_character', character.char_dump)
        await message.delete()
        if character.points == 0:
            await ctx.send("You have used all your skill points")
        else:
            await ctx.send(f"You still have {character.points:,} 🔸 Skill Points available!\n\nRun the `{self.bot.prefix}levelup` command when ready to spend them.")

    @commands.group(name="Travel", aliases=['T'])
    async def travel_CMD(self, ctx):
        user = User(self.bot, ctx)

        character_dump = user.active_character

        if not user.active_character:
            return await ctx.send(f"You do not have a character created yet! Create one with {self.bot.prefix}setup")

        character_class_name = character_dump.split(";")[1]
        character = eval(character_class_name)(character_dump)
        location = eval(character.location.lower())()

        if user.character_1 == user.active_character:
            column = 'character_1'
        elif user.character_2 == user.active_character:
            column = 'character_2'
        elif user.character_3 == user.active_character:
            column = 'character_3'
        else:
            return await ctx.send("INVALID PLAYER DATA")

        if character.in_party and character.party_master != ctx.author.id:
            return await ctx.send("You must `&leave` your current party to travel!")

        travel_map = {}
        for area in location.travel_locations:
            travel_map[area().icon] = area().place

        embed = discord.Embed(title=":globe_with_meridians: Travel :globe_with_meridians:", color=discord.Color.blue())
        embed.add_field(name=f"*Current locations you can travel to*\n\u200b", value='\n'.join([f"{area().icon} | {area().place.capitalize()}\n" for area in location.travel_locations]))
        message = await ctx.send(embed=embed)
        for icon in [area().icon for area in location.travel_locations]:
            await message.add_reaction(icon)
        while True:
            react, _ = await self.bot.wait_for('reaction_add', check=lambda _, check: check.id == ctx.author.id)
            await react.remove(ctx.author)
            if react.emoji in [area().icon for area in location.travel_locations]:

                for icon in [area().icon for area in location.travel_locations]:
                    await message.remove_reaction(icon, member=self.bot.user)

                traveling_to = travel_map[react.emoji]
                travel_time = 0
                await message.edit(content=f"{ctx.author.nick if ctx.author.nick else ctx.author.name} is traveling to {traveling_to.capitalize()}\n*Estimated Travel Time: {travel_time} seconds*", embed=None)
                await asyncio.sleep(travel_time)
                character.location = traveling_to.capitalize()
                user.update_value('active_character', character.char_dump)
                user.update_value(column, character.char_dump)
                location_roles = [735321849591758858, 735325510787399730, 735325656086478989, 735332070359826475,
                                  735331817070002176, 735331591559053627, 735332168816918528, 735325383829749850,
                                  735325249134002256, 735325120519864340, 735324814989983744, 735324672517996548,
                                  735324547062169751, 735324419362390029, 735323202057666602, 735322980334436443,
                                  735322817327005748, 735322659189031024, 735322494302552145, 735322392796200961]

                location_role = discord.utils.get(self.bot.get_guild(734592074342727771).roles, name=react.emoji)

                for role in ctx.author.roles:
                    if role.id in location_roles:
                        await ctx.author.remove_roles(role)

                for follower in character.party:
                    follower_discord_user = ctx.guild.get_member(follower)
                    follower_user = User(self.bot, ctx, user=follower_discord_user)

                    character_follower_dump = follower_user.active_character
                    character_class_name = character_follower_dump.split(";")[1]
                    follower_character = eval(character_class_name)(character_follower_dump)

                    if follower_user.character_1 == follower_user.active_character:
                        follower_column = 'character_1'
                    elif follower_user.character_2 == follower_user.active_character:
                        follower_column = 'character_2'
                    elif follower_user.character_3 == follower_user.active_character:
                        follower_column = 'character_3'
                    else:
                        return

                    for role in follower_discord_user.roles:
                        if role.id in location_roles:
                            await follower_discord_user.remove_roles(role)

                    follower_character.location = traveling_to.capitalize()
                    await follower_discord_user.add_roles(location_role)

                    follower_user.update_value('active_character', follower_character.char_dump)
                    follower_user.update_value(follower_column, follower_character.char_dump)

                await ctx.author.add_roles(location_role)
                await message.edit(content=f"{ctx.author.nick if ctx.author.nick else ctx.author.name} traveled to {traveling_to.capitalize()}" if not character.party else f"{ctx.author.nick if ctx.author.nick else ctx.author.name} and their party of {len(character.party):,} traveled to {traveling_to.capitalize()}")

                await eval(traveling_to.lower())().start_fight(self.bot, ctx, user)
            else:
                continue

    # @commands.command(name="Attack", aliases=[])
    # async def attack_CMD(self, ctx):
    #     await ctx.send("TEST COMMAND -- WILL NOT BE IN BOT SOON")
    #     user = User(self.bot, ctx)
    #
    #     character_dump = user.active_character
    #     character_class_name = character_dump.split(";")[1]
    #     character = eval(character_class_name)(character_dump)
    #     ghost = utils.monsters.Ghost(name="Ghost", location=styx(), level=5, power=12, speed=1, health=10, armor=0)
    #
    #     if user.character_1 == user.active_character:
    #         column = 'character_1'
    #     elif user.character_2 == user.active_character:
    #         column = 'character_2'
    #     elif user.character_3 == user.active_character:
    #         column = 'character_3'
    #     else:
    #         return
    #
    #     character.number = 1
    #     ghost.number = 6
    #
    #     monsters = [ghost]
    #     party = [character]
    #
    #     play_area = pits()
    #
    #     play_area.place_person_on_map(character, (3, 4))
    #     play_area.place_person_on_map(ghost, (7, 4))
    #
    #     while True:
    #         image = play_area.draw_to_map(character, character.last_cords)
    #         play_area.draw_to_map(ghost, ghost.last_cords, image)
    #
    #         files = [discord.File('images/modified/modified_map.png')]
    #         await ctx.send(files=files)
    #
    #         await ctx.send("Where do you want to move? (&move <up | down | left | right>)")
    #         next_move_message = await self.bot.wait_for('message', check=lambda check: check.author.id == ctx.author.id)
    #         next_move = next_move_message.content.lower()
    #         try:
    #             if " " in next_move:
    #                 command, option = next_move.split(" ")
    #             else:
    #                 command, option = next_move, None
    #             if command in ["&m", "&move"]:
    #                 if option in ['u', 'up']:
    #                     moved, err_msg = play_area.move_player(character, (0, -1))
    #                     if moved:
    #                         pass
    #                     else:
    #                         await ctx.send("You cant move further up" if not err_msg else err_msg)
    #                         continue
    #                 elif option in ['d', 'down']:
    #                     moved, err_msg = play_area.move_player(character, (0, 1))
    #                     if moved:
    #                         pass
    #                     else:
    #                         await ctx.send("You cant move further down" if not err_msg else err_msg)
    #                         continue
    #                 elif option in ['l', 'left']:
    #                     moved, err_msg = play_area.move_player(character, (-1, 0))
    #                     if moved:
    #                         pass
    #                     else:
    #                         await ctx.send("You cant move further left" if not err_msg else err_msg)
    #                         continue
    #                 elif option in ['r', 'right']:
    #                     moved, err_msg = play_area.move_player(character, (1, 0))
    #                     if moved:
    #                         pass
    #                     else:
    #                         await ctx.send("You cant move further right" if not err_msg else err_msg)
    #                         continue
    #                 else:
    #                     continue
    #             elif command in ["&a", "&att", "&attack"]:
    #                 near_monster_list = play_area.is_near_monster(character, monsters)
    #                 if not near_monster_list:
    #                     await ctx.send("No monsters near you to attack!")
    #                 elif len(near_monster_list) > 1:
    #                     await ctx.send(f"There are {len(near_monster_list)} monsters near you! What one do you want to attack?\n{', '.join([f'{enum+1}) {monster.name}' for enum, monster in enumerate(near_monster_list)])}")
    #                     while True:
    #                         attacking = await self.bot.wait_for('message', check=lambda check: check.author.id == ctx.author.id)
    #                         try:
    #                             attacking_num = int(attacking)
    #                             if attacking_num in range(len(near_monster_list)):
    #                                 player_damage, weapon = character.attack(near_monster_list[attacking])
    #                                 await ctx.send(f"{character.name} attacked {ghost.name} with {weapon} and hit them for {player_damage} damage! {ghost.name} now has {ghost.health} health left!")
    #                             else:
    #                                 continue
    #                         except ValueError:
    #                             continue
    #                 else:
    #                     player_damage, weapon = character.attack(near_monster_list[0])
    #                     await ctx.send(f"{character.name} attacked {ghost.name} with {weapon} and hit them for {player_damage} damage! {ghost.name} now has {ghost.health} health left!")
    #             elif command in ['&pass']:
    #                 pass
    #             moved, monster_damage = play_area.target_player(ghost, character)
    #             if moved:
    #                 pass
    #             else:
    #                 await ctx.send(f"{character.name} was attacked by {ghost.name} using {monster_damage[1]} for {monster_damage[0]} damage! You now have {character.health} health left")
    #         except ValueError:
    #             continue

    @commands.command(name="Invite", aliases=[])
    async def invite_CMD(self, ctx, user: discord.User):
        party_master_user = User(self.bot, ctx)
        character_dump_master = party_master_user.active_character
        character_class_name = character_dump_master.split(";")[1]
        party_master = eval(character_class_name)(character_dump_master)

        if party_master_user.character_1 == party_master_user.active_character:
            master_column = 'character_1'
        elif party_master_user.character_2 == party_master_user.active_character:
            master_column = 'character_2'
        elif party_master_user.character_3 == party_master_user.active_character:
            master_column = 'character_3'
        else:
            return

        party_follower_user = User(self.bot, ctx, user=user)
        character_dump_follower = party_follower_user.active_character
        character_class_name = character_dump_follower.split(";")[1]
        party_follower = eval(character_class_name)(character_dump_follower)

        if party_follower_user.character_1 == party_follower_user.active_character:
            follower_column = 'character_1'
        elif party_follower_user.character_2 == party_follower_user.active_character:
            follower_column = 'character_2'
        elif party_follower_user.character_3 == party_follower_user.active_character:
            follower_column = 'character_3'
        else:
            return

        if party_follower.location != party_master.location:
            return await ctx.send("To invite a user to your party they must be in the same area as you!")
        if party_follower.in_party:
            return await ctx.send(f"{user.name} is already in a party and can not be invited to a new one until they leave")
        if party_master.party_master and party_master.party_master != ctx.author.id:
            return await ctx.send(f"Only the party master can invite people to the party!")

        reaction_message = await ctx.send(f"{ctx.author.nick if ctx.author.nick else ctx.author.name} has invited you to join their party! Do you want to join?")
        await reaction_message.add_reaction('✅')
        await reaction_message.add_reaction('❌')
        while True:
            reaction, _ = await self.bot.wait_for('reaction_add', check=lambda _, check: check.id == user.id)
            if reaction.emoji == '✅':
                if not party_master.party:
                    party_master.party = []

                party_master.party_master = ctx.author.id
                party_master.in_party = True
                party_master.party = party_master.party + [user.id]

                party_follower.in_party = True
                party_follower.party_master = ctx.author.id

                party_follower_user.update_value(follower_column, party_follower.char_dump)
                party_follower_user.update_value('active_character', party_follower.char_dump)

                party_master_user.update_value(master_column, party_master.char_dump)
                party_master_user.update_value('active_character', party_master.char_dump)

                await ctx.send(f"{user.name} has joined your party {ctx.author.mention}!")
                break
            elif reaction.emoji == '❌':
                await ctx.send(f"{user.name} has declined your party invite {ctx.author.mention}!")
                break
            else:
                continue

    @commands.command(name="Disband", aliases=[])
    async def disband_CMD(self, ctx):
        party_master_user = User(self.bot, ctx)
        character_dump_master = party_master_user.active_character
        character_class_name = character_dump_master.split(";")[1]
        party_master = eval(character_class_name)(character_dump_master)

        if party_master_user.character_1 == party_master_user.active_character:
            master_column = 'character_1'
        elif party_master_user.character_2 == party_master_user.active_character:
            master_column = 'character_2'
        elif party_master_user.character_3 == party_master_user.active_character:
            master_column = 'character_3'
        else:
            return

        if party_master.party:
            for follower in party_master.party:
                party_follower_user = User(self.bot, ctx, user=ctx.guild.get_member(follower))
                character_dump_follower = party_follower_user.active_character
                character_class_name = character_dump_follower.split(";")[1]
                party_follower = eval(character_class_name)(character_dump_follower)

                if party_follower_user.character_1 == party_follower_user.active_character:
                    follower_column = 'character_1'
                elif party_follower_user.character_2 == party_follower_user.active_character:
                    follower_column = 'character_2'
                elif party_follower_user.character_3 == party_follower_user.active_character:
                    follower_column = 'character_3'
                else:
                    return

                party_follower.party_master = None
                party_follower.in_party = False
                party_follower.party = []

                party_follower_user.update_value(follower_column, party_follower.char_dump)
                party_follower_user.update_value('active_character', party_follower.char_dump)

        party_master.party_master = None
        party_master.in_party = False
        party_master.party = []

        party_master_user.update_value(master_column, party_master.char_dump)
        party_master_user.update_value('active_character', party_master.char_dump)

        await ctx.send(f"Okay! I have disbanded your party")

    @commands.command(name="Leave", aliases=[])
    async def leave_CMD(self, ctx):
        party_follower_user = User(self.bot, ctx)
        character_dump_master = party_follower_user.active_character
        character_class_name = character_dump_master.split(";")[1]
        party_follower = eval(character_class_name)(character_dump_master)

        party_master_user = User(self.bot, ctx, user=self.bot.get_user(party_follower.party_master))
        character_dump_master = party_master_user.active_character
        character_class_name = character_dump_master.split(";")[1]
        party_master = eval(character_class_name)(character_dump_master)

        if party_follower_user.character_1 == party_follower_user.active_character:
            follower_column = 'character_1'
        elif party_follower_user.character_2 == party_follower_user.active_character:
            follower_column = 'character_2'
        elif party_follower_user.character_3 == party_follower_user.active_character:
            follower_column = 'character_3'
        else:
            return

        if party_master_user.character_1 == party_master_user.active_character:
            master_column = 'character_1'
        elif party_master_user.character_2 == party_master_user.active_character:
            master_column = 'character_2'
        elif party_master_user.character_3 == party_master_user.active_character:
            master_column = 'character_3'
        else:
            return

        if party_follower.party:
            return await ctx.send("You can not leave the party because you are the party leader! To close the party use `&disband`")

        party_master.party_master = party_follower.party_master
        party_follower.party_master = None
        party_follower.party = []
        party_follower.in_party = False

        party_master.party = [user_id for user_id in party_master.party if user_id != ctx.author.id]

        party_follower_user.update_value(follower_column, party_follower.char_dump)
        party_follower_user.update_value('active_character', party_follower.char_dump)

        party_master_user.update_value(master_column, party_master.char_dump)
        party_master_user.update_value('active_character', party_master.char_dump)

        await ctx.send("Okay, you have left the party!")

    @commands.command(name="Party", aliases=[])
    async def party_CMD(self, ctx):
        party_master_user = User(self.bot, ctx)
        character_dump_master = party_master_user.active_character
        character_class_name = character_dump_master.split(";")[1]
        party_master = eval(character_class_name)(character_dump_master)

        await ctx.send(" ".join([ctx.guild.get_member(user).name for user in party_master.party]) if party_master.party else "Nobody is in your party")

    @commands.command(name="Suggest", aliases=[])
    async def suggest_CMD(self, ctx, *, message):
        suggestion_channel = ctx.guild.get_channel(735415970872557588)
        check_anon = message.split(" ")
        if check_anon[0].lower() in ['-a', '-an', '-ano', '-anon', '-anony', '-anonym', '-anonymo', '-anonymous']:
            by = 'Anonymous'
            message = " ".join(check_anon[1:])
        else:
            by = ctx.author.nick if ctx.author.nick else ctx.author.name
        embed = discord.Embed(color=discord.Color.green())
        embed.add_field(name=f"Suggestion #{len(await suggestion_channel.history().flatten())}", value=message)
        embed.set_author(name=by, icon_url=ctx.author.avatar_url if not by == "Anonymous" else "https://cdn.discordapp.com/attachments/735154858092658758/737148777147662386/anon.png")
        suggestion = await suggestion_channel.send(embed=embed)
        await suggestion.add_reaction('⬆️')
        await suggestion.add_reaction('⬇️')


def setup(bot):
    bot.add_cog(General(bot))
