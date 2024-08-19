def print_messages(recipient, messages, sender, config): 
    if "callback" in config and  config["callback"] is not None:
        callback = config["callback"]
        callback(sender, recipient, messages[-1])
    print(f"Messages sent to: {recipient.name} | num messages: {len(messages)}")
    return False, None  # required to ensure the agent communication flow continues

writer.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
)