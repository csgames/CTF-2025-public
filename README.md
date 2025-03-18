`CTF 2025`
----------------

This is the code of the CTF of 2025. The challenges, solutions and text are all in the challenge directory. If you want to run this with a local CTFd, you can do the following:

First, run this on linux or wsl. Make sure to have Docker installed and running and that your user is part of the docker group.
```
# (Optional) Setup venv
python -m venv .venv
source .venv/bin/activate

# Install tool
pip install ctf-builder

# Start challenge
ctf build
ctf docker start

# CTFd (keep terminal open to keep CTFd running)
ctf ctfd dev

# Stop challenge
ctf docker stop
```