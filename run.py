from app import app
import os

if __name__ == '__main__':
    app.run(port=os.environ.get('PORT') or 5000)