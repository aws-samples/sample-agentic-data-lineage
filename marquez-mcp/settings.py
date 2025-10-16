from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="MARQUEZ",
    settings_files=["settings.toml"],
)
