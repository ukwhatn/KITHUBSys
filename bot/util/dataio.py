import json


class DataIO(object):
    def __init__(self):
        self.filename = "/opt/data.json"

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

        if str(guild_id) in data:
            return data["deletion"][str(guild_id)]

        return None

    @staticmethod
    def set_delete_target(guild_id: int, channel_id: int):
        data = DataIO()._get_all_data()

        if "deletion" not in data:
            data["deletion"] = {}

        if str(guild_id) not in data:
            data["deletion"][str(guild_id)] = []

        if channel_id not in data["deletion"][str(guild_id)]:
            data["deletion"][str(guild_id)].append(channel_id)

        DataIO()._save_all_data(data)

    @staticmethod
    def remove_delete_target(guild_id: int, channel_id: int):
        data = DataIO()._get_all_data()

        if "deletion" in data and str(guild_id) in data["deletion"] and channel_id in data["deletion"][str(guild_id)]:
            data["deletion"][str(guild_id)].remove(channel_id)

        DataIO()._save_all_data(data)

    @staticmethod
    def get_keep_ignore_targets_in_guild(guild_id: int) -> dict | None:
        data = DataIO()._get_all_data()

        if "ignore" not in data:
            return None

        if "keep" not in data["ignore"]:
            return None

        if str(guild_id) in data["ignore"]["keep"]:
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
    def get_notify_ignore_targets_in_guild(guild_id: int) -> dict | None:
        data = DataIO()._get_all_data()

        if "ignore" not in data:
            return None

        if "notify" not in data["ignore"]:
            return None

        if str(guild_id) in data["ignore"]["notify"]:
            return data["ignore"]["notify"][str(guild_id)]

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

