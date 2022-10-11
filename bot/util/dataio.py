import json
import os.path


class DataIO(object):
    def __init__(self):
        self.filename = "/opt/data.json"
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump({}, f, indent=4)

    def _get_all_data(self):
        with open(self.filename, "r") as f:
            data = json.load(f)
        return data

    def _save_all_data(self, data: dict):
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def get_delete_targets_in_guild(guild_id: int) -> list | None:
        data = DataIO()._get_all_data()

        if "deletion" not in data:
            return None

        if str(guild_id) in data["deletion"]:
            if len(data["deletion"][str(guild_id)]) == 0:
                return None
            return data["deletion"][str(guild_id)]

        return None

    @staticmethod
    def set_delete_target(guild_id: int, channel_id: int):
        data = DataIO()._get_all_data()

        if "deletion" not in data:
            data["deletion"] = {}

        if str(guild_id) not in data["deletion"]:
            data["deletion"][str(guild_id)] = []

        if channel_id not in data["deletion"][str(guild_id)]:
            data["deletion"][str(guild_id)].append(channel_id)

        DataIO()._save_all_data(data)

    @staticmethod
    def remove_delete_target(guild_id: int, channel_id: int):
        data = DataIO()._get_all_data()

        if "deletion" in data \
                and str(guild_id) in data["deletion"] \
                and channel_id in data["deletion"][str(guild_id)]:
            data["deletion"][str(guild_id)].remove(channel_id)

        DataIO()._save_all_data(data)

    @staticmethod
    def get_notify_roles_in_guild(guild_id: int) -> list | None:
        data = DataIO()._get_all_data()

        if "notify_roles" not in data:
            return None

        if str(guild_id) in data["notify_roles"]:
            if len(data["notify_roles"][str(guild_id)]) == 0:
                return None
            return data["notify_roles"][str(guild_id)]

        return None

    @staticmethod
    def set_notify_role(guild_id: int, role_id: int):
        data = DataIO()._get_all_data()

        if "notify_roles" not in data:
            data["notify_roles"] = {}

        if str(guild_id) not in data["notify_roles"]:
            data["notify_roles"][str(guild_id)] = []

        if role_id not in data["notify_roles"][str(guild_id)]:
            data["notify_roles"][str(guild_id)].append(role_id)

        DataIO()._save_all_data(data)

    @staticmethod
    def remove_notify_roles(guild_id: int, role_id: int):
        data = DataIO()._get_all_data()

        if "notify_roles" in data \
                and str(guild_id) in data["notify_roles"] \
                and role_id in data["notify_roles"][str(guild_id)]:
            data["notify_roles"][str(guild_id)].remove(role_id)

        DataIO()._save_all_data(data)

    @staticmethod
    def get_timeline_chs_in_guild(guild_id: int) -> dict | None:
        data = DataIO()._get_all_data()

        if "timeline_chs" not in data:
            return None

        if str(guild_id) in data["timeline_chs"]:
            if len(data["timeline_chs"][str(guild_id)]) == 0:
                return None
            return {int(parent_channel_id): data for parent_channel_id, data in data["timeline_chs"][str(guild_id)].items()}

        return None

    @staticmethod
    def set_timeline_ch(guild_id: int, parent_channel_id: int, timeline_channel_id: int):
        data = DataIO()._get_all_data()

        if "timeline_chs" not in data:
            data["timeline_chs"] = {}

        if str(guild_id) not in data["timeline_chs"]:
            data["timeline_chs"][str(guild_id)] = {}

        if str(parent_channel_id) not in data["timeline_chs"][str(guild_id)]:
            data["timeline_chs"][str(guild_id)].update({str(parent_channel_id): [timeline_channel_id]})
        else:
            if timeline_channel_id not in data["timeline_chs"][str(guild_id)][str(parent_channel_id)]:
                data["timeline_chs"][str(guild_id)][str(parent_channel_id)].append(timeline_channel_id)

        DataIO()._save_all_data(data)

    @staticmethod
    def remove_timeline_ch(guild_id: int, parent_channel_id: int, timeline_channel_id: int):
        data = DataIO()._get_all_data()

        if "timeline_chs" in data \
                and str(guild_id) in data["timeline_chs"] \
                and str(parent_channel_id) in data["timeline_chs"][str(guild_id)] \
                and timeline_channel_id in data["timeline_chs"][str(guild_id)][str(parent_channel_id)]:
            data["timeline_chs"][str(guild_id)][str(parent_channel_id)].remove(timeline_channel_id)

        DataIO()._save_all_data(data)

    @staticmethod
    def get_keep_ignore_targets_in_guild(guild_id: int) -> dict | None:
        data = DataIO()._get_all_data()

        if "ignore" not in data:
            return None

        if "keep" not in data["ignore"]:
            return None

        if str(guild_id) in data["ignore"]["keep"]:
            if len(data["ignore"]["keep"][str(guild_id)]) == 0:
                return None
            return data["ignore"]["keep"][str(guild_id)]

        return None

    @staticmethod
    def set_keep_ignore_target(*, guild_id: int = None, category_id: int = None, channel_id: int = None, thread_id: int = None):
        if guild_id is None and category_id is None and channel_id is None and thread_id is None:
            raise AttributeError("At least one of the arguments must be set.")

        data = DataIO()._get_all_data()

        if "ignore" not in data:
            data["ignore"] = {}

        if "keep" not in data["ignore"]:
            data["ignore"]["keep"] = {key: [] for key in ["guilds", "categories", "channels", "threads"]}

        if guild_id is not None:
            if "guilds" not in data["ignore"]["keep"]:
                data["ignore"]["keep"]["guilds"] = []

            if guild_id not in data["ignore"]["keep"]["guilds"]:
                data["ignore"]["keep"]["guilds"].append(guild_id)

        if category_id is not None:
            if "categories" not in data["ignore"]["keep"]:
                data["ignore"]["keep"]["categories"] = []

            if category_id not in data["ignore"]["keep"]["categories"]:
                data["ignore"]["keep"]["categories"].append(category_id)

        if channel_id is not None:
            if "channels" not in data["ignore"]["keep"]:
                data["ignore"]["keep"]["channels"] = []

            if channel_id not in data["ignore"]["keep"]["channels"]:
                data["ignore"]["keep"]["channels"].append(channel_id)

        if thread_id is not None:
            if "threads" not in data["ignore"]["keep"]:
                data["ignore"]["keep"]["threads"] = []

            if thread_id not in data["ignore"]["keep"]["threads"]:
                data["ignore"]["keep"]["threads"].append(thread_id)

        DataIO()._save_all_data(data)

    @staticmethod
    def get_notify_ignore_targets() -> dict | None:
        data = DataIO()._get_all_data()

        if "ignore" not in data:
            return None

        if "notify" in data["ignore"]:
            if len(data["ignore"]["notify"]) == 0:
                return None

            return data["ignore"]["notify"]

        return None

    @staticmethod
    def set_notify_ignore_target(*, guild_id: int = None, category_id: int = None, channel_id: int = None, thread_id: int = None):
        if guild_id is None and category_id is None and channel_id is None and thread_id is None:
            raise AttributeError("At least one of the arguments must be set.")

        data = DataIO()._get_all_data()

        if "ignore" not in data:
            data["ignore"] = {}

        if "notify" not in data["ignore"]:
            data["ignore"]["notify"] = {key: [] for key in ["guilds", "categories", "channels", "threads"]}

        if guild_id is not None:
            if "guilds" not in data["ignore"]["notify"]:
                data["ignore"]["notify"]["guilds"] = []

            if guild_id not in data["ignore"]["notify"]["guilds"]:
                data["ignore"]["notify"]["guilds"].append(guild_id)

        if category_id is not None:
            if "categories" not in data["ignore"]["notify"]:
                data["ignore"]["notify"]["categories"] = []

            if category_id not in data["ignore"]["notify"]["categories"]:
                data["ignore"]["notify"]["categories"].append(category_id)

        if channel_id is not None:
            if "channels" not in data["ignore"]["notify"]:
                data["ignore"]["notify"]["channels"] = []

            if channel_id not in data["ignore"]["notify"]["channels"]:
                data["ignore"]["notify"]["channels"].append(channel_id)

        if thread_id is not None:
            if "threads" not in data["ignore"]["notify"]:
                data["ignore"]["notify"]["threads"] = []

            if thread_id not in data["ignore"]["notify"]["threads"]:
                data["ignore"]["notify"]["threads"].append(thread_id)

        DataIO()._save_all_data(data)
