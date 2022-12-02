import sys

def initCfg(env: str) -> dict:
    cfgs = {
        "dev": {
            "appenv": "dev",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///../dev.db",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SECRET_KEY": "%%Dtacva82564^@GJsujjysdGSA",
        },
    }

    try:
        return cfgs[env]
    except KeyError:
        print(f"Env [{env}] does not exist!")
        sys.exit(1)
