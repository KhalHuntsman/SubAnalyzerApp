#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Hunter
# Date: February 5th 2026
# Version: 0.1.0

from app import create_app


# Create the Flask application instance
app = create_app()


if __name__ == "__main__":
    # Start the development server
    app.run(
        host="127.0.0.1",
        port=5555,
        debug=True
    )
