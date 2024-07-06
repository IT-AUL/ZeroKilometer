from dotenv import load_dotenv

load_dotenv()


def allowed_file(filename, allowed_extensions):
    return (filename != '') and '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions
