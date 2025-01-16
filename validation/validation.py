import re


def validate_connection_string(connection_string) -> bool:
    pattern = re.compile(
        r"^(?:(?P<username>[a-zA-Z0-9_-]+)@)?(?P<ip>(?:\d{1,3}\.){3}\d{1,3})(?::(?P<port>\d{1,5}))?$"
    )

    match = pattern.fullmatch(connection_string)
    if not match:
        return False

    port = match.group("port")
    if port and not (1 <= int(port) <= 65535):
        return False

    ip = match.group("ip")
    if not all(0 <= int(octet) <= 255 for octet in ip.split('.')):
        return False

    return True


def is_valid_docker_id_or_name(identifier: str) -> bool:
    name_pattern = re.compile(r"^[a-zA-Z0-9_.-]+$")

    if not identifier:
        return False

    if len(identifier) == 64 or len(identifier) == 12:
        if all(c in "0123456789abcdef" for c in identifier):
            return True

    if name_pattern.match(identifier):
        return True

    return False
