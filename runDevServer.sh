#! /bin/zsh

export FLASK_APP="sigs:makeApp('dev')"
export FLASK_ENV="development"
flask run
