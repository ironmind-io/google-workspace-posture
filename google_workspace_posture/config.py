import os
import dotenv
dotenv.load_dotenv()

class ConfigError(Exception):
    pass


def get_config():
    config = {
        'google': {
            'customer_id': os.getenv('GOOGLE_CUSTOMER_ID', ''),
            'admin_email': os.getenv('GOOGLE_ADMIN_EMAIL', ''),
            'api_key': os.getenv('GOOGLE_API_KEY', '')
        }
    }
    validate_config(config)
    return config



def validate_config(c):
    missing_vals = []
    for key, value in c['google'].items():
        if not value:
            missing_vals.append(key)
    if missing_vals:
        raise ConfigError(f"Missing values for: {', '.join(missing_vals)}")


config = get_config()





