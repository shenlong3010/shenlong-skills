from config import parse_config


def main():
    cfg = parse_config("settings.json")
    print(cfg)
