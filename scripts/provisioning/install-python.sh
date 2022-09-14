#!/usr/bin/env bash

# Run the installer
curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash

# Update the bashrc file
cat >> ~/.bashrc <<'EOL'
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"

# Down arrow for next history, Up arrow for previous history.
if [[ $- == *i* ]]
then
    bind '"\e[A": history-search-backward'
    bind '"\e[B": history-search-forward'
fi

# Activate venv if exists.
if [ -d "/home/vagrant/.cache/pypoetry" ]
then
    source /home/vagrant/.cache/pypoetry/virtualenvs/apihub-users-79pwuLWT-py3.8/bin/activate
fi
EOL

################### Export the env vars #####################
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"

################# Use pyenv to install Python ################
pyenv install 3.8.10

pyenv global 3.8.10
