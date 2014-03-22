if __name__ == "__main__":

    import configparser
    import picollider.brain

    CONFIG_LOCATIONS = (
        '/etc/picollider.conf',
        '~/.picollider.conf',
    )

    cp = configparser.ConfigParser()
    for location in CONFIG_LOCATIONS:
        cp.read(location)

    brain = picollider.brain.Brain( 
        scsynth_server = cp['PiCollider']['scsynth_server'],
        scsynth_port = int(cp['PiCollider']['scsynth_port']),
        message_server = cp['PiCollider']['message_server'],
        message_recipients = cp['PiCollider']['message_recipients'].split(',')
        message_port = int(cp['PiCollider']['message_port'])
    )

    brain.main()
