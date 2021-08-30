user_data_structure = {
            "user_id": None,
            "guild_id": None,
            "vip_free": False,
            "version": [1.0, "ashley-db-user-04-2021"],
            "recipes": list(),
            "user": {
                "experience": 0,
                "level": 1,
                "xp_time": None,
                "ranking": "Bronze",
                "titling": "Vagabond",
                "patent": 0,
                "raid": 0,
                "married": False,
                "married_at": None,
                "married_in": None,
                "about": "Mude seu about, usando o comando \"ash about <text>\"",
                "stars": 0,
                "rec": 0,
                "commands": 0,
                "ia_response": False,
                "achievements": list(),
                "stickers": 0
            },
            "treasure": {
                "money": 0,
                "gold": 0,
                "silver": 0,
                "bronze": 0
            },
            "true_money": {
                "blessed": 0,
                "fragment": 0,
                "real": 0,
                "adfly": 0
            },
            "ship": dict(),
            "rank": 0,
            "config": {
                "provinces": None,
                "vip": False,
                "roles": [],
                "points": 0,
                "create_at": None
            },
            "moderation": {
                "credibility": {
                    "ashley": 100,
                    "guilds": {
                        "guild_id": {"points": 100}
                    }
                },
                "warns": {
                      "ashley": {
                            "date": {"status": False, "reason": None, "point": 0}
                      },
                      "guilds": {
                            "date": {"status": False, "reason": None, "author_id": None, "point": 0}
                      }
                },
                "behavior": {
                    "guild_id": {
                        "input": {"author_id": {"reason": None, "date": None}},
                        "output": {"author_id": {"reason": None, "date": None}}
                    }
                },
                "notes": {
                    "guild_id": {"author": None, "date": None, "note": None}
                },
                "door": {
                    "guild_id": {"input": 0, "output": 0}
                }
            },
            "rpg": {
                "vip": False,
                "class": 'default',
                "class_now": None,
                "sex": "male",
                "skin": "default",
                "skins": list(),
                "sub_class": {
                    "paladin": {"level": 1, "xp": 0, "level_max": False},
                    "warrior": {"level": 1, "xp": 0, "level_max": False},
                    "necromancer": {"level": 1, "xp": 0, "level_max": False},
                    "wizard": {"level": 1, "xp": 0, "level_max": False},
                    "warlock": {"level": 1, "xp": 0, "level_max": False},
                    "assassin": {"level": 1, "xp": 0, "level_max": False},
                    "priest": {"level": 1, "xp": 0, "level_max": False}
                },
                "status": {"con": 5, "prec": 5, "agi": 5, "atk": 5, "luk": 0, "pdh": 1},
                "intelligence": 0,
                'items': dict(),
                'skills': [0, 0, 0, 0, 0],
                "armors": {
                    "shoulder": [0, 0, 0, 0, 0, 0],
                    "breastplate": [0, 0, 0, 0, 0, 0],
                    "gloves": [0, 0, 0, 0, 0, 0],
                    "leggings": [0, 0, 0, 0, 0, 0],
                    "boots": [0, 0, 0, 0, 0, 0],
                    "shield": [0, 0, 0, 0, 0, 0],
                    "necklace": [0, 0, 0, 0, 0, 0],
                    "earring": [0, 0, 0, 0, 0, 0],
                    "ring": [0, 0, 0, 0, 0, 0]
                },
                'equipped_items': {
                    "shoulder": None,
                    "breastplate": None,
                    "gloves": None,
                    "leggings": None,
                    "boots": None,
                    "consumable": None,
                    "sword": None,
                    "shield": None,
                    "necklace": None,
                    "earring": None,
                    "ring": None
                },
                "active": False,
                "activated_at": None,
                "quests": dict()
            },
            "pet": {
                "status": False,
                "pet_equipped": None,
                "pet_bag": list(),
                "pet_skin_status": None,
                "pet_skin": None
            },
            "inventory": {
                "medal": 0,
                "rank_point": 0,
                "coins": 100
            },
            "artifacts": dict(),
            "box": {"status": {"active": False, "secret": 0, "ur": 0, "sr": 0, "r": 0, "i": 0, "c": 0}},
            "security": {
                "commands": 0,
                "commands_today": 0,
                "last_command": None,
                "last_channel": None,
                "last_verify": None,
                "last_blocked": None,
                "warns": {
                    "80": False,
                    "85": False,
                    "90": False,
                    "95": False,
                    "100": False
                },
                "strikes": 0,
                "strikes_today": 0,
                "captcha_code": None,
                "self_baned": False,
                "strikes_to_ban": 0,
                "status": True,
                "blocked": False
            },
            "statistic": {
                "pvp_total": 0,
                "pvp_win": 0,
                "pvp_lose": 0,
                "battle_total": 0,
                "battle_win": 0,
                "battle_lose": 0,
                "raid_total": 0,
                "raid_max": 0,
                "raid_lose": 0,
                "otk": 0,
                "hit_max": 0,
                "critical": 0,
                "critical_max": 0,
                "trade": 0,
                "give": 0,
                "pay": 0,
                "boxes": 0,
                "boxes_finished": 0,
                "boosters": 0,
                "crafts": 0
            },
            "reward": dict(),
            "cooldown": dict(),
            "event": dict(),
            "research": dict(),
            "stickers": dict()
}

guild_data_structure = {
            "guild_id": None,
            "vip": False,
            "vip_free": False,
            "version": [1.0, "ashley-db-user-04-2021"],
            "available": 0,
            "webhook": None,
            "event": {
                "Capsule": {
                    "WrathofNatureCapsule": 0,
                    "UltimateSpiritCapsule": 0,
                    "SuddenDeathCapsule": 0,
                    "InnerPeacesCapsule": 0,
                    "EternalWinterCapsule": 0,
                    "EssenceofAsuraCapsule": 0,
                    "DivineCalderaCapsule": 0,
                    "DemoniacEssenceCapsule": 0
                },
                "points": 0
            },
            "data": {
                "commands": 0,
                "ranking": "Bronze",
                "accounts": 0,
                "create_at": None,
                "total_money": 0,
                "total_gold": 0,
                "total_silver": 0,
                "total_bronze": 0,
            },
            "treasure": {
                "total_money": 0,
                "total_gold": 0,
                "total_silver": 0,
                "total_bronze": 0
            },
            "log_config": {
                "log": False,
                "log_channel_id": None,
                "msg_delete": True,
                "msg_edit": True,
                "channel_edit_topic": True,
                "channel_edit_name": True,
                "channel_created": True,
                "channel_deleted": True,
                "channel_edit": True,
                "role_created": True,
                "role_deleted": True,
                "role_edit": True,
                "guild_update": True,
                "member_edit_avatar": True,
                "member_edit_nickname": True,
                "member_voice_entered": True,
                "member_voice_exit": True,
                "member_ban": True,
                "member_unBan": True,
                "emoji_update": True
            },
            "ia_config": {
                "auto_msg": False,
            },
            "bot_config": {
                "ash_draw": False,
                "ash_draw_id": None,
            },
            "func_config": {
                "cont_users": False,
                "cont_users_id": None,
                "member_join": False,
                "member_join_id": None,
                "member_remove": False,
                "member_remove_id": None,
                "level_up_channel": False,
                "level_up_channel_id": None,
            },
            "moderation": {
                "status": False,
                "moderation_log": False,
                "moderation_channel_id": None,
                "bad_word": False,
                "bad_word_list": list(),
                "flood": False,
                "flood_channels": list(),
                "ping": False,
                "ping_channels": list(),
                "join_system": {
                    "join_system": False,
                    "join_system_channel_door": None,
                    "join_system_channel_log": None,
                    "join_system_role": None,
                },
                "prison": {
                    "status": False,
                    "prison_channel": None,
                    "prison_role": None,
                    "prisoners": {"id": {"time": 0, "reason": None, "roles": list()}}
                }
            },
            "command_locked": {
                "status": False,
                "while_list": list(),
                "black_list": list()
            }
}
