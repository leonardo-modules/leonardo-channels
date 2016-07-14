from leonardo_channels import Channel


def send_message(path, msg):

    try:
        Channel(path).send(msg)
    except:
        # TODO handle channel error more properly
        pass
