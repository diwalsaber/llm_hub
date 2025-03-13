import chainlit as cl

@cl.on_chat_start
async def start():
    await cl.Message(content="Bienvenue sur LLM Hub (version minimaliste)!").send()

@cl.on_message
async def main(message: cl.Message):
    await cl.Message(content=f"Vous avez dit: {message.content}").send()