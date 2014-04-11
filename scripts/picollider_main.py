def parse_raw_address(address):
    location, port = address.strip().split(',')
    return (location, int(port))

if __name__ == "__main__":

    import configparser
    import picollider.brain

    CONFIG_LOCATIONS = (
        '/etc/picollider.conf',
        '~/.picollider.conf',
        './picollider.conf',
    )

    cp = configparser.ConfigParser()
    for location in CONFIG_LOCATIONS:
        cp.read(location)

    brain = picollider.brain.Brain( 
        scsynth_address=parse_raw_address(cp['PiCollider']['scsynth_address']),
        message_address=parse_raw_address(cp['PiCollider']['message_address']),
        recipient_addresses=(parse_raw_address(raw) for raw in
                cp['PiCollider']['recipient_addresses'].split(';') if raw),
        nids_start=int(cp['PiCollider']['nids_start']),
        nids_end=int(cp['PiCollider']['nids_end']),
        pan=float(cp['PiCollider']['pan']),
    )

    brain.start()
    input("Press return to stop\n")
    brain.stop()
