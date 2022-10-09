class MessageTemplates:
    @staticmethod
    def on_thread_create_main():
        return "スレッドが作成されました"

    @staticmethod
    def on_thread_create_roles(guild_id: int):
        if guild_id == 958663674216718366:
            return "\n" \
               "<@&958710640166445067>"
        elif guild_id == 983648664327192576:
            return "\n" \
               "<@&983660150281879572>"
        else:
            return

