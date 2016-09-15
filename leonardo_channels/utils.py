from leonardo_channels import Channel


def send_message(path, msg):

    try:
        Channel(path).send(msg)
    except Exception as e:
        # TODO handle channel error more properly
        raise e
