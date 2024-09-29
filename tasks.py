from bot import Bot
from robocorp.tasks import task, teardown

bot = Bot()

@task
def start_bot():
    try:
        bot.start()
    except Exception as e:
        print(f"error occurred: {e}")
        raise

@teardown
def cleanup():
    bot.teardown()

if __name__ == "__main__":
    start_bot()
